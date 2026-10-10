# Task 1.7 — Admin catalogue integration

**Owner:** Codex
**Status:** In Progress
**Work owner:** Codex

## Objective
Replace Products placeholder within the supplied admin design with a paginated catalogue and reusable editor for listings, categories/tags, prices, variants and uploaded photos.

## Scope and dependencies
Subtasks 1.7.1 list/filter, 1.7.2 create/edit/categories, 1.7.3 variants/pricing, 1.7.4 media, 1.7.6 tags/local acceptance. Existing admin product/category/variant/upload routes are verified in backend/app/api/v1/admin.py. Tag discovery/create requires Gemini 1.7.5. Do not invent tags or redesign admin shell. Preserve inactive products and existing identity/order relationships. Work016 owns bulk classification audit.

## Relevant files
src/admin/AdminApp.tsx; src/lib/api/admin.ts; src/admin/pages; docs/api-admin.md; backend/app/api/v1/admin.py.

## Acceptance and tests
- [ ] List/search/status/category filters and pagination use persisted API data; stale requests cannot overwrite current filter results.
- [ ] Create/edit validates required name/image and variant SKU/price; API errors preserve form; saved data reloads accurately.
- [ ] Variants add/edit price and stock through existing API; no negative values or duplicate submissions.
- [ ] Photo upload uses multipart endpoint and backend URL; failures preserve form and gallery order/primary selection.
- [ ] Tags come from backend, support existing and new tags after 1.7.5 returns.
- [ ] Meaningful success, failure, boundary and mutation tests pass; typecheck passes.
- [ ] Rebuild affected local Docker services; verify admin and changed storefront product on desktop/mobile before delivery.

## Security validation
Existing credentials-included admin APIs enforce admin authorization. No storage credentials or hardcoded business data in UI. Reject unsupported uploads through existing API; preserve safe React text rendering. Auth/validation backend regressions and frontend failure tests required. Disposition pending implementation.

## Handoff back
Update task status, work-local notes and coordination with tests, browser evidence, exact blockers and next action. No push/deployment until local verification and owner review.

## Integration discovery — Task 1.7.7 (Codex)
Admin read responses expose storage keys, causing broken photos. Add primaryImageUrl/galleryImageUrls as additive computed response fields using the existing backend resolver. Preserve primaryImage/galleryImages write keys; upload must persist returned key and render returned URL. Test exact key preservation and environment-configurable URL resolution.

## Current evidence and remaining acceptance
2026-10-09: 18 frontend/admin tests and TypeScript pass in Docker; 2 backend media tests pass. Local no-change product save succeeded; both sunflower photos loaded. Mobile page width 390px without document overflow. Self-review recorded in notes.md. Dependency: Gemini 1.7.5 returned; concurrent case-insensitive tag creation needs Gemini 1.7.9 follow-up. Pending: real create/upload/tag roundtrip and Firefox browser acceptance. No release authorized by this record.

2026-10-09 continuation: Local editor loaded persisted tags and existing selections. Adding the already-selected “sunflowers” tag returned the existing tag without duplicate choices; product save succeeded. TypeScript and 18 prior tests passed; added 2 tag regression cases, all 6 ProductEditor tests passed. Final create/upload and Firefox acceptance remain pending. No push or deployment.

## Authoritative subtask records — workflow repair
This file retains the catalogue parent blueprint/history. Checklist subtasks now link to individual contracts task-014 through task-018 with their matching IDs/statuses; no completed work was deleted. Final acceptance remains1.7.6 Pending; prior concurrency dependency resolved by returned1.7.9.
