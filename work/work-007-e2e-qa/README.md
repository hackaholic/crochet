# Work 007 — End-to-end purchase & mobile rendering QA

**Objective:** Execute exhaustive quality assurance across the entire customer journey (browsing, search, occasion filtering, cart, login auto-merge, checkout, multi-provider payment, order tracking, returns) across mobile and desktop viewport targets.

**Scope:** Guest-to-customer cart merge regression in Docker, Cashfree hosted checkout with Mock and retained Razorpay provider regressions, payment intent/webhook verification, mobile rendering matrix (`390×844`, `430×932`, tablet, desktop), cross-browser testing (Chromium, Firefox), and pre-launch acceptance checks.

**Owner:** Codex

**Status:** In Progress

**Current state:** 7.2.2 / 7.2.4.2 Cashfree frontend and local Mock acceptance are complete. 7.12 adds full-width, layered API recommendations to the order confirmation and is locally verified. Gemini is working on 7.2.4.1 preprod runtime wiring; dev Sandbox acceptance remains gated on its return. 7.11 signed-in checkout contact prefill and 7.1 Docker cart/login/purchase regressions are recorded. No Cashfree transaction or deployment is assumed complete.

**Dependencies:** `docs/testing-plan.md`; live local Docker stack.

**Done when:** Full purchase flow runs flawlessly without manual interventions; payment webhooks reconcile orders reliably; zero layout overflows or touch target violations on mobile devices; automated regression suite passes.
