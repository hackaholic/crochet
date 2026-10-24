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
