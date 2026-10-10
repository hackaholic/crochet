# Decisions

- DEC018-1: Retain the current modular React/FastAPI architecture and reusable tracking components. Backend controls persisted customer/order data; frontend controls layout. Avoid another account/tracking subsystem.
- DEC018-2: Phone is delivery contact data, never an authentication credential. Profile updates do not rewrite saved addresses or existing order snapshots. Names must support Unicode; validation must not reject ordinary punctuation merely as “garbage”.
- DEC018-3: Account email is an authentication identifier. Keep it read-only until a verified email-change contract is implemented. Never silently move identities or weaken login security.
- DEC018-4: Progress shows placed → confirmed → ready for shipment → shipped → delivered. PROCESSING and OUT_FOR_DELIVERY remain visible intermediate updates. Use existing READY_TO_SHIP for ready for shipment; do not invent a PACKED status. Missing historical timestamps stay unknown; no fake completion/events. Cancelled/refunded orders have a distinct terminal explanation.
- DEC018-5: Profile, Addresses and Orders are the core menus. Keep wishlist navigation and sign-out. No password/2FA menus for features that do not exist. India phone/PIN rules must be explicit validation policy with future country support, not scattered regexes.
