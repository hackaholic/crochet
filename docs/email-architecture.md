# Sulocraft V1 email architecture

This is the canonical email plan for `sulocraft.com`. DNS is managed in Cloudflare. The owner's destination Gmail address is private configuration and must never appear in source code, documentation, logs, frontend responses, or customer-facing pages.

## Service split

```text
Incoming customer email
  → Cloudflare Email Routing
  → owner's private Gmail inbox

Outgoing transactional email
  → Sulocraft FastAPI EmailService
  → Resend
  → customer
```

Cloudflare Email Routing only receives and forwards mail. It is not a mailbox service and is not used by the backend to send automated messages.

## Incoming email with Cloudflare

Create these forwarding routes:

| Public address | Destination |
| --- | --- |
| `hello@sulocraft.com` | Owner's private Gmail inbox |
| `support@sulocraft.com` | Owner's private Gmail inbox |
| `orders@sulocraft.com` | Owner's private Gmail inbox |

Setup checklist:

1. Enable Cloudflare Email Routing for `sulocraft.com`.
2. Add and verify the private Gmail destination without committing it to the repository.
3. Create all three routing rules.
4. Apply Cloudflare's required MX and SPF records.
5. Test every public address and confirm forwarding.

Customers only see and use `@sulocraft.com` addresses.

## Outgoing email with Resend

Resend is the V1 transactional provider. Verify `sulocraft.com` in Resend and add its required SPF and DKIM records in Cloudflare. Add the recommended DMARC policy, starting in monitoring mode if necessary and strengthening it after verified delivery.

Default V1 sender:

```text
Sulocraft <orders@sulocraft.com>
```

Optional sender identities:

```text
Sulocraft <hello@sulocraft.com>
Sulocraft Support <support@sulocraft.com>
```

Personal Gmail must never be used for automated transactional mail.

## Transactional events

Resend sends:

- magic-link login;
- order and payment confirmation;
- processing and packed updates;
- shipment confirmation and tracking information;
- out-for-delivery and delivered updates;
- cancellation and refund notifications.

Events must be idempotent where retries could send duplicates. Provider failures must not corrupt authentication, payment, or order state.

## Backend boundary

Business and authentication services depend on `EmailService`, never directly on Resend:

```text
EmailService
├── send_magic_link()
├── send_order_confirmation()
├── send_payment_confirmation()
├── send_shipping_update()
├── send_delivery_update()
└── send_refund_notification()
```

The provider adapter owns Resend API behavior. Templates, event selection, audit records, retries, and idempotency remain provider independent. Local development uses the mock/capture provider through the same interface.

## Environment configuration

```ini
EMAIL_PROVIDER=resend
RESEND_API_KEY=
EMAIL_FROM_ORDERS=Sulocraft <orders@sulocraft.com>
EMAIL_FROM_SUPPORT=Sulocraft Support <support@sulocraft.com>
EMAIL_FROM_HELLO=Sulocraft <hello@sulocraft.com>
FRONTEND_URL=https://sulocraft.com
```

API keys and the private forwarding destination belong in deployment secrets. `.env.example` contains variable names and safe placeholders only.

## Acceptance checks

- Cloudflare forwards all three public addresses to the verified private destination.
- Resend reports the domain verified and SPF/DKIM passing; DMARC exists in Cloudflare DNS.
- A production-like test arrives from `Sulocraft <orders@sulocraft.com>` and never exposes Gmail.
- Magic-link and every order lifecycle event uses `EmailService`.
- Local mock tests cover every event without network credentials.
- Logs redact magic-link tokens, API keys, and the private forwarding address.
