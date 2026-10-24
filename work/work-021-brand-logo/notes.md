# Notes
Source: /home/anu/Downloads/Website logo.PNG. No source file renamed or removed.

Verified local DB key and API logoUrl; storefront/header/footer images loaded. R2 public URL verified by upload script. Fixed missing sqlalchemy alias in sequence alignment discovered during API startup; Docker startup now healthy. Frontend 18 tests, backend 5 tests passed. Local customer fixtures use real catalogue products; unused dummy listings removed from local DB only. No production data changed.

21.5: Removed separate header/footer wordmark. Original header height preserved (86.19px), 53.19px logo slot; desktop/mobile loaded image and no page overflow verified. Screenshots /tmp/sulocraft-logo-fixed-height-{mobile,desktop}.png. Four focused tests/typecheck passed. Changes local only.
21.6 diagnosis: live api-dev.sulocraft.com/api/v1/storefront returns brand without logoUrl; R2 images.sulocraft.com/brand/sulocraft-logo.png returns HTTP200. Latest backend/migration must deploy before dev frontend can resolve DB logo. Do not reupload or hardcode CDN fallback.

21.7 correction: Compared against HEAD^ pre-brand-logo SVG, which used width/height=size38. Restored actual slot38 instead of post-logo53.2. Header padding/classes unchanged. Actual menu73px desktop and75px mobile because action controls are40/42px, not logo. Earlier estimate71px excluded control heights. Four tests/typecheck passed; local screenshot /tmp/sulocraft-menu-original-height.png. No push.

2026-10-25 — 21.8: AuthDialogHeader official API-backed logo enlarged from 80×32 to 200×80, shared by loading/live/sent states; removed small white square around wide artwork. Dialog outer geometry and navigation logo unchanged. Added asynchronous size-parity regression. Security scope: presentation-only, no new URL/auth/cookie/API changes; retain safe media validation, image-error fallback, Escape/focus and social-login fail-closed checks. Initial new test corrected to await API logo after remount; initial separate AuthModal worker startup timed out during concurrent build, so focused suite rerun after build. Browser inventory empty: actual desktop/mobile visual check remains unverified, no push.

21.8 final checks: 10/10 AuthDialogFrame/AuthModal/BrandLogo tests passed after async assertion correction; TypeScript passed. Local frontend image rebuilt and restarted; API dependency healthy. Diff whitespace clean. Visual check remains blocked by empty browser inventory; no release performed.
