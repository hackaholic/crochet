# E-commerce Website — Multi-Agent Implementation Specification

We are building a modern e-commerce website focused primarily on handmade/crochet products.

Two development agents will work together:

- **Frontend Agent: ChatGPT**
- **Backend Agent: Gemini**

Codex acts as the implementation/orchestration agent and should keep both sides aligned through clearly defined API contracts.

The architecture must be production-oriented, modular, secure, and flexible enough that new product types can be introduced without database redesign.

---

# 1. Agent Responsibilities

## Frontend — ChatGPT

ChatGPT owns:

- UI/UX architecture
- responsive website
- homepage
- product browsing
- category pages
- search/filter UI
- product detail page
- cart
- authentication UI
- checkout flow
- user account
- order history
- order tracking
- loading/error/empty states
- API integration
- accessibility
- frontend state management

The frontend MUST NOT duplicate business rules owned by the backend.

Backend API responses are the source of truth.

Frontend should consume an OpenAPI-generated or typed API client rather than manually creating unrelated request/response structures.

---

## Backend — Gemini

Gemini owns:

- database schema
- database migrations
- authentication
- authorization
- user management
- customer profiles
- product/catalog APIs
- categories
- product attributes
- variants
- SKU management
- inventory
- carts
- orders
- order tracking
- pricing
- coupons/discount support architecture
- payment integration interfaces
- API validation
- security
- caching
- logging
- auditability
- OpenAPI specification

Recommended baseline:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic
- Redis where caching/session/rate-limiting provides value

PostgreSQL remains the canonical persistent datastore.

---

# 2. API Contract Between Agents

Backend must publish the API contract before frontend implementation depends on an endpoint.

Maintain:

`/docs/openapi.yaml`

or generate the OpenAPI document automatically from FastAPI.

Frontend must generate/use TypeScript types from the backend contract.

Do NOT independently define:

```text
Frontend Product
Backend Product
```

with different fields.

There must be one agreed contract.

For example:

```text
GET /api/v1/products/{slug}

{
    id,
    name,
    slug,
    description,
    category,
    categories,
    tags,
    images,
    variants,
    price,
    compare_at_price,
    inventory_status,
    attributes
}
```

---

# 3. Authentication UX

Customer convenience is extremely important.

Customers SHOULD NOT be forced to register before browsing.

Flow:

```text
Visitor
   ↓
Browse website anonymously
   ↓
Search / explore products
   ↓
Add products to cart
   ↓
Continue shopping
   ↓
Checkout
   ↓
Login / identify customer
```

Support:

### Google Sign-In

One-click Google authentication.

### Phone Number Authentication

```text
Phone number
    ↓
Send OTP
    ↓
Verify OTP
    ↓
Logged in
```

Do NOT initially implement username/password authentication unless there is a strong requirement.

This avoids:

- registration forms
- password creation
- forgot-password flows
- password storage/security burden

---

# 4. Unified User Model

A customer may authenticate using:

```text
Google
Phone OTP
```

but internally there should still be ONE user.

Example conceptual model:

```text
User

id
name
email
phone
created_at
updated_at
last_login_at
status
```

And authentication identities separately:

```text
UserIdentity

id
user_id
provider
provider_subject
created_at
```

Examples:

```text
provider = google
provider = phone
```

This allows additional providers later without redesigning the User table.

---

# 5. Sessions / Tokens

Do not automatically use JWT just because this is an API.

For the normal browser application, prefer secure authentication using an:

```text
HttpOnly
Secure
SameSite
cookie
```

with either:

- server-managed session IDs, or
- short-lived signed access tokens with properly designed refresh handling.

JavaScript should NOT be able to read authentication tokens unnecessarily.

Avoid storing sensitive auth tokens in `localStorage`.

Backend must implement:

```text
POST /auth/google
POST /auth/phone/send-otp
POST /auth/phone/verify-otp
POST /auth/logout
GET  /auth/me
POST /auth/refresh       # if token architecture requires it
```

The frontend should only care that:

```text
GET /auth/me
```

returns the currently authenticated customer.

---

# 6. Guest Cart

Anonymous users MUST be able to add products to their cart.

On the first cart operation, generate a guest cart identifier stored in a secure cookie.

Example:

