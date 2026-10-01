"""Authentication API endpoints conforming to docs/api-auth.md (V1 contract)."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, Header, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.session import get_db
from app.models.cart import Cart, CartItem
from app.models.catalogue import ProductVariant
from app.models.user import MagicLinkToken, User, UserIdentity, UserSession
from app.schemas.auth import (
    AuthResponse,
    EmailStartRequest,
    EmailStartResponse,
    FacebookAuthRequest,
    GoogleAuthRequest,
    UserOut,
)
from app.services.notification.service import dispatch_magic_link_background

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_COOKIE_NAME = "session_token"
SESSION_MAX_AGE = 30 * 24 * 3600  # 30 days
MAGIC_LINK_EXPIRY_MINUTES = 15
MAGIC_LINK_COOLDOWN_SECONDS = 60  # rate-limit: one request per email per minute
MAGIC_LINK_ALLOWED_RETURN_PATHS = {"/", "/shop", "/account", "/orders", "/wishlist", "/checkout"}


def ensure_utc(dt: datetime | None) -> datetime:
    """Ensure datetime has UTC timezone to avoid SQLite tz-naive errors."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _get_session_token(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    authorization: str | None = Header(default=None),
    x_session_token: str | None = Header(default=None),
) -> str | None:
    """Extract session token from cookie or header."""
    if session_token:
        return session_token
    if x_session_token:
        return x_session_token
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return None


def get_current_user(
    token: str | None = Depends(_get_session_token),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to retrieve currently authenticated user or raise 401."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    now = datetime.now(timezone.utc)
    session = (
        db.query(UserSession)
        .options(joinedload(UserSession.user).joinedload(User.identities))
        .filter(
            UserSession.session_token == token,
            UserSession.is_revoked.is_(False),
        )
        .first()
    )

    if not session or ensure_utc(session.expires_at) <= now or not session.user or session.user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again.",
        )

    return session.user


