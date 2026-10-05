# Task 15.6 — Optimize hero image loading

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Reduce mobile hero image transfer and protect first-contentful/LCP behavior.

## Context and contract

The first visible slide is likely the homepage LCP image. Prioritize only that image; avoid downloading desktop-sized or offscreen slide assets unnecessarily on mobile.

## Scope

- In scope: responsive image sizes/source selection, first-slide priority, deferred non-visible slide loading, and supported modern formats.
- Out of scope: unrelated image optimization or asset replacement.

## Dependencies and relevant files

- Depends on: Tasks 15.2 and 15.3.
- Inspect/edit: `src/components/HeroCarousel.tsx`, image utility/components if present, and performance-related tests.

## Acceptance checks

- [x] First visible hero image receives `loading="eager"`, `fetchpriority="high"`, and `decoding="async"`; later active slides use lazy loading and low fetch priority.
- [x] Mobile requests responsive mobile source below 640px when configured via `<picture><source media="(max-width: 639px)" ... /></picture>`.
- [x] Responsive sizes hint configured: `sizes="(max-width: 639px) 100vw, (max-width: 1023px) 100vw, 1280px"`.
- [x] Image behavior is verified in unit tests, TypeScript check, and production build (9/9 focused tests pass).

## Handoff back

- Record loading strategy, evidence, tests, and remaining limits in Work 015 notes; update task and coordination.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 015 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Change this task to In Progress before starting.
