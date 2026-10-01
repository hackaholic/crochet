# Sulocraft product taxonomy — V1 business contract

This document is the canonical source of truth for product classification. The existing Sulocraft visual design is frozen. Taxonomy work changes database data, APIs, admin tools, navigation data, filtering, and SEO content; it does not redesign the header, footer, cards, typography, colors, hero, product page, or responsive behavior.

## Classification boundaries

Sulocraft uses three independent concepts:

| Concept | Purpose | Examples |
| --- | --- | --- |
| Category | What the product is; stable catalogue navigation | `Flowers → Bouquets`, `Amigurumi → Bunny` |
| Collection | Why, when, or how the product is merchandised | `Birthday Gifts`, `Best Sellers`, `Diwali Collection` |
| Tag | Flexible attributes and discovery terms | `pink`, `handmade`, `customizable`, `sunflower` |

There is one product record. Classification uses relationships; products are never duplicated into gift or campaign records.

## Category tree

Top-level storefront order is backend-controlled:

1. Flowers
2. Amigurumi
3. Baby
4. Home & Decor
5. Pooja & Devotional

### Flowers

- Bouquets
- Single Flowers
- Roses
- Sunflowers
- Tulips
- Daisies
- Cosmos
- Lilies
- Lavender
- Custom Bouquets

### Amigurumi

- Bunny
- Rabbit
- Teddy Bear
- Octopus
- Dolls
- Animals
- Cartoon-Inspired Characters
- Mini Amigurumi
- Custom / Personalized Figures

Animal and character types such as cats, dogs, dinosaurs, penguins, frogs, bees, ducks, or unicorns are data additions. Copyrighted character names must not be built into application code.

### Baby

- Blankets
- Rattles
- Baby Mobiles
- Toys
- Caps & Beanies
- Bassinets / Baby Baskets
- Baby Gift Sets

### Home & Decor

- Doilies
- Table Runners
- Sofa Throws
- Motifs
- Coasters
- Flower / Plant Decor
- Wall Decor
- Decorative Covers
- Other Home Decor

### Pooja & Devotional

- Garlands
- Thalpos / Decorative Covers
- Torans
- Poshak / God Clothes
- Laddu Gopal Clothes
- Temple Decor
- Festival Decor

`Thalpos / Decorative Covers` is editable data. Administrators can rename it later without a migration or deployment.

## Gift and merchandising collections

Initial evergreen gift collections:

- Gifts
- Birthday Gifts
- Anniversary Gifts
- Wedding Gifts
- Baby Shower Gifts
- Newborn Gifts
- Housewarming Gifts
- Festival Gifts
- Gifts for Kids
- Gifts for Her
- Gifts for Him
- Personalized Gifts
- Custom Gifts

The same collection mechanism supports Best Sellers, New Arrivals, Diwali, Mother's Day, Valentine's Day, and other scheduled merchandising. A product may belong to multiple collections.

## Data model requirements

### Category

Required fields:

```text
id
name
slug
description
image_key or image_url
parent_id
display_order
is_active
show_when_empty
seo_title
seo_description
created_at
updated_at
```

Categories support arbitrary depth without code changes. Slugs are unique and stable. Parent changes must reject cycles. Inactive ancestors hide their descendants from the public tree.

### ProductCategory

Replace the metadata-free join table with a managed association or add an equivalent primary-category mechanism:

```text
product_id
category_id
is_primary
display_order
```

Every published product has exactly one primary leaf category. Additional categories are allowed when genuinely useful. The primary category drives breadcrumbs, canonical category labeling, and default catalogue placement.

### Collection

Create a real collection entity and product relationship:

```text
id
name
slug
description
image_key or image_url
collection_type
display_order
is_active
starts_at
ends_at
seo_title
seo_description
created_at
updated_at
```

```text
ProductCollection
product_id
collection_id
display_order
```

`collection_type` may distinguish evergreen gift, manual merchandising, seasonal campaign, and system-generated collections. V1 may keep automatic Best Sellers/New Arrivals rules in controlled backend code, but customer-visible content and membership must be returned through the collection contract.

### Tag and attributes

Keep tags many-to-many and flexible. Color, material, dimensions, customization, made-to-order state, readiness, age recommendation, flower type, and bouquet size use the agreed flexible attribute/variant architecture unless a field is needed for core inventory or fulfilment behavior.

## Public API

### Categories

```text
GET /api/v1/categories?flat=false&includeEmpty=false
GET /api/v1/categories/{slug}
GET /api/v1/categories/{slug}/products
```

Public category output uses camelCase consistently:

```json
{
  "id": 1,
  "name": "Amigurumi",
  "slug": "amigurumi",
  "description": "Hand-stitched crochet figures and keepsakes.",
  "imageUrl": "https://images.sulocraft.com/categories/amigurumi/card.webp",
  "parentId": null,
  "displayOrder": 2,
  "isActive": true,
  "productCount": 8,
  "children": []
}
```

