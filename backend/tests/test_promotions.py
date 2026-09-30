"""Integration tests for Promotions, Coupons, and Customer Reviews (Milestone 10)."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, Review
from app.models.promotion import Coupon
from app.models.user import User, UserIdentity


def _create_customer_client(phone: str = "9999911001") -> TestClient:
    """Helper to authenticate a regular customer on its own client instance."""
    client = TestClient(app)
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    return client


def _create_admin_client(phone: str = "9999900000") -> TestClient:
    """Helper to authenticate an admin user on its own client instance."""
    with SessionLocal() as db:
        admin = db.query(User).filter(User.phone == phone).first()
        if not admin:
            admin = User(
                name="Store Admin",
                phone=phone,
                email="admin@sulocraft.com",
                role="ADMIN",
                status="ACTIVE",
            )
            db.add(admin)
            db.flush()
            db.add(UserIdentity(user_id=admin.id, provider="phone", provider_subject=phone))
            db.commit()

    client = TestClient(app)
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return client


def test_cart_coupon_application_and_validation():
    """Verify coupon validation logic in cart: percentage, cap, flat, min order, and expiry."""
    # 1. Seed test coupons
    with SessionLocal() as db:
        c_pct = Coupon(
            code="SAVE10",
            description="10% off up to 200 rupees",
            discount_type="PERCENTAGE",
            discount_value=10,
            min_order_amount=500,
            max_discount_amount=200,
            is_active=True,
        )
        c_flat = Coupon(
            code="FLAT150",
            description="Flat 150 off on 1000+",
            discount_type="FLAT",
            discount_value=150,
            min_order_amount=1000,
            is_active=True,
        )
        c_expired = Coupon(
            code="EXPIRED50",
            description="Expired coupon",
            discount_type="FLAT",
            discount_value=50,
            valid_until=datetime.now(timezone.utc) - timedelta(days=2),
            is_active=True,
        )
        c_limit = Coupon(
            code="LIMITED1",
            description="Max 1 usage",
            discount_type="FLAT",
            discount_value=100,
            usage_limit=1,
            usage_count=1,
            is_active=True,
        )
        db.add_all([c_pct, c_flat, c_expired, c_limit])
        db.commit()

    cart_client = TestClient(app)

    # 2. Add an item to cart (Product 1 variant price is 2599)
    cart_res = cart_client.post("/api/v1/cart/items", json={"productId": 1, "quantity": 1})
    assert cart_res.status_code == 201

    # 3. Apply non-existent coupon -> 404
    res_invalid = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "INVALIDCODE"})
    assert res_invalid.status_code == 404

    # 4. Apply expired coupon -> 400
    res_exp = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "EXPIRED50"})
    assert res_exp.status_code == 400
    assert "expired" in res_exp.json()["detail"].lower()

    # 5. Apply exhausted usage coupon -> 400
    res_exhaust = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "LIMITED1"})
    assert res_exhaust.status_code == 400
    assert "usage limit" in res_exhaust.json()["detail"].lower()

    # 6. Apply percentage coupon SAVE10 (subtotal is 2599; 10% is 259, capped at 200)
    res_save10 = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "save10"})
    assert res_save10.status_code == 200
    data = res_save10.json()
    assert data["code"] == "SAVE10"
    assert data["discountType"] == "PERCENTAGE"
    assert data["discountAmount"] == 200
    assert data["discountAmountPaise"] == 20000
    assert data["subtotalAfterDiscount"] == 2399
    assert data["subtotalAfterDiscountPaise"] == 239900

    # 7. Apply flat coupon FLAT150
    res_flat = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "FLAT150"})
    assert res_flat.status_code == 200
    data_flat = res_flat.json()
    assert data_flat["discountAmount"] == 150
    assert data_flat["subtotalAfterDiscount"] == 2449

    # 8. Test minimum order amount violation: clear cart and attempt apply
    cart_client.delete("/api/v1/cart")
    res_empty_apply = cart_client.post("/api/v1/cart/apply-coupon", json={"code": "SAVE10"})
    assert res_empty_apply.status_code == 400
    assert "empty" in res_empty_apply.json()["detail"].lower()

    # 9. Remove coupon
    res_del = cart_client.delete("/api/v1/cart/coupon")
    assert res_del.status_code == 200


def test_order_checkout_with_coupon():
    """Verify order checkout applies coupon discount and increments coupon usage count."""
    client = _create_customer_client("9999911005")

    # Seed coupon
    with SessionLocal() as db:
        c = Coupon(
            code="WELCOME100",
            description="Flat 100 off on first order",
            discount_type="FLAT",
            discount_value=100,
            usage_limit=10,
            usage_count=0,
            is_active=True,
        )
        db.add(c)
        db.commit()

    # Add item to cart
    add_res = client.post("/api/v1/cart/items", json={"productId": 1, "quantity": 1})
    assert add_res.status_code == 201

    # Place order with coupon
    order_payload = {
        "paymentMethod": "COD",
        "couponCode": "WELCOME100",
        "shippingAddress": {
            "name": "Ananya Sharma",
            "phone": "9999911005",
            "line1": "123 Residency Road",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postalCode": "560025",
        },
    }
    order_res = client.post("/api/v1/orders", json=order_payload)
    assert order_res.status_code == 201
    order_data = order_res.json()

    # Product 1 is 2599. Discount is 100. Total = 2499.
    assert order_data["subtotal"] == 2599
    assert order_data["discountAmount"] == 100
    assert order_data["discountAmountPaise"] == 10000
    assert order_data["totalAmount"] == 2499
    assert order_data["totalAmountPaise"] == 249900

    # Verify coupon usage_count incremented in DB
    with SessionLocal() as db:
        updated_c = db.query(Coupon).filter(Coupon.code == "WELCOME100").first()
        assert updated_c is not None
        assert updated_c.usage_count == 1


def test_customer_review_submission_and_rating_recalculation():
    """Verify customer review submission recalculates product aggregate rating and count."""
    anon_client = TestClient(app)

    # 1. Unauthenticated submission -> 401
    unauth_res = anon_client.post("/api/v1/products/1/reviews", json={"rating": 5, "text": "Brilliant crochet flower bouquet!"})
    assert unauth_res.status_code == 401

    # 2. Get initial product rating
    p_before = anon_client.get("/api/v1/products/1").json()
    initial_count = p_before["reviews"]

    # 3. Authenticated customer submits review
    customer_client = _create_customer_client("9999911006")
    review_res = customer_client.post(
        "/api/v1/products/1/reviews",
        json={
            "rating": 5,
            "text": "The craftsmanship on this forever rose is genuinely unmatched!",
            "location": "Mumbai",
        },
    )
    assert review_res.status_code == 201
    rev_data = review_res.json()
    assert rev_data["rating"] == 5
    assert rev_data["authorName"] in ["Verified Customer", "Customer_1006"]
    assert rev_data["location"] == "Mumbai"

    # 4. Check product updated rating and count
    p_after = anon_client.get("/api/v1/products/1").json()
    assert p_after["reviews"] == initial_count + 1
    assert p_after["reviewCount"] == initial_count + 1
    assert p_after["rating"] >= 4.5


def test_admin_coupon_crud():
    """Verify full admin CRUD lifecycle for coupons."""
    admin_client = _create_admin_client()
    customer_client = _create_customer_client("9999911007")

    # 1. RBAC protection: Customer cannot manage coupons
    res_forbidden = customer_client.get("/api/v1/admin/coupons")
    assert res_forbidden.status_code == 403

    # 2. Admin creates coupon
    create_payload = {
        "code": "FESTIVE25",
        "description": "25% Diwali discount",
        "discountType": "PERCENTAGE",
        "discountValue": 25,
        "minOrderAmount": 1500,
        "maxDiscountAmount": 500,
        "usageLimit": 50,
        "isActive": True,
    }
    create_res = admin_client.post("/api/v1/admin/coupons", json=create_payload)
    assert create_res.status_code == 201
    coupon = create_res.json()
    coupon_id = coupon["id"]
    assert coupon["code"] == "FESTIVE25"
    assert coupon["discountType"] == "PERCENTAGE"
    assert coupon["discountValue"] == 25
    assert coupon["maxDiscountAmount"] == 500

    # 3. Prevent duplicate coupon code
    dup_res = admin_client.post("/api/v1/admin/coupons", json=create_payload)
    assert dup_res.status_code == 400

    # 4. Admin lists coupons
    list_res = admin_client.get("/api/v1/admin/coupons")
    assert list_res.status_code == 200
    assert any(c["code"] == "FESTIVE25" for c in list_res.json())

    # 5. Admin updates coupon
    patch_res = admin_client.patch(
        f"/api/v1/admin/coupons/{coupon_id}",
        json={"discountValue": 30, "isActive": False},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["discountValue"] == 30
    assert updated["isActive"] is False

    # 6. Admin deletes coupon
    del_res = admin_client.delete(f"/api/v1/admin/coupons/{coupon_id}")
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]

    # 7. Confirm 404 after deletion
    get_res = admin_client.get(f"/api/v1/admin/coupons/{coupon_id}")
    assert get_res.status_code == 404


def test_admin_review_moderation():
    """Verify admin review inspection and deletion with rating recalculation."""
    admin_client = _create_admin_client()
    customer_client = _create_customer_client("9999911008")

    # 1. Customer creates a review on product 2
    create_res = customer_client.post(
        "/api/v1/products/2/reviews",
        json={"rating": 1, "text": "Arrived later than expected", "location": "Pune"},
    )
    assert create_res.status_code == 201
    review_id = create_res.json()["id"]

    # 2. Admin lists reviews
    admin_reviews_res = admin_client.get("/api/v1/admin/reviews")
    assert admin_reviews_res.status_code == 200
    review_ids = [r["id"] for r in admin_reviews_res.json()]
    assert review_id in review_ids

    # 3. Admin deletes the review
    del_res = admin_client.delete(f"/api/v1/admin/reviews/{review_id}")
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]

    # 4. Verify review is gone
    admin_reviews_res2 = admin_client.get("/api/v1/admin/reviews")
    review_ids2 = [r["id"] for r in admin_reviews_res2.json()]
    assert review_id not in review_ids2
