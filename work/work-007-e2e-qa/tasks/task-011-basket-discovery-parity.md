# Task 7.9 — Shared basket and checkout catalogue template

**Owner:** Codex
**Status:** Completed
**Work item:** Work 007

## Objective and scope
Use the same extended discovery feed on full basket page (empty/filled), preserving summary/coupon/items and real cart callbacks. Drawer also uses paged discovery while retaining the compact two-column ProductCard layout. Backend/API content updates must render dynamically; no repeated hardcoded sections or products. Test basket add/navigation/failure and verify local browser.

## Dependencies
- Depends on: 7.7
- Dependency context: 7.6 supplies ranked sections; 7.7 can implement typed client and honest catalogue compatibility independently.
- Blocked by: None
- Blocker reason: None
- Next action: Execute assigned scope and return evidence.

## Security and acceptance
Meaningful tests and security validation are mandatory: escaped API text, no private errors, no duplicate add/order side effects, bounded requests and safe URLs, keyboard/touch controls. Run focused Docker tests/typecheck, SAST, rebuild frontend and inspect actual localhost before completion. Record evidence, self-review and remaining limitations. No push/deploy.

## Return — 2026-10-20
- Full basket and drawer now use the same paged discovery/Card template as checkout. Drawer keeps compact two columns; full basket uses available page width. Shared discovery stylesheet imports directly with the component, so controls work without first visiting checkout.
- Tests: CartPage covers API-fed recommendations even when empty, exact canonical add callback and no checkout side effect. CartDrawer tests updated for discovery contract and 3/3 pass; common feed failure/duplicate/escape tests apply to the same renderer. Typecheck passed.
- Actual localhost /cart rendered real API photos and discovery; drawer also rendered five eligible cards. Across checkout Contact/Delivery/Payment/Review, discovery persisted and entered Anupama remained after returning to Contact; no order/payment placed.
- Security disposition Pass: shared adapter validates image destinations and product data; shared duplicate/request guards, generic errors and existing server-authoritative cart API remain. No new authorization boundary. SAST zero blocking High/Critical; self-review complete. No push.

Browser evidence: [wide checkout](../reports/discovery-wide-checkout.jpg), [mobile checkout](../reports/discovery-mobile-checkout.jpg), [catalogue preview](../reports/discovery-catalogue-preview.jpg). Native browser/device matrix remains 7.3; only local in-app rendering is claimed.
