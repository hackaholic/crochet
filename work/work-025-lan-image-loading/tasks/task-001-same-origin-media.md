# Task 25.1 / 25.2 — Same-origin media on LAN

**Owner:** Codex
**Status:** Completed
**Work item:** Work 025

## Objective / scope
Local images and suppliedresponsivevariants load through storefronthost, not clientlocalhost. Configurable localmedia base/proxytarget; existing deployedCDN URLs untouched. Preserve metadata/absoluteURL behavior. No IP literals, DB data replacement, openproxy, CORSrelaxation or secret changes.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing local frontend/API/data/images; no uploads/setup needed.
- Blocked by: None
- Blocker reason: None
- Next action: Tests for relative media normalization first, thenconfig/proxyandlocalverification.
- Inspect/edit: docker/compose.yaml, vite.config.ts, backend/app/core/images.py, backend/app/services/media.py, backend/tests/test_media_metadata.py, .env.example.

## Test cases
|ID|Category|Action|Expected|Evidence|
|---|---|---|---|---|
|25-TC01|Regression|Root-relative configuredbase,key/alreadyresolvedinput|Exactlyone/static/imagesprefix; correctassetkey/dimensions/variants|Pass — return below|
|25-TC02|Compatibility|HTTPSCDNbase,externalURL,emptyinput|Existingbehaviorunchanged|Pass — return below|
|25-TC03|Security|Traversal/unknownexternalmedia|Nooutboundprobing,newSSRF/openproxy; traversaldenied|Pass — return below|
|25-TC04|Acceptance|BrowseLANandlocalhost originsafterDockerrebuild|Logo,hero,productphotosandvariantsload; no loopbackmediaURLs|Pass — return below|

## Acceptance / security
- [x] Relevant backendtestsandfrontendtypecheck pass.
- [x] API/frontend rebuilt; actual LANbrowser images verified andlocalhostregressionchecked.
- [x] Record self-review and sourceofconfig; no weakenedCORS/auth/pathguards.
- [x] Updatework-localstate; no pushrequested.

## Handoff back
Record exact configuration/files, tests, browserproofandremainingrisks hereandwork-localnotes. Do not log secrets or rawcustomerdata.

## Scope update — API calls and local origin configuration
Owner explicitly requested API calls too. All API helpers already use shared relative`/api/v1`base. Expose exact local frontend/public API/additional-origin settings through Compose; keep deployment configuration unchanged. Local ignored`.env`selects the owner's LAN storefront as the primary sign-in destination. No wildcard/trusted-origin bypass. Verify browser catalogue/cart requests, local mock sign-in, authenticated cart mutation and logout. `.env`must remain ignored and never be printed/committed.

## Return — 2026-10-19
- 25.1,25.2,25.3 completed locally. Read README for exact config and startup command. Relative API paths are unchanged; tests prove local same-origin and configured deployed base behavior.
- Initial regression reproduced failure before media fix. Backend media/storage27passed; final frontend typecheck+10tests passed; separate client/cart3tests passed. Fallback AST/pattern SAST0findings. Relevant logs:`/tmp/work025-tests.log`, `/tmp/work025-final-frontend-tests.log`, `/tmp/work025-api-client-tests.log`, `/tmp/work025-sast.log`.
- Actual LAN browser: loaded logo/hero/catalogue images, mock sign-in stays on configured LAN origin, authenticated add-to-cart/account and logout work. Both LAN/localhost API and image endpoints200. Untrusted-origin mutation403; CSRF intact. Native phone/Firefox not claimed.
- Security disposition: Pass for scoped changes. Self-review completed. No new auth bypass, database migration, host exposure or arbitrary upstream selection. `.env` remains ignored.
- [Browser proof](../reports/lan-storefront.jpg). No push/deployment.
