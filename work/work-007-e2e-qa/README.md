# Work 007 — End-to-end purchase & mobile rendering QA

**Objective:** Execute exhaustive quality assurance across the entire customer journey (browsing, search, occasion filtering, cart, login auto-merge, checkout, multi-provider payment, order tracking, returns) across mobile and desktop viewport targets.

**Scope:** Guest-to-customer cart merge regression in Docker, Cashfree hosted checkout with Mock and retained Razorpay provider regressions, payment intent/webhook verification, mobile rendering matrix (`390×844`, `430×932`, tablet, desktop), cross-browser testing (Chromium, Firefox), and pre-launch acceptance checks.

**Owner:** Codex

**Status:** In Progress

**Current state:** Cashfree hosted checkout and retry are implemented; Sandbox success and initial failure behavior are recorded, with cancellation, pending, same-order retry and customer-history browser scenarios still tracked in 7.2.4.3. 7.13 removed COD from new purchases while preserving historical records; full local gates passed and dev deployment plus browser verification succeeded. 7.12 recommendations, 7.11 contact prefill, and 7.1 cart/login/purchase regressions are recorded in their task contracts.

**Dependencies:** `docs/testing-plan.md`; live local Docker stack.

**Done when:** Full purchase flow runs flawlessly without manual interventions; payment webhooks reconcile orders reliably; zero layout overflows or touch target violations on mobile devices; automated regression suite passes.