```text
Guest visitor
    ↓
cart_id cookie
    ↓
Cart stored server-side
```

When the visitor eventually logs in:

```text
Guest Cart
     +
Existing Customer Cart
     ↓
Cart Merge
     ↓
Customer Cart
```

Define deterministic merge rules.

Example:

If SKU already exists:

```text
quantity =
guest_quantity + existing_quantity
```

subject to inventory limits.

---

# 7. Cart Persistence

Do NOT store the only copy of the shopping cart in application memory.

Recommended architecture:

```text
PostgreSQL
    ↓
Canonical cart data

Redis
    ↓
Optional cache / temporary acceleration
```

Example entities:

```text
Cart
CartItem
```

Cart:

```text
id
user_id nullable
guest_token nullable
status
created_at
updated_at
expires_at
```

CartItem:

```text
id
cart_id
product_variant_id
quantity
created_at
updated_at
```

---

# 8. Catalog Design

Do NOT create rigid database structures such as:

```text
flower_type
rose_type
baby_product_type
amigurumi_type
```

inside the Product table.

We need a catalog system capable of handling products we haven't thought of yet.

Use:

```text
Category hierarchy
+
Tags
+
Attributes
+
Variants
+
JSONB metadata where appropriate
```

---

# 9. Category Architecture

Categories need parent-child relationships.

Conceptually:

```text
Category

id
name
slug
parent_id
description
image
display_order
is_active
```

`parent_id` references another Category.

Therefore arbitrary depth is possible.

Example:

```text
Flowers
 ├── Rose
 ├── Tulip
 │    ├── Open Tulip
 │    └── Closed Tulip
 ├── Daisy
 ├── Sunflower
 ├── Cosmos
 ├── Lily
 ├── Lavender
 ├── Peony
 └── Orchid
```

A product may belong to MULTIPLE categories.

Therefore use:

```text
ProductCategory
```

instead of putting one `category_id` directly into Product.

---

# 10. Initial Product Taxonomy

Start with the following storefront structure.

## Flowers

```text
Flowers
├── Roses
├── Tulips
│   ├── Open Tulip
│   └── Closed Tulip
├── Sunflowers
├── Daisies
├── Cosmos
├── Lily
├── Lavender
├── Peony
├── Orchid
├── Carnation
└── Flower Bouquets
```

Etsy's crochet marketplace also commonly combines flowers into bouquets, wedding arrangements, Mother's Day gifts, Valentine's products, nursery décor and home décor, demonstrating why category + tag classification should be flexible rather than exclusive. 

---

## Baby

```text
Baby
├── Blankets
├── Rattles
├── Toys
├── Baby Mobiles
├── Hanging Toys
├── Caps
├── Woollen Caps
├── Booties
├── Comforters
├── Nursery Decor
└── Baby Gift Sets
```

---

## Amigurumi

```text
Amigurumi
├── Bunny
├── Teddy Bear
├── Rabbit
├── Cats
├── Dogs
├── Farm Animals
├── Jungle Animals
├── Sea Animals
├── Birds
├── Dinosaurs
├── Dolls
├── Cartoon-Inspired Characters
├── Fantasy Characters
├── Food
├── Fruits
├── Vegetables
└── Miniatures
```

Do not hard-code particular copyrighted character names as structural product categories.

Character-inspired products can use tags/attributes where legally appropriate.

---

## Keychains

```text
Keychains
├── Flowers
├── Sunflower
├── Chilli / Mirchi
├── Octopus
├── Fruits
├── Animals
├── Food
├── Mini Amigurumi
├── Characters
├── Hearts
└── Personalized Keychains
```

---

## Home Decor

```text
Home Decor
├── Tablecloths
├── Table Runners
├── Coasters
├── Motifs
├── Wall Hangings
├── Doilies
├── Sofa Armrest Covers
├── Cushion Covers
├── Torans
├── Garlands
├── Plant Decor
├── Baskets
└── Seasonal Decor
```

---

## Special Gifts

This category should be based more on **occasion/intention** than product construction.

```text
Special Gifts
├── Birthday Gifts
├── Anniversary Gifts
├── Wedding Gifts
├── Engagement Gifts
├── Valentine's Gifts
├── Mother's Day Gifts
├── Father's Day Gifts
├── Baby Shower Gifts
├── Newborn Gifts
├── Housewarming Gifts
├── Friendship Gifts
├── Teacher Gifts
├── Return Gifts
├── Personalized Gifts
├── Couple Gifts
├── Gift Hampers
└── Custom Orders
```

