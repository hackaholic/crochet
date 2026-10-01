# SEO Contract

**Status:** Backend implementation requested; frontend integration in progress

SEO is data-driven. React owns valid metadata markup and Schema.org serialization; FastAPI/PostgreSQL own page titles, descriptions, canonical paths, share images, indexing rules, breadcrumbs, and entity data.

## Page metadata resolver

`GET /api/v1/seo/resolve?path=/products/forever-crochet-rose-bouquet`

```ts
interface SeoMetadata {
  title: string;
  description: string;
  canonicalPath: string;
  robots: 'index,follow' | 'noindex,nofollow';
  imageUrl?: string | null;
  imageAlt?: string | null;
  pageType: 'website' | 'product' | 'collection' | 'article';
  breadcrumbs: Array<{ name: string; path: string }>;
}
```

The resolver uses current database entities. Product/category SEO fields remain editable, but defaults may be generated from the current product/category record. Private routes (`/account`, `/cart`, `/checkout`, `/admin`, `/wishlist`) and missing pages must return `noindex,nofollow`.

## Sitemap and robots

- Backend generates a dynamic XML sitemap from active products, categories, collections, and public content pages, including `lastmod`.
- Production exposes it at `https://sulocraft.com/sitemap.xml` through a Cloudflare route/proxy to the backend generator.
- Production exposes `https://sulocraft.com/robots.txt`, referencing the canonical sitemap and disallowing private/admin routes.
- Exclude inactive, out-of-policy, duplicate, filtered-query, customer, checkout, and admin URLs.

## Frontend metadata

The frontend converts `SeoMetadata` to:

- `<title>`, description, canonical, and robots tags.
- Open Graph and Twitter Card tags.
- `Organization` and `WebSite` structured data on public storefront pages.
- `Product`, `Offer`, `AggregateRating`, and `BreadcrumbList` structured data from typed entity data.

The backend must not return arbitrary HTML or JSON-LD scripts. It returns typed data; the frontend owns safe serialization.

## Rendering requirement

Client-side metadata is the first integration step. Before public launch, public home, collection, category, and product URLs must be pre-rendered or server-rendered so metadata and meaningful content exist in the initial HTML response. Cloudflare Pages deployment must preserve clean canonical URLs and return real 404 status behavior.
