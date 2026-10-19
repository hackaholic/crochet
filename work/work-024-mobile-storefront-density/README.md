# Work 024 — Compact mobile storefront spacing

**Owner:** Codex
**Status:** In Progress (24.7 labelled content-width sorting)

## Objective
Reduce excessive homepage gaps and heading blocks so more real product imagery appears on screen. Earlier tasks compacted mobile;24.4 extends shared spacing to tablet/desktop.24.5 compacts shared shop/category/filter headers and moves full API description below results while preserving card sizes and controls.

## Scope / architecture
Reusable frontend CSS design tokens in `src/mobileDensity.css`, semantic classes on existing section/card/footer templates. Mobile breakpoint follows existing Tailwind sm640px;24.4 supplies shared tablet/desktop section spacing as well. Backend remains source for all business content/order/media. No per-product/section business-text matching, database spacing fields, admin changes, gateway work, API migration or deployment.

## Definition of done
Shared tokens control section padding, heading/card gaps and mobile typography. All six API section templates and existing homepage fallback use them. Empty/disabled sections remain omitted; CTA/heading semantics unchanged. Test/typecheck and Docker rebuild pass; actual local320/390/430px browser layout checked, header/hero/product frame geometry unchanged at matching widths. Native Firefox/device coverage recorded accurately.
