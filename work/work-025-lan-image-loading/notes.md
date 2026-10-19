# Notes

2026-10-19 diagnosis: homepage API emitted 172 localhost:8000 media URLs. On a phone these resolve to the phone. Frontend already proxied API calls but not images. Local authenticated mutations also require an exact trusted origin, and sign-in links used localhost configuration.

Implementation: root-relative configured media base; fixed-target static-media proxy; idempotent backend builder and metadata/variant key extraction; safe relative logo support. Configurable local frontend/public API/additional origins. LAN primary origin values are in ignored `.env`; explicitly load it with `--env-file .env`. Source/config examples contain no machine LAN IP. Port bindings, production config, CSRF middleware and database content remain unchanged, except disposable local mock customer/cart fixtures used for acceptance.

Evidence: initial root-relative regression failed before fix; final media/storage run 27 passed. Final frontend typecheck plus 10 tests passed; separate client/cart run 3 passed (client tests overlap). Fallback SAST 0 findings; diff self-review passed for scoped changes. New URL guard reuses responsive-media safety policy; no new remote image probing or arbitrary upstream proxy.

Actual browser at LAN origin loaded 11 images, including both logos, with zero localhost:8000 image URLs. Local mock sign-in destination stayed on LAN; authenticated basket addition and sign-out succeeded. LAN and localhost catalogue/image endpoints return 200 with JSON/image MIME types. Forged authenticated POST from untrusted.example returned 403. Viewport override reset. [Screenshot](reports/lan-storefront.jpg).

No credentials printed or committed; `.env` ignore verified. No push/deployment. Native Firefox/actual phone engine not connected; LAN-origin verification uses the in-app browser.
