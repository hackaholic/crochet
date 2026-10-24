# Task 19.6 — Preprod backend product-information acceptance

**Owner:** Codex
**Status:** Completed

## Objective / scope
Confirm preprod runs verified19.4 resolver and all6 sections render publicly. Use existing deployment workflow only if stale; do not redeploy or alter DB defaults when current service already passes.

## Dependencies
- Depends on: 19.4, 19.5
- Blocked by: None
- Next action: None; Work 019 complete.

## Evidence / acceptance
2026-10-24 current read-only VPS inspection: resolver present in running preprod API, Heart Bear3 detail reports6populated fields. Prior stale-backend finding superseded by latest deployment. Existing19.4 local tests/security evidence retained; no application changes or repeated setup needed.

2026-10-24 public preprod API & browser acceptance completed:
- Verified `https://api-dev.sulocraft.com/api/v1/products/3` (`heart-bear`, HTTP 200) returns all 6 populated specification fields (`handmadeDetails`, `materialsUsed`, `sizeDimensions`, `processingTime`, `careInstructions`, `shippingDelivery`).
- Verified `https://dev.sulocraft.com/products/heart-bear` in headless Chrome: all 6 disclosure labels (`Handmade Details`, `Materials Used`, `Size & Dimensions`, `Processing Time`, `Care Instructions`, `Shipping & Delivery`) render, expand on click (`aria-expanded="true"`), display visible controlled panels (`hidden === false`), and match the resolved API content (`disclosuresCount: 6/6`).
- Evidence recorded in `reports/task-006-preprod-acceptance.json` and `reports/preprod-heart-bear-information.jpg`.
- Security: read-only public API and browser verification only; no customer data/secret reads, DB writes, redeployments, or production changes. No Gemini dependency.
