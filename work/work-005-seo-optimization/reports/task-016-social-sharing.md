# 5.16 — frontend sharing return

## Implemented
Shared `src/lib/seo/socialMetadata.mjs` now generates both initial and client OG/Twitter fields. Added initial Twitter card/title/description/image/alt and OG alt/dimensions/MIME from existing API fields. Preserved article type. Removed stale route social groups, omitted unsafe/nonabsolute/credential-bearing image URLs, unknown dimensions/types and private/error images. Failed metadata fallback no longer borrows the prior page's description/title. No business content, asset or backend mutations.

## Evidence
- Docker test runner: typecheck +8 Node prerender tests +7 SeoManager tests passed. `/tmp/work005-social-docker-tests.log`.
- Local affected frontend Docker rebuild/restart passed. API/DB reused unchanged.
- Full API-backed96-page build passed; initialJSgzip111425, CSSgzip14115 within budgets. `/tmp/work005-social-build.log`.
- All96 generated pages match shared tag values exactly with one instance each. `/tmp/work005-social-html.log`.
- Actual localhost8080 rose→About navigation: oneH1, loaded images; image/title/type/alt/dimensions replaced without duplicate/stale product tags. About type article. IAB browser checked; no native Chrome/Firefox claim.
- Public resolver and image GETs for home/flowers/rose/About:200 and image/png. `/tmp/work005-social-api.json`.
- Security gate: fallback AST/pattern SAST runner PASS; zero findings. No secret/PII/schema/auth boundary changes. Unsafe URL/private/error/missing image negative tests pass; accurately labeled self-review.

## Remaining
Backend-generated product metadata adds blanket milk-cotton/100% claims and About alt describes crocheting instead of the supplied portrait. Exact Gemini5.16.1 contract addresses these after5.13.1 shared-file ownership returns. Main5.16 remains Blocked for this data correction and final parity acceptance.

External WhatsApp/social platform preview/cache check is not performed against localhost: remote crawlers cannot access it. After authorized preprod deployment, share a representative public URL and compare title/image; allow platform cache refresh. Do not submit nonpublic data to external preview services. This release check belongs to integrated5.4; no deployment/push this turn.

Reference reviewed: [Open Graph structured image fields](https://ogp.me/#structured). X's former card documentation redirected to its overview and was not treated as validation evidence.

## Final return acceptance — 2026-10-16
Gemini5.16.1 returned; generated material/activity claims removed. Codex corrected remaining portrait `crochet bouquet` wording to neutral `with a bouquet`; four focused backend tests pass (49 deselected, one existing Starlette/httpx deprecation warning). Local API rebuilt, actual About/rose browser tags/images verified; fresh96-page build and exact tag parity passed including portrait assertion. Logs `/tmp/work005-social-return-tests.log`, `/tmp/work005-social-return-build.log`, `/tmp/work005-social-return-html.log`. Supersedes backend-copy blocker above; main5.16 Completed. No external cache/production validation claimed.
