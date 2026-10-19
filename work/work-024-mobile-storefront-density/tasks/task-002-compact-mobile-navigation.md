# Task 24.3 — Compact mobile navigation and menu edge clearance

**Owner:** Codex
**Status:** Completed
**Work item:** Work 024

## Objective / scope
Fit the logo/action group inside mobile width, add a real right gutter and reduce navigation height while keeping44pxbutton targets. Reuse shared mobile design tokens. Preserve desktop layout, logo proportions, navigation actions and Work015 measured header/hero clearance. Do not change backend content, menu choices or announcement copy.

## Dependencies and relevant files
- Depends on: 15.9
- Dependency context: Existing measured-header fix is implemented/tested locally; preserve pending Work024/025 changes.
- Blocked by: None
- Blocker reason: None
- Next action: Responsive brand/action allocation and navigation tokens, then tests/rebuild/browser.
- Inspect/edit: src/components/Header.tsx, src/mobileDensity.css, src/components/Header.test.tsx.

## Test cases
|ID|Category|Action|Expected|Evidence|
|---|---|---|---|---|
|24.3-TC01|Regression|320/390/430px menu/brand/actions|All inside viewport, at least16pxbutton right gutter,44pxtap targets, navaround53px|Pass — return below|
|24.3-TC02|Behavior|Open/close menu and select account/cart|Expanded state accurate; existing callbacks work|Pass — return below|
|24.3-TC03|Regression|All hero slides and1280px desktop|No reintroduced label overlap; desktop unchanged|Pass — return below|

## Acceptance / security
- [x] Relevant header/hero/hook tests and typecheck pass; frontend rebuilt.
- [x] Actual local mobile/desktop geometry and screenshot recorded.
- [x] Self-review/security disposition recorded; no trust boundary changed.
- [x] Update work records; no push requested.

## Handoff back
Record exact token source, geometry/results and screenshot in this contract and work-local notes. No Gemini dependency or asset work needed.

## Return — 2026-10-19
- Before390px: menu button right396px extended6pxbeyondviewport; icon right386px, navigation75pxhigh. Fixed nonshrinking190pxbrand allocation was crowding actions.
- Shared tokens in`src/mobileDensity.css` now control mobile nav insets, vertical space, brand cap and44pxtap size. Brand can shrink horizontally and retains38pxheight/proportions. Desktop styles are unchanged. Added accurate menu expanded/control attributes.
- Docker frontend typecheck+17header/hero/header-offset tests passed (`/tmp/work024-nav-tests.log`); final frontend rebuilt/restarted (`/tmp/work024-nav-final-build.log`).
- Actual local320/390/430px: navigation53px, menu rightgutter16px, menu44×44px, hero labelclearance13px, no horizontaloverflow. Allfivecampaigns checked at320px: CTA-controls gap21px and labelclearance13px. Menu opens/closes; expandedstate verified.1280pxdesktop navigation73px andhero620px retained.
- [Mobile preview](../reports/mobile-navigation-390.jpg). Native Firefox/realdevice not connected; coverage is in-app viewport rendering. Override reset.
- Security disposition: Pass for presentation-only scope. Diff self-review: no new API/auth/HTML boundary; actions/callbacks and observed-header cleanup remain tested. No new backend dependency or asset work. No push/deployment.
