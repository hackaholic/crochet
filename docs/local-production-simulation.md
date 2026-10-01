# Local production simulation

This environment exercises the same HTTP contracts, cookies, state changes, and UI flows used in production while replacing paid external providers with deterministic local adapters.

## Environment switches

| Concern | Local value | Production value |
| --- | --- | --- |
| Application | `APP_ENV=development` | `APP_ENV=production` |
| Email provider | local capture/mock mailbox | configured transactional provider |
| Payment provider | `PAYMENT_PROVIDER=mock` | `PAYMENT_PROVIDER=razorpay` |
| Image origin | `IMAGE_BASE_URL=http://localhost:8000/static/images` | `IMAGE_BASE_URL=https://images.sulocraft.com` |
| Google client | real public client ID with localhost origin | same client or production client ID |
| Facebook client | real public app ID with localhost origin | same app or production app ID |

Provider choice belongs in environment configuration. React and business services must use the same typed API responses in both modes.

## Local identities

### Google and Facebook

Local development uses the real Google Identity Services and Facebook Login SDKs. Register these development URLs in the provider consoles:

- JavaScript origin: `http://localhost:8080`
- Frontend domain: `localhost`
- Backend/API origin: `http://localhost:8000`
- OAuth redirect URI, when redirect mode is used: the exact callback route implemented by the frontend/backend contract

The frontend obtains a real Google ID token or Facebook access token and sends it through the normal `/auth/google` or `/auth/facebook` endpoint. The backend validates token issuer, audience/app ID, expiry, and verified email as it will in production. No frontend-created session and no development token bypass is used for manual local sign-in.

### Email magic link

Local development uses the production `/auth/email/start` and `/auth/email/verify` routes with a local email capture provider. The captured link must contain a real single-use, short-lived token and establish the same HttpOnly session as production. Phone OTP is not part of V1.

## Production-shaped customer scenario

1. Browse catalogue as a guest.
2. Add distinct variants to the persistent guest cart.
3. Continue as a guest or sign in using Google, Facebook, or email magic link.
4. Confirm the backend merges the guest cart into the authenticated cart.
5. Add/select a delivery address.
6. Apply a valid coupon and verify totals come from the backend.
7. Create an order using `UPI`, `CARD`, or `NETBANKING`.
8. Create a mock payment intent and complete the simulated gateway modal.
9. Verify payment through the normal `/payments/verify` endpoint.
10. Confirm order state becomes `CONFIRMED` and payment state becomes `PAID`.
11. As local admin, move the order through `PROCESSING → READY_TO_SHIP → SHIPPED → OUT_FOR_DELIVERY → DELIVERED` and assign a mock courier/tracking number.
12. As the customer, reload order tracking after every transition and confirm the chronological timeline updates.

Also verify COD, failed payment, cancellation before shipment, inventory restoration, session persistence after reload, logout, and unauthorized order access.

## Mock shipment fixture

- Courier: `Sulocraft Local Express`
- Tracking number: `SLC-LOCAL-000001`
- Estimated delivery: five days after order creation
- Tracking remains backend-owned. The frontend renders the status and timeline returned by `/orders/{orderNumber}/tracking`.

## Acceptance gate

- No frontend-only fake cart, fake order, fake payment success, or fake tracking state.
- Every simulated action calls the same API route used by production.
- Cookies are HttpOnly and requests use `credentials: 'include'`.
- Email capture, payment, and shipment mock providers are impossible to activate when `APP_ENV=production`.
- Google and Facebook manual browser tests use real provider tokens in local development.
- One automated browser scenario covers guest cart → login merge → checkout → payment → tracking.
- Backend integration tests cover email magic link, Google, Facebook, payment success/failure, order transitions, authorization, and idempotency.

## Local verification — 2026-10-01

The Docker stack completed the production-shaped commerce journey successfully:

- a guest cart item survived the legacy phone sign-in and merged into the customer cart before phone authentication was removed from V1;
- checkout created an order through the normal `/orders` API;
- the mock provider created and verified a payment intent;
- a separately authenticated admin advanced the order through `PROCESSING`, `READY_TO_SHIP`, `SHIPPED`, `OUT_FOR_DELIVERY`, and `DELIVERED`;
- customer tracking returned the assigned courier, tracking number, and complete timeline.

Manual Google and Facebook verification remains configuration-dependent. Supply real public app IDs and register `http://localhost:8080` with both providers. The storefront no longer creates fake social identities when configuration or provider scripts are unavailable.

Backend work still required:

- replace the removed legacy phone-auth flow with the email magic-link implementation in `docs/api-auth.md`;
- make the payment factory explicitly consume `PAYMENT_PROVIDER` and reject mock in production.
