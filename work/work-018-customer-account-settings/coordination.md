# Work 018 coordination

**Work lead:** Codex.

| Task | Owner | Handoff | Dependency |
| --- | --- | --- | --- |
| [18.2](tasks/task-002-profile-contact-api.md) | Gemini | Returned; Completed | Existing auth/account API |
| [18.3](tasks/task-003-address-management-api.md) | Gemini | Returned; Completed | Existing address CRUD |
| [18.4](tasks/task-004-order-progress-api.md) | Gemini | Returned; Completed | Existing Work017 tracking |
| [18.5](tasks/task-005-account-experience-ui.md) | Codex | Returned; Completed | Backend contracts returned |
| [18.6](tasks/task-006-local-account-acceptance.md) | Codex | Blocked — account checks pass; remaining browser/guest-flow acceptance | Firefox availability and Work01717.5 |
| [18.12](tasks/task-010-clickable-account-summary-cards.md) | Codex | Blocked — authenticated visual review | Existing account navigation and wishlist route; local demo account magic-link cooldown |
| [18.13](tasks/task-011-auth-provider-signout.md) | Codex | Blocked — reported runtime not identified | Existing email/Google server session contract; authenticated browser reproduction needed |

Gemini must read work/GEMINI_WORKFLOW_PROMPT.md then this folder and the one selected contract. Pick one task at a time unless explicitly parallelized; preserve already implemented APIs. Update exact task, notes and coordination on return. No email secrets or raw login links in docs.

- 18.4 Gemini Returned/Completed: Lifecycle milestone progress contract (`OrderMilestoneOut`, `OrderTerminalStateOut`) added additively to `/orders/{number}/tracking`. Follows DEC018-4 with truthful timestamps from `OrderStatusHistory` without backfilling inventions. Terminal states (CANCELLED, REFUNDED) provide honest explanation without false delivery milestones. 18 backend tests passed (`test_orders.py`, `test_tracking_security.py`), 4 vitest transport tests passed (`tracking.test.ts`). Codex unblocked for 18.5.
- 18.3 Gemini Returned/Completed: Address validation (strict Indian PIN `^[1-9][0-9]{5}$`, phone, Unicode and trimming), single default invariant preservation on update and fallback on deletion, IDOR ownership check, historical order snapshot immutability, frontend accountApi methods transport tests. Passed all 32 backend regression tests and 4 vitest transport tests.
- 18.2 Gemini Returned/Completed: Delivery phone validation & persistence, email immutability DEC018-3, Unicode/whitespace handling, uniqueness conflict prevention. 11 backend tests in `tests/test_account.py` passed, vitest `account.test.ts` passed.
- 18.5.1 Codex Returned/Completed — independent navigation shell in task-007-account-navigation-shell.md. Parent 18.5 remains dependent on backend returns.

Customer visual refinement:18.7 and18.8 Pending, owner Codex; no backend handoff needed with current contracts. Pick up exact contracts before implementation.18.6 acceptance dependencies unchanged.

Codex18.7 Active: shared shipment palette and accessible progress cards;18.8 follows. Existing backend contracts unchanged.

18.7 implementation complete, verification queued together with18.8 (shared frontend rebuild/test batch). Codex18.8 Active.

18.7 and18.8 Returned/Completed by Codex:17 frontend tests/typecheck pass, rebuilt local frontend and real demo customer desktop/mobile reviewed. No Gemini work required.18.6 browser/guest-flow acceptance remains separate. Nothing pushed.

18.12 Codex Blocked: implementation, focused tests and typecheck pass; local authenticated visual review cannot proceed because Playwright has no customer session and the demo account is inside magic-link cooldown. Contract: `tasks/task-010-clickable-account-summary-cards.md`. No backend work expected.

18.13 Codex Blocked: backend proves email and Google sessions revoke; 3 backend logout cases and 12 customer/admin UI tests pass; live local endpoint HTTP 200. Could not reproduce the reported runtime because page/environment were not identified and local browser has no authenticated session; Google client ID is missing and email mock is withholding a development link. Contract: `tasks/task-011-auth-provider-signout.md`.
