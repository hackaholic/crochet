# Task 15.4 — Reduce mobile content density

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Make each mobile slide quick to understand while preserving the backend-managed campaign content.

## Context and contract

Mobile display should prioritize one headline, one short supporting line, and one primary CTA. Do not hardcode or silently delete backend content; use responsive presentation rules.

## Scope

- In scope: mobile typography, text width/line limits, spacing, and responsive CTA presentation.
- Out of scope: changing stored campaign copy, adding competing CTAs, or altering desktop content unnecessarily.

## Dependencies and relevant files

- Depends on: Task 15.1 and Task 15.2.
- Inspect/edit: `src/components/HeroCarousel.tsx`, component styles, and hero tests.

## Acceptance checks

- [x] Mobile slide presents one clear headline (`text-2xl sm:text-4xl lg:text-5xl`), one brief supporting line (2-line clamp on mobile), and one primary CTA ("Shop Collection").
- [x] Headline does not wrap into excessive lines; copy and button do not clip or overlap (flexible min-height wrapper).
- [x] Desktop campaign text remains intact and API-driven; secondary CTA ("Create Something Custom") remains visible on desktop via `hidden sm:inline-flex`.
- [x] Tests cover mobile content behavior and pass (9/9 tests pass).

## Handoff back

- Record the display rules and tests in Work 015 notes; update this task and coordination.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 015 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Change this task to In Progress before starting.
