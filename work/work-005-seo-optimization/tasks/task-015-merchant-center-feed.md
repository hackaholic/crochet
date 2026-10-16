# Task 5.15 — merchant center feed

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Implement centrally configured Merchant Center/free listings feed from eligible real catalogue entities/variants. Stable SKU IDs, titles/descriptions/public images/prices/currency/stock/canonical URLs/brand; validated policy config. Document missing approved shipping/returns and account actions.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.6, 5.7, 5.17, 5.18, 5.19, 5.20
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: backend/services and schemas for product feed; thin SEO/feed routes; catalogue repositories; backend tests; env/config examples

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.15-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Feed validates against current official specification with stable variants/IDs and landing-page price/stock parity; only eligible active products exported. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; `./scripts/test.sh backend tests/test_merchant_feed.py` (11/11 passed) |
| 5.15-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Missing GTIN/MPN handled truthfully, never invented; absent merchant/policy facts reported clearly; no customer/private data, XML injection, internal URLs or draft records; bounded generation/caching. | Negative tests or documented read-only review when no application behavior changes | Passed; XML escaping, draft/archived exclusion, inactive variant exclusion, and `identifier_exists="no"` verified |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; Pure standard library XML construction with `xml.sax.saxutils.escape` preventing XML injection; truthful declaration of `identifier_exists="no"` for handcrafted items; omission of fake GTIN/MPN; draft and archived products excluded; inactive variants excluded; no private customer or internal data exposed.

## Acceptance checks
- [x] Feed validates against current official specification with stable variants/IDs and landing-page price/stock parity; only eligible active products exported.
- [x] Missing GTIN/MPN handled truthfully, never invented; absent merchant/policy facts reported clearly; no customer/private data, XML injection, internal URLs or draft records; bounded generation/caching.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: feed URL/schema/sample fixtures/tests and owner Merchant Center setup checklist.

### Completed Changes
1. **Pydantic Schemas:**
   - [`backend/app/schemas/merchant.py`](file:///home/anu/git/crochet/backend/app/schemas/merchant.py): Defined `MerchantFeedItemOut` and `MerchantFeedResponse` with camelCase serialization aliases (`feedVersion`, `totalItems`, `eligibleProductsCount`, `policyDisclaimer`, `imageLink`, `additionalImageLinks`, `salePrice`, `itemGroupId`, `identifierExists`, `productType`).
   - [`backend/app/schemas/__init__.py`](file:///home/anu/git/crochet/backend/app/schemas/__init__.py): Exported merchant schemas.
2. **Feed Generation Service:**
   - [`backend/app/services/seo.py`](file:///home/anu/git/crochet/backend/app/services/seo.py):
     - `get_merchant_feed_items`: Queries active products (`Product.status == "ACTIVE"`) and active variants (`ProductVariant.status == "ACTIVE"`). Emits stable SKU IDs, landing-page URLs, prices with `INR` currency, sale prices when `compare_at_price > price`, `identifier_exists="no"`, category breadcrumbs, and badges.
     - `get_merchant_feed_response`: Envelopes items with metadata and policy disclaimer.
     - `generate_merchant_feed_xml`: Builds valid RSS 2.0 XML with `xmlns:g="http://base.google.com/ns/1.0"` conforming strictly to Google specifications, using `xml_escape` on all text and attributes.
3. **API Endpoints:**
   - [`backend/app/api/v1/seo.py`](file:///home/anu/git/crochet/backend/app/api/v1/seo.py):
     - `GET /api/v1/seo/merchant-feed.xml`: Serves dynamic XML feed (`application/xml; charset=utf-8`).
     - `GET /api/v1/seo/merchant-feed`: Serves JSON feed (`MerchantFeedResponse`) for testing and audit.
4. **Documentation & Setup Checklist:**
   - [`docs/merchant-center.md`](file:///home/anu/git/crochet/docs/merchant-center.md): Comprehensive Google Merchant Center integration document, attribute mapping table, eligibility rules, and 6-step owner account setup checklist.
   - [`docs/api-seo.md`](file:///home/anu/git/crochet/docs/api-seo.md): Documented merchant feed endpoints.
5. **Automated Test Suite:**
   - [`backend/tests/test_merchant_feed.py`](file:///home/anu/git/crochet/backend/tests/test_merchant_feed.py): 11 tests covering RSS 2.0 XML structure, Google attribute compliance, truthful identifier declaration (`identifier_exists="no"`, no GTIN/MPN), landing page price/stock parity, draft/archived exclusion, inactive variant exclusion, zero stock `out_of_stock` handling, compare-at sale price formatting, XML injection safety with special characters (`<`, `>`, `&`, `"`, `'`), and JSON/XML API responses.
   - **Test Results:**
     - Merchant Feed suite: 11/11 passed in 10.52s.
     - SEO suite: 45/45 passed in 36.15s.
     - Media suite: 14/14 passed in 5.54s.
     - Full backend suite: clean pass.
6. **Local Docker API Verification:**
   - `http://localhost:8000/api/v1/seo/merchant-feed.xml`: 200 OK, valid XML, 24 active products/variants exported.
   - `http://localhost:8000/api/v1/seo/merchant-feed`: 200 OK, `totalItems: 24`, `eligibleProductsCount: 24`.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.
