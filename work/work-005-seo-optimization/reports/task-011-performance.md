#5.11 — local performance pass,2026-10-14
Owner Codex. No push, preprod deployment or field claim.

## Reproduction
1. Build affected local Docker frontend/API, preserving the DB. Use normal public API snapshot build with identical environment configuration before/after.
2. Stage built `dist` into separate directories; run `node scripts/performance/lab-server.mjs <artifact-directory> 4182`. It binds127.0.0.1, serves read-only files with no-store and injects a local metrics probe. Temporarily allow that origin in local API CORS through a Compose override; remove when finished.
3. Connected IAB viewport390×844. Unthrottled host CPU and loopback network; shared warm image/font cache, HTML/JS/CSS no-store. Three homepage loads plus one rose product load each revision. Open search, type a query, verify database results. Read meta[name=sulocraft-lab-metrics]. Probe observes real LCP, CLS session windows, event durations and long tasks; no telemetry or identifiers sent.
4. `node scripts/performance/budgets.mjs <artifact-directory>`. Includes static manifest dependencies/CSS, excludes dynamic chunks until used. `pnpm perf:budget` repeats on dist. Build now runs this gate automatically. Environment overrides `PERF_INITIAL_JS_GZIP_BUDGET` and `PERF_INITIAL_CSS_GZIP_BUDGET` must be positive byte integers; defaults120000/20000.

## Results
| Metric | Before | After |
|---|---:|---:|
| Initial JS raw bytes |556498|376439|
| Initial JS gzip bytes |152245|110687|
| Initial CSS gzip bytes |14529|14056|
| Homepage LCP samples ms |748,260,252|368,220,296|
| Homepage CLS samples |0.01053,0.000003,0|0,0,0.000005|
| Rose product LCP ms, single sample |412|220|
| Rose product CLS |0|0|

Initial JS compressed payload drops27.3%. Homepage median LCP260→296ms illustrates local measurement noise; this is not evidence of a guaranteed latency improvement. All observed local LCP samples remain below2.5s and CLS below0.1. Maximum observed search event duration216ms before/80ms after is a lab event sample, **not field INP or75th-percentile INP**. The interaction sequences/sample windows differ; do not claim a causal INP win. No Lighthouse score or mobile4G/CPU-throttled measurement was collected.

## Changes
- App lazy-loads admin, account, checkout and unopened search/auth overlays. Public pages remain eagerly available to the shared build renderer;96 generated pages still contain public initial markup. Accessible Suspense loading states preserve fixed overlay positioning.
- Fonts keep the same families/styles and display=swap; discovery moved from CSS import to head stylesheet/preconnect links, avoiding that late dependency chain.
- Carousel skips rotation while document.hidden, preserving existing reduced-motion, controls and fixed frames.
- Manifest-aware initial bundle budget is a repeatable release guard, not an analytics platform.

## Verification / limits
Docker typecheck;8 Node budget/hydration checks;28 Vitest carousel/auth/search tests passed.96-page build and initial bundle budget passed. Actual built mobile homepage/product/search and local account/login/admin gate inspected; no hydration errors, images loaded, existing design intact. Demo customer remains authenticated; admin correctly denies access. Login popup verified through invalid-link display path without changing that session. Existing gallery/image attributes from5.10 retained.
SAST: zero blocking High/Critical findings. Fixture-only script-tag warning and existing repository nonblocking warnings are documented, not suppressed. Lab probe/server never enter application code; no secrets, sessions, customer payloads or external telemetry captured. Review is Codex self-review. Incremental codebase index refreshed.

Original hero PNGs still2–2.5MB. Warm loopback results cannot demonstrate a good cold mobile-network LCP. Optimized verified derivatives/API variant delivery are a separate recorded follow-up5.11.1, not permission to invent CDN URLs. Actual device/network/preprod and field monitoring remain5.4/5.21 gates. Firefox engine unavailable; no claim of Firefox verification.
