#5.11.1 asset/frontend return —2026-10-14
Owner Codex. Asset phase verified; final API/srcset integration awaits Gemini5.11.2. No git push or VPS deployment.

## Verified results
- YAML-configured Sharp pipeline,62 approved original images,212 smaller WebP variants. Widths480/800/1200/1600 plus native width when configured; never upscaled/cropped. Non-beneficial variants omitted. Animated/oriented sources fail for review rather than silently changing composition.
- All62 original SHA256 values independently rechecked unchanged. All212 derivative hashes, byte lengths, decoded dimensions and WebP format independently rechecked against manifest.
- `public/images/optimized/manifest.json` contains immutable content-addressed keys and provenance. Encoder settings `config/media-variants.yaml`; generation `pnpm media:variants` or alternate YAML path argument. Originals and existing DB image keys preserved.
- Existing R2 uploader uploaded ONLY212 new WebP files with optimized/ prefix using explicitly present preprod storage configuration.212 public HTTP200 checks passed; no original object uploaded/replaced. Current configured bucket/base were sulocraft-products / https://images.sulocraft.com. This records actual existing configuration, not a new environment fallback. No secret data in reports.

|Source|Original bytes|800px WebP bytes|Transfer reduction|
|---|---:|---:|---:|
|hero/heritage.png|2172121|58494|97.3%|
|categories/amigurumi/card-v2.png|2477091|77500|96.9%|
|products/forever-crochet-rose-bouquet/primary.png|2449035|120200|95.1%|

## Frontend / local evidence
Shared metadata types and validation cover heroes (independent desktop/mobile source), categories, occasion images and editorial/promo images. Product/gallery support was already5.10. No filename-to-URL construction in GUI, no static content replacement, no frame/control redesign. Source attributes exclude img-only alt and use validated API width variants only.
API/frontend Docker services rebuilt so new asset files are locally served. Actual browser original-vs-WebP comparison of hero/category/rose product verified loading, subject/composition/color/texture retained at display sizes.390×844 viewport: no broken images or horizontal overflow. Normal localhost storefront rendered; console had no errors. **Current API has not yet attached new manifest variants; real storefront hero srcset is absent. Do not claim optimized production delivery yet.**

## Tests/security
Encoder fixture tests verify source preservation, deterministic content keys, actual WebP dimensions/aspect, transfer reduction, invalid configuration/widths, traversal, missing sources and symlink denial. Frontend regression tests cover API-provided desktop/mobile srcset and existing carousel/home behavior. Host typecheck +2 encoder tests +20 Vitest tests passed. Docker dependency cache initially lacked Sharp; image rebuild alone does not replace persisted test node_modules. Frozen force-refresh addresses that dedicated cache; final shared Docker run passed typecheck,2 encoder tests and20 Vitest tests.
SAST zero blocking High/Critical findings; final path-overlap/unsafe-key strengthening self-reviewed and negative tested. pnpm dependency audit: zero advisories across240 dependencies. Tools bind local only; no remote dimension probes, auth/customer data, telemetry or provider-plan changes. Self-review, not independent review.

## Exact handoff
[Gemini5.11.2](../tasks/task-027-backend-responsive-media.md) consumes verified manifest and attaches metadata through configured IMAGE_BASE_URL; no copying/generation/upload by Gemini. It also updates public snapshot version when manifest changes. Final Codex5.11.1 acceptance then rebuilds actual services/artifact and verifies browser currentSrc/transfer, fixed frames, gallery and hero priority.
Cold-device/network throttle controls are unavailable in connected browser; byte reductions verified, field INP/cold4G performance not claimed. Local warm paint measurements remain the limited5.11 evidence. No push/deployment until required local acceptance and user instruction.
