# Work 019 decisions

- DEC019-1: Frontend controls presentation; backend/database owns six product descriptions and default content.
- DEC019-2: New products snapshot current defaults. Editing existing products loads their persisted values; default changes do not silently rewrite existing products. Explicit reset-to-default is an admin action, not automatic on every render/save.
- DEC019-3: Plain text only, with bounded field lengths and safe rendering. Materials, dimensions, safety and shipping claims must reflect each actual product; factual default copy needs owner confirmation before release. Existing hardcoded values are audit references, not approved defaults.

- DEC019-4: Explicit empty string clears/hides a product section and must not reuse defaults. Omitted/null creation fields preserve snapshot behavior; frontend sends explicit strings. Existing migrated products stay empty until admin edits them.

- DEC019-5 (owner, 2026-10-11): Remove timing and delivery promises until confirmed. Defaults use neutral per-order confirmation wording. Migration changes only exact original seeded defaults, preserving custom defaults and every saved product description; downgrade does not reinstate unconfirmed promises.
