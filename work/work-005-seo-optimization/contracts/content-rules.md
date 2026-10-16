# Product/category content rules —5.13

Presentation belongs to reusable frontend components. Business facts come from saved catalogue/SEO entities and the existing Work019 product fields. No arbitrary HTML from the API is rendered.

## Category and collection pages
Use the entity name/H1 supplied by the resolver and its own saved description as an intro. Match the entity slug to the current canonical route before showing its description. Missing/blank intro remains absent; generic /shop and mixed filters must not inherit a previous category's copy. Use descriptive real entity links and breadcrumbs; no lists of SEO keywords or city names.

## Products
- Keep product name, price/availability, gallery/alt and metadata consistent with the actual catalogue item. Full body description is separate from optional short listing description and search-engine meta-description.
- Description should explain the actual creation, intended use and meaningful distinctions. Do not pad it with repeated keywords or unverifiable “best”, “premium”, customer-count or purchase claims.
- Reuse existing editable Work019 fields: handmadeDetails, materialsUsed, sizeDimensions, processingTime, careInstructions, shippingDelivery. Show only saved nonblank values. Initial HTML uses matching SeoProductEntity data; client refresh uses the same product detail API. Never copy one product's text into another during route changes.
- Materials: name the actual fibre/components only when known. Dimensions: include real measurement/unit and any actual variation. Processing/delivery: only owner-approved commitments. Care instructions must suit that product's real materials. Customization must reflect actual catalogue capability; don't imply unavailable colour/size options.
- Do not fill unknown fields with yarn, shipping schedules, delivery markets, gift-wrapping or handmade promises. Owner-approved neutral admin creation defaults remain in Work019; changing defaults does not rewrite existing products.
- Catalogue seed rating/count fields and static demo testimonials are not genuine review evidence. Display a rating only with a nonempty actual-review aggregate carrying the explicit backend provenance. Do not equate that marker with verified purchase.

## Admin / owner review
Existing ProductEditor Description and all six ProductInformationFields remain the authoring surface; reuse Work019 saved-value/clear/default semantics. No parallel SEO copy database or new editor introduced. SEO title/summary generation remains backend-owned; don't blindly repeat a long body into a meta-description.
Before approving an item, review its real name/description, unique photos/alt, classification, actual materials/measurements, customization, care and any processing/shipping promises. Unknown values stay blank; no agent should manufacture them to satisfy SEO. Shared delivery/returns policy changes require owner confirmation.
Existing DB seed descriptions/homepage testimonials/customer counts and the global announcement's shipping promise require business-owner factual review; reading from the DB alone does not establish their truth. These are flagged for final5.4 acceptance, not silently rewritten by this template task. No fake public reviews are created during tests.

## Freshness / publishing
Database edits feed the detail/resolver APIs and client refresh. Initial static HTML needs the configured build/content publication process to regenerate the snapshot (5.6); do not claim an already deployed artifact changes immediately. Local→preprod→accepted production gates apply. Backend5.13.1 supplies full-description snapshot and catalogue actual-review summary; Codex verifies parity after return.
