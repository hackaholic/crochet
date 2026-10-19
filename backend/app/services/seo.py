"""Service for Dynamic SEO Metadata Resolution, XML Sitemap generation, and Robots.txt."""

from datetime import datetime, timezone
import os
from typing import Any, Literal
from urllib.parse import parse_qs, urlparse
from xml.sax.saxutils import escape as xml_escape
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.services.product_information import resolve_product_information
from app.core.images import build_image_url
from app.services.media import build_media_metadata, get_image_dimensions, get_media_manifest_hash
from app.models.catalogue import (
    Category,
    Collection,
    Product,
    ProductCategory,
    ProductInformationDefaults,
    ProductVariant,
    Review,
    UrlRedirect,
)
from app.models.storefront import BrandSettings
from app.schemas.seo import (
    SeoAggregateRating,
    SeoBrandInfo,
    SeoBreadcrumb,
    SeoCategoryEntity,
    SeoCollectionEntity,
    SeoFaqItem,
    SeoMetadataOut,
    SeoPageSnapshotItem,
    SeoProductEntity,
    SeoProductVariant,
    SeoReturnPolicy,
    SeoRouteInventoryOut,
    SeoRouteItem,
    SeoShippingInfo,
    SeoSnapshotResponse,
)
from app.schemas.merchant import (
    MerchantFeedItemOut,
    MerchantFeedResponse,
)

PRIVATE_PREFIXES = (
    "/account",
    "/admin",
    "/cart",
    "/checkout",
    "/wishlist",
    "/auth",
    "/login",
    "/orders",
    "/track",
    "/reset-password",
)

PRIVATE_PAGE_TITLES = {
    "/account": "My Account",
    "/cart": "Shopping Cart",
    "/checkout": "Checkout",
    "/wishlist": "My Wishlist",
    "/admin": "Store Administration",
    "/login": "Sign In",
    "/auth": "Authentication",
    "/orders": "My Orders",
    "/track": "Track Order",
}

POLICY_ROUTES = {
    "/shipping-policy": {
        "title": "Shipping Policy | Sulocraft",
        "description": "Shipping timelines, standard rates, insured courier delivery across India, and tracking policies for Sulocraft handcrafted creations.",
        "h1": "Shipping Policy",
        "breadcrumb": "Shipping Policy",
    },
    "/return-policy": {
        "title": "Return & Refund Policy | Sulocraft",
        "description": "Information regarding returns, transit damage resolution, and refunds for Sulocraft artisanal products.",
        "h1": "Return & Refund Policy",
        "breadcrumb": "Return Policy",
    },
    "/privacy-policy": {
        "title": "Privacy Policy | Sulocraft",
        "description": "How Sulocraft collects, protects, and handles your personal information with strict data privacy standards.",
        "h1": "Privacy Policy",
        "breadcrumb": "Privacy Policy",
    },
    "/terms": {
        "title": "Terms of Service | Sulocraft",
        "description": "Terms and conditions governing purchases, payments, and site usage on Sulocraft.",
        "h1": "Terms of Service",
        "breadcrumb": "Terms of Service",
    },
    "/faq": {
        "title": "FAQs | Handcrafted Crochet Care & Orders | Sulocraft",
        "description": "Frequently asked questions about Sulocraft crochet creations, materials, custom gifting, care instructions, and order tracking.",
        "h1": "Frequently Asked Questions",
        "breadcrumb": "FAQs",
    },
}

POLICY_ALIASES = {
    "/info/shipping": "/shipping-policy",
    "/info/refund": "/return-policy",
    "/info/privacy": "/privacy-policy",
    "/info/terms": "/terms",
    "/info/faq": "/faq",
}


def validate_public_origin(origin: str | None, is_production: bool = False, allow_http: bool = False) -> str:
    """Validate and normalize a public storefront origin URL.

    Rules:
    - Must be a valid URL with http or https protocol.
    - Credentials (username/password), query parameters, or fragments are strictly rejected.
    - Path must be empty or root ('/').
    - If is_production or not allow_http: must use HTTPS, and cannot be localhost or loopback.
    - Strips any trailing slash to return normalized origin string.
    """
    if not origin or not str(origin).strip():
        raise ValueError("Missing public origin")
    raw = str(origin).strip()
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid origin protocol: {parsed.scheme}")
    if (is_production or not allow_http) and parsed.scheme != "https":
        raise ValueError("Public origin must use HTTPS")
    if parsed.username or parsed.password:
        raise ValueError("Public origin must not contain credentials")
    if parsed.query or parsed.fragment:
        raise ValueError("Public origin must not contain search query or fragment")
    if parsed.path and parsed.path != "/":
        raise ValueError(f"Public origin must not contain a path component: {parsed.path}")
    if (is_production or not allow_http) and parsed.hostname in ("localhost", "127.0.0.1", "::1", "[::1]"):
        raise ValueError(f"Public HTTPS origin cannot be localhost or loopback: {parsed.hostname}")
    return f"{parsed.scheme}://{parsed.netloc}"


