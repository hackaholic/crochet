# Work 001 — Admin dashboard integration

**Work owner:** Codex

**Objective:** Integrate the owner-provided Figma admin export into Sulocraft's existing `/admin` experience, preserving the supplied design while connecting real APIs.

**Scope:** Reuse the provided admin design; omit demo data and unrelated Figma metadata/branding; connect dashboard, orders, finance, returns, and catalogue APIs as agreed. Track customer/settings functionality separately if it requires new backend contracts.

**Current state:** In Progress. Supplied layout and API-backed dashboard, orders/details, finance, returns, products, inventory, customers and brand Settings are integrated.1.11screen regressions and1.6local desktop/mobile audit Completed. Remaining: catalogue1.7.6 local acceptance; 1.7.13/1.7.14 product production profile proposal is deferred for V1 pending a narrower owner-approved scope; Firefox follow-up1.6.1, private notes/shipment creation API audit1.17, owner acceptance1.12. Unsupported note/shipment controls are explicitly disabled; no blanket release acceptance yet.

**Dependencies:** Backend contracts in `docs/api-admin.md`; Gemini's prior completion report is in the [handoff archive](../../docs/archive/handoffs-history.md).

**Constraints:** Do not redesign from scratch or hardcode business data. Run local Docker/browser verification before delivery.

**Done when:** The owner-provided visual design is preserved; scoped screens render persisted API data with loading, empty, error, and mutation feedback; remaining placeholders are explicitly accepted or implemented from agreed contracts; meaningful tests pass; and the owner can verify the integrated experience at `http://localhost:8080/admin` before any push/deploy.
