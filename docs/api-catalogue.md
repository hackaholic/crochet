# API Contract: Product Catalogue Domain

> **Taxonomy update**: [product-taxonomy.md](product-taxonomy.md) is the controlling launch taxonomy contract. Existing examples that model gift occasions as product categories are legacy fixtures and must be replaced by first-class collections.

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT  

---

## 1. Overview & Base URL

* **Base URL**: `http://localhost:8000/api/v1` (or relative path in Docker: `/api/v1`)
* **Interactive Docs**: `http://localhost:8000/docs`
* **Raw Schema**: [`docs/openapi.yaml`](openapi.yaml)

All endpoints conform to Section 2, 8, 10, 13, and 18 of the [Multi-Agent Implementation Specification](SPECIFICATION.md).

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/categories` | Retrieve hierarchical categories tree (or flat list if `?flat=true`) |
| `GET` | `/categories/{slug}` | Single category detail |
| `GET` | `/categories/{slug}/products` | All products belonging to a category or its subcategories |
| `GET` | `/collections` | Active gift and merchandising collections with product counts |
| `GET` | `/products` | Filterable, searchable, and sortable product catalogue |
| `GET` | `/products/search?q={query}` | Keyword search across product name, description, tags, and categories |
| `GET` | `/products/{slug_or_id}` | Full product detail with variants, SKUs, gallery, and reviews |
| `GET` | `/occasions` | Curated gift occasions for navigation and filters |
| `GET` | `/reviews` | Testimonials & customer reviews for homepage and storefront |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id?: number | null;
  description?: string | null;
  image?: string | null;
  icon?: string | null;
  display_order: number;
  is_active: boolean;
  children?: Category[];
}

export interface ProductVariant {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  price: number;
  compareAtPrice?: number | null;
  stockQuantity: number;
  weight?: number | null;
  status: string;
  attributes: Record<string, any>;
}

export interface ProductImage {
  id: number;
  url: string;
  alt_text?: string | null;
  sort_order: number;
  is_primary: boolean;
  variant_id?: number | null;
}

export interface Review {
  id: number;
  product_id?: number | null;
  product_name?: string | null;
  author_name: string;
  location?: string | null;
  rating: number;
  text: string;
  avatar_url?: string | null;
  date?: string | null;
}

export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  price: number;
  compareAtPrice?: number | null;
  originalPrice?: number | null; // Backward compatibility
  rating: number;
  reviews: number;
  image: string;
  category: string;
  categories: string[];
  badge?: string | null;
  tags: string[];
  description?: string | null;
  customizable: boolean;
  inventoryStatus: 'IN_STOCK' | 'OUT_OF_STOCK';
}

export interface ProductDetail extends ProductListItem {
  short_description?: string | null;
  brand: string;
  images: string[];
  gallery: ProductImage[];
  variants: ProductVariant[];
  attributes: Record<string, any>;
  customerReviews: Review[];
}

export interface Occasion {
  id: string;
  name: string;
  icon?: string | null;
  image_url?: string | null;
}
```

---

## 4. Endpoint Details & Examples

### `GET /categories`
Retrieve category tree with subcategories.

**Query Parameters:**
* `flat` (boolean, optional, default: `false`): If `true`, returns a flat list of all categories instead of a nested tree.
* `includeEmpty` (boolean, optional, default: `false`): If `false`, excludes empty leaf categories. Parent counts include all active descendant categories.

Each category returns `productCount`. Customer-facing filters must omit options with `productCount = 0`; selecting a parent category must match products assigned to any descendant.

### `GET /collections`

