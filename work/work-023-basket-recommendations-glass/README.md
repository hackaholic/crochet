# Work 023 — Basket recommendations and glass presentation

**Owner:** Codex
**Status:** In Progress

## Objective
Make empty and filled baskets useful discovery surfaces, starting a restrained liquid-glass-inspired presentation without changing Sulocraft branding.

## Scope and architecture
Keep the existing modular React/FastAPI application. Drawer layout/material belongs to frontend; product names, photos, prices, availability and ranking come from the database/API. Reuse the bounded catalogue endpoint for newest products initially. Never call this customer personalization. A separate backend contract adds basket-aware ranking and authenticated signals later.

Blueprint: `src/components/CartDrawer.tsx` (shell), `src/components/basketGlass.css` (material/fallback), `src/components/BasketRecommendations.tsx` (reusable discovery), `src/lib/api/basketRecommendations.ts` (bounded catalogue adapter). No new infrastructure/dependencies.

## Constraints / definition of done
Both basket states show eligible discovery products without duplicates or basket items; failure never blocks checkout. Keep text/cards opaque enough to read, native modal focus/Escape handling, mobile scrolling, reduced-motion/transparency fallbacks. Verify Docker/browser locally before any push. Preserve current totals; their existing hardcoded shipping/coupon limitations remain Work007 findings, not validated pricing rules. No deployment authorized by this work request.

## Dependencies
Work007 continues separately; Gemini is already working on payment files. This work must not edit those files. Full personalization awaits task23.3, not required for initial newest-product discovery.
