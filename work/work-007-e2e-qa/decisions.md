# Work 007 decisions

### DEC-007-1 — Mobile-First Quality Gate

**Decision:** Mobile (`390×844` viewport) is the primary target for all shopping QA tests. Mobile tests must pass before desktop verification.

**Reason:** Over 75% of Indian D2C e-commerce traffic originates from mobile devices (iOS Safari and Android Chrome).

### DEC-007-2 — Idempotent Webhook Processing

**Decision:** Payment webhooks must be verified with idempotency keys and state checks. Repeated webhook deliveries must never create duplicate orders or double-charge stock.

**Reason:** Razorpay webhooks can retry upon transient network timeouts.
