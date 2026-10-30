# Work 001 decisions

- Use the owner-provided Figma admin export as the design source; preserve its layout and visual language.
- Keep the existing Sulocraft routing/API architecture; admin business data must come from the backend.
- Do not treat Figma metadata or demo records as product data.
- The exported `mockData.ts` is prototype-only and must not be imported by the runtime admin screens.
- Keep Products, Inventory, Customers, and Settings clearly identified as unfinished until their screens and data contracts are implemented; do not make placeholder content look like working management tools.
- Local browser/Docker verification and owner review are acceptance gates before push or deployment.

- Customers V1 is read-only registered CUSTOMER accounts plus order history by exact Order.user_id. Guest orders remain in Orders; no email/phone identity inference. Defer customer mutation/export and lifetime-value accounting until explicitly scoped. Dedicated list/profile/history APIs are required; global search is not the directory.

- Product enable/disable reuses ACTIVE/DRAFT status through existing API; no second visibility flag. Archived products require separate deliberate handling.

## Finance analytics scope — 2026-10-10

1.14 uses existing supplied Finance design and shared date/eligibility/currency definitions. Category accounting counts each line once; historical destination comes from order snapshots. Tags/multiple categories must not multiply money. Profit/conversion/gateway-fee estimates are deferred without source data. Missing refund attribution and unknown destinations are explicit, never fabricated zeros. Frontend/backend tests required per subtask; local reconciliation precedes release.

Settings V1 edits persisted brand/owner/social profile only through existing admin API. Provider keys, roles, payment/shipping rules remain separately scoped. Frontend length limits follow actual schema/DB100 names and255 links; optional links clear without invented defaults.

## Product entry production profile — 2026-10-29

- Keep existing public descriptions and six product-detail fields as the curated customer-facing summary. A production profile is internal-only; never serialize it, variant costs, supplier names, or shade codes into storefront/SEO responses. Do not add per-field visibility toggles; the owner writes only approved facts into the existing public fields.
- Reuse existing SKU/variant, price, stock, status, categories/tags, image gallery, customization, variant cost/weight, and product dimension fields. Calculate margin from per-variant selling price and total cost; do not persist another margin value.
- Apply the generic production profile to every product category, not only flowers: flowers/bouquets, amigurumi, baby gifts, home/decor, pooja/devotional and others. Keep the existing customer-facing product name unchanged. Capture flexible component rows rather than fixed three-flower slots. Keep production fields optional and collapsed in the product editor. Use existing product occasion relationships through API-driven occasion options.
- Defer cost breakdown, lead-time promises, add-on relations, and repeated fields already supported elsewhere.
