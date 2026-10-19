# Work 025 — API and images on LAN development URLs

**Owner:** Codex
**Status:** Completed (local)

## Objective
The storefront opened from another device must use its reachable origin for API requests and images, with explicit trusted local origins for authenticated actions.

## Implementation
- Local Compose defaults `IMAGE_BASE_URL` to `/static/images`; the frontend proxies that path and `/api/v1` to its fixed configured API target.
- Generic backend media resolution supports root-relative URLs, intrinsic dimensions and responsive variants without duplicating route prefixes. Absolute CDN URLs remain supported.
- The shared logo URL guard accepts safe relative media as well as HTTP(S) CDN URLs.
- API helpers already use relative URLs when `VITE_API_BASE_URL` is empty. Deployed environments retain their configured remote base.
- `LOCAL_FRONTEND_URL`, `LOCAL_PUBLIC_API_URL` and `LOCAL_ADDITIONAL_CORS_ORIGINS` select local sign-in destinations/trusted origins. The owner's LAN URL is in ignored `.env`, not application code. No wildcard origin or CSRF bypass.

## Local configuration
Run from repository root with the explicit environment file:

```sh
docker-compose --env-file .env -f docker/compose.yaml up -d --build api frontend
```

Compose resolves its default environment-file location relative to the compose project; use `--env-file .env` to load root settings reliably. Change the local URL values if the machine's LAN address changes. Keep `.env` ignored. Production/preprod use their existing environment configuration and private API/database network behind HTTPS proxy; no deployment files or port bindings changed in this work.

## Acceptance
27 backend media/storage tests, frontend typecheck and 10 final frontend logo/media/API tests passed; cart request regression also passed separately. Fallback SAST passed with zero findings. Local API/frontend rebuilt. Actual LAN browser verified loaded logo/hero/products, mock sign-in on the LAN origin, authenticated add-to-cart/account and sign-out. LAN and localhost API/image requests return 200. Untrusted-origin state-changing request returns 403. No push/deployment.
