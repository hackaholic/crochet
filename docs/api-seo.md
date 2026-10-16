# SEO Contract

**Status:** Backend implementation requested; frontend integration in progress

SEO is data-driven. React owns valid metadata markup and Schema.org serialization; FastAPI/PostgreSQL own page titles, descriptions, canonical paths, share images, indexing rules, breadcrumbs, and entity data.

## Page metadata resolver

`GET /api/v1/seo/resolve?path=/products/forever-crochet-rose-bouquet`

```ts
interface SeoBreadcrumb {
  name: string;
  path: string;
}

interface SeoFaqItem {
  question: string;
  answer: string;
}

interface SeoShippingInfo {
  freeShippingThreshold: number;
  standardFee: number;
  currency: string;
  transitTime: string;
  country: string;
}

interface SeoReturnPolicy {
  returnWindowDays: number;
  policyUrl: string;
  returnFees: string;
}

interface SeoBrandInfo {
  name: string;
  legalName?: string | null;
  logoUrl?: string | null;
  ownerName?: string | null;
  instagramUrl?: string | null;
  whatsappUrl?: string | null;
  sameAs: string[];
}

interface SeoProductVariant {
  id: number;
  sku: string;
  name: string;
  price: number;
  pricePaise: number;
  stockQuantity: number;
  inStock: boolean;
  attributes: Record<string, any>;
}

interface SeoAggregateRating {
  ratingValue: number;
  reviewCount: number;
  bestRating: number;
  worstRating: number;
  provenance: string; // e.g. "VERIFIED_REVIEWS"
}

interface SeoProductEntity {
  id: number;
  name: string;
  slug: string;
  sku: string;
  price: number;
  pricePaise: number;
  currency: string;
  inStock: boolean;
  inventoryStatus: 'IN_STOCK' | 'OUT_OF_STOCK';
  brand: string;
  primaryCategoryName?: string | null;
  categoryNames: string[];
  imageUrls: string[];
  variants: SeoProductVariant[];
  aggregateRating?: SeoAggregateRating | null;
  handmadeDetails?: string | null;
  materialsUsed?: string | null;
  sizeDimensions?: string | null;
  careInstructions?: string | null;
  shippingDelivery?: string | null;
  processingTime?: string | null;
}

interface SeoCategoryEntity {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  imageUrl?: string | null;
  parentId?: number | null;
  parentName?: string | null;
  parentSlug?: string | null;
  productCount: number;
}

interface SeoCollectionEntity {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  imageUrl?: string | null;
  collectionType: string;
}

interface SeoMetadata {
  title: string;
  description: string;
  canonicalPath: string;
  canonicalUrl?: string | null;
  robots: 'index,follow' | 'noindex,nofollow';
  h1?: string | null;
  imageUrl?: string | null;
  imageAlt?: string | null;
  pageType: 'website' | 'product' | 'collection' | 'article';
  breadcrumbs: SeoBreadcrumb[];
  faqs?: SeoFaqItem[];
  shippingInfo?: SeoShippingInfo | null;
  returnPolicy?: SeoReturnPolicy | null;
  brand?: SeoBrandInfo | null;
  productEntity?: SeoProductEntity | null;
  categoryEntity?: SeoCategoryEntity | null;
  collectionEntity?: SeoCollectionEntity | null;
  httpStatus: number; // 200 (OK), 301 (Moved Permanently), 404 (Not Found), 410 (Gone)
  redirectTo?: string | null; // Canonical target path for 301 redirects
}
```

The resolver derives data directly from active database entities and historical URL aliases. Pricing, SKU, and availability derive from active database variants. Ratings omit `aggregateRating` when review count is 0. Work 019 product information fields provide truthful product attributes and FAQs.
URL aliases / slug renames return `httpStatus: 301` with `redirectTo`. Archived/discontinued products return `httpStatus: 410` with `robots: "noindex,nofollow"`. Nonexistent routes return `httpStatus: 404`. Private routes (`/account`, `/cart`, `/checkout`, `/admin`, `/wishlist`) return `noindex,nofollow`. Preprod environments default to `noindex,nofollow` per DEC-005-7.

