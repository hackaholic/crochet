# Decisions

## DEC-024-001 — Mobile-only shared design tokens
Owner clarified screenshot is mobile. Preserve desktop. Declare spacing/type tokens once and consume them through semantic section/header/card/footer classes; do not scatter per-section padding overrides or hardcode business content. CSS is frontend design configuration, not a backend CMS field.

## DEC-024-002 — Compact without clipping
Reduce combined adjacent padding and heading gaps; keep content natural-height, wrapping, all API text/images, product proportions and touch controls. Never hide descriptions, force fixed heading heights or shrink buttons to gain space.

## DEC-024-003 — Responsive spacing refinement
2026-10-20 owner requests tighter homepage section gaps generally. Extend shared spacing configuration to tablet/desktop and tighten mobile further. This supersedes DEC-024-001 desktop-preservation only for section spacing; hero/header/card sizing and API content remain intact.

DEC-024-004 — Shared listing header uses the measured storefront-header token, compact responsive design tokens and44px controls. Keep full backend category/collection description after results so mobile products appear sooner without losing crawlable copy. No content or per-category layout hardcoding.

DEC-024-005 — Catalogue sort is breadcrumb-sized native select in a shared navigation strip directly beneath menu; filter remains inline with heading.24.6 supersedes24.5 sort-control44px sizing with compact32px target while preserving accessible label/native keyboard interaction.

DEC-024-006 — Category routes are fixed catalogue context; only descendant category choices and scoped price/occasion/customizable options apply. Shop supports multiple categories with dynamic heading. Remove active chips in favor of checkbox deselection/Clear. Desktop uses breadcrumb/summary/sort columns; mobile wraps into two compact rows to retain legibility.

DEC-024-007 — Replace price brackets with a reusable native dual-range control and precise Min/Max inputs. No slider dependency exists, so retain browser keyboard/pointer mechanics rather than adding a library. Validated public VITE_CATALOGUE_PRICE_MIN/MAX defaults0/100000; full/reset range means no price restriction. Whole rupee, finite/safe integer edits only; clamp crossed/out-of-range values. Checkout/backend remains price authority.

DEC-024-008 — Price is scoped to current listing path/category/collection/occasion identity. Navigation resets it to configured full range; same-listing sorting/drawer/checkbox interactions retain it. No new cross-page persistence.