An individual product can simultaneously belong to:

```text
Flowers > Roses
Special Gifts > Anniversary Gifts
Special Gifts > Valentine's Gifts
```

Do NOT duplicate the product.

Use category relationships.

---

## Pooja / Devotional Items

```text
Pooja Items
├── Aasan
├── Garlands
├── Laddu Gopal Clothes
├── Handmade God Clothes
├── Temple Decor
├── Toran
├── Decorative Flowers
├── Festival Decor
├── Pooja Mats
└── Gift Sets
```

---

# 11. Tags

Categories represent navigation.

Tags represent cross-cutting discovery.

Examples:

```text
handmade
crochet
wool
cotton
vegan-yarn
birthday
wedding
baby-shower
valentines
cute
floral
personalized
customizable
made-to-order
ready-to-ship
eco-friendly
gift-for-her
gift-for-him
gift-for-baby
```

Product:

```text
Product ↔ ProductTag ↔ Tag
```

Many-to-many.

---

# 12. Product Schema

Conceptually:

```text
Product

id
name
slug
short_description
description
status
brand
primary_image
metadata JSONB
created_at
updated_at
published_at
```

Do NOT store SKU directly on Product if variants exist.

SKU belongs to the sellable variant.

---

# 13. Product Variants

Example:

Crochet Rose:

```text
Red / Small
Red / Large
Pink / Small
Pink / Large
White / Small
White / Large
```

Each one may have different:

```text
price
stock
SKU
weight
image
```

Therefore:

```text
ProductVariant

id
product_id
sku
price
compare_at_price
cost
stock_quantity
weight
status
attributes JSONB
created_at
updated_at
```

Example variant attributes:

```json
{
  "color": "Pink",
  "size": "Large"
}
```

SKU must be UNIQUE.

Example SKU strategy:

```text
FLR-ROSE-PNK-L
FLR-TULIP-WHT-O
AMG-BUNNY-BRN-M
KEY-SUNFLWR-YLW
```

But SKU generation logic must not depend on these exact categories.

---

# 14. Flexible Product Attributes

Products will have radically different properties.

A blanket may have:

```text
size
material
color
length
width
```

A flower may have:

```text
flower_type
stem_length
color
bouquet_size
```

Amigurumi may have:

```text
character_type
height
material
recommended_age
```

Do NOT add all of these as columns on Product.

Support flexible attributes.

Either:

```text
AttributeDefinition
AttributeValue
ProductAttribute
```

or a carefully validated hybrid using PostgreSQL JSONB.

Recommended architecture:

Use normalized structures for attributes used heavily for filtering and JSONB for uncommon metadata.

---

# 15. Important Product Information

Each product should be capable of storing:

```text
Name
Slug
SKU / variants
Short description
Full description
Price
Discount/compare price
Images
Category/categories
Tags
Material
Color
Size
Dimensions
Weight
Stock
Made-to-order status
Estimated preparation time
Care instructions
Customization availability
Gift-wrap availability
Search metadata
SEO title
SEO description
```

---

# 16. Search and Filtering

Architecture should support eventual filtering by:

```text
Category
Product type
Price
Color
Size
Material
Occasion
Availability
Ready to ship
Made to order
Customizable
```

Do not build a schema that prevents this later.

Initial search can use PostgreSQL.

Do NOT introduce Elasticsearch just because this is e-commerce.

Add a dedicated search engine only once scale/search requirements justify it.

---

# 17. Product Images

Support multiple product images.

```text
ProductImage

id
product_id
variant_id nullable
url
alt_text
sort_order
is_primary
```

Never store image binaries directly inside PostgreSQL.

Use object storage/CDN eventually.

---

# 18. Main Backend API

Version all APIs:

```text
/api/v1/
```

## Authentication

```text
POST /auth/google
POST /auth/phone/send-otp
POST /auth/phone/verify-otp
POST /auth/logout
GET  /auth/me
```

## Categories

```text
GET /categories
GET /categories/{slug}
GET /categories/{slug}/products
```

## Products