## Public Route Inventory & Build Snapshot

### Public Route Inventory
`GET /api/v1/seo/routes`

Returns the complete, database-driven list of all indexable public routes across the store (beyond any 100-item limit), including last modification timestamps, change frequency, and priority:

```ts
interface SeoRouteItem {
  path: string;
  canonicalUrl: string;
  pageType: 'website' | 'product' | 'collection' | 'article';
  lastmod?: string | null; // YYYY-MM-DD (null for static pages without database modification source)
  changefreq: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority: number;
}

interface SeoRouteInventoryOut {
  totalRoutes: number;
  routes: SeoRouteItem[];
  generatedAt: string; // ISO 8601
}
```

### Paginated Content Snapshot
`GET /api/v1/seo/snapshot?page=1&limit=50`

Returns a versioned, paginated snapshot of public pages and their fully resolved metadata/entities for static pre-rendering without hardcoding product lists:

```ts
interface SeoPageSnapshotItem {
  path: string;
  metadata: SeoMetadata;
}

interface SeoSnapshotResponse {
  page: number;
  limit: number;
  totalCount: number;
  totalPages: number;
  items: SeoPageSnapshotItem[];
  versionHash: string; // Deterministic global hash shared across all pages, sensitive to entity/price/stock/brand changes
}
```

## Sitemap and robots

- Backend generates a dynamic XML sitemap from active products, categories, collections, and public content pages, omitting `<lastmod>` for static pages without DB modification source.
- Production exposes it at `https://sulocraft.com/sitemap.xml` through a Cloudflare route/proxy to the backend generator.
- Production exposes `https://sulocraft.com/robots.txt`, referencing the canonical sitemap and disallowing private/admin routes. In preprod/staging or when `SEO_INDEXING_ENABLED=false`, robots.txt allows crawler access to public routes (so crawlers can discover the `noindex,nofollow` meta tags / headers) while omitting the sitemap reference and disallowing private routes.
- Development and preprod default to `noindex,nofollow` and local/preprod origins, never silently advertising production canonical URLs. Production missing or malformed origin/indexing configuration fails closed.
- Exclude inactive, out-of-policy, duplicate, filtered-query, customer, checkout, and admin URLs.

## Google Merchant Center feed

- **Primary XML Feed:** `GET /api/v1/seo/merchant-feed.xml` returns RSS 2.0 XML with the Google base namespace (`xmlns:g="http://base.google.com/ns/1.0"`).
- **Inspection JSON Feed:** `GET /api/v1/seo/merchant-feed` returns structured `MerchantFeedResponse` for testing and audit.
- Only active products (`status == "ACTIVE"`) and active variants (`status == "ACTIVE"`) are included.
- Handcrafted items declare `<g:identifier_exists>no</g:identifier_exists>` truthfully without fake GTIN/MPN.
- Image links are absolute, high-resolution URLs (R2 or public origin).
- Complete setup and attribute mappings are documented in [docs/merchant-center.md](merchant-center.md).

## Frontend metadata

The frontend converts `SeoMetadata` to:

- `<title>`, description, canonical, and robots tags.
- Open Graph and Twitter Card tags.
- `Organization` and `WebSite` structured data on public storefront pages.
- `Product`, `Offer`, `AggregateRating`, and `BreadcrumbList` structured data from typed entity data.

The backend must not return arbitrary HTML or JSON-LD scripts. It returns typed data; the frontend owns safe serialization.

## Rendering requirement

Client-side metadata is the first integration step. Before public launch, public home, collection, category, and product URLs must be pre-rendered or server-rendered so metadata and meaningful content exist in the initial HTML response. Cloudflare Pages deployment must preserve clean canonical URLs and return real 404 status behavior.