Default public behavior returns only active categories with available published/in-stock products. `showWhenEmpty=true` may explicitly expose an empty category. Admin endpoints can retrieve inactive and empty records.

Storefront filter controls must also derive their availability and counts from the currently loaded catalogue. Parent-category filters include products assigned to any descendant category. Empty category, collection, and price options are not shown to customers.

Category product queries include descendant categories and deduplicate products.

### Collections

```text
GET /api/v1/collections
GET /api/v1/collections/{slug}
GET /api/v1/collections/{slug}/products
```

Only active, currently scheduled public collections are returned. Product listing also supports `collection={slug}` independently of `category={slug}` and `tag={slug}`.

### Products

Product list/detail responses expose structured classification, not only display-name arrays:

```json
{
  "primaryCategory": { "name": "Bouquets", "slug": "bouquets" },
  "categories": [{ "name": "Flowers", "slug": "flowers" }, { "name": "Bouquets", "slug": "bouquets" }],
  "collections": [{ "name": "Birthday Gifts", "slug": "birthday-gifts" }],
  "tags": ["sunflower", "yellow", "customizable"]
}
```

Temporary compatibility fields may remain for one migration window, but new frontend work uses the structured fields.

## Admin API requirements

Administrators need CRUD and ordering for categories and collections, including:

- create, rename, describe, activate/deactivate, reorder, and move a category;
- prevent hierarchy cycles and unsafe deletion;
- configure images using backend-returned media URLs/object keys;
- see effective product counts before hiding/deleting a category;
- create, schedule, activate, reorder, and populate collections;
- assign one primary category and optional secondary categories to a product;
- assign multiple collections and tags to a product;
- preview inactive/empty taxonomy without exposing it publicly.

Deletion must be blocked while products or children depend on a record unless an explicit reassignment is supplied. Changes must be auditable.

## R2 media keys

Store relative managed-media keys and resolve them through `IMAGE_BASE_URL`:

```text
categories/<category-slug>/card.webp
collections/<collection-slug>/card.webp
```

The frontend renders `imageUrl` exactly as returned and never constructs R2 paths.

## Development reset and migration

Sulocraft has not launched and has no real customer, catalogue, order, inventory, or production data to preserve. The current records are development fixtures. Gemini is authorized to drop and recreate the affected development catalogue/taxonomy tables and discard existing local test products, carts, wishlists, reviews, orders, payments, and related fixture records when dependencies require it.

Gemini must still provide reproducible Alembic migrations and deterministic seed commands that:

1. create the collection tables and primary-category mechanism;
2. create the approved category and collection records using stable slugs;
3. seed a small representative product set across all five top-level categories;
4. demonstrate multi-category, multi-collection, and tag relationships;
5. rebuild a clean local database from zero without manual SQL;
6. remain safe for future environments once production data exists.

The reset authorization applies to current development fixture data only. It does not authorize destructive resets after real staging or production data is introduced.

Representative development seeds are sufficient. Do not generate dozens of fake products.

The representative seed catalogue must use the exact SKU and image mapping in [product-media.md](product-media.md). Every seeded product needs a real, distinct primary asset; every sellable variant needs a unique SKU. Seeds must not repeat images, substitute stock photography, or create media records for missing objects. `heart-bear` may demonstrate genuine cross-classification with `Baby → Toys` as its primary category and `Amigurumi → Teddy Bear` as a secondary category.

## SEO and URL behavior

- Category URL: `/shop/category/{slug}` or the single canonical pattern selected in the routing contract.
- Collection URL: `/collections/{slug}`.
- Primary-category breadcrumbs are backend-driven.
- Inactive or unknown taxonomy routes return the agreed not-found behavior.
- Sitemap includes active non-empty categories and active scheduled collections.
- Renaming display text does not silently break a stable slug.

## Frontend acceptance criteria

- Existing `CategoryCard`, `ProductCard`, `ProductGrid`, navigation, product page, and homepage section templates are reused unchanged visually.
- No permanent category/collection name arrays exist in UI components.
- Adding `Amigurumi → Dinosaur`, `Flowers → Orchid`, or `Home & Decor → Cushion Cover` in admin appears through APIs without a frontend deployment.
- Backend order, activation, images, counts, and schedules control what the existing UI renders.
- Desktop Chrome, Firefox, and mobile viewport checks pass.

## Backend acceptance tests

- Tree ordering, nesting, inactive ancestors, empty-category hiding, and `showWhenEmpty` behavior.
- Cycle prevention, slug uniqueness, safe deletion/reassignment, and one-primary-category enforcement.
- Descendant product filtering and product deduplication.
- Multi-collection membership without product duplication.
- Gift-category-to-collection migration preserves all existing product relationships.
- Admin authorization and validation.
- Structured product/category/collection responses match OpenAPI.
- Changing `IMAGE_BASE_URL` changes managed media origins without data updates.
- Duplicate/missing SKUs, duplicate primary image keys across products, missing primary images, and unreachable/missing managed media fail seed validation.
