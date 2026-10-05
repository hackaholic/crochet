# Task 15.5 — Tune carousel controls for mobile

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Keep carousel navigation compact, touch-friendly, and accessible on phones.

## Context and contract

Preserve the current focused slide count. Prefer swipe support, small pagination indicators, and arrows only when useful. Controls must respect keyboard use and reduced motion.

## Scope

- In scope: touch/swipe behavior, pagination, optional arrows, focus states, labels, and reduced-motion behavior.
- Out of scope: adding slides or placing large controls over important product details.

## Dependencies and relevant files

- Depends on: Task 15.1; coordinate styling with Task 15.2.
- Inspect/edit: `src/components/HeroCarousel.tsx`, `src/components/HeroCarousel.test.tsx`, and component styles.

## Acceptance checks

- [x] Swipe works without blocking ordinary page scrolling or other controls (`Math.abs(deltaX) > Math.abs(deltaY)` and `> 40px`).
- [x] Pagination remains compact; arrow circles retain the original 36px visual size while an invisible 44px hit area preserves mobile touch access, and pagination stays 44px tall with compact widths and accessible names/focus styles.
- [x] Keyboard controls/focus (`ArrowLeft` / `ArrowRight`) and reduced-motion behavior remain correct.
- [x] Tests cover slide navigation, `pan-y` touch behavior, accessible names, compact target styling, and reduced-motion autoplay (10/10 tests pass).

## Handoff back

- Record control behavior, accessibility checks, and tests in Work 015 notes; update task and coordination.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 015 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Change this task to In Progress before starting.
