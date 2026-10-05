# Task 15.2 — Implement compact responsive layout

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Keep the desktop hero strong while reducing mobile hero height and visual dominance.

## Context and contract

Follow Task 15.1 audit and Work 015 decisions. Target approximately 460–520px desktop, 380–440px tablet, and 300–340px mobile. Do not use viewport-height takeover on mobile.

## Scope

- In scope: responsive height, layout, spacing, and responsive CSS behavior for the current hero.
- Out of scope: redesigning desktop, changing homepage order, campaign content, or increasing/removing slides.

## Dependencies and relevant files

- Depends on: Task 15.1.
- Inspect/edit: `src/components/HeroCarousel.tsx` and its component styles; add meaningful component/CSS tests as needed.

## Acceptance checks

- [x] Mobile hero image area is approximately 312px and never forced to `100vh`/`100svh` (`408px` section minus `96px` top offset).
- [x] The next homepage section begins within the first viewport on the phone-sized local browser.
- [x] Responsive sizing preserves the full-width composition and removes the fixed-height copy wrapper; local mobile render shows no CTA/control overlap.
- [x] Focused hero tests (4/4) and TypeScript typecheck pass; local Docker frontend/API are healthy and the browser renders API-fed hero and homepage sections.

## Handoff back

- Record changed files, measured heights, tests, and browser results in Work 015 notes; update task status and coordination.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 015 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Change this task to In Progress before starting.

## Verification notes

- Section heights are 408px mobile, 540px tablet, and 620px desktop. After reserved header space (96px mobile, 112px at `sm`+), image areas are 312px, 428px, and 508px.
- Rebuilt with `docker-compose -f docker/compose.yaml up -d --build frontend api db`.
- `vitest run src/components/HeroCarousel.test.tsx`: 4 tests passed; `tsc --noEmit`: passed.
- Local browser at `http://localhost:8080/` rendered campaign image/text/CTA, bottom-centered controls, and the following category section. The browser viewport available in this session was phone-sized; desktop visual inspection remains for Task 15.7.
