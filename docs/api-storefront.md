# Storefront Content API Contract

**Status:** Implemented & Published (Controlled sections and hero campaigns ready for Frontend integration)
**Backend Owner:** Gemini  
**Frontend Consumer:** Codex / ChatGPT  

This contract makes Sulocraft homepage content database-managed. The frontend owns reusable rendering templates only; it must not own campaign copy, image URLs, owner identity, or scheduling decisions.

## Public endpoint

`GET /api/v1/storefront`

## Homepage composition extension

Add `GET /api/v1/storefront/home` and keep `/api/v1/storefront` as a compatibility alias during migration. The response must use a controlled schema: React owns presentation; the backend owns content, ordering, visibility, scheduling, and resolved catalogue references.

```ts
interface StorefrontHomeResponse {
  brand: BrandSettings;
  hero: HomepageCampaign[]; // 1–3 active slides recommended, maximum 5
  sections: HomepageSection[];
}

type HomepageSection =
  | CategoryGridSection
  | ProductCollectionSection
  | OccasionGridSection
  | PromoBannerSection
  | ReviewSection
  | ImageTextSection;

interface BaseSection { id: number; order: number; enabled: boolean; }
interface CategoryGridSection extends BaseSection { type: 'category_grid'; title: string; eyebrow?: string | null; categories: CategorySummary[]; }
interface ProductCollectionSection extends BaseSection { type: 'product_collection'; title: string; eyebrow?: string | null; description?: string | null; collectionSlug: string; products: ProductSummary[]; }
interface OccasionGridSection extends BaseSection { type: 'occasion_grid'; title: string; eyebrow?: string | null; description?: string | null; occasions: OccasionSummary[]; }
interface OccasionSummary { id: string; name: string; icon?: string | null; imageUrl?: string | null; }
interface PromoBannerSection extends BaseSection { type: 'promo_banner'; title: string; description?: string | null; imageUrl?: string | null; imageAlt?: string | null; ctaText?: string | null; ctaUrl?: string | null; }
interface ReviewSection extends BaseSection { type: 'review_section'; title: string; reviews: ReviewSummary[]; }
interface ImageTextSection extends BaseSection { type: 'image_text'; title: string; description: string; imageUrl: string; imageAlt: string; imagePosition: 'left' | 'right'; ctaText?: string | null; ctaUrl?: string | null; }
```

The backend must never return HTML, CSS, JSX, Tailwind classes, arbitrary component trees, or executable presentation data. Product configuration stores references such as `collection_slug`; FastAPI resolves current product/category/review records before returning the response. Product collection rows must return distinct products with distinct primary image URLs; the frontend also filters repeated IDs and image URLs as a defensive guard.