```text
GET /products
GET /products/{slug}
GET /products/search
```

Support pagination/filtering:

```text
/products?category=flowers&page=1
/products?category=flowers&color=pink
/products?min_price=500&max_price=1500
/products?tag=birthday
```

## Cart

```text
GET    /cart
POST   /cart/items
PATCH  /cart/items/{item_id}
DELETE /cart/items/{item_id}
DELETE /cart
```

## Orders

```text
POST /orders
GET  /orders
GET  /orders/{order_id}
GET  /orders/{order_id}/tracking
```

---

# 19. Customer Account

After logging in, user should have:

```text
My Account
├── Profile
├── My Orders
├── Track Order
├── Saved Addresses
├── Wishlist
└── Logout
```

Customer should see:

```text
Order number
Order date
Products
Total
Payment status
Order status
Delivery/tracking status
```

---

# 20. Order State Model

Don't use arbitrary text statuses.

Use controlled states.

Example:

```text
PENDING_PAYMENT
PAID
CONFIRMED
PROCESSING
READY_TO_SHIP
SHIPPED
OUT_FOR_DELIVERY
DELIVERED
CANCELLED
REFUNDED
```

Order status history should also be recorded:

```text
OrderStatusHistory

id
order_id
status
timestamp
note
```

This makes order tracking possible.

---

# 21. Order Data Must Be Snapshotted

Do not rely on current Product data when displaying old orders.

Suppose:

```text
Rose Bouquet = ₹999 today
```

Customer purchased it at:

```text
₹799 six months ago
```

The order must continue displaying ₹799.

Therefore OrderItem should snapshot:

```text
product_name
sku
variant_description
unit_price
quantity
tax
discount
```

at purchase time.

---

# 22. Security Requirements

Treat all frontend input as untrusted.

Backend must protect against:

## SQL Injection

Use SQLAlchemy query APIs and parameterized queries.

Never generate SQL using:

```python
"... WHERE name = '" + user_input + "'"
```

---

## Input Validation

Every request must have Pydantic schemas.

Validate:

```text
IDs
quantity
phone numbers
prices
search input
pagination
addresses
coupon codes
```

Never trust frontend validation alone.

---

## Authentication Security

Implement:

```text
HttpOnly cookies
Secure cookies
SameSite policy
CSRF protection where applicable
CORS restrictions
token/session expiration
session revocation
```

---

## OTP Abuse

Implement:

```text
rate limiting
OTP expiration
attempt limit
resend cooldown
IP/user/device throttling
```

Prevent attackers from using the endpoint to send unlimited SMS messages.

---

## API Security

Implement:

```text
authorization on every private resource
rate limiting
secure headers
request size limits
safe error messages
structured logging
```

A customer requesting:

```text
GET /orders/123
```

must never get another customer's order simply because they know the ID.

Authorization must verify:

```text
order.user_id == authenticated_user.id
```

---

# 23. Database Integrity

Important fields must have constraints.

Examples:

```text
sku UNIQUE
slug UNIQUE
quantity > 0
price >= 0
stock >= 0
```

Use database transactions for operations involving multiple related writes.

Example:

```text
Create Order
 ↓
Create OrderItems
 ↓
Update Inventory
 ↓
Create Payment Record
```

must not leave half-created state if something fails.

---

# 24. Inventory Concurrency

Do not implement:

```text
read stock
if stock > 0
    stock = stock - 1
```

without concurrency protection.

Two customers may purchase simultaneously.

Inventory mutation must be transactional/atomic.

Design the data model so inventory reservation can later support:

```text
AVAILABLE
RESERVED
SOLD
```

without major redesign.

---

# 25. Payment Architecture

Do NOT tightly couple Order directly to one payment company.

Create:

```text
Payment

id
order_id
provider
provider_payment_id
amount
currency
status
created_at
updated_at
```

Then Razorpay, Stripe, Cashfree, etc. can be integrated later.

---

# 26. Address Architecture

Users may have multiple addresses.

```text
Address

id
user_id
name
phone
line1
line2
landmark
city
state
postal_code
country
is_default
```

But ORDER must snapshot the shipping address.

If the customer modifies their saved address tomorrow, an already placed order must retain its original address.

---

# 27. Wishlist

Architecture should support:

```text
Wishlist
WishlistItem
```