def get_optional_current_user(
    token: str | None = Depends(_get_session_token),
    db: Session = Depends(get_db),
) -> User | None:
    """Dependency to retrieve authenticated user if present, or None."""
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to retrieve authenticated user with ADMIN role or raise 403."""
    if getattr(current_user, "role", "CUSTOMER") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def _to_user_out(user: User) -> UserOut:
    """Convert User ORM to UserOut schema."""
    identities = [i.provider for i in user.identities] if user.identities else []
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=getattr(user, "role", "CUSTOMER") or "CUSTOMER",
        status=user.status,
        identities=identities,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def _merge_guest_cart_to_user(db: Session, user_id: int, guest_token: str | None) -> bool:
    """Merge active guest cart into authenticated user cart upon login (Section 6)."""
    if not guest_token:
        return False

    guest_cart = (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.variant))
        .filter(Cart.guest_token == guest_token, Cart.status == "ACTIVE")
        .first()
    )

    if not guest_cart or not guest_cart.items:
        return False

    user_cart = (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.variant))
        .filter(Cart.user_id == user_id, Cart.status == "ACTIVE")
        .first()
    )

    if not user_cart:
        # Assign guest cart directly to user
        guest_cart.user_id = user_id
        db.commit()
        return True

    # Deterministic merge rule: quantity = min(guest_qty + user_qty, stock)
    for g_item in guest_cart.items:
        existing = next(
            (
                u_item
                for u_item in user_cart.items
                if u_item.product_variant_id == g_item.product_variant_id
                and (u_item.personalization_json or {}) == (g_item.personalization_json or {})
            ),
            None,
        )

        stock = g_item.variant.stock_quantity if g_item.variant else 10
        if existing:
            existing.quantity = min(existing.quantity + g_item.quantity, stock)
        else:
            merged_qty = min(g_item.quantity, stock)
            if merged_qty > 0:
                user_cart.items.append(
                    CartItem(
                        product_variant_id=g_item.product_variant_id,
                        quantity=merged_qty,
                        personalization_json=g_item.personalization_json or {},
                    )
                )

    guest_cart.status = "CONVERTED"
    db.commit()
    return True


# -----------------------------------------------------------------------------
# Authentication Endpoints (V1 Contract: Email Magic Link, Google, Facebook)
# -----------------------------------------------------------------------------

@router.post("/email/start", response_model=EmailStartResponse, status_code=status.HTTP_202_ACCEPTED)
def start_email_login(
    payload: EmailStartRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> EmailStartResponse:
    """Send a single-use magic sign-in link via email. Always returns generic non-enumerating 202."""
    now = datetime.now(timezone.utc)
    email = payload.email.strip().lower()

    # Rate limiting: check recent magic link token for this email within cooldown window
    cutoff = now - timedelta(seconds=MAGIC_LINK_COOLDOWN_SECONDS)
    recent_token = (
        db.query(MagicLinkToken)
        .filter(
            MagicLinkToken.email == email,
            MagicLinkToken.created_at >= cutoff,
        )
        .first()
    )

    is_dev = (
        settings.app_env == "development"
        or os.getenv("TESTING", "false").lower() == "true"
    )

    dev_magic_link: str | None = None

    if not recent_token:
        # Generate cryptographically secure 32-byte URL-safe token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        token_record = MagicLinkToken(
            email=email,
            token_hash=token_hash,
            created_at=now,
            expires_at=now + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES),
            is_used=False,
        )
        db.add(token_record)
        db.commit()

        api_base = settings.public_api_url.rstrip("/")
        magic_link = f"{api_base}/api/v1/auth/email/verify?token={raw_token}"
        if is_dev:
            dev_magic_link = magic_link

        # Dispatch email asynchronously without logging raw token
        background_tasks.add_task(
            dispatch_magic_link_background,
            email,
            magic_link,
            MAGIC_LINK_EXPIRY_MINUTES,
        )

    return EmailStartResponse(
        message="If the email address is valid, a sign-in link has been sent.",
        dev_magic_link=dev_magic_link,
    )


@router.get("/email/verify")
def verify_email_magic_link(
    token: str | None = None,
    returnTo: str | None = None,
    guest_cart_token: str | None = Cookie(default=None),
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Consume a magic-link token, authenticate/link user, merge guest cart, and redirect."""
    now = datetime.now(timezone.utc)
    fallback_redirect = f"{settings.frontend_url.rstrip('/')}/?error=invalid_link"

    if not token or len(token) < 16:
        return RedirectResponse(url=fallback_redirect, status_code=status.HTTP_303_SEE_OTHER)

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    token_record = (
        db.query(MagicLinkToken)
        .filter(MagicLinkToken.token_hash == token_hash)
        .first()
    )

    if not token_record or token_record.is_used or ensure_utc(token_record.expires_at) <= now:
        return RedirectResponse(url=fallback_redirect, status_code=status.HTTP_303_SEE_OTHER)

    # Invalidate token atomically
    token_record.is_used = True
    token_record.used_at = now
    db.commit()

    # Unified user lookup / creation
    email = token_record.email
    user = (
        db.query(User)
        .options(joinedload(User.identities))
        .filter(User.email == email)
        .first()
    )

    if not user:
        name_prefix = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        user = User(
            email=email,
            name=name_prefix,
            status="ACTIVE",
            last_login_at=now,
        )
        db.add(user)
        db.flush()

        identity = UserIdentity(
            user_id=user.id,
            provider="email",
            provider_subject=email,
        )
        db.add(identity)
    else:
        user.last_login_at = now
        has_email_identity = any(i.provider == "email" for i in (user.identities or []))
        if not has_email_identity:
            identity = UserIdentity(
                user_id=user.id,
                provider="email",
                provider_subject=email,
            )
            db.add(identity)

    # Create server session
    session_token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=now + timedelta(days=30),
        is_revoked=False,
    )
    db.add(session)
    db.commit()
    db.refresh(user)

    # Auto-merge guest cart if token present
    active_cart_token = guest_cart_token or x_cart_token
    _merge_guest_cart_to_user(db, user.id, active_cart_token)

    # Validate safe returnTo path
    target_path = "/"
    if returnTo and returnTo.startswith("/") and not returnTo.startswith("//") and ":" not in returnTo:
        target_path = returnTo

    target_url = f"{settings.frontend_url.rstrip('/')}{target_path}"
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)

    # Set HttpOnly, SameSite=Lax session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        domain=settings.cookie_domain,
    )

    return response