Returns active, currently scheduled collections with `productCount`. The backend should exclude empty collections by default and may support `includeEmpty=true` for administrative preview. Customer-facing filters must never display collections with `productCount = 0`.

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Flowers",
    "slug": "flowers",
    "parent_id": null,
    "description": "Handcrafted permanent blooms, bouquets, and stems",
    "image": "https://images.unsplash.com/photo-1700171394718-2457b1190444?w=500&h=600&fit=crop&auto=format",
    "icon": null,
    "display_order": 0,
    "is_active": true,
    "children": [
      {
        "id": 2,
        "name": "Roses",
        "slug": "roses",
        "parent_id": 1,
        "description": null,
        "image": null,
        "icon": null,
        "display_order": 0,
        "is_active": true,
        "children": []
      },
      {
        "id": 3,
        "name": "Tulips",
        "slug": "tulips",
        "parent_id": 1,
        "description": null,
        "image": null,
        "icon": null,
        "display_order": 1,
        "is_active": true,
        "children": []
      }
    ]
  }
]
```

---

### `GET /products`
Retrieve filterable, sortable list of products.

**Query Parameters:**
* `category` (string, optional): Category slug or name (e.g., `flowers`, `amigurumi`).
* `tag` (string, optional): Tag name (e.g., `romantic`, `birthday`, `diwali`).
* `occasion` (string, optional): Occasion alias for tag filtering.
* `min_price` (integer, optional): Min price in INR.
* `max_price` (integer, optional): Max price in INR.
* `customizable` (boolean, optional): Filter products with custom personalization.
* `badge` (string, optional): Filter by badge (`Bestseller`, `New`, `Limited`, `Handmade`).
* `sort` (string, optional, default: `featured`): `featured`, `price_asc`, `price_desc`, `rating`, `newest`, `best_selling`.
* `page` (integer, optional, default: `1`): 1-indexed page number.
* `limit` (integer, optional, default: `50`): Max products per page.

**Headers Returned:**
* `X-Total-Count`: Total number of matching items across all pages.

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Forever Crochet Rose Bouquet",
    "slug": "forever-crochet-rose-bouquet",
    "price": 2599,
    "compareAtPrice": null,
    "originalPrice": null,
    "rating": 4.9,
    "reviews": 128,
    "image": "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
    "category": "Flowers",
    "categories": ["Flowers", "Roses", "Flower Bouquets", "Anniversary Gifts", "Valentine's Gifts"],
    "badge": "Bestseller",
    "tags": ["romantic", "anniversary", "valentine", "handmade", "roses"],
    "description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.",
    "customizable": true,
    "inventoryStatus": "IN_STOCK"
  }
]
```

---

### `GET /products/{slug_or_id}`
Retrieve complete product details. Supports both slug (`forever-crochet-rose-bouquet`) and integer ID (`1`).

**Example Response:**
```json
{
  "id": 1,
  "name": "Forever Crochet Rose Bouquet",
  "slug": "forever-crochet-rose-bouquet",
  "short_description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand...",
  "description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.",
  "category": "Flowers",
  "categories": ["Flowers", "Roses", "Flower Bouquets", "Anniversary Gifts", "Valentine's Gifts"],
  "tags": ["romantic", "anniversary", "valentine", "handmade", "roses"],
  "images": [
    "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1700171394718-2457b1190444?w=600&h=600&fit=crop&auto=format"
  ],
  "gallery": [
    {
      "id": 1,
      "url": "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
      "alt_text": null,
      "sort_order": 0,
      "is_primary": true,
      "variant_id": null
    }
  ],
  "variants": [
    {
      "id": 1,
      "product_id": 1,
      "sku": "FLR-ROSE-RED-5S",
      "name": "5 Roses / Deep Crimson",
      "price": 2599,
      "compareAtPrice": null,
      "stockQuantity": 15,
      "weight": null,
      "status": "ACTIVE",
      "attributes": {
        "color": "Deep Crimson",
        "stems": 5
      }
    }
  ],
  "price": 2599,
  "compareAtPrice": null,
  "originalPrice": null,
  "rating": 4.9,
  "reviews": 128,
  "inventoryStatus": "IN_STOCK",
  "badge": "Bestseller",
  "brand": "Crochet Bloom",
  "customizable": true,
  "attributes": {
    "customizable": true
  },
  "customerReviews": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Forever Crochet Rose Bouquet",
      "name": "Priya Sharma",
      "location": "Mumbai",
      "rating": 5,
      "text": "Bought the Forever Rose bouquet for our anniversary and it looked even better than the pictures! My husband was completely surprised. The quality is exceptional.",
      "image": "https://i.pravatar.cc/60?img=47",
      "date": "15 Aug 2026"
    }
  ]
}
```

---

### `GET /products/search`
Full-text keyword search across product names, descriptions, tags, and category names.

**Query Parameters:**
* `q` (string, required): Search query string.
* `limit` (integer, optional, default: `20`): Maximum results to return.
