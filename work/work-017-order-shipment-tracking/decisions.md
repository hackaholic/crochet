# Decisions

## DEC-017-001 — Shared tracking presentation, verified access
Use existing modular backend and one reusable frontend tracking component for account and guest orders. This fits current scale, avoids another system, and keeps access rules separate from presentation. Guest access must require a secure order-scoped credential; order number, numeric ID, email or phone alone is insufficient. Prefer an expiring unguessable link delivered to the checkout email, with a rate-limited generic-response request flow. Gemini must define issuance/expiry/revocation and confirm compatibility with current guest checkout before implementation; if delivery contact is unavailable, record the decision required rather than expose public order lookup.

## DEC-017-002 — Honest shipment state
Render persisted tracking fields only. Missing courier/tracking/ETA means not yet available. Existing locally generated SLC-LOCAL values require audit and must not be presented as verified carrier tracking. Automatic updates are a separate provider capability, not implied by an order timeline.

## DEC-017-003 — Independent presentation preparation
Task17.6 isolates data-only presentation and tests from API access. This is an explicit additive subtask, not a relaxation of17.1 authorization dependency. Account/guest runtime integration still waits for returned secure contract.

## DEC-017-004 — Guest browser credential transport
Frontend uses fragment links (#token=...) and API X-Guest-Order-Token header; no local/session storage or token query in fetch. Legacy emailed query links are replaced with fragment form on page mount. Fragment survives refresh without being sent as HTTP URL/referrer. Request-link response remains generic; frontend ignores devTrackingLink. Gemini should change email-generated query link to fragment to avoid first-request query logging; frontend cannot erase upstream logs of old links.
