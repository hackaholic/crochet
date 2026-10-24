# Task 7.11 — Prefill signed-in checkout contact

**Owner:** Codex
**Status:** Completed

## Objective / scope
Checkout currently initializes blank contact fields and receives no signed-in customer. Reuse App auth user and existing authenticated account overview/profile API to prefill saved name/email/phone. Split full name on whitespace (first token/rest), retain single-word names. Refresh canonical profile so recently edited details appear. Only untouched fields may be hydrated; preserve manual draft edits, including intentional clearing. Guest stays blank. No address auto-selection, auth API/payment changes, real orders/emails or deployment.

## Dependencies
- Depends on: None
- Dependency context: Work018 profile API and App auth.me user already available. No Gemini/backend enhancement needed.
- Blocked by: None
- Next action: Reusable checkout form hook, wire customer prop, tests/security checks and local Docker/browser verification.

## Acceptance / security
Tests: immediate signed-in prefill, late auth/profile arrivals, one-word/multiword names, missing optional details, preserve edited fields, guests no account request, profile fetch failure leaves checkout usable; stale/mismatched identities cannot hydrate another user's draft; logout/account switch clears prior PII. Existing checkout/discovery tests pass; no createOrder/payment side effects during prefill. Typecheck, rebuild frontend, compare actual demo profile/checkout locally without changing session/profile or placing order. Record unverified native engines. Keep PII out of repository evidence/screenshots where practical.

## Return — 2026-10-24
- Root cause affects all customers: CheckoutPage initialized blank form and App passed no current user; screenshot sample names/email were placeholders, not actual values.
- App now passes auth user. Reusable useCheckoutForm seeds name/email/phone, refreshes canonical existing account overview/profile and hydrates untouched fields only. Guest fields stay blank; single/multiword name split supported. Account switch/logout clears previous contact/address draft; cancelled/stale/mismatched profile responses ignored. No addresses selected automatically; generic name/email placeholders replace sample identities.
- Docker frontend typecheck and11 tests passed (CheckoutPage6/hook5). Coverage: actual form prefill, current profile refresh, late login/profile, guest no-fetch, missing optional fields/API failure, preserved manual edits/intentional clearing, basket updates, mismatched identity/old-response rejection and logout/account-switch PII clearing. No createOrder/payment calls during hydration test. Existing checkout/discovery regressions passed.
- Security self-review Pass: authenticated profile uses existing credentialed API, no client-supplied account lookup or storage/new HTML sink; request ownership guarded both before and inside state update. No backend/auth/payment authority changed. Negative mismatch/stale/logout/failure tests executed. No fresh SAST scan; existing backend authorization controls not changed/retested.
- Frontend rebuilt/restarted. Actual localhost signed-in profile compared to checkout: first/last/email/phone match (all4true). Saved phone absent→blank, not fabricated. Browser session was not the demo account; live current profile checked, demo fixture covered automatically.390px viewport has populated name/email and no horizontal overflow. No order/payment/email/profile/session changes made. Native Firefox/phone engines and live demo-session login not repeated.
- Evidence reports/task-014-prefill-check.json contains booleans only. Private screenshot /tmp/sulocraft-checkout-prefill-private.jpg intentionally excluded from Git; no customer PII stored in work evidence.
- No Gemini/backend dependency. Local only; no push/deployment.
