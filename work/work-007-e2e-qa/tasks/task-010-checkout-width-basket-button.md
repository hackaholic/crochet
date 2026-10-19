# Task 7.8 — Full-width checkout and visible basket action

**Owner:** Codex
**Status:** Completed
**Work item:** Work 007

## Objective and scope
Remove checkout/catalogue maximum-width cap, preserve small responsive gutters. Replace understated back text with substantial accessible outlined button. Keep measured-header compact spacing. Verify 320/390/430/768/1920 widths without overflow and test button navigates cart. No payment policy changes.

## Dependencies
- Depends on: 7.5
- Dependency context: 7.6 supplies ranked sections; 7.7 can implement typed client and honest catalogue compatibility independently.
- Blocked by: None
- Blocker reason: None
- Next action: Execute assigned scope and return evidence.

## Security and acceptance
Meaningful tests and security validation are mandatory: escaped API text, no private errors, no duplicate add/order side effects, bounded requests and safe URLs, keyboard/touch controls. Run focused Docker tests/typecheck, SAST, rebuild frontend and inspect actual localhost before completion. Record evidence, self-review and remaining limitations. No push/deploy.

## Return — 2026-10-20
- Removed 80rem width cap; checkout/basket/catalogue container fills available width with narrow responsive gutters. Back to basket now has a substantial warm outlined button, hover/focus styles and 44px minimum height.
- Tests: CheckoutPage navigation regression passes and asserts cart navigation with no order call. Real localhost layout at widths 320/390/430/768/1920: no horizontal overflow. At 1920 container spans available 1910px (vertical scrollbar accounts for difference); mobile button height 44px.
- Security disposition Pass: presentation only, no new trust boundary; navigation and no-order-side-effect negative regression passes, common SAST gate zero blocking High/Critical. Self-review retained native button semantics and visible focus. Docker rebuilt; screenshots recorded. No push.

Browser evidence: [wide checkout](../reports/discovery-wide-checkout.jpg), [mobile checkout](../reports/discovery-mobile-checkout.jpg), [catalogue preview](../reports/discovery-catalogue-preview.jpg). Native browser/device matrix remains 7.3; only local in-app rendering is claimed.
