# Work 024 — Compact mobile storefront spacing

**Owner:** Codex
**Status:** Completed (local, including24.3mobile navigation; native Firefox/device coverage unavailable)

## Objective
Reduce excessive mobile homepage gaps and heading blocks so more real product imagery appears on screen. Apply consistently to every homepage section and footer, retaining desktop layout and readable/tappable controls.

## Scope / architecture
Reusable frontend CSS design tokens in `src/mobileDensity.css`, semantic classes on existing section/card/footer templates. Mobile breakpoint follows existing Tailwind sm640px; desktop styles unchanged. Backend remains source for all business content/order/media. No per-product/section business-text matching, database spacing fields, admin changes, gateway work, API migration or deployment.

## Definition of done
Shared tokens control section padding, heading/card gaps and mobile typography. All six API section templates and existing homepage fallback use them. Empty/disabled sections remain omitted; CTA/heading semantics unchanged. Test/typecheck and Docker rebuild pass; actual local320/390/430px browser layout checked, desktop baseline unchanged. Native Firefox/device coverage recorded accurately.
