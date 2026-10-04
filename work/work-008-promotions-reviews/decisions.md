# Work 008 decisions

### DEC-008-1 — Server-Side Discount Calculation

**Decision:** The frontend never computes final discounted cart subtotals. It sends the coupon code to `POST /api/v1/cart/coupon`, and the backend returns the authoritative discount in integer paise.

**Reason:** Prevents tampering with discounts, minimum order value thresholds, or expiration dates.

### DEC-008-2 — Moderation Default for Reviews

**Decision:** New customer reviews default to `is_approved=False` or verified-purchase gating before appearing publicly on product pages.

**Reason:** Protects brand integrity against spam and abusive content.
