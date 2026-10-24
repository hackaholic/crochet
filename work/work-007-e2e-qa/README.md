# Work 007 — End-to-end purchase & mobile rendering QA

**Objective:** Execute exhaustive quality assurance across the entire customer journey (browsing, search, occasion filtering, cart, login auto-merge, checkout, multi-provider payment, order tracking, returns) across mobile and desktop viewport targets.

**Scope:** Guest-to-customer cart merge regression in Docker, Razorpay/Mock payment intent and webhook verification, mobile rendering matrix (`390×844`, `430×932`, tablet, desktop), cross-browser testing (Chromium, Firefox), and pre-launch acceptance checks.

**Owner:** Codex

**Status:** In Progress

**Current state:**7.11 signed-in checkout contact prefill locally complete;7.1 guest/login/cart acceptance remains pending. Existing tests/assets/services reused. Mock-provider local QA only; real OAuth/provider/browser or owner approval gaps are recorded rather than assumed complete.

**Dependencies:** `docs/testing-plan.md`; live local Docker stack.

**Done when:** Full purchase flow runs flawlessly without manual interventions; payment webhooks reconcile orders reliably; zero layout overflows or touch target violations on mobile devices; automated regression suite passes.
