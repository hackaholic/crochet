# Work 007 decisions

### DEC-007-1 — Mobile-First Quality Gate

**Decision:** Mobile (`390×844` viewport) is the primary target for all shopping QA tests. Mobile tests must pass before desktop verification.

**Reason:** Over 75% of Indian D2C e-commerce traffic originates from mobile devices (iOS Safari and Android Chrome).

### DEC-007-2 — Idempotent Webhook Processing

**Decision:** Payment webhooks must be verified with idempotency keys and state checks. Repeated webhook deliveries must never create duplicate orders or double-charge stock.

**Reason:** Razorpay webhooks can retry upon transient network timeouts.

### DEC-007-3 — Incremental checkout polish, shared discovery
- Context: owner requests premium styling with compact spacing and suggestions, added layer by layer.
- Decision: measured fixed-header offset, shared checkout CSS tokens, warm panels and mobile-visible summary; reuse ProductRecommendations/ProductCard. Existing newest catalogue supplies data until backend ranking is ready.
- Consequence: no fake trending claims, duplicate fetching logic, new UI framework or altered payment protocol. Details open separately to preserve the checkout draft. Existing shipping/payment limitations remain tracked independently.

### DEC-007-4 — Sectioned, scrollable discovery without invented rankings
- Context: owner wants New arrivals/Featured/Trending/Popular below checkout and basket, full page width, same template in all steps.
- Decision: one bounded, abortable discovery adapter/feed; server controls section titles/order/rankings. Auto paging plus explicit retry/load-more, deduplication, shared request budgets and canonical cart adds. Missing endpoint alone uses honest newest compatibility; never disguise forbidden/error responses as success.
- Consequence: 7.6 belongs to Gemini, integrated named-section acceptance is 7.10. Full-width container retains narrow mobile gutters and does not resize navigation.

DEC-007-5 — Checkout contact uses existing authenticated user immediately and fresh canonical account profile for untouched fields. Preserve manual edits including clearing; guest no profile fetch; identity changes clear prior PII and stale/mismatched responses cannot hydrate. Do not auto-select saved addresses or change account identity from checkout.

### DEC-007-6 — Cashfree hosted checkout

- **Context:** Owner selected Cashfree for the hosted web payment flow.
- **Decision:** Use Cashfree server-created orders and hosted JS checkout; retain Mock for local/CI and the Razorpay adapter for regression compatibility. Select provider/environment through validated backend configuration. Verify payment server-side and process authenticated, idempotent webhooks; a browser redirect never marks an order paid.
- **Consequence:** Gemini owns the Cashfree backend contract; Codex owns frontend integration and integrated local/sandbox acceptance. Sandbox credentials remain in the configured vault/environment.

### DEC-007-7 — Cashfree environment parity

- **Context:** Owner requests a complete Cashfree Sandbox purchase in preprod and a production path that does not require code changes.
- **Decision:** Local uses Mock; preprod explicitly uses Cashfree Sandbox; production explicitly uses Cashfree Production with a separate SOPS secret group. Provider/environment values belong in validated per-environment deployment configuration; credentials belong in SOPS backend groups. Never fall back across environments.
- **Consequence:** Passing dev Sandbox is required before production readiness. Production also requires Cashfree live activation, production domain/webhook configuration, and owner approval; swapping credentials alone is insufficient.
