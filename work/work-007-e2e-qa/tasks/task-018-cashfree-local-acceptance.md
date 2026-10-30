# Task 7.2.4.2 — Cashfree frontend and local checkout acceptance

**Owner:** Codex  
**Status:** Completed

## Objective

Reconcile the reported-complete 7.2.2 hosted checkout frontend with this checkout, then verify local Mock checkout and Cashfree SDK handoff without repeating already-recorded tests.

## Context

Read Work 007 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, this contract, and [7.2.2](task-006-hosted-checkout-integration.md). The owner reports 7.2.2 complete. On 2026-10-30, its contract still said Pending and source search found no Cashfree SDK/session handling in `src` or package manifests. Reconcile against delivered code first. Do not recreate tests already present in the 7.2.2 return.

## Scope

- In scope: inspect the reported 7.2.2 implementation/evidence; reuse existing tests; fill only missing checkout behavior; verify local Mock order completion and provider error states; ensure Cashfree uses the server-returned `paymentSessionId` and configured environment.
- Out of scope: real Cashfree transactions, secrets in browser code, VPS deployment, backend provider behavior assigned to Gemini.

## Dependencies and relevant files

- Depends on: [7.2.2](task-006-hosted-checkout-integration.md)
- Dependency context: Backend provider 7.2.3 is complete; local Compose explicitly selects Mock. If 7.2.2 changes are not in this checkout, record the exact gap before implementing and do not claim undocumented tests passed.
- Blocked by: None
- Blocker reason: None
- Next action: Gemini completes 7.2.4.1 runtime wiring; then perform preprod Cashfree sandbox acceptance under 7.2.4.3.
- Inspect/edit: `src/lib/api/payments.ts`, checkout payment step, SDK integration, related frontend tests, `docker/compose.yaml`.

## Test cases

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.4.2-TC01 | 7.2.2 evidence matches code | Acceptance | Compare task contract, implementation and recorded tests | Status reflects current code; accepted tests are not duplicated | Source review and task-006 | Pass — SDK/session/return handling implemented and this contract records fresh evidence |
| 7.2.4.2-TC02 | Local Mock remains complete | Regression | Use local Docker storefront and real catalogue item | Mock success updates local order; no Cashfree request occurs | Playwright local browser flow | Pass — created a local guest Mock order for Forever Crochet Rose Bouquet; confirmation and tracking link rendered |
| 7.2.4.2-TC03 | Browser return cannot claim payment success | Security | Supply a fake `payment_status=PAID`, then backend reports PENDING; retry | UI remains unconfirmed; successful view requires backend status and ID bindings | `src/pages/CheckoutPage.test.tsx` | Pass — pending/tampered query stays unconfirmed; matching backend SUCCESS shows confirmation |
| 7.2.4.2-TC04 | Browser receives no credential | Security | Inspect build/source and browser flow | No App ID/Secret Key or provider secret in bundle; SDK receives only session ID | `pnpm build`, SAST, frontend bundle scan, `cashfreeCheckout.test.ts` | Pass — no credential/config names in `dist`; SAST 0 findings |
| 7.2.4.2-TC05 | Invalid return IDs rejected before API request | Security | Use zero/out-of-range payment ID, empty or oversized order ID | No verification request is sent | `src/lib/api/payments.test.ts` | Pass — 4 malformed values rejected before `fetch` |
| 7.2.4.2-TC06 | SDK failure is safe and retryable | Failure | Fail script load or reject SDK with private provider text | Generic UI error; no provider/session text leaked; no false order completion | `src/lib/payment/cashfreeCheckout.test.ts` | Pass — script-load and SDK rejection cases pass |

## Security validation

- Changed trust boundary: customer browser opens hosted checkout using a server-created session.
- Controls: no secret in Vite vars, storage, URL or logs; redirect never marks an order paid; session is bound to server-created order; local Mock is explicit.
- Commands/results: record reused/new frontend tests, typecheck/SAST and local Docker/browser evidence.
- Disposition: Pass for frontend scope; sandbox E2E remains a separate gated task.
- Findings/blockers: Backend verification response does not currently include a server-derived `orderNumber`; UI therefore uses a generic verified-payment receipt if absent. Gemini's 7.2.4.1 contract now requires the response field and includes guest-payment isolation checks. This does not affect payment proof; the browser's orderNumber query is ignored.

## Acceptance checks

- [x] 7.2.2 status/evidence match current checkout; no redundant tests are added.
- [x] Local Mock checkout passes with a real catalogue item.
- [x] Cashfree SDK opens using the server-created session and environment.
- [x] Return handling confirms only through the backend; pending, failed, cancelled and retry states do not show paid.
- [x] No credentials reach the frontend; focused tests/security checks pass.
- [x] Local Docker/browser evidence is recorded before preprod deployment.

## Handoff back

Updated task-006 and Work 007 state with local verification. Gemini's preprod runtime handoff remains ready; do not deploy until that task and the sandbox gate pass.

## Verification summary

- `docker-compose -f docker/compose.test.yaml run --rm --entrypoint pnpm frontend typecheck` — passed.
- Focused Vitest: `payments.test.ts`, `cashfreeCheckout.test.ts`, `CheckoutPage.test.tsx` — 20/20 passed.
- Docker frontend production build — passed; JS/CSS budgets passed (72.3 KB JS gzip / 17.2 KB CSS gzip).
- `./scripts/test.sh security sast` — passed, 0 findings.
- `dist` scan for Cashfree credential/config names — no matches.
- Local Docker API health and storefront (`:8000/health`, `:8080`) passed. Playwright confirmed the catalog image/product, checkout payment selector, local Mock order confirmation and tracking link. Anonymous `/auth/me` and wishlist return 401, and favicon returns 404 in dev; these were unrelated to payment and did not block checkout.
- No Cashfree sandbox or live payment submitted. Preprod runtime, API-derived order number, and provider E2E remain in 7.2.4.1 / 7.2.4.3.
