# Decisions

## DEC-023-001 — Glass is a presentation material
- Context: owner wants an Apple-style glass direction beginning with basket.
- Approach: warm translucent drawer shell/controls, clear cards, native modal semantics, solid fallback; no literal Apple shader reproduction or heavy graphics package.
- Consequence: predictable performance/accessibility and reusable CSS; this is an incremental direction, not a site redesign.

## DEC-023-002 — Honest discovery before personalization
- Context: both guest and customer baskets need suggestions; customer signals are not yet contracted.
- Approach: bounded API newest-product discovery now; exclude current basket/duplicates/unavailable products. Backend task23.3 handles ranking/authorized customer signals later.
- Consequence: no hardcoded catalogue, fake personalized labels or full-catalogue downloads. Empty/error results omit suggestions without blocking basket actions.