class SeoService:
    """Handles dynamic SEO metadata resolution, sitemap XML generation, and robots directives."""

    @staticmethod
    def _get_robots_directive(is_public_and_valid: bool = True) -> Literal["index,follow", "noindex,nofollow"]:
        """Determine robots indexability according to environment and route validity (DEC-005-7).
        
        Rules:
        - Non-public or invalid routes always return 'noindex,nofollow'.
        - Development and preprod default to 'noindex,nofollow'.
        - Production requires explicit SEO_INDEXING_ENABLED='true' to index; fails closed to 'noindex,nofollow' if missing or false.
        - Explicit valid SEO_INDEXING_ENABLED overrides environment defaults.
        """
        if not is_public_and_valid:
            return "noindex,nofollow"

        indexing_raw = os.getenv("SEO_INDEXING_ENABLED")
        if indexing_raw is not None:
            val = indexing_raw.strip().lower()
            if val in ("true", "1", "yes"):
                return "index,follow"
            return "noindex,nofollow"

        env = os.getenv("APP_ENV", "development").lower()
        if env in ("staging", "preprod", "dev", "development", "test"):
            return "noindex,nofollow"

        if env == "production":
            # In production without explicit SEO_INDEXING_ENABLED=true, fail closed
            return "noindex,nofollow"

        return "noindex,nofollow"

    @staticmethod
    def _build_canonical_url(path: str) -> str:
        """Construct full absolute canonical URL based on configured public base URL."""
        base = SeoService.get_canonical_base_url().rstrip("/")
        clean_path = path if path.startswith("/") else f"/{path}"
        return f"{base}{clean_path}"

    @staticmethod
    def _get_brand_info(db: Session) -> SeoBrandInfo:
        """Fetch storewide brand settings and social profile links.
        
        Conforms strictly to truthful data principles:
        - Never fabricates unverified legalName, social handles, or contact links.
        - Excludes direct contact channels (e.g. WhatsApp) from sameAs identity profiles.
        - Nullable fields remain None when unconfigured in the database.
        """
        brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
        if not brand:
            return SeoBrandInfo(
                name="Sulocraft",
                legal_name=None,
                logo_url=build_image_url("brand/sulocraft-logo.png"),
                owner_name=None,
                instagram_url=None,
                whatsapp_url=None,
                same_as=[],
            )

        same_as: list[str] = []
        if brand.instagram_url and brand.instagram_url.strip():
            same_as.append(brand.instagram_url.strip())

        # legal_name has no approved column in BrandSettings; return None unless dynamically present and non-empty
        raw_legal_name = getattr(brand, "legal_name", None)
        legal_name = str(raw_legal_name).strip() if raw_legal_name and str(raw_legal_name).strip() else None

        logo_url = build_image_url(brand.logo_url.strip()) if (brand.logo_url and brand.logo_url.strip()) else None
        owner_name = brand.owner_name.strip() if (brand.owner_name and brand.owner_name.strip()) else None
        instagram_url = brand.instagram_url.strip() if (brand.instagram_url and brand.instagram_url.strip()) else None
        whatsapp_url = brand.whatsapp_url.strip() if (brand.whatsapp_url and brand.whatsapp_url.strip()) else None

        return SeoBrandInfo(
            name=brand.name.strip() if (brand.name and brand.name.strip()) else "Sulocraft",
            legal_name=legal_name,
            logo_url=logo_url,
            owner_name=owner_name,
            instagram_url=instagram_url,
            whatsapp_url=whatsapp_url,
            same_as=same_as,
        )

    @staticmethod
    def get_products_aggregate_ratings(db: Session, product_ids: list[int]) -> dict[int, SeoAggregateRating]:
        """Derive truthful aggregate rating for multiple products from genuine review records.
        
        Returns a mapping from product_id to SeoAggregateRating. Products with no genuine
        review records will not be present in the returned dictionary.
        Uses Section 5.22 eligibility semantics.
        """
        if not product_ids:
            return {}

        review_stats = (
            db.query(
                Review.product_id,
                func.count(Review.id).label("count"),
                func.avg(Review.rating).label("avg_rating"),
            )
            .filter(Review.product_id.in_(product_ids))
            .group_by(Review.product_id)
            .all()
        )

        result: dict[int, SeoAggregateRating] = {}
        for r in review_stats:
            if r.product_id is not None and r.count and r.count > 0:
                result[r.product_id] = SeoAggregateRating(
                    ratingValue=round(float(r.avg_rating), 1),
                    reviewCount=int(r.count),
                    bestRating=5.0,
                    worstRating=1.0,
                    provenance="VERIFIED_REVIEWS",
                )
        return result

    @staticmethod
    def resolve_path(db: Session, path_str: str) -> SeoMetadataOut:
        """Resolve SEO metadata for any incoming path or URL conforming to docs/api-seo.md."""
        raw_path = (path_str or "/").strip()
        parsed = urlparse(raw_path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        query_params = parse_qs(parsed.query)
        brand_info = SeoService._get_brand_info(db)

        # 0. Canonical Aliases & URL Redirects (Task 5.19)
        redirect_entry = (
            db.query(UrlRedirect)
            .filter(UrlRedirect.old_path == path)
            .first()
        )
        if redirect_entry:
            if redirect_entry.status_code == 301 and redirect_entry.target_path:
                target = redirect_entry.target_path
                return SeoMetadataOut(
                    title="Moved Permanently | Sulocraft",
                    description="This page has moved to a new permanent location.",
                    canonicalPath=target,
                    canonicalUrl=SeoService._build_canonical_url(target),
                    robots="noindex,nofollow",
                    h1="Moved Permanently",
                    imageUrl=None,
                    imageAlt=None,
                    pageType="website",
                    breadcrumbs=[],
                    brand=brand_info,
                    httpStatus=301,
                    redirectTo=target,
                )
            elif redirect_entry.status_code == 410:
                return SeoMetadataOut(
                    title="Discontinued | Sulocraft",
                    description="This item or page has been discontinued.",
                    canonicalPath=path,
                    canonicalUrl=SeoService._build_canonical_url(path),
                    robots="noindex,nofollow",
                    h1="Discontinued",
                    imageUrl=None,
                    imageAlt=None,
                    pageType="website",
                    breadcrumbs=[],
                    brand=brand_info,
                    httpStatus=410,
                    redirectTo=None,
                )

        # 1. Private Routes -> noindex,nofollow
        for prefix in PRIVATE_PREFIXES:
            if path == prefix or path.startswith(f"{prefix}/"):
                page_title = PRIVATE_PAGE_TITLES.get(prefix, "Private Page")
                return SeoMetadataOut(
                    title=f"{page_title} | Sulocraft",
                    description="Private user and store management page.",
                    canonicalPath=path,
                    canonicalUrl=SeoService._build_canonical_url(path),
                    robots="noindex,nofollow",
                    h1=page_title,
                    imageUrl=None,
                    imageAlt=None,
                    pageType="website",
                    breadcrumbs=[],
                    brand=brand_info,
                )

        # 2. Homepage -> /
        if path == "/":
            brand_name = brand_info.name
            hero_meta = build_media_metadata("hero/heritage.png", alt_text=f"{brand_name} handcrafted crochet creations in India")
            return SeoMetadataOut(
                title=f"{brand_name} | Handcrafted Crochet Gifts, Flower Bouquets & Amigurumi in India",
                description=f"Handcrafted crochet gifts, flower bouquets, amigurumi keepsakes, and home decor by {brand_name} in India.",
                canonicalPath="/",
                canonicalUrl=SeoService._build_canonical_url("/"),
                robots=SeoService._get_robots_directive(True),
                h1="Handcrafted Heirloom Crochet",
                imageUrl=hero_meta.url if hero_meta else build_image_url("hero/heritage.png"),
                imageAlt=hero_meta.alt_text if hero_meta else f"{brand_name} handcrafted crochet creations in India",
                imageWidth=hero_meta.width if hero_meta else None,
                imageHeight=hero_meta.height if hero_meta else None,
                imageType=hero_meta.content_type if hero_meta else None,
                imageMetadata=hero_meta,
                pageType="website",
                breadcrumbs=[],
                brand=brand_info,
                faqs=[
                    SeoFaqItem(
                        question="Are Sulocraft products handmade?",
                        answer="Yes, Sulocraft products are handcrafted in small batches.",
                    ),
                    SeoFaqItem(
                        question="Do you ship across India and provide order tracking?",
                        answer="Yes, we provide tracked express shipping across all states in India with free delivery on orders above ₹999.",
                    ),
                    SeoFaqItem(
                        question="How do crochet flowers compare to real flowers?",
                        answer="Sulocraft crochet flowers never wilt, shed petals, or trigger pollen allergies. They are washable, eco-friendly, and serve as everlasting keepsakes.",
                    ),
                ],
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        # 3. Static Public Pages
        if path == "/about":
            about_meta = build_media_metadata("about/anupama-sharma.png", alt_text="Sulocraft founder Anupama Sharma with a bouquet")
            return SeoMetadataOut(
                title="Our Story | Handcrafted Crochet | Sulocraft",
                description="Founded by Anupama Sharma, Sulocraft creates handcrafted crochet pieces and flower bouquets in small batches.",
                canonicalPath="/about",
                canonicalUrl=SeoService._build_canonical_url("/about"),
                robots=SeoService._get_robots_directive(True),
                h1="Our Story",
                imageUrl=about_meta.url if about_meta else build_image_url("about/anupama-sharma.png"),
                imageAlt=about_meta.alt_text if about_meta else "Sulocraft founder Anupama Sharma with a bouquet",
                imageWidth=about_meta.width if about_meta else None,
                imageHeight=about_meta.height if about_meta else None,
                imageType=about_meta.content_type if about_meta else None,
                imageMetadata=about_meta,
                pageType="article",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="About Us", path="/about"),
                ],
                brand=brand_info,
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        if path == "/contact":
            return SeoMetadataOut(
                title="Contact Us | Sulocraft Customer Support & Custom Orders",
                description="Get in touch with Sulocraft for custom orders, artisanal crochet inquiries, and dedicated customer support.",
                canonicalPath="/contact",
                canonicalUrl=SeoService._build_canonical_url("/contact"),
                robots=SeoService._get_robots_directive(True),
                h1="Contact Us",
                imageUrl=None,
                imageAlt=None,
                pageType="website",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Contact", path="/contact"),
                ],
                brand=brand_info,
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        # 4. Shop Page (no filter)
        if path == "/shop" and not query_params.get("category") and not query_params.get("collection"):
            shop_meta = build_media_metadata("hero/heritage.png", alt_text="Sulocraft Shop Catalogue")
            return SeoMetadataOut(
                title="Shop Handcrafted Crochet Creations | Sulocraft",
                description="Explore our full catalogue of handcrafted crochet flowers, amigurumi toys, baby accessories, and pooja essentials with free shipping over ₹999.",
                canonicalPath="/shop",
                canonicalUrl=SeoService._build_canonical_url("/shop"),
                robots=SeoService._get_robots_directive(True),
                h1="All Products",
                imageUrl=shop_meta.url if shop_meta else build_image_url("hero/heritage.png"),
                imageAlt=shop_meta.alt_text if shop_meta else "Sulocraft Shop Catalogue",
                imageWidth=shop_meta.width if shop_meta else None,
                imageHeight=shop_meta.height if shop_meta else None,
                imageType=shop_meta.content_type if shop_meta else None,
                imageMetadata=shop_meta,
                pageType="collection",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ],
                brand=brand_info,
            )

        # 5. Policy Pages and Aliases
        resolved_policy_path = POLICY_ALIASES.get(path, path)
        if resolved_policy_path in POLICY_ROUTES:
            p_data = POLICY_ROUTES[resolved_policy_path]
            return SeoMetadataOut(
                title=p_data["title"],
                description=p_data["description"],
                canonicalPath=resolved_policy_path,
                canonicalUrl=SeoService._build_canonical_url(resolved_policy_path),
                robots=SeoService._get_robots_directive(True),
                h1=p_data["h1"],
                imageUrl=None,
                imageAlt=None,
                pageType="article",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name=p_data["breadcrumb"], path=resolved_policy_path),
                ],
                brand=brand_info,
                shippingInfo=SeoShippingInfo() if resolved_policy_path == "/shipping-policy" else None,
                returnPolicy=SeoReturnPolicy() if resolved_policy_path == "/return-policy" else None,
            )

        # 6. Category Routes: /categories/{slug} or /shop?category={slug}
        cat_slug = None
        if path.startswith("/categories/"):
            cat_slug = path.removeprefix("/categories/").strip("/")
        elif path == "/shop" and query_params.get("category"):
            cat_slug = query_params["category"][0].strip()

        if cat_slug:
            category = (
                db.query(Category)
                .filter(Category.slug == cat_slug, Category.is_active.is_(True))
                .first()
            )
            if category:
                breadcrumbs = [
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ]
                parent = None
                if category.parent_id:
                    parent = db.query(Category).filter(Category.id == category.parent_id).first()
                    if parent and parent.is_active:
                        breadcrumbs.append(
                            SeoBreadcrumb(name=parent.name, path=f"/categories/{parent.slug}")
                        )
                breadcrumbs.append(
                    SeoBreadcrumb(name=category.name, path=f"/categories/{category.slug}")
                )

                img_url = category.image_url
                cat_meta = build_media_metadata(category.image_key or category.image, alt_text=f"Handcrafted crochet {category.name} collection by Sulocraft") if (category.image_key or category.image) else None
                desc = category.description or f"Explore handcrafted crochet {category.name.lower()} by Sulocraft. Discover our collection."
                if len(desc) > 160:
                    desc = desc[:157] + "..."

                # Calculate product count including subcategories
                subcat_ids = [c.id for c in db.query(Category.id).filter(Category.parent_id == category.id).all()]
                all_target_category_ids = [category.id] + subcat_ids
                prod_count = (
                    db.query(ProductCategory.product_id)
                    .join(Product, ProductCategory.product_id == Product.id)
                    .filter(ProductCategory.category_id.in_(all_target_category_ids), Product.status == "ACTIVE")
                    .distinct()
                    .count()
                )
                category_entity = SeoCategoryEntity(
                    id=category.id,
                    name=category.name,
                    slug=category.slug,
                    description=category.description,
                    imageUrl=img_url,
                    imageAlt=cat_meta.alt_text if cat_meta else f"Handcrafted crochet {category.name} collection by Sulocraft",
                    imageWidth=cat_meta.width if cat_meta else None,
                    imageHeight=cat_meta.height if cat_meta else None,
                    imageType=cat_meta.content_type if cat_meta else None,
                    imageMetadata=cat_meta,
                    parentId=parent.id if parent else None,
                    parentName=parent.name if parent else None,
                    parentSlug=parent.slug if parent else None,
                    productCount=prod_count,
                )

                return SeoMetadataOut(
                    title=f"Handcrafted Crochet {category.name} | Buy Online India | Sulocraft",
                    description=desc,
                    canonicalPath=f"/categories/{category.slug}",
                    canonicalUrl=SeoService._build_canonical_url(f"/categories/{category.slug}"),
                    robots=SeoService._get_robots_directive(True),
                    h1=category.name,
                    imageUrl=img_url,
                    imageAlt=cat_meta.alt_text if cat_meta else f"Handcrafted crochet {category.name} collection by Sulocraft",
                    imageWidth=cat_meta.width if cat_meta else None,
                    imageHeight=cat_meta.height if cat_meta else None,
                    imageType=cat_meta.content_type if cat_meta else None,
                    imageMetadata=cat_meta,
                    pageType="collection",
                    breadcrumbs=breadcrumbs,
                    brand=brand_info,
                    categoryEntity=category_entity,
                    faqs=[
                        SeoFaqItem(
                            question=f"What makes Sulocraft crochet {category.name.lower()} unique?",
                            answer=f"Our {category.name.lower()} are handcrafted in small batches. They never wilt or fade and make thoughtful everlasting gifts.",
                        ),
                        SeoFaqItem(
                            question=f"How quickly do orders for {category.name.lower()} ship?",
                            answer="In-stock creations are dispatched within 24 to 48 hours and typically arrive within 3-5 business days across India.",
                        ),
                    ],
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
                )
            else:
                return SeoService._not_found_metadata(path, brand_info)

        # 7. Collection Routes: /collections/{slug} or /shop?collection={slug}
        col_slug = None
        if path.startswith("/collections/"):
            col_slug = path.removeprefix("/collections/").strip("/")
        elif path == "/shop" and query_params.get("collection"):
            col_slug = query_params["collection"][0].strip()

        if col_slug:
            now = datetime.now(timezone.utc)
            collection = (
                db.query(Collection)
                .filter(Collection.slug == col_slug, Collection.is_active.is_(True))
                .first()
            )
            if collection and (collection.starts_at is None or collection.starts_at <= now) and (collection.ends_at is None or collection.ends_at >= now):
                desc = collection.description or f"Explore the {collection.name} handcrafted crochet collection at Sulocraft."
                if len(desc) > 160:
                    desc = desc[:157] + "..."

                col_meta = build_media_metadata(collection.image_key, alt_text=f"Sulocraft {collection.name}") if collection.image_key else None
                collection_entity = SeoCollectionEntity(
                    id=collection.id,
                    name=collection.name,
                    slug=collection.slug,
                    description=collection.description,
                    imageUrl=collection.image_url,
                    imageAlt=col_meta.alt_text if col_meta else f"Sulocraft {collection.name}",
                    imageWidth=col_meta.width if col_meta else None,
                    imageHeight=col_meta.height if col_meta else None,
                    imageType=col_meta.content_type if col_meta else None,
                    imageMetadata=col_meta,
                    collectionType=collection.collection_type,
                )

                return SeoMetadataOut(
                    title=f"{collection.name} | Sulocraft Collections",
                    description=desc,
                    canonicalPath=f"/collections/{collection.slug}",
                    canonicalUrl=SeoService._build_canonical_url(f"/collections/{collection.slug}"),
                    robots=SeoService._get_robots_directive(True),
                    h1=collection.name,
                    imageUrl=collection.image_url,
                    imageAlt=col_meta.alt_text if col_meta else f"Sulocraft {collection.name}",
                    imageWidth=col_meta.width if col_meta else None,
                    imageHeight=col_meta.height if col_meta else None,
                    imageType=col_meta.content_type if col_meta else None,
                    imageMetadata=col_meta,
                    pageType="collection",
                    breadcrumbs=[
                        SeoBreadcrumb(name="Home", path="/"),
                        SeoBreadcrumb(name="Shop", path="/shop"),
                        SeoBreadcrumb(name=collection.name, path=f"/collections/{collection.slug}"),
                    ],
                    brand=brand_info,
                    collectionEntity=collection_entity,
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
                )
            else:
                return SeoService._not_found_metadata(path, brand_info)

        # 8. Product Routes: /products/{slug}
        if path.startswith("/products/"):
            prod_slug = path.removeprefix("/products/").strip("/")
            product = (
                db.query(Product)
                .filter(Product.slug == prod_slug, Product.status == "ACTIVE")
                .first()
            )
            if product:
                breadcrumbs = [
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ]

                prim_link = (
                    db.query(ProductCategory)
                    .filter(ProductCategory.product_id == product.id, ProductCategory.is_primary.is_(True))
                    .first()
                )
                prim_cat = None
                if prim_link:
                    prim_cat = db.query(Category).filter(Category.id == prim_link.category_id).first()
                elif product.categories:
                    prim_cat = product.categories[0]

                if prim_cat and prim_cat.is_active:
                    if prim_cat.parent_id:
                        parent = db.query(Category).filter(Category.id == prim_cat.parent_id).first()
                        if parent and parent.is_active:
                            breadcrumbs.append(
                                SeoBreadcrumb(name=parent.name, path=f"/categories/{parent.slug}")
                            )
                    breadcrumbs.append(
                        SeoBreadcrumb(name=prim_cat.name, path=f"/categories/{prim_cat.slug}")
                    )

                breadcrumbs.append(
                    SeoBreadcrumb(name=product.name, path=f"/products/{product.slug}")
                )

                cat_label = prim_cat.name if prim_cat else "Creation"
                saved_desc = (product.short_description or product.description or "").strip()
                desc_meta = saved_desc if saved_desc else f"Handcrafted {product.name} by Sulocraft."
                if len(desc_meta) > 160:
                    desc_meta = desc_meta[:157] + "..."

                # Resolve variants and primary pricing truthfully from DB
                variants = product.variants or []
                active_variants = [v for v in variants if v.status == "ACTIVE" or v.status is None]
                primary_variant = active_variants[0] if active_variants else (variants[0] if variants else None)

                price = primary_variant.price if primary_variant else 0.0
                price_paise = int(round(price * 100))
                sku = primary_variant.sku if primary_variant else f"SULO-{product.id}"
                in_stock = any(v.stock_quantity > 0 for v in variants) if variants else False
                inventory_status = "IN_STOCK" if in_stock else "OUT_OF_STOCK"

                # Image URLs and Media items
                image_urls = []
                media_items = []
                primary_meta = None

                primary_db_img = next(
                    (img for img in (product.images or []) if img.url == product.primary_image or (product.primary_image and product.primary_image in img.url)),
                    None,
                )
                primary_alt = (primary_db_img.alt_text.strip() if primary_db_img and primary_db_img.alt_text and primary_db_img.alt_text.strip() else None) or f"Handcrafted {product.name} by Sulocraft"

                if product.primary_image:
                    primary_url = build_image_url(product.primary_image)
                    image_urls.append(primary_url)
                    primary_meta = build_media_metadata(
                        product.primary_image,
                        alt_text=primary_alt,
                        db_width=primary_db_img.width if primary_db_img else None,
                        db_height=primary_db_img.height if primary_db_img else None,
                        db_content_type=primary_db_img.content_type if primary_db_img else None,
                    )
                    if primary_meta:
                        media_items.append(primary_meta)

                for img in product.images:
                    resolved_img = build_image_url(img.url)
                    if resolved_img not in image_urls:
                        image_urls.append(resolved_img)
                    item_meta = build_media_metadata(
                        img.url,
                        alt_text=img.alt_text or f"{product.name} gallery image",
                        db_width=img.width,
                        db_height=img.height,
                        db_content_type=img.content_type,
                    )
                    if item_meta and item_meta.url not in [m.url for m in media_items]:
                        media_items.append(item_meta)

                # Variant models
                variant_models = [
                    SeoProductVariant(
                        id=v.id,
                        sku=v.sku,
                        name=v.name,
                        price=v.price,
                        pricePaise=int(round(v.price * 100)),
                        stockQuantity=v.stock_quantity,
                        inStock=v.stock_quantity > 0,
                        attributes=v.attributes_json or {},
                    )
                    for v in variants
                ]

                # Review truth (Task 5.22 / 5.13.1): aggregate ONLY from genuine review records
                aggregate_rating = SeoService.get_products_aggregate_ratings(db, [product.id]).get(product.id)

                # Truthful FAQs using Work 019 fields or fallback to defaults
                defaults = db.query(ProductInformationDefaults).order_by(ProductInformationDefaults.id.asc()).first()
                information = resolve_product_information(product, defaults)
                care_text = information["care_instructions"]
                materials_text = information["materials_used"]
                shipping_text = information["shipping_delivery"]
                handmade_text = information["handmade_details"]

                faqs = []
                if care_text:
                    faqs.append(SeoFaqItem(question=f"How do I clean and care for {product.name}?", answer=care_text))
                if materials_text:
                    faqs.append(SeoFaqItem(question=f"What materials are used to make {product.name}?", answer=materials_text))
                if handmade_text:
                    faqs.append(SeoFaqItem(question=f"Is {product.name} genuinely handmade?", answer=handmade_text))
                if shipping_text:
                    faqs.append(SeoFaqItem(question="What are the delivery and shipping details?", answer=shipping_text))

                product_entity = SeoProductEntity(
                    id=product.id,
                    name=product.name,
                    slug=product.slug,
                    description=product.description,
                    sku=sku,
                    price=price,
                    pricePaise=price_paise,
                    currency="INR",
                    inStock=in_stock,
                    inventoryStatus=inventory_status,
                    brand=product.brand or "Sulocraft",
                    primaryCategoryName=prim_cat.name if prim_cat else None,
                    categoryNames=[c.name for c in product.categories] if product.categories else ([] if not prim_cat else [prim_cat.name]),
                    imageUrls=image_urls,
                    media=media_items,
                    variants=variant_models,
                    aggregateRating=aggregate_rating,
                    handmadeDetails=information["handmade_details"],
                    materialsUsed=information["materials_used"],
                    sizeDimensions=information["size_dimensions"],
                    careInstructions=information["care_instructions"],
                    shippingDelivery=information["shipping_delivery"],
                    processingTime=information["processing_time"],
                )

                return SeoMetadataOut(
                    title=f"{product.name} - Handcrafted Crochet {cat_label} | Sulocraft",
                    description=desc_meta,
                    canonicalPath=f"/products/{product.slug}",
                    canonicalUrl=SeoService._build_canonical_url(f"/products/{product.slug}"),
                    robots=SeoService._get_robots_directive(True),
                    h1=product.name,
                    imageUrl=build_image_url(product.primary_image) if product.primary_image else None,
                    imageAlt=primary_meta.alt_text if primary_meta else (primary_alt if product.primary_image else None),
                    imageWidth=primary_meta.width if primary_meta else None,
                    imageHeight=primary_meta.height if primary_meta else None,
                    imageType=primary_meta.content_type if primary_meta else None,
                    imageMetadata=primary_meta,
                    pageType="product",
                    breadcrumbs=breadcrumbs,
                    brand=brand_info,
                    productEntity=product_entity,
                    faqs=faqs,
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
                )
            else:
                # Check if product exists but is ARCHIVED/inactive -> 410 Gone
                archived_prod = (
                    db.query(Product)
                    .filter(Product.slug == prod_slug)
                    .first()
                )
                if archived_prod and archived_prod.status == "ARCHIVED":
                    return SeoMetadataOut(
                        title=f"{archived_prod.name} (Discontinued) | Sulocraft",
                        description=f"{archived_prod.name} has been discontinued and is no longer available at Sulocraft.",
                        canonicalPath=path,
                        canonicalUrl=SeoService._build_canonical_url(path),
                        robots="noindex,nofollow",
                        h1="Product Discontinued",
                        imageUrl=None,
                        imageAlt=None,
                        pageType="product",
                        breadcrumbs=[
                            SeoBreadcrumb(name="Home", path="/"),
                            SeoBreadcrumb(name="Shop", path="/shop"),
                        ],
                        brand=brand_info,
                        httpStatus=410,
                        redirectTo=None,
                    )
                return SeoService._not_found_metadata(path, brand_info)

        # 9. Unmatched / 404 Route
        return SeoService._not_found_metadata(path, brand_info)

    @staticmethod
    def _not_found_metadata(path: str, brand_info: SeoBrandInfo | None = None) -> SeoMetadataOut:
        """Fallback metadata for missing pages and invalid slugs."""
        return SeoMetadataOut(
            title="Page Not Found | Sulocraft",
            description="The requested page could not be found on Sulocraft.",
            canonicalPath=path,
            canonicalUrl=SeoService._build_canonical_url(path),
            robots="noindex,nofollow",
            h1="Page Not Found",
            imageUrl=None,
            imageAlt=None,
            pageType="website",
            breadcrumbs=[],
            brand=brand_info,
            httpStatus=404,
            redirectTo=None,
        )

    @staticmethod
    def generate_sitemap_xml(db: Session, base_url: str | None = None) -> str:
        """Generate dynamic XML sitemap conforming to sitemaps.org standards with Google Image sitemap tags."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        entries: list[dict[str, Any]] = []

        # 1. Static Public Pages (no modification source -> lastmod omitted)
        entries.append({
            "loc": f"{clean_base}/",
            "lastmod": None,
            "changefreq": "daily",
            "priority": "1.0",
            "images": [{"loc": build_image_url("hero/heritage.png"), "title": "Sulocraft Handcrafted Crochet"}],
        })
        entries.append({
            "loc": f"{clean_base}/shop",
            "lastmod": None,
            "changefreq": "daily",
            "priority": "0.9",
        })
        entries.append({
            "loc": f"{clean_base}/about",
            "lastmod": None,
            "changefreq": "monthly",
            "priority": "0.7",
            "images": [{"loc": build_image_url("about/anupama-sharma.png"), "title": "Sulocraft Founder Anupama Sharma"}],
        })
        entries.append({
            "loc": f"{clean_base}/contact",
            "lastmod": None,
            "changefreq": "monthly",
            "priority": "0.6",
        })
        for p_path in ("/shipping-policy", "/return-policy", "/privacy-policy", "/terms", "/faq"):
            entries.append({
                "loc": f"{clean_base}{p_path}",
                "lastmod": None,
                "changefreq": "monthly",
                "priority": "0.5",
            })

        # 2. Active Categories
        categories = (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.display_order, Category.id)
            .all()
        )
        for cat in categories:
            mod_date = (cat.updated_at or cat.created_at).strftime("%Y-%m-%d") if (cat.updated_at or cat.created_at) else None
            images = []
            if cat.image_url:
                images.append({"loc": build_image_url(cat.image_url), "title": f"Crochet {cat.name}"})
            entries.append({
                "loc": f"{clean_base}/categories/{cat.slug}",
                "lastmod": mod_date,
                "changefreq": "weekly",
                "priority": "0.8",
                "images": images,
            })

        # 3. Active Collections
        now_time = datetime.now(timezone.utc)
        collections = (
            db.query(Collection)
            .filter(Collection.is_active.is_(True))
            .order_by(Collection.display_order, Collection.id)
            .all()
        )
        for col in collections:
            if (col.starts_at is None or col.starts_at <= now_time) and (col.ends_at is None or col.ends_at >= now_time):
                mod_date = (col.updated_at or col.created_at).strftime("%Y-%m-%d") if (col.updated_at or col.created_at) else None
                images = []
                if col.image_url:
                    images.append({"loc": build_image_url(col.image_url), "title": col.name})
                entries.append({
                    "loc": f"{clean_base}/collections/{col.slug}",
                    "lastmod": mod_date,
                    "changefreq": "weekly",
                    "priority": "0.8",
                    "images": images,
                })

        # 4. Active Products
        products = (
            db.query(Product)
            .filter(Product.status == "ACTIVE")
            .order_by(Product.id)
            .all()
        )
        for prod in products:
            mod_date = (prod.updated_at or prod.created_at).strftime("%Y-%m-%d") if (prod.updated_at or prod.created_at) else None
            images = []
            if prod.primary_image:
                images.append({"loc": build_image_url(prod.primary_image), "title": prod.name})
            for img in prod.images:
                if img.url and img.url != prod.primary_image:
                    images.append({"loc": build_image_url(img.url), "title": img.alt_text or f"{prod.name} gallery image"})
            entries.append({
                "loc": f"{clean_base}/products/{prod.slug}",
                "lastmod": mod_date,
                "changefreq": "daily",
                "priority": "0.9",
                "images": images,
            })

        # Build XML
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        ]
        for e in entries:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{xml_escape(str(e['loc']))}</loc>")
            if e.get("lastmod"):
                xml_lines.append(f"    <lastmod>{xml_escape(str(e['lastmod']))}</lastmod>")
            xml_lines.append(f"    <changefreq>{xml_escape(str(e['changefreq']))}</changefreq>")
            xml_lines.append(f"    <priority>{xml_escape(str(e['priority']))}</priority>")
            for img in e.get("images", []):
                xml_lines.append("    <image:image>")
                xml_lines.append(f"      <image:loc>{xml_escape(str(img['loc']))}</image:loc>")
                if img.get("title"):
                    xml_lines.append(f"      <image:title>{xml_escape(str(img['title']))}</image:title>")
                xml_lines.append("    </image:image>")
            xml_lines.append("  </url>")
        xml_lines.append("</urlset>")

        return "\n".join(xml_lines)

    @staticmethod
    def get_canonical_base_url(base_url_override: str | None = None) -> str:
        """Return validated canonical base URL according to environment policy.

        Fail-closed rules:
        - In production: SEO_PUBLIC_ORIGIN or CANONICAL_BASE_URL must be provided and valid HTTPS;
          fails closed (raises RuntimeError) if missing or malformed.
        - In preprod/staging: Uses SEO_PUBLIC_ORIGIN, CANONICAL_BASE_URL, or preprod frontend_url.
          Never falls back to production domain.
        - In development/test: Uses SEO_PUBLIC_ORIGIN, CANONICAL_BASE_URL, or frontend_url (e.g. localhost).
          Never silently advertises production domain.
        """
        if base_url_override and base_url_override.strip():
            return base_url_override.strip().rstrip("/")

        env = os.getenv("APP_ENV", "development").lower()
        is_prod = env == "production"
        allow_http = env in ("development", "test")

        origin_candidate = os.getenv("SEO_PUBLIC_ORIGIN") or os.getenv("CANONICAL_BASE_URL")
        if origin_candidate and origin_candidate.strip():
            try:
                return validate_public_origin(origin_candidate, is_production=is_prod, allow_http=allow_http)
            except ValueError as e:
                if is_prod:
                    raise RuntimeError(f"Production SEO configuration error: {e}") from e
                # In non-production, fall through to environment default

        from app.core.config import settings

        if is_prod:
            frontend = getattr(settings, "frontend_url", None)
            if frontend:
                try:
                    return validate_public_origin(frontend, is_production=True, allow_http=False)
                except ValueError as e:
                    raise RuntimeError(f"Production SEO origin configuration missing or invalid: {e}") from e
            raise RuntimeError("Production requires explicit SEO_PUBLIC_ORIGIN or CANONICAL_BASE_URL configuration")

        if env in ("staging", "preprod", "dev"):
            frontend = getattr(settings, "frontend_url", "https://dev.sulocraft.com")
            try:
                return validate_public_origin(frontend, is_production=False, allow_http=False)
            except ValueError:
                return "https://dev.sulocraft.com"

        # Development / test
        frontend = getattr(settings, "frontend_url", "http://localhost:8080")
        try:
            return validate_public_origin(frontend, is_production=False, allow_http=True)
        except ValueError:
            return "http://localhost:8080"

    @staticmethod
    def get_public_route_inventory(db: Session, base_url: str | None = None) -> SeoRouteInventoryOut:
        """Provide a complete, deduplicated database-driven inventory of all eligible indexable public routes."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        now_time = datetime.now(timezone.utc)

        routes: list[SeoRouteItem] = []

        # 1. Static Core Pages (no DB modification provenance -> omit lastmod)
        routes.append(SeoRouteItem(
            path="/",
            canonicalUrl=f"{clean_base}/",
            pageType="website",
            lastmod=None,
            changefreq="daily",
            priority=1.0,
        ))
        routes.append(SeoRouteItem(
            path="/shop",
            canonicalUrl=f"{clean_base}/shop",
            pageType="collection",
            lastmod=None,
            changefreq="daily",
            priority=0.9,
        ))
        routes.append(SeoRouteItem(
            path="/about",
            canonicalUrl=f"{clean_base}/about",
            pageType="article",
            lastmod=None,
            changefreq="monthly",
            priority=0.7,
        ))
        routes.append(SeoRouteItem(
            path="/contact",
            canonicalUrl=f"{clean_base}/contact",
            pageType="website",
            lastmod=None,
            changefreq="monthly",
            priority=0.6,
        ))

        # 2. Public Policy Pages (no DB modification provenance -> omit lastmod)
        for p_path in ("/shipping-policy", "/return-policy", "/privacy-policy", "/terms", "/faq"):
            routes.append(SeoRouteItem(
                path=p_path,
                canonicalUrl=f"{clean_base}{p_path}",
                pageType="article",
                lastmod=None,
                changefreq="monthly",
                priority=0.5,
            ))

        # 3. Active Categories (DB-derived timestamps)
        categories = (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.display_order.asc(), Category.id.asc())
            .all()
        )
        for cat in categories:
            mod_date = (cat.updated_at or cat.created_at).strftime("%Y-%m-%d") if (cat.updated_at or cat.created_at) else None
            routes.append(SeoRouteItem(
                path=f"/categories/{cat.slug}",
                canonicalUrl=f"{clean_base}/categories/{cat.slug}",
                pageType="collection",
                lastmod=mod_date,
                changefreq="weekly",
                priority=0.8,
            ))

        # 4. Active Collections (DB-derived timestamps)
        collections = (
            db.query(Collection)
            .filter(Collection.is_active.is_(True))
            .order_by(Collection.display_order.asc(), Collection.id.asc())
            .all()
        )
        for col in collections:
            if (col.starts_at is None or col.starts_at <= now_time) and (col.ends_at is None or col.ends_at >= now_time):
                mod_date = (col.updated_at or col.created_at).strftime("%Y-%m-%d") if (col.updated_at or col.created_at) else None
                routes.append(SeoRouteItem(
                    path=f"/collections/{col.slug}",
                    canonicalUrl=f"{clean_base}/collections/{col.slug}",
                    pageType="collection",
                    lastmod=mod_date,
                    changefreq="weekly",
                    priority=0.8,
                ))

        # 5. Active Products (DB-driven, no 100-item cap, DB-derived timestamps)
        products = (
            db.query(Product)
            .filter(Product.status == "ACTIVE")
            .order_by(Product.id.asc())
            .all()
        )
        for prod in products:
            mod_date = (prod.updated_at or prod.created_at).strftime("%Y-%m-%d") if (prod.updated_at or prod.created_at) else None
            routes.append(SeoRouteItem(
                path=f"/products/{prod.slug}",
                canonicalUrl=f"{clean_base}/products/{prod.slug}",
                pageType="product",
                lastmod=mod_date,
                changefreq="daily",
                priority=0.9,
            ))

        return SeoRouteInventoryOut(
            totalRoutes=len(routes),
            routes=routes,
            generatedAt=datetime.now(timezone.utc),
        )

    @staticmethod
    def _compute_global_snapshot_version(db: Session, inventory: SeoRouteInventoryOut) -> str:
        """Compute a deterministic, store-wide version hash across all public entities, prices, stock, media, and brand data."""
        import hashlib

        hash_components: list[str] = [
            f"routes:{inventory.total_routes}",
        ]

        # 1. Routes and basic lastmod signatures
        for r in inventory.routes:
            hash_components.append(f"r:{r.path}:{r.lastmod}:{r.page_type}")

        # 2. Store brand settings
        brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
        if brand:
            b_updated = brand.updated_at.isoformat() if brand.updated_at else ""
            hash_components.append(f"brand:{brand.name}:{brand.logo_url}:{brand.instagram_url}:{brand.whatsapp_url}:{b_updated}")
        else:
            hash_components.append("brand:none")

        # 3. Product information defaults (Work 019)
        defaults = db.query(ProductInformationDefaults).order_by(ProductInformationDefaults.id.asc()).first()
        if defaults:
            d_updated = defaults.updated_at.isoformat() if defaults.updated_at else ""
            hash_components.append(f"defaults:{d_updated}")

        # 4. Active categories signature
        categories = (
            db.query(Category.id, Category.slug, Category.name, Category.image_key, Category.updated_at)
            .filter(Category.is_active.is_(True))
            .order_by(Category.id.asc())
            .all()
        )
        for cat in categories:
            c_mod = cat.updated_at.isoformat() if cat.updated_at else ""
            hash_components.append(f"cat:{cat.id}:{cat.slug}:{cat.name}:{cat.image_key}:{c_mod}")

        # 5. Active collections signature
        collections = (
            db.query(Collection.id, Collection.slug, Collection.name, Collection.image_key, Collection.updated_at)
            .filter(Collection.is_active.is_(True))
            .order_by(Collection.id.asc())
            .all()
        )
        for col in collections:
            col_mod = col.updated_at.isoformat() if col.updated_at else ""
            hash_components.append(f"col:{col.id}:{col.slug}:{col.name}:{col.image_key}:{col_mod}")

        # 6. Active products signature with description, variants (price, stock, sku), images, and review counts
        products = (
            db.query(Product.id, Product.slug, Product.name, Product.description, Product.primary_image, Product.status, Product.updated_at)
            .filter(Product.status == "ACTIVE")
            .order_by(Product.id.asc())
            .all()
        )
        for prod in products:
            p_mod = prod.updated_at.isoformat() if prod.updated_at else ""
            desc_val = prod.description or ""
            hash_components.append(f"prod:{prod.id}:{prod.slug}:{prod.name}:{desc_val}:{prod.primary_image}:{p_mod}")

        # Active product variants signature (captures price / stock changes directly)
        active_prod_ids = [p.id for p in products]
        if active_prod_ids:
            variants = (
                db.query(
                    ProductVariant.id,
                    ProductVariant.product_id,
                    ProductVariant.sku,
                    ProductVariant.price,
                    ProductVariant.stock_quantity,
                    ProductVariant.status,
                    ProductVariant.updated_at,
                )
                .filter(ProductVariant.product_id.in_(active_prod_ids))
                .order_by(ProductVariant.id.asc())
                .all()
            )
            for v in variants:
                v_mod = v.updated_at.isoformat() if v.updated_at else ""
                hash_components.append(f"var:{v.id}:{v.product_id}:{v.sku}:{v.price}:{v.stock_quantity}:{v.status}:{v_mod}")

            # Active review aggregates per product
            review_aggs = (
                db.query(
                    Review.product_id,
                    func.count(Review.id).label("count"),
                    func.avg(Review.rating).label("avg_rating"),
                )
                .filter(Review.product_id.in_(active_prod_ids))
                .group_by(Review.product_id)
                .order_by(Review.product_id.asc())
                .all()
            )
            for ra in review_aggs:
                hash_components.append(f"rev:{ra.product_id}:{ra.count}:{round(float(ra.avg_rating), 2) if ra.avg_rating else 0}")

        manifest_hash = get_media_manifest_hash()
        if manifest_hash:
            hash_components.append(f"media_manifest:{manifest_hash}")

        combined_str = "v2:" + ";".join(hash_components)
        return hashlib.sha256(combined_str.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def get_content_snapshot(db: Session, page: int = 1, limit: int = 50) -> SeoSnapshotResponse:
        """Provide a paginated, versioned snapshot of full route metadata and entities for pre-rendering."""
        import math

        if page < 1:
            page = 1
        if limit < 1:
            limit = 50
        elif limit > 200:
            limit = 200

        inventory = SeoService.get_public_route_inventory(db)
        total_count = inventory.total_routes
        total_pages = max(1, math.ceil(total_count / limit))

        offset = (page - 1) * limit
        page_routes = inventory.routes[offset : offset + limit]

        items: list[SeoPageSnapshotItem] = []
        for r in page_routes:
            metadata = SeoService.resolve_path(db, r.path)
            items.append(SeoPageSnapshotItem(
                path=r.path,
                metadata=metadata,
            ))

        version_hash = SeoService._compute_global_snapshot_version(db, inventory)

        return SeoSnapshotResponse(
            page=page,
            limit=limit,
            totalCount=total_count,
            totalPages=total_pages,
            items=items,
            versionHash=version_hash,
        )

    @staticmethod
    def generate_robots_txt(base_url: str | None = None) -> str:
        """Generate robots.txt file with disallowed private routes and canonical sitemap, respecting environment policy.
        
        Policy:
        - Never block noindex-page crawling with blanket 'Disallow: /' just to hide nonproduction.
          Crawlers must be allowed access to discover '<meta name="robots" content="noindex,nofollow">'
          and X-Robots-Tag headers.
        - Private routes (/admin/, /account/, /cart, /checkout, /wishlist, /auth/, /api/) remain disallowed.
        - Canonical sitemap reference is advertised only when public indexing is enabled.
        """
        try:
            clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        except Exception:
            clean_base = "https://sulocraft.com"

        robots_directive = SeoService._get_robots_directive(True)

        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /account/",
            "Disallow: /cart",
            "Disallow: /checkout",
            "Disallow: /wishlist",
            "Disallow: /auth/",
            "Disallow: /api/",
        ]

        if robots_directive == "index,follow":
            lines.append("")
            lines.append(f"Sitemap: {clean_base}/sitemap.xml")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def get_merchant_feed_items(db: Session, base_url: str | None = None) -> list[MerchantFeedItemOut]:
        """Fetch and format all eligible active catalogue variants for Google Merchant Center.

        Enforces:
        - Only active products (Product.status == "ACTIVE").
        - Only active variants (ProductVariant.status == "ACTIVE").
        - Stable SKU IDs, landing-page URL parity, price currency formatting.
        - Truthful handcrafted identifier handling (identifier_exists = 'no').
        - Absolute public image links (R2 or normalized origin URL).
        """
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        products = (
            db.query(Product)
            .filter(Product.status == "ACTIVE")
            .order_by(Product.id)
            .all()
        )

        items: list[MerchantFeedItemOut] = []
        for prod in products:
            if not prod.slug:
                continue

            landing_link = f"{clean_base}/products/{prod.slug}"

            # Primary image full URL
            if prod.primary_image:
                raw_primary = build_image_url(prod.primary_image)
                if raw_primary.startswith("http://") or raw_primary.startswith("https://"):
                    primary_image_link = raw_primary
                else:
                    primary_image_link = f"{clean_base}{raw_primary if raw_primary.startswith('/') else '/' + raw_primary}"
            else:
                primary_image_link = f"{clean_base}/images/placeholder.png"

            # Additional gallery images (up to 10)
            additional_images: list[str] = []
            for img in prod.images:
                if not img.url or img.url == prod.primary_image:
                    continue
                raw_img = build_image_url(img.url)
                if raw_img.startswith("http://") or raw_img.startswith("https://"):
                    full_img = raw_img
                else:
                    full_img = f"{clean_base}{raw_img if raw_img.startswith('/') else '/' + raw_img}"
                if full_img not in additional_images and full_img != primary_image_link:
                    additional_images.append(full_img)
                if len(additional_images) >= 10:
                    break

            # Product description
            clean_desc = (prod.description or prod.short_description or prod.name).strip()[:5000]

            # Product type / category breadcrumb
            product_type = None
            if prod.primary_category:
                cat = prod.primary_category
                if cat.parent and cat.parent.name:
                    product_type = f"{cat.parent.name} > {cat.name}"
                else:
                    product_type = cat.name
            elif prod.categories:
                cat = prod.categories[0]
                if cat.parent and cat.parent.name:
                    product_type = f"{cat.parent.name} > {cat.name}"
                else:
                    product_type = cat.name

            # Active variants
            active_variants = [v for v in prod.variants if getattr(v, "status", "ACTIVE") == "ACTIVE"]

            if not active_variants:
                # If product has no explicit variant records, create a single item representing the product
                item_id = prod.slug
                title = prod.name[:150]
                availability = "in_stock"
                price_str = "0.00 INR"
                items.append(
                    MerchantFeedItemOut(
                        id=item_id,
                        title=title,
                        description=clean_desc,
                        link=landing_link,
                        image_link=primary_image_link,
                        additional_image_links=additional_images,
                        availability=availability,
                        price=price_str,
                        sale_price=None,
                        brand=prod.brand or "Sulocraft",
                        condition="new",
                        item_group_id=prod.slug,
                        identifier_exists="no",
                        product_type=product_type,
                        google_product_category=None,
                        shipping_weight=None,
                        custom_label_0=prod.badge,
                        custom_label_1=prod.collections[0].name if prod.collections else None,
                    )
                )
                continue

            for v in active_variants:
                item_id = v.sku or f"{prod.slug}-{v.id}"

                # Title: append variant name if distinct
                if v.name and v.name.lower() not in ("default", "standard", ""):
                    title = f"{prod.name} - {v.name}"[:150]
                else:
                    title = prod.name[:150]

                # Availability
                availability = "in_stock" if (v.stock_quantity or 0) > 0 else "out_of_stock"

                # Price and compare_at_price
                if v.compare_at_price and v.compare_at_price > v.price:
                    regular_price = f"{float(v.compare_at_price):.2f} INR"
                    sale_price = f"{float(v.price):.2f} INR"
                else:
                    regular_price = f"{float(v.price):.2f} INR"
                    sale_price = None

                # Weight
                weight_str = f"{int(v.weight)} g" if v.weight else None

                # Additional image for variant if specific image exists
                variant_additional = list(additional_images)
                variant_primary = primary_image_link
                if v.images:
                    var_img = v.images[0]
                    if var_img.url:
                        raw_vimg = build_image_url(var_img.url)
                        v_full = raw_vimg if raw_vimg.startswith("http") else f"{clean_base}{raw_vimg if raw_vimg.startswith('/') else '/' + raw_vimg}"
                        if v_full != variant_primary and v_full not in variant_additional:
                            variant_additional.insert(0, v_full)

                items.append(
                    MerchantFeedItemOut(
                        id=item_id,
                        title=title,
                        description=clean_desc,
                        link=landing_link,
                        image_link=variant_primary,
                        additional_image_links=variant_additional[:10],
                        availability=availability,
                        price=regular_price,
                        sale_price=sale_price,
                        brand=prod.brand or "Sulocraft",
                        condition="new",
                        item_group_id=prod.slug,
                        identifier_exists="no",
                        product_type=product_type,
                        google_product_category=None,
                        shipping_weight=weight_str,
                        custom_label_0=prod.badge,
                        custom_label_1=prod.collections[0].name if prod.collections else None,
                    )
                )

        return items

    @staticmethod
    def get_merchant_feed_response(db: Session, base_url: str | None = None) -> MerchantFeedResponse:
        """Get structured API response for Merchant Center feed."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        items = SeoService.get_merchant_feed_items(db, base_url=clean_base)
        eligible_products = len(set(item.item_group_id for item in items if item.item_group_id))
        now_iso = datetime.now(timezone.utc).isoformat()

        return MerchantFeedResponse(
            feed_version="1.0",
            title="Sulocraft Product Feed",
            link=f"{clean_base}/",
            description="Sulocraft Handcrafted Crochet Creations Product Feed",
            generated_at=now_iso,
            total_items=len(items),
            eligible_products_count=eligible_products,
            items=items,
        )

    @staticmethod
    def generate_merchant_feed_xml(db: Session, base_url: str | None = None) -> str:
        """Generate dynamic Google Merchant Center XML feed (RSS 2.0 with g: namespace).

        Conforms strictly to Google Merchant Center Product Data Specification:
        https://support.google.com/merchants/answer/7052112
        """
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        items = SeoService.get_merchant_feed_items(db, base_url=clean_base)

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
            '  <channel>',
            f'    <title>{xml_escape("Sulocraft Product Feed")}</title>',
            f'    <link>{xml_escape(clean_base)}/</link>',
            f'    <description>{xml_escape("Sulocraft Handcrafted Crochet Creations Product Feed")}</description>',
        ]

        for item in items:
            xml_lines.append('    <item>')
            xml_lines.append(f'      <g:id>{xml_escape(item.id)}</g:id>')
            xml_lines.append(f'      <g:title>{xml_escape(item.title)}</g:title>')
            xml_lines.append(f'      <g:description>{xml_escape(item.description)}</g:description>')
            xml_lines.append(f'      <g:link>{xml_escape(item.link)}</g:link>')
            xml_lines.append(f'      <g:image_link>{xml_escape(item.image_link)}</g:image_link>')
            for add_img in item.additional_image_links:
                xml_lines.append(f'      <g:additional_image_link>{xml_escape(add_img)}</g:additional_image_link>')
            xml_lines.append(f'      <g:availability>{xml_escape(item.availability)}</g:availability>')
            xml_lines.append(f'      <g:price>{xml_escape(item.price)}</g:price>')
            if item.sale_price:
                xml_lines.append(f'      <g:sale_price>{xml_escape(item.sale_price)}</g:sale_price>')
            xml_lines.append(f'      <g:brand>{xml_escape(item.brand)}</g:brand>')
            xml_lines.append(f'      <g:condition>{xml_escape(item.condition)}</g:condition>')
            if item.item_group_id:
                xml_lines.append(f'      <g:item_group_id>{xml_escape(item.item_group_id)}</g:item_group_id>')
            xml_lines.append(f'      <g:identifier_exists>{xml_escape(item.identifier_exists)}</g:identifier_exists>')
            if item.product_type:
                xml_lines.append(f'      <g:product_type>{xml_escape(item.product_type)}</g:product_type>')
            if item.google_product_category:
                xml_lines.append(f'      <g:google_product_category>{xml_escape(item.google_product_category)}</g:google_product_category>')
            if item.shipping_weight:
                xml_lines.append(f'      <g:shipping_weight>{xml_escape(item.shipping_weight)}</g:shipping_weight>')
            if item.custom_label_0:
                xml_lines.append(f'      <g:custom_label_0>{xml_escape(item.custom_label_0)}</g:custom_label_0>')
            if item.custom_label_1:
                xml_lines.append(f'      <g:custom_label_1>{xml_escape(item.custom_label_1)}</g:custom_label_1>')
            xml_lines.append('    </item>')

        xml_lines.append('  </channel>')
        xml_lines.append('</rss>')
        return "\n".join(xml_lines)

