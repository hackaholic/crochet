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
  | PromoBannerSection
  | ReviewSection
  | ImageTextSection;

interface BaseSection { id: number; order: number; enabled: boolean; }
interface CategoryGridSection extends BaseSection { type: 'category_grid'; title: string; eyebrow?: string | null; categories: CategorySummary[]; }
interface ProductCollectionSection extends BaseSection { type: 'product_collection'; title: string; eyebrow?: string | null; collectionSlug: string; products: ProductSummary[]; }
interface PromoBannerSection extends BaseSection { type: 'promo_banner'; title: string; description?: string | null; imageUrl?: string | null; imageAlt?: string | null; ctaText?: string | null; ctaUrl?: string | null; }
interface ReviewSection extends BaseSection { type: 'review_section'; title: string; reviews: ReviewSummary[]; }
interface ImageTextSection extends BaseSection { type: 'image_text'; title: string; description: string; imageUrl: string; imageAlt: string; imagePosition: 'left' | 'right'; ctaText?: string | null; ctaUrl?: string | null; }
```

The backend must never return HTML, CSS, JSX, Tailwind classes, arbitrary component trees, or executable presentation data. Product configuration stores references such as `collection_slug`; FastAPI resolves current product/category/review records before returning the response.

Gemini owns section persistence, scheduling, ordering, enable/disable behavior, admin CRUD, seed data, the `/storefront/home` endpoint, and OpenAPI updates. Codex owns the strict section registry and the five approved templates. Unknown section types are ignored safely.

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
| `POST` | `/api/v1/admin/storefront/sections` | Create a new controlled homepage section (`category_grid`, `product_collection`, `promo_banner`, `review_section`, `image_text`). |
| `GET` | `/api/v1/admin/storefront/sections/{id}` | Retrieve details for a single homepage section. |
| `PUT` | `/api/v1/admin/storefront/sections/{id}` | Update attributes, visibility, ordering, or schedule of a section. |
| `DELETE` | `/api/v1/admin/storefront/sections/{id}` | Remove a homepage section. |

## Backend implementation notes (Gemini)

- Database-backed `BrandSettings`, `HomepageCampaign`, and `HomepageSection` models with Alembic migrations `a85462db2fec_add_storefront_models.py` and `f5399f52930d_add_homepage_sections.py`.
- Seeded five editable local campaigns (Brand Story, Festive Gifting, New Arrivals, Home Décor, Custom Creations) and five editable homepage sections:
  1. `category_grid`: "Shop by Category" (eyebrow: "Browse by Collection", dynamically resolves root categories)
  2. `product_collection`: "Most Loved Creations" (eyebrow: "Customer Favourites", dynamically resolves `collection_slug="bestsellers"`)
  3. `promo_banner`: "Gift Handcrafted Warmth This Season" (with artisanal CTA `/shop?category=Gifts`)
  4. `review_section`: "Loved by Over 500+ Happy Customers" (dynamically resolves verified customer testimonials)
  5. `image_text`: "Handmade with Love, Thread by Thread" (artisanal story highlight with CTA `/about`)
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
