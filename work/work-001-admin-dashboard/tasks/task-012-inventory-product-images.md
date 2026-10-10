# Task 1.8.5 — Inventory product thumbnails

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective and scope
Show each product photo beside its name/variant in Inventory for reliable identification. Reusable fixed-size thumbnail renders backend primaryImageUrl (or already-absolute legacy image URL); never construct storage paths or insert unrelated images. Missing/broken image has a neutral labeled fallback, retaining product/SKU/stock/actions. No backend changes or release.

## Dependencies and files
AdminProduct primaryImageUrl already resolves storage keys. src/admin/pages/InventoryPage.tsx, components/ProductThumbnail.tsx, InventoryPage.test.tsx. Existing stock handoff1.8.4 remains unchanged.

## Acceptance/tests/security
- API image URL and accessible product name used; fixed64px square, contain fit, lazy loading.
- Missing URL/storage-key-only and network error show neutral fallback; SKU/actions remain usable.
- Regression tests/typecheck pass; rebuild local frontend and inspect real image desktop/mobile.
- No credentials or invented content; React escapes text, only HTTP(S) images render. Security self-review recorded.

## Handoff back
Update tasks/notes/coordination with local evidence and status. No push/deployment.

## Verification — 2026-10-10
TypeScript and all5 Inventory tests pass in Docker, including backend URL, broken-image fallback and storage-key rejection. Frontend rebuilt/restarted. Real sunflower image loads at64×64px beside product/variant; mobile390px document has no overflow. Corrected global image height override with explicit thumbnail dimensions. Security/self-review: HTTP(S) URLs only, no storage-path construction or API contract change; product/SKU/actions retained on failure. No push/deployment; no Gemini work required for this image subtask.
