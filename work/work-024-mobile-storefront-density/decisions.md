# Decisions

## DEC-024-001 — Mobile-only shared design tokens
Owner clarified screenshot is mobile. Preserve desktop. Declare spacing/type tokens once and consume them through semantic section/header/card/footer classes; do not scatter per-section padding overrides or hardcode business content. CSS is frontend design configuration, not a backend CMS field.

## DEC-024-002 — Compact without clipping
Reduce combined adjacent padding and heading gaps; keep content natural-height, wrapping, all API text/images, product proportions and touch controls. Never hide descriptions, force fixed heading heights or shrink buttons to gain space.
