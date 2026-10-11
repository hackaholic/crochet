# Task 1.10.3 — Brand name null/control-character regression
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001
## Objective/context
Follow-up review of returned1.10.1 found explicit null name accepted by _validate_name_field, but BrandSettings.name/owner_name are NOT NULL. PUT assigns null and can raise database failure. Helper also exempts internal tab/newline/carriage-return although original contract rejects control characters. Preserve completed1.10.1 work; make a focused correction only.
## Dependencies/files
Depends on: 1.10.1
Dependency context: Returned code present; UI already uses actual DB limits100 names/255 URLs, rejects controls, and never submits null names. No schema expansion needed.
Files: backend/app/schemas/storefront.py, backend/tests/test_storefront.py; minimal route change only if necessary.
## Scope/tests/security
- TC01: PUT with explicit `{"name": null}` or `{"ownerName": null}` rejected with 422 Unprocessable Entity, zero database writes, brand row remains intact. Pass.
- TC02: Internal control characters (null bytes, `\t`, `\n`, `\r`, and `\x7f` DEL) rejected with 422. Surrounding spaces cleanly trimmed on legitimate inputs. Pass.
- TC03: Omitted fields preserve existing values; optional links (`instagramUrl`, `whatsappUrl`) clear on null or whitespace; 100-character max names supported. Pass.

Command: `uv run pytest tests/test_storefront.py -k "brand" -v` -> 3/3 passed (25.29s).
Returned to Codex. No push or deployment.
