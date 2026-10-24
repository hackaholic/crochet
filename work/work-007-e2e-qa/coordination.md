# Work 007 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

Current implementation owner and status are recorded in the selected task entry in tasks.md. If no task is In Progress, the work is queued, completed, or blocked as that file states. A cross-agent handoff becomes active only when an exact contract is assigned and this section links to it.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

## Previous pickup — 2026-10-19
- Codex: 7.1 In Progress (guest merge & cart regression).
- Gemini: 7.2.1 Completed ([task-005-payment-provider-hardening.md](tasks/task-005-payment-provider-hardening.md)). Provider abstraction and Razorpay boundary hardened; 11/11 payment tests passed. Unblocks 7.2.2 for Codex.
- Codex: 7.2.2 Ready for pickup ([task-006-hosted-checkout-integration.md](tasks/task-006-hosted-checkout-integration.md)).

## Current return — 2026-10-20
**Owner:** Codex
**Status:** Returned — 7.5 Completed
[7.5 checkout presentation/discovery](tasks/task-007-checkout-presentation-discovery.md) includes exact tests/security/local screenshot evidence. No new Gemini dependency; existing backend recommendation enhancement remains Work023/23.3. 7.1 and 7.2.2 remain pending; no push or deployment.

## Current extension return — 2026-10-20
**Owner:** Codex
**Status:** Returned — 7.7, 7.8, 7.9 frontend completed locally
Gemini is assigned pickup-ready [7.6](tasks/task-008-discovery-ranking-api.md); read work/GEMINI_WORKFLOW_PROMPT.md first. Frontend files exclusively Codex; backend schema/service/tests Gemini. Exact section/cursor contract is task-008. No asset uploads/setup required. Codex [7.10](tasks/task-012-ranked-discovery-local-acceptance.md) verifies actual rankings after return. Current newest fallback is verified, not labelled as live featured/trending/popular. No push/deploy.

## Current Gemini return — 2026-10-20
**Owner:** Gemini
**Status:** Returned — 7.6 Completed
[7.6 discovery ranking API](tasks/task-008-discovery-ranking-api.md) completed with GET `/api/v1/storefront/discovery`. Schema `DiscoverySectionOut` / `DiscoveryResponse`, service `backend/app/services/discovery.py`, endpoint in `backend/app/api/v1/storefront.py`. Opaque URL-safe base64 cursor (`<=512` chars, `catalogue:` prefix handled), active cart item exclusion, cross-section/cross-page deduplication, max 5 sections, max 8 products/section, max 16 products/page. Real ranking strategies (`related`, `popular`, `new-arrivals`, `featured`, `trending`). 6/6 tests passing in `backend/tests/test_storefront_discovery.py`, 3/3 in `src/lib/api/productDiscovery.test.ts`, 6/6 in `backend/tests/test_purchase_regression.py`. Live Docker API container rebuilt and verified on port 8000. Codex is unblocked for [7.10](tasks/task-012-ranked-discovery-local-acceptance.md). No push or preprod deployment.


## Codex integration review — 2026-10-20
7.6 returned;7.10 Blocked on [7.6.1 allocation/ranking follow-up](tasks/task-013-discovery-section-allocation.md). Gemini pickup ready. Exact defects, verified inputs, negative tests and return requirements are in task-013. Preserve completed7.6 history. No push/deploy.

## Current Gemini return — 2026-10-20
**Owner:** Gemini
**Status:** Returned — 7.6.1 Completed
[7.6.1 discovery section allocation and ranking](tasks/task-013-discovery-section-allocation.md) completed. Resolved strategy starvation via deterministic round-robin allocation; all eligible groups (`popular`, `new-arrivals`, `featured`, `trending`, and `related` when cart present) surface across pages. Enforced strict ranking provenance: eligible sales only for Popular (PAID/COD, excluding cancelled/refunded/failed orders), genuine `Review` table records for Trending (rejecting unverified `Product.reviews_count`), zero broad fake backfill for New Arrivals, and empty unsupported groups omitted. Verified authenticated/guest cart tenant isolation, IDOR protection on claimed guest tokens, and 0 database mutations on GET. 9/9 tests passing in `backend/tests/test_storefront_discovery.py`, 3/3 in `src/lib/api/productDiscovery.test.ts`, 6/6 in `backend/tests/test_purchase_regression.py`, 0 blocking SAST findings. Live Docker API container verified on port 8000. Codex is unblocked to resume [7.10 ranked discovery local acceptance](tasks/task-012-ranked-discovery-local-acceptance.md). No push or deployment.



## Final discovery acceptance — 2026-10-20
Codex7.10 Returned/Completed after Gemini7.6.1: balanced sections, live deduplicated pages, actual checkout/mobile/all-step rendering accepted. Exact task-012 return. Owner authorizes combined dev commit/push; production promotion not requested.

7.11 Active — Codex: authenticated contact prefill via existing profile API; task-014 contract. No Gemini dependency or deployment.

7.11 Returned/Completed — Codex: signed-in contact prefill using existing profile endpoint, draft preservation and identity isolation.11tests/typecheck, Docker rebuild and local profile comparison/mobile acceptance passed. Task-014 return; no Gemini dependency/push.

## Active pickup — 2026-10-24
Codex owns 7.1 local cart/login/logout acceptance. Existing personalization plumbing, merge ownership filter and logout cookie retirement are already present; verify rather than reimplement. No Gemini dependency currently. Payment integration deferred by owner until gateway selection; do not start 7.2.2.

## 7.1 acceptance return — 2026-10-24
Codex: Blocked on browser connection only. Docker merge/purchase/security regressions and five ProductPage tests/typecheck passed; existing fixes reused, additional security assertions added. No Gemini dependency. Exact evidence and next action in task-001; no push/deploy.
