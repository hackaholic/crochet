# Task 5.17.1 — Brand schema truth

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex
**Completed At:** 2026-10-14T14:42:00+05:30

## Objective/context
Read work/GEMINI_WORKFLOW_PROMPT.md and this work's README/tasks/decisions/coordination. 5.9 found `_get_brand_info` returns invented legalName "Sulocraft Handcrafted Creations" even when a DB brand exists, and fallback social/contact URLs when no brand exists. Public Organization data must reflect configured/approved facts only.

## Scope
Return nullable legalName unless sourced from an actual approved DB field. Never manufacture social/contact identity URLs for a missing brand record. Keep contact URLs distinct from real sameAs identity profiles; no asset uploads, resets or frontend edits. Preserve snapshot global hash and existing metadata contract compatibility.

## Dependencies and files
- Depends on: 5.17
- Dependency context: Returned; coordinate services/seo.py ownership with active 5.19 and pending 5.18.2 before editing.
- Blocked by: None
- Blocker reason: None
- Next action: Completed and returned to Codex for integration.
- Files: backend/app/services/seo.py; backend/app/schemas/seo.py; backend/tests/test_seo.py; docs/api-seo.md

## Verified inputs
Official logo already exists at brand/sulocraft-logo.png; do not upload again. Frontend 5.9 omits unverified legalName/founder/foundingDate/SearchAction and excludes whatsappUrl from sameAs. Other identity profile links come only from the returned API configuration.

## Acceptance/tests/security
Existing configured brand name/logo preserved. Empty brand/social fields yield null/empty fields, not seeded claims. legalName has explicit DB provenance or null; contact-only links excluded from sameAs. Test existing/missing brand, empty fields, genuine profiles, snapshot consistency and private-field exclusion using shared backend runner. No secrets/private owner data in public response. Record security results and migrations/config needs, if any.

## Return handoff
- **Files Modified:**
  - `backend/app/services/seo.py`:
    - Updated `_get_brand_info`: returns `legal_name: None` unless present on DB model; strips fallback social/contact URLs when missing brand record (`instagram_url=None`, `whatsapp_url=None`, `same_as=[]`); keeps `whatsapp_url` distinct as direct contact channel and excludes it from `same_as` identity profiles.
    - Updated `_compute_global_snapshot_version`: hashes brand social URLs and handles missing brand setting gracefully.
  - `backend/tests/test_seo.py`:
    - Updated `test_domain_01_homepage_brand_and_social_profiles` to assert `legalName is None`, `whatsappUrl` present on brand, and `whatsappUrl` excluded from `sameAs`.
    - Added 4 dedicated test cases: `test_brand_truth_missing_brand_settings`, `test_brand_truth_empty_brand_fields`, `test_brand_truth_contact_vs_same_as`, and `test_brand_truth_no_secrets_and_snapshot_brand`.
- **Wire Example (`GET /api/v1/seo/resolve?path=/`):**
  ```json
  {
    "brand": {
      "name": "Sulocraft",
      "legalName": null,
      "logoUrl": "http://testserver/brand/sulocraft-logo.png",
      "ownerName": "Anupama Sharma",
      "instagramUrl": "https://instagram.com/sulocraft",
      "whatsappUrl": "https://wa.me/919876543210",
      "sameAs": [
        "https://instagram.com/sulocraft"
      ]
    }
  }
  ```
- **Test Results:**
  - `./scripts/test.sh backend tests/test_seo.py`: 37 passed, 1 warning in 43.87s.
  - `./scripts/test.sh backend`: 425 passed, 7 skipped in 51.28s. Zero regressions.
- **Security & Data Isolation:**
  - No internal table IDs, secret keys, or database timestamps exposed in public brand schema.
  - Safe against parameter injection; no frontend file edits or asset uploads.
- **Blockers:** None. Returned to Codex for integration.
