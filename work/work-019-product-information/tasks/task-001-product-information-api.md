# Task 19.1 — Persist six fields and editable default configuration

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 019

## Objective and context
Define additive typed fields `handmade_details`, `materials_used`, `size_dimensions`, `processing_time`, `care_instructions`, `shipping_delivery` (follow existing API alias conventions: `handmadeDetails`, `materialsUsed`, `sizeDimensions`, `processingTime`, `careInstructions`, `shippingDelivery`). Provide admin defaults read/update contract and include product values in admin create/update/read and public product-detail output. Defaults must be administratively configurable in DB; new creation fills omitted values from defaults, explicit product values win. Partial updates preserve omitted existing values; define null/blank semantics consistently. Existing records remain intact; no material/dimension or safety assumptions during migration. Return typed fixtures and owner-review default-copy matrix; seed only confirmed factual defaults, distinguish unconfigured values. Use bounded plain text and reject invalid shapes/oversized input, preserve legitimate Unicode/newlines. No public defaults mutation.

## Scope
In scope: six product descriptions and configurable defaults within existing catalogue architecture. Out of scope: deployment, arbitrary HTML, rewriting all existing products or unrelated commerce features.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing catalogue editor/API reused; required prior task returns before dependent implementation.
- Blocked by: None
- Next action: Codex picks up 19.2 (Admin editor and storefront accordions).
- Modified:
  - `backend/app/models/catalogue.py`: Added 6 nullable `Text` fields on `Product`; added `ProductInformationDefaults` model.
  - `backend/app/models/__init__.py`: Registered and exported `ProductInformationDefaults`.
  - `backend/alembic/versions/d1e2f3a4b5c6_add_product_information_and_defaults.py`: Migration adding columns and creating defaults table with honest templates.
  - `backend/app/schemas/catalogue.py`: Added 6 fields with camelCase aliases to `ProductDetail`.
  - `backend/app/schemas/admin.py`: Added `_validate_product_info_text` validator (max 5,000 chars, rejects HTML injection/disallowed control chars); added 6 fields to `AdminProductCreate`, `AdminProductUpdate`, and `AdminProductOut`; added `AdminProductInfoDefaultsOut` and `AdminProductInfoDefaultsUpdate`.
  - `backend/app/api/v1/catalogue.py`: Populated 6 fields in `get_product_detail` (`GET /api/v1/products/{slug_or_id}`).
  - `backend/app/api/v1/admin.py`: Added `GET /api/v1/admin/storefront/product-defaults` and `PUT /api/v1/admin/storefront/product-defaults`; updated `create_product` to snapshot defaults when fields are omitted; updated `update_product` and `_product_to_admin_out`.
  - `backend/app/db/seed.py`: Seeded initial `ProductInformationDefaults`.
  - `backend/tests/test_product_information.py`: Added 9 automated tests for snapshotting, overrides, partial updates, 401/403 authorization, length limits, XSS prevention, and unicode/newlines.

## Test cases
- 19.1-TC01 acceptance/regression:
  - `test_get_product_defaults_admin`: PASSED
  - `test_update_product_defaults_admin`: PASSED
  - `test_product_creation_snapshots_defaults_when_omitted`: PASSED
  - `test_product_creation_explicit_overrides_win`: PASSED
  - `test_partial_update_preserves_omitted_product_fields`: PASSED
  - Public detail matches saved values: PASSED
  - Existing products regression in `test_catalogue.py` (12/12 passed): PASSED
- 19.1-TC02 security:
  - `test_unauthorized_product_defaults_access` (401/403 for anonymous/customer): PASSED
  - `test_reject_oversized_info_text` (>5000 chars returns 422): PASSED
  - `test_reject_html_injection_in_info_fields` (stored XSS raw HTML tags rejected): PASSED
  - `test_accept_legitimate_unicode_and_newlines` (emojis, bullet points, linebreaks preserved): PASSED
- 19.1-TC03 failure/boundary:
  - Controlled field limits and null/blank policy verified. Denied writes leave DB unchanged.

## Security validation
- Admin write trust boundary strictly enforced via `get_current_admin`. Anonymous and customer requests receive 401/403.
- Parameterized SQLAlchemy ORM persistence prevents SQL injection.
- Plain text validation disallows `<tags>` preventing stored XSS while preserving newlines and Unicode formatting.
- Mass-assignment protection via Pydantic model validations.

## Acceptance checks
- [x] Scope/API semantics documented and compatible with existing products.
- [x] Focused tests and security negatives pass; counterpart contract evidence linked.
- [x] Local integration evidence and limitations recorded.
- [x] Work-local return handoff updated, no unauthorized push/deploy.

## Handoff back
Task 19.1 is completed. Ready for Codex to pick up Task 19.2 (Admin editor and storefront accordions).
API Contract Summary for Codex:
- `GET /api/v1/admin/storefront/product-defaults` -> returns `AdminProductInfoDefaultsOut`:
  `{ handmadeDetails, materialsUsed, sizeDimensions, processingTime, careInstructions, shippingDelivery, updatedAt }`
- `PUT /api/v1/admin/storefront/product-defaults` -> accepts `AdminProductInfoDefaultsUpdate`:
  `{ handmadeDetails?, materialsUsed?, sizeDimensions?, processingTime?, careInstructions?, shippingDelivery? }`
- `POST /api/v1/admin/products` -> accepts same 6 camelCase or snake_case fields. If omitted (`null` / not provided), automatically snapshots storewide defaults.
- `PATCH / PUT /api/v1/admin/products/{id}` -> accepts same 6 fields for partial/full update.
- `GET /api/v1/products/{slug_or_id}` -> returns full `ProductDetail` with the 6 camelCase fields.