def _verify_google_credential(
    credential: str,
    fallback_sub: str | None = None,
    fallback_email: str | None = None,
    fallback_name: str | None = None,
) -> tuple[str, str | None, str | None]:
    """Verify Google ID token or fallback to provided claims in dev/mock mode."""
    is_test = os.getenv("TESTING", "false").lower() == "true" or credential.startswith("mock_")
    if not is_test and settings.google_client_id and "." in credential:
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}")
                if r.status_code == 200:
                    info = r.json()
                    aud = info.get("aud")
                    if aud != settings.google_client_id:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Google token audience.",
                        )
                    return (
                        info.get("sub", fallback_sub or secrets.token_hex(8)),
                        info.get("email", fallback_email),
                        info.get("name", fallback_name or "Google User"),
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired Google ID token.",
                    )
        except HTTPException:
            raise
        except Exception:
            pass

    if settings.app_env == "production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication token could not be verified in production.",
        )

    is_mock = credential.startswith("mock_") or settings.app_env == "development"
    sub = fallback_sub or (credential if credential.startswith("mock_") else f"google_{secrets.token_hex(8)}")
    email = fallback_email or ("anupama.demo@gmail.com" if is_mock else None)
    name = fallback_name or ("Anupama Sharma (Google)" if is_mock else "Google User")
    return sub, email, name


def _verify_facebook_token(
    access_token: str,
    fallback_id: str | None = None,
    fallback_email: str | None = None,
    fallback_name: str | None = None,
) -> tuple[str, str | None, str | None]:
    """Verify Facebook User Access Token via Graph API or fallback in dev/mock mode."""
    is_test = os.getenv("TESTING", "false").lower() == "true" or access_token.startswith("mock_")
    if not is_test and settings.facebook_app_id:
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(
                    "https://graph.facebook.com/me",
                    params={"fields": "id,name,email", "access_token": access_token},
                )
                if r.status_code == 200:
                    info = r.json()
                    fb_id = info.get("id") or fallback_id or secrets.token_hex(8)
                    email = info.get("email") or fallback_email
                    name = info.get("name") or fallback_name or "Facebook User"
                    return fb_id, email, name
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired Facebook access token.",
                    )
        except HTTPException:
            raise
        except Exception:
            pass

    if settings.app_env == "production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Facebook authentication token could not be verified in production.",
        )

    is_mock = access_token.startswith("mock_") or settings.app_env == "development"
    fb_id = fallback_id or (access_token if access_token.startswith("mock_") else f"fb_{secrets.token_hex(8)}")
    email = fallback_email or ("anupama.demo@facebook.com" if is_mock else None)
    name = fallback_name or ("Anupama Sharma (Facebook)" if is_mock else "Facebook User")
    return fb_id, email, name


