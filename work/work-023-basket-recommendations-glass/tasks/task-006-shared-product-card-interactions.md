# Task 23.6 — Shared catalogue interactions in basket recommendations

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective and scope
Reuse ProductCard for basket recommendations: identical portrait image, subtle hover zoom and Quick Add overlay. Keep touch and keyboard actions available. Preserve real asynchronous basket pending/error/retry behavior and product navigation. No backend or deployment changes.

## Dependencies and relevant files
- Depends on: 23.5
- Dependency context: Existing API discovery and canonical cart mutation are verified locally.
- Blocked by: None
- Blocker reason: None
- Next action: Implement shared card, run focused tests, rebuild frontend and inspect locally.
- Inspect/edit: src/components/ProductCard.tsx, BasketRecommendations.tsx, related tests, src/index.css.

## Tests and acceptance
- Shared ProductCard rendered in recommendations; portrait image and zoom interaction match catalogue.
- Quick Add uses real pending state, prevents duplicate submissions, safely reports failure and allows retry.
- Product link opens detail; adding keeps basket open. No nested interactive elements.
- Touch/small viewport and keyboard focus expose Quick Add without hover.
- Focused tests/typecheck, Docker rebuild and actual local browser verification required.

## Security validation
No new API, authorization or database boundary. Preserve server-authoritative cart data, React text escaping and generic errors; existing negative tests must pass.

## Return handoff
Update task status, notes and work-local coordination with checks and browser evidence. Self-review required. No push requested.

## Verification return — 2026-10-20
- Typecheck and 8 focused tests passed: ProductCard, BasketRecommendations and CartDrawer. Covers shared portrait/zoom classes, text escaping, API exclusion, duplicate submission, pending state, safe failure/retry and non-navigation on add.
- Docker frontend rebuilt/restarted using root .env. Actual localhost:8080 Quick Add increased cart from 1 to 2 items, subtotal 2098, kept dialog open and excluded the added product. No checkout/payment created.
- Local LAN browser at 390×844: all four portrait frames measured 159.5×212.65625; Quick Add opacity 1, target height 44px. Desktop keyboard focus exposes the same action. [Mobile screenshot](../reports/shared-card-mobile.jpg).
- Hover image zoom reuses the existing catalogue component and class; browser tooling cannot synthesize a pointer hover, so direct pointer animation/native Firefox coverage remains under 23.4 rather than claimed tested.
- Security: scan-sast.sh PASS, zero blocking High/Critical; existing repository lower-severity warnings remain. React escaping/generic-error negative tests pass. No new server authorization or secret handling. Disposition: Pass for this scoped UI change.
- Self-review: no nested controls, no new business data, async basket guard preserved; optional controlled add state leaves existing catalogue callers compatible. No push.