even if it isn't required in milestone one.

---

# 28. Product Personalization

Handmade products frequently require customizations.

Architecture should support eventual inputs such as:

```text
Name embroidery
Color request
Gift message
Custom size
Character request
Bouquet composition
```

Product can define personalization options.

Example:

```json
{
  "personalization": {
    "enabled": true,
    "fields": [
      {
        "name": "gift_message",
        "type": "text",
        "required": false,
        "max_length": 200
      }
    ]
  }
}
```

Snapshot the customer's selected personalization into the OrderItem.

---

# 29. Frontend Pages

ChatGPT frontend agent should implement:

```text
/
├── Home
├── Shop
├── Category
├── Search
├── Product Detail
├── Cart
├── Login
├── Checkout
├── Order Confirmation
├── Account
│   ├── Profile
│   ├── Orders
│   ├── Order Details
│   └── Addresses
├── Track Order
├── About
├── Contact
├── Shipping Policy
├── Return Policy
├── Privacy Policy
└── Terms
```

---

# 30. Homepage UX

Homepage should include:

```text
Hero section

Shop by Category

Flowers
Baby
Amigurumi
Keychains
Home Decor
Special Gifts
Pooja Items

Best Sellers

New Arrivals

Shop by Occasion

Birthday
Wedding
Anniversary
Baby Shower
Housewarming

Featured Collections

Personalized Products

Customer Reviews

Why Choose Us

Instagram/Social gallery

Footer
```

Do not overcrowd it.

The visual identity should communicate:

```text
handmade
warm
premium
playful
personal
crafted
```

without looking childish or like a generic marketplace template.

---

# 31. Mobile First

A significant percentage of customers will shop through phones.

Design mobile-first.

Must properly support:

```text
small-screen category navigation
sticky Add To Cart
mobile cart
OTP entry
Google login
touch targets
image swipe
filter drawer
checkout
order tracking
```

---

# 32. SEO

Product/category pages should be server-renderable/indexable.

Support:

```text
semantic HTML
clean URLs
meta title
meta description
canonical URL
OpenGraph
Product structured data
Breadcrumb structured data
sitemap.xml
robots.txt
```

URLs should look like:

```text
/flowers
/flowers/roses
/products/pink-crochet-rose-bouquet
```

not:

```text
/product?id=172839
```

---

# 33. Performance

Frontend:

```text
responsive images
lazy loading
code splitting
image optimization
CDN-ready architecture
```

Backend:

```text
pagination
DB indexes
connection pooling
selective caching
avoid N+1 queries
```

Add indexes based on actual query patterns.

Likely candidates:

```text
product.slug
variant.sku
category.slug
order.user_id
order.created_at
cart.user_id
product.status
```

---

# 34. Admin Architecture

Even if the first UI doesn't implement the admin dashboard completely, APIs/database should support eventual administration of:

```text
Products
Variants
Inventory
Categories
Tags
Orders
Customers
Coupons
Homepage collections
Reviews
Images
```

We must NOT need code deployments simply to add:

```text
a new flower
new animal
new gift occasion
new product category
```

These should be data/admin operations.

---

# 35. Milestone Strategy

Do NOT attempt the complete e-commerce system in one giant change.

## Milestone 1 — Foundation

Implement:

```text
project structure
PostgreSQL
SQLAlchemy
Alembic
configuration
logging
health endpoint
OpenAPI contract
```

## Milestone 2 — Catalog

Implement:

```text
categories
products
variants
SKU
tags
images
attributes
catalog APIs
```

Seed test data.

## Milestone 3 — Frontend Catalog

Implement:

```text
homepage
category browsing
product list
product page
search
```

using real backend APIs.

## Milestone 4 — Cart

Implement:

```text
guest cart
cart persistence
add/update/delete
guest → customer cart merge
```

## Milestone 5 — Authentication

Implement:

```text
Google
Phone OTP
session management
/auth/me
```

## Milestone 6 — Checkout / Orders

Implement:

```text
addresses
checkout
orders
order items
status history
```

## Milestone 7 — Payments

Integrate payment provider behind the Payment abstraction.

## Milestone 8 — Customer Account

Implement:

```text
order history
order details
tracking
addresses
profile
```

## Milestone 9 — Admin

Implement catalog
