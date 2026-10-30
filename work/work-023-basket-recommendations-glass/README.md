# Work 023 — Basket recommendations and glass presentation

**Owner:** Codex
**Status:** In Progress — 23.10 completed locally; 23.11 adds wishlist heart controls to all recommendation cards

## Objective
Make basket and Wishlist pages useful database-driven product discovery surfaces, starting a restrained liquid-glass-inspired basket presentation without changing Sulocraft branding.

## Scope and architecture
Keep the existing modular React/FastAPI application. Drawer layout/material belongs to frontend; product names, photos, prices, availability and ranking come from the database/API. Reuse the bounded catalogue endpoint for newest products initially. Never call this customer personalization. 23.3 provides basket-aware ranking/authenticated signals;23.7 integrates its bounded lead with the existing ranked/paginated feed.

Blueprint: `src/components/CartDrawer.tsx` (basket shell), `src/components/basketGlass.css` (material/fallback), `src/components/ProductRecommendations.tsx` (reusable layered discovery), `src/lib/api/productDiscovery.ts` (bounded catalogue adapter). Wishlist follow-up reuses this feed; no new infrastructure/dependencies.

## Constraints / definition of done
Both basket states show eligible discovery products without duplicates or basket items; failure never blocks checkout. Keep text/cards opaque enough to read, native modal focus/Escape handling, mobile scrolling, reduced-motion/transparency fallbacks. Verify Docker/browser locally before any push. Preserve current totals; their existing hardcoded shipping/coupon limitations remain Work007 findings, not validated pricing rules. No deployment authorized by this work request.

## Dependencies
Work007 continues separately; Gemini is already working on payment files. This work must not edit those files. 23.3 backend and23.7 frontend integration are completed. 23.4 browser acceptance was provided by the owner2026-10-24. Wishlist currently shows saved items or an empty state only; 23.9 adds the API's `wishlist` cursor context and 23.8 renders reusable discovery layers beneath either state.