@router.post("/google", response_model=AuthResponse)
def google_auth(
    payload: GoogleAuthRequest,
    response: Response,
    guest_cart_token: str | None = Cookie(default=None),
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthResponse:
    """One-Click Google Authentication with Unified User Model."""
    now = datetime.now(timezone.utc)

    google_sub, email, name = _verify_google_credential(
        credential=payload.credential,
        fallback_sub=payload.sub,
        fallback_email=payload.email,
        fallback_name=payload.name,
    )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google profile must contain a verified email address.",
        )

    # 1. Check if identity already exists
    identity = (
        db.query(UserIdentity)
        .options(joinedload(UserIdentity.user).joinedload(User.identities))
        .filter(UserIdentity.provider == "google", UserIdentity.provider_subject == google_sub)
        .first()
    )

    if identity:
        user = identity.user
        user.last_login_at = now
        if not user.email:
            user.email = email
    else:
        # 2. Check if user exists by email (unify account)
        user = db.query(User).options(joinedload(User.identities)).filter(User.email == email).first()
        if user:
            user.last_login_at = now
            if name and not user.name:
                user.name = name
            # Link Google identity
            new_id = UserIdentity(user_id=user.id, provider="google", provider_subject=google_sub)
            db.add(new_id)
        else:
            # 3. Create fresh User and Identity
            user = User(
                name=name,
                email=email,
                status="ACTIVE",
                last_login_at=now,
            )
            db.add(user)
            db.flush()

            new_id = UserIdentity(user_id=user.id, provider="google", provider_subject=google_sub)
            db.add(new_id)

    # Create server session
    session_token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=now + timedelta(days=30),
        is_revoked=False,
    )
    db.add(session)
    db.commit()
    db.refresh(user)

    # Set HttpOnly, SameSite=Lax session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        domain=settings.cookie_domain,
    )

    # Auto-merge guest cart
    active_cart_token = guest_cart_token or x_cart_token
    cart_merged = _merge_guest_cart_to_user(db, user.id, active_cart_token)

    return AuthResponse(
        user=_to_user_out(user),
        message="Google login successful",
        cart_merged=cart_merged,
    )


@router.post("/facebook", response_model=AuthResponse)
def facebook_auth(
    payload: FacebookAuthRequest,
    response: Response,
    guest_cart_token: str | None = Cookie(default=None),
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Facebook (Meta) Authentication with Unified User Model."""
    now = datetime.now(timezone.utc)

    fb_id, email, name = _verify_facebook_token(
        access_token=payload.access_token,
        fallback_id=payload.user_id,
        fallback_email=payload.email,
        fallback_name=payload.name,
    )

    # 1. Check if Facebook identity already exists
    identity = (
        db.query(UserIdentity)
        .options(joinedload(UserIdentity.user).joinedload(User.identities))
        .filter(UserIdentity.provider == "facebook", UserIdentity.provider_subject == fb_id)
        .first()
    )

    if identity:
        user = identity.user
        user.last_login_at = now
        if email and not user.email:
            user.email = email
        if name and not user.name:
            user.name = name
    else:
        # 2. Check if user exists by email (unify account)
        user = None
        if email:
            user = db.query(User).options(joinedload(User.identities)).filter(User.email == email).first()

        if user:
            user.last_login_at = now
            if name and not user.name:
                user.name = name
            # Link Facebook identity
            new_id = UserIdentity(user_id=user.id, provider="facebook", provider_subject=fb_id)
            db.add(new_id)
        else:
            # 3. Create fresh User and Identity
            user = User(
                name=name or "Facebook User",
                email=email,
                status="ACTIVE",
                last_login_at=now,
            )
            db.add(user)
            db.flush()

            new_id = UserIdentity(user_id=user.id, provider="facebook", provider_subject=fb_id)
            db.add(new_id)

    # Create server session
    session_token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=now + timedelta(days=30),
        is_revoked=False,
    )
    db.add(session)
    db.commit()
    db.refresh(user)

    # Set HttpOnly, SameSite=Lax session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        domain=settings.cookie_domain,
    )

    # Auto-merge guest cart
    active_cart_token = guest_cart_token or x_cart_token
    cart_merged = _merge_guest_cart_to_user(db, user.id, active_cart_token)

    return AuthResponse(
        user=_to_user_out(user),
        message="Facebook login successful",
        cart_merged=cart_merged,
    )



@router.get("/me", response_model=UserOut)
def get_current_customer(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """Retrieve authenticated customer profile from session cookie."""
    return _to_user_out(current_user)


@router.post("/logout")
def logout(
    response: Response,
    token: str | None = Depends(_get_session_token),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoke session and clear HttpOnly cookie."""
    if token:
        db.query(UserSession).filter(UserSession.session_token == token).update({"is_revoked": True})
        db.commit()

    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/", domain=settings.cookie_domain)
    return {"status": "ok", "message": "Logged out successfully"}