`occasion_grid.occasions` is dynamically resolved from admin-managed occasion records, never from a frontend list. Birthday, Anniversary, Wedding, and Baby Shower are core evergreen occasions and remain visible year-round. Other occasions (including Valentine's Day, Decor, Diwali, Mother's Day, Father's Day, Christmas, and future campaigns) are admin-managed and may be enabled, disabled, or scheduled in the `Asia/Kolkata` timezone. Keep stable existing IDs (`birthday`, `anniversary`, `wedding`, `babyshower`) so existing product associations and links continue to work; do not create a duplicate Baby Shower record. Return active, enabled seasonal occasions first, then evergreen occasions; preserve admin display order within each group. This way an enabled occasion leads the grid without frontend sorting. Do not display Rakhi. If no seasonal occasions are active, retain the four evergreen cards; omit the occasion section only if there are no eligible records at all. Give every configured occasion distinct, bright artwork and reject/review duplicate image keys. Product-to-occasion membership is database-managed (one product can belong to multiple occasions), and `/shop?occasion=<id>` filters using those backend associations or tags.

### Image-origin configuration

Persist stable relative object keys in content records, for example `products/heart-bear/primary.webp`, rather than environment-specific absolute URLs. When serializing API responses, prepend `IMAGE_BASE_URL`:

- local Docker: `IMAGE_BASE_URL=http://localhost:8000/static/images`
- production: `IMAGE_BASE_URL=https://images.sulocraft.com`

The frontend always renders the absolute URL returned by the API. Changing the image origin must require only an environment change and an API restart; it must not require React edits or bulk replacement of database rows. Admin APIs may accept an existing absolute external URL when explicitly needed, but Sulocraft-managed assets should use object keys.

Gemini owns section persistence, scheduling, ordering, enable/disable behavior, admin CRUD, seed data, the `/storefront/home` endpoint, and OpenAPI updates. Codex owns the strict section registry and approved templates, including reusable `occasion_grid` and `product_collection` renderers. Unknown section types are ignored safely.

Returns public brand settings and currently active homepage campaigns. No authentication is required.

```ts
interface StorefrontResponse {
  brand: {
    name: string;             // "Sulocraft"
    ownerName: string;        // "Anupama"
    instagramUrl?: string | null;
    whatsappUrl?: string | null;
  };
  heroCampaigns: HomepageCampaign[];
}

interface HomepageCampaign {
  id: number;
  title: string;
  emphasis?: string | null;
  description: string;
  eyebrow?: string | null;
  imageUrl: string;
  imageAlt: string;
  destination?: string | null; // storefront route such as /shop?category=Gifts
  priority: number;
  startsAt?: string | null;
  endsAt?: string | null;
}
```

## Managed homepage section images

The following approved assets have distinct purposes. Persist their relative keys; the API resolves each with `IMAGE_BASE_URL`.

| Homepage section | Required database `image_url` key | Asset |
| --- | --- | --- |
| `promo_banner` — “Gift Handcrafted Warmth This Season” | `sections/gift-handcrafted-warmth.png` | Original warm festive crochet gift hamper artwork, wide composition with text-safe space |
| `image_text` — “Handmade with Love, Thread by Thread” | `about/anupama-sharma.png` | Owner-provided portrait of Anupama Sharma; same asset is used on the static About page |

The previous keys `campaigns/promo-gift-warmth.jpg` and `sections/artisan-story.jpg` do not have corresponding local files or public R2 objects. They must not remain in the live development section records. Gemini must update both seed defaults and existing development rows, verify the new public URLs return HTTP 200, and verify `/api/v1/storefront/home` returns those exact resolved `imageUrl` values. Since the seed only inserts sections when none exist, updating seed defaults alone is insufficient. Add a backend regression test for the expected keys and serialized URLs.

## Admin endpoints (Requires Admin Session)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/storefront/brand` | Retrieve storewide brand settings (`name`, `ownerName`, `instagramUrl`, `whatsappUrl`). |
| `PUT` | `/api/v1/admin/storefront/brand` | Update storewide brand settings. |
| `GET` | `/api/v1/admin/storefront/campaigns` | List all homepage campaigns (including inactive or scheduled) ordered by priority. |
| `POST` | `/api/v1/admin/storefront/campaigns` | Create a new homepage campaign with scheduling, priority, and route destination. |
| `PUT` | `/api/v1/admin/storefront/campaigns/{id}` | Update existing campaign attributes, priority, image, or active flag. |
| `DELETE` | `/api/v1/admin/storefront/campaigns/{id}` | Remove a homepage campaign. |
| `GET` | `/api/v1/admin/storefront/sections` | List all configured homepage sections ordered by `display_order`. |
| `POST` | `/api/v1/admin/storefront/sections` | Create a new controlled homepage section (`category_grid`, `product_collection`, `occasion_grid`, `promo_banner`, `review_section`, `image_text`). |
| `GET` | `/api/v1/admin/storefront/sections/{id}` | Retrieve details for a single homepage section. |
| `PUT` | `/api/v1/admin/storefront/sections/{id}` | Update attributes, visibility, ordering, or schedule of a section. |
| `DELETE` | `/api/v1/admin/storefront/sections/{id}` | Remove a homepage section. |
| `GET` | `/api/v1/admin/occasions` | List configured occasions, including hidden and scheduled records. |
| `POST` | `/api/v1/admin/occasions` | Create an occasion with name, stable ID, image key, display order, visibility, schedule, and product associations. |
| `PUT` | `/api/v1/admin/occasions/{id}` | Edit occasion details, image, visibility, display order, schedule, and associated product IDs/tags. |
| `DELETE` | `/api/v1/admin/occasions/{id}` | Remove an unused occasion configuration; preserve historical order/product data. Prefer hiding when referenced. |

Occasion records require `id`, `name`, `image_key`, `display_order`, and `is_enabled`, with optional `starts_at` and `ends_at`. A product may be associated with multiple occasions. Date windows use `Asia/Kolkata`; start/end are inclusive. Seasonal occasions are filtered by the admin enable flag and active date window. Evergreen occasions ignore those seasonal controls in public resolution and reject attempts to disable, delete, or schedule them. Admin occasion responses expose `isEvergreen` so the interface can display “Always on” without repeating the backend's business rule. Admin can save a future occasion while it is disabled, then enable it manually for the season or schedule its active dates; explicitly sending `null` for a schedule date clears that date, while omitting the property leaves it unchanged. Existing occasion rows must be safely migrated/updated so Anniversary/Wedding artwork is replaced, Birthday artwork refreshed, Baby Shower enabled year-round, and Rakhi hidden.

## Backend implementation notes (Gemini)

- Database-backed `BrandSettings`, `HomepageCampaign`, and `HomepageSection` models with Alembic migrations `a85462db2fec_add_storefront_models.py` and `f5399f52930d_add_homepage_sections.py`.
- Seeded five editable local campaigns (Brand Story, Festive Gifting, New Arrivals, Home Décor, Custom Creations) and editable homepage sections:
  1. `category_grid`: "Shop by Category" (eyebrow: "Browse by Collection", dynamically resolves root categories)
  2. `product_collection`: "Most Loved Creations" (eyebrow: "Customer Favourites", dynamically resolves `collection_slug="bestsellers"`)
  3. `product_collection`: "Tiny Friends, Big Smiles 🐾" (eyebrow: "Handmade Companions", collection resolved from existing tagged Amigurumi products)
  4. `occasion_grid`: "Gift by Occasion" (dynamically resolves admin-enabled, currently scheduled occasion records/images in display order)
  5. `promo_banner`: "Gift Handcrafted Warmth This Season" (with artisanal CTA `/shop?category=Gifts`)
  6. `review_section`: "Loved by Over 500+ Happy Customers" (dynamically resolves verified customer testimonials)
  7. `image_text`: "Handmade with Love, Thread by Thread" (artisanal story highlight with CTA `/about`)
- Public endpoints:
  - `GET /api/v1/storefront/home`: returns `brand`, `hero` (and `heroCampaigns`), and `sections` with resolved catalogue/review items.
  - `GET /api/v1/storefront`: backwards-compatibility alias returning `brand` and `heroCampaigns`.
- Filtered by `is_enabled=True` and active schedule bounds, ordered by `display_order` ascending.
- Full Admin CRUD/reordering/activation controls implemented under `/api/v1/admin/storefront/*`.
- Schema and endpoints published in `docs/openapi.yaml` (61 paths). 77 automated backend tests passing.



## Frontend responsibilities (Codex)

- Fetch this endpoint through the configured API base URL.
- Render `heroCampaigns` with a reusable carousel, lazy-loaded responsive images, accessible controls, and no content fallback embedded in the component.
- Keep the reusable **Shop Collection** and **Create Something Custom** actions in the template.
- Render `brand.ownerName` wherever founder/owner attribution is displayed.

## Hero artwork handoff

The approved source assets live in `public/images/hero/`. Gemini should upload them to R2 and store the returned public URLs in `HomepageCampaign.image_url`; the frontend must continue rendering the URL verbatim.

These mappings are mandatory. Development and production must use the generated project files themselves; do not substitute Unsplash or other stock-image fallbacks when the approved asset is available.

| Campaign | Source asset | Production R2 URL |
| --- | --- | --- |
| Our Heritage | `heritage.png` | `https://images.sulocraft.com/hero/heritage.png` |
| Festive Collection | `festive-gifting.png` | `https://images.sulocraft.com/hero/festive-gifting.png` |
| New Releases / Flowers | `flower-bouquet.png` | `https://images.sulocraft.com/hero/flower-bouquet.png` |
| Home & Living | `home-decor.png` | `https://images.sulocraft.com/hero/home-decor.png` |
| Custom Orders | `custom-bouquet.png` | `https://images.sulocraft.com/hero/custom-bouquet.png` |
| Amigurumi feature | `amigurumi.png` | `https://images.sulocraft.com/hero/amigurumi.png` |

Artwork contains no baked-in marketing copy. This is intentional: titles, descriptions, ordering, visibility, and destinations stay editable in the database while React provides accessible full-width overlay text and reusable action buttons.

## Category artwork handoff

Category cards also render backend-provided URLs verbatim. A URL stored in PostgreSQL is only a reference; the matching R2 object must exist and be publicly reachable before the image can render.

| Category slug | Local development asset | Production R2 URL |
| --- | --- | --- |
| `flowers` | `/images/hero/flower-bouquet.png` | `https://images.sulocraft.com/categories/flowers.png` |
| `pooja-items` | `/images/hero/festive-gifting.png` | `https://images.sulocraft.com/categories/pooja-items.png` |
| `amigurumi` | `/images/hero/amigurumi.png` | `https://images.sulocraft.com/categories/amigurumi.png` |

Local seed/development records may use the frontend origin for these assets. Production records must use the corresponding public R2 URLs after the objects are uploaded and verified with an HTTP `200` response.
