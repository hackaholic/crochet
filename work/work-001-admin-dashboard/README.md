# Work 001 — Admin dashboard integration

**Work owner:** Codex

**Objective:** Integrate the owner-provided Figma admin export into Sulocraft's existing `/admin` experience, preserving the supplied design while connecting real APIs.

**Scope:** Reuse the provided admin design; omit demo data and unrelated Figma metadata/branding; connect dashboard, orders, finance, returns, and catalogue APIs as agreed. Track customer/settings functionality separately if it requires new backend contracts.

**Current state:** In Progress. The supplied layout and core dashboard, orders/order detail, finance, and returns screens are present in the existing `/admin` route and use API services. Gemini's backend handoff reports the dashboard, finance, order search/filter, and returns endpoints complete. Products now has a paginated API catalogue and reusable product/category/media/variant editor. Local catalogue/editor and a no-change product save were verified, with both sunflower images loading. Gemini 1.7.5 returned; live tag discovery, duplicate-tag reuse and product save verified. Gemini reports 1.7.9 complete. Inventory UI is implemented and locally verified; Gemini 1.8.4 atomic adjustment API returned. Customers list/search/profile/linked history is implemented and locally verified. Settings remains a placeholder; broader admin acceptance remains pending.

**Dependencies:** Backend contracts in `docs/api-admin.md`; Gemini's prior completion report is in the [handoff archive](../../docs/archive/handoffs-history.md).

**Constraints:** Do not redesign from scratch or hardcode business data. Run local Docker/browser verification before delivery.

**Done when:** The owner-provided visual design is preserved; scoped screens render persisted API data with loading, empty, error, and mutation feedback; remaining placeholders are explicitly accepted or implemented from agreed contracts; meaningful tests pass; and the owner can verify the integrated experience at `http://localhost:8080/admin` before any push/deploy.
