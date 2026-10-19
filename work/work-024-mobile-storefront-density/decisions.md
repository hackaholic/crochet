# Decisions

## DEC-024-001 — Mobile-only shared design tokens
Owner clarified screenshot is mobile. Preserve desktop. Declare spacing/type tokens once and consume them through semantic section/header/card/footer classes; do not scatter per-section padding overrides or hardcode business content. CSS is frontend design configuration, not a backend CMS field.

## DEC-024-002 — Compact without clipping
Reduce combined adjacent padding and heading gaps; keep content natural-height, wrapping, all API text/images, product proportions and touch controls. Never hide descriptions, force fixed heading heights or shrink buttons to gain space.

## DEC-024-003 — Responsive spacing refinement
2026-10-20 owner requests tighter homepage section gaps generally. Extend shared spacing configuration to tablet/desktop and tighten mobile further. This supersedes DEC-024-001 desktop-preservation only for section spacing; hero/header/card sizing and API content remain intact.

DEC-024-004 — Shared listing header uses the measured storefront-header token, compact responsive design tokens and44px controls. Keep full backend category/collection description after results so mobile products appear sooner without losing crawlable copy. No content or per-category layout hardcoding.

DEC-024-005 — Catalogue sort is breadcrumb-sized native select in a shared navigation strip directly beneath menu; filter remains inline with heading.24.6 supersedes24.5 sort-control44px sizing with compact32px target while preserving accessible label/native keyboard interaction.
