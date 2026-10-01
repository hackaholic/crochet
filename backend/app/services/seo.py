"""Service for Dynamic SEO Metadata Resolution, XML Sitemap generation, and Robots.txt."""

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from sqlalchemy.orm import Session

from app.core.images import build_image_url
from app.models.catalogue import Category, Collection, Product, ProductCategory
from app.models.storefront import BrandSettings
from app.schemas.seo import SeoBreadcrumb, SeoMetadataOut

PRIVATE_PREFIXES = (
    "/account",
    "/admin",
    "/cart",
    "/checkout",
    "/wishlist",
    "/auth",
    "/login",
    "/orders",
    "/track",
    "/reset-password",
)

PRIVATE_PAGE_TITLES = {
    "/account": "My Account",
    "/cart": "Shopping Cart",
    "/checkout": "Checkout",
    "/wishlist": "My Wishlist",
    "/admin": "Store Administration",
    "/login": "Sign In",
    "/auth": "Authentication",
    "/orders": "My Orders",
    "/track": "Track Order",
}


class SeoService:
    """Handles dynamic SEO metadata resolution, sitemap XML generation, and robots directives."""

    @staticmethod
    def resolve_path(db: Session, path_str: str) -> SeoMetadataOut:
        """Resolve SEO metadata for any incoming path or URL conforming to docs/api-seo.md."""
        raw_path = (path_str or "/").strip()
        parsed = urlparse(raw_path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        query_params = parse_qs(parsed.query)

        # 1. Private Routes -> noindex,nofollow
        for prefix in PRIVATE_PREFIXES:
            if path == prefix or path.startswith(f"{prefix}/"):
                page_title = PRIVATE_PAGE_TITLES.get(prefix, "Private Page")
                return SeoMetadataOut(
                    title=f"{page_title} | Sulocraft",
                    description="Private user and store management page.",
                    canonicalPath=path,
                    robots="noindex,nofollow",
                    imageUrl=None,
                    imageAlt=None,
                    pageType="website",
                    breadcrumbs=[],
                )

        # 2. Homepage -> /
        if path == "/":
            brand = db.query(BrandSettings).first()
            brand_name = brand.name if brand else "Sulocraft"
            return SeoMetadataOut(
                title=f"{brand_name} | Handcrafted Heirloom Crochet Creations",
                description="Discover handcrafted heirloom crochet creations, floral bouquets, amigurumi keepsakes, and home decor lovingly made by Anupama Sharma.",
                canonicalPath="/",
                robots="index,follow",
                imageUrl=build_image_url("hero/heritage.png"),
                imageAlt=f"{brand_name} handcrafted crochet creations",
                pageType="website",
                breadcrumbs=[],
            )

        # 3. Static Public Pages
        if path == "/about":
            return SeoMetadataOut(
                title="Our Story | Sulocraft",
                description="Founded by Anupama Sharma, Sulocraft preserves traditional crochet artistry through modern heirloom designs crafted in small artisanal batches.",
                canonicalPath="/about",
                robots="index,follow",
                imageUrl=build_image_url("sections/artisan-story.jpg"),
                imageAlt="Sulocraft artisan creating handcrafted crochet",
                pageType="article",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="About Us", path="/about"),
                ],
            )

        if path == "/contact":
            return SeoMetadataOut(
                title="Contact Us | Sulocraft",
                description="Get in touch with Sulocraft for custom orders, artisanal crochet inquiries, and customer support.",
                canonicalPath="/contact",
                robots="index,follow",
                imageUrl=None,
                imageAlt=None,
                pageType="website",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Contact", path="/contact"),
                ],
            )

        # 4. Shop Page (no filter)
        if path == "/shop" and not query_params.get("category") and not query_params.get("collection"):
            return SeoMetadataOut(
                title="Shop Handcrafted Crochet Creations | Sulocraft",
                description="Explore our full catalogue of handcrafted crochet flowers, amigurumi toys, baby accessories, and pooja essentials.",
                canonicalPath="/shop",
                robots="index,follow",
                imageUrl=build_image_url("hero/heritage.png"),
                imageAlt="Sulocraft Shop Catalogue",
                pageType="collection",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ],
            )

        # 5. Category Routes: /categories/{slug} or /shop?category={slug}
        cat_slug = None
        if path.startswith("/categories/"):
            cat_slug = path.removeprefix("/categories/").strip("/")
        elif path == "/shop" and query_params.get("category"):
            cat_slug = query_params["category"][0].strip()

        if cat_slug:
            category = (
                db.query(Category)
                .filter(Category.slug == cat_slug, Category.is_active.is_(True))
                .first()
            )
            if category:
                breadcrumbs = [
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ]
                if category.parent_id:
                    parent = db.query(Category).filter(Category.id == category.parent_id).first()
                    if parent and parent.is_active:
                        breadcrumbs.append(
                            SeoBreadcrumb(name=parent.name, path=f"/categories/{parent.slug}")
                        )
                breadcrumbs.append(
                    SeoBreadcrumb(name=category.name, path=f"/categories/{category.slug}")
                )

                img_url = category.image_url
                desc = category.description or f"Discover our collection of handcrafted crochet {category.name.lower()} made with love by Sulocraft artisans."
                return SeoMetadataOut(
                    title=f"{category.name} | Handcrafted Crochet | Sulocraft",
                    description=desc,
                    canonicalPath=f"/categories/{category.slug}",
                    robots="index,follow",
                    imageUrl=img_url,
                    imageAlt=f"Handcrafted crochet {category.name}",
                    pageType="collection",
                    breadcrumbs=breadcrumbs,
                )
            else:
                return SeoService._not_found_metadata(path)

        # 6. Collection Routes: /collections/{slug} or /shop?collection={slug}
        col_slug = None
        if path.startswith("/collections/"):
            col_slug = path.removeprefix("/collections/").strip("/")
        elif path == "/shop" and query_params.get("collection"):
            col_slug = query_params["collection"][0].strip()

        if col_slug:
            now = datetime.now(timezone.utc)
            collection = (
                db.query(Collection)
                .filter(Collection.slug == col_slug, Collection.is_active.is_(True))
                .first()
            )
            if collection and (collection.starts_at is None or collection.starts_at <= now) and (collection.ends_at is None or collection.ends_at >= now):
                desc = collection.description or f"Explore the {collection.name} handcrafted collection at Sulocraft."
                return SeoMetadataOut(
                    title=f"{collection.name} | Sulocraft Collections",
                    description=desc,
                    canonicalPath=f"/collections/{collection.slug}",
                    robots="index,follow",
                    imageUrl=collection.image_url,
                    imageAlt=f"Sulocraft {collection.name}",
                    pageType="collection",
                    breadcrumbs=[
                        SeoBreadcrumb(name="Home", path="/"),
                        SeoBreadcrumb(name="Shop", path="/shop"),
                        SeoBreadcrumb(name=collection.name, path=f"/collections/{collection.slug}"),
                    ],
                )
            else:
                return SeoService._not_found_metadata(path)

        # 7. Product Routes: /products/{slug}
        if path.startswith("/products/"):
            prod_slug = path.removeprefix("/products/").strip("/")
            product = (
                db.query(Product)
                .filter(Product.slug == prod_slug, Product.status == "ACTIVE")
                .first()
            )
            if product:
                breadcrumbs = [
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Shop", path="/shop"),
                ]

                prim_link = (
                    db.query(ProductCategory)
                    .filter(ProductCategory.product_id == product.id, ProductCategory.is_primary.is_(True))
                    .first()
                )
                prim_cat = None
                if prim_link:
                    prim_cat = db.query(Category).filter(Category.id == prim_link.category_id).first()
                elif product.categories:
                    prim_cat = product.categories[0]

                if prim_cat and prim_cat.is_active:
                    if prim_cat.parent_id:
                        parent = db.query(Category).filter(Category.id == prim_cat.parent_id).first()
                        if parent and parent.is_active:
                            breadcrumbs.append(
                                SeoBreadcrumb(name=parent.name, path=f"/categories/{parent.slug}")
                            )
                    breadcrumbs.append(
                        SeoBreadcrumb(name=prim_cat.name, path=f"/categories/{prim_cat.slug}")
                    )

                breadcrumbs.append(
                    SeoBreadcrumb(name=product.name, path=f"/products/{product.slug}")
                )

                desc = product.short_description or product.description or f"Buy {product.name} handcrafted with premium yarn by Sulocraft."
                if len(desc) > 160:
                    desc = desc[:157] + "..."

                return SeoMetadataOut(
                    title=f"{product.name} | Sulocraft",
                    description=desc,
                    canonicalPath=f"/products/{product.slug}",
                    robots="index,follow",
                    imageUrl=build_image_url(product.primary_image),
                    imageAlt=product.name,
                    pageType="product",
                    breadcrumbs=breadcrumbs,
                )
            else:
                return SeoService._not_found_metadata(path)

        # 8. Unmatched / 404 Route
        return SeoService._not_found_metadata(path)

    @staticmethod
    def _not_found_metadata(path: str) -> SeoMetadataOut:
        """Fallback metadata for missing pages and invalid slugs."""
        return SeoMetadataOut(
            title="Page Not Found | Sulocraft",
            description="The requested page could not be found on Sulocraft.",
            canonicalPath=path,
            robots="noindex,nofollow",
            imageUrl=None,
            imageAlt=None,
            pageType="website",
            breadcrumbs=[],
        )

    @staticmethod
    def generate_sitemap_xml(db: Session, base_url: str | None = None) -> str:
        """Generate dynamic XML sitemap conforming to sitemaps.org standards."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        entries: list[dict[str, str]] = []

        # 1. Static Public Pages
        entries.append({
            "loc": f"{clean_base}/",
            "lastmod": now_date,
            "changefreq": "daily",
            "priority": "1.0",
        })
        entries.append({
            "loc": f"{clean_base}/shop",
            "lastmod": now_date,
            "changefreq": "daily",
            "priority": "0.9",
        })
        entries.append({
            "loc": f"{clean_base}/about",
            "lastmod": now_date,
            "changefreq": "monthly",
            "priority": "0.7",
        })
        entries.append({
            "loc": f"{clean_base}/contact",
            "lastmod": now_date,
            "changefreq": "monthly",
            "priority": "0.6",
        })

        # 2. Active Categories
        categories = (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.display_order, Category.id)
            .all()
        )
        for cat in categories:
            mod_date = (cat.updated_at or cat.created_at).strftime("%Y-%m-%d") if hasattr(cat, "updated_at") and cat.updated_at else now_date
            entries.append({
                "loc": f"{clean_base}/categories/{cat.slug}",
                "lastmod": mod_date,
                "changefreq": "weekly",
                "priority": "0.8",
            })

        # 3. Active Collections
        now_time = datetime.now(timezone.utc)
        collections = (
            db.query(Collection)
            .filter(Collection.is_active.is_(True))
            .order_by(Collection.display_order, Collection.id)
            .all()
        )
        for col in collections:
            if (col.starts_at is None or col.starts_at <= now_time) and (col.ends_at is None or col.ends_at >= now_time):
                mod_date = (col.updated_at or col.created_at).strftime("%Y-%m-%d") if hasattr(col, "updated_at") and col.updated_at else now_date
                entries.append({
                    "loc": f"{clean_base}/collections/{col.slug}",
                    "lastmod": mod_date,
                    "changefreq": "weekly",
                    "priority": "0.8",
                })

        # 4. Active Products
        products = (
            db.query(Product)
            .filter(Product.status == "ACTIVE")
            .order_by(Product.id)
            .all()
        )
        for prod in products:
            mod_date = (prod.updated_at or prod.created_at).strftime("%Y-%m-%d") if hasattr(prod, "updated_at") and prod.updated_at else now_date
            entries.append({
                "loc": f"{clean_base}/products/{prod.slug}",
                "lastmod": mod_date,
                "changefreq": "daily",
                "priority": "0.9",
            })

        # Build XML
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for e in entries:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{e['loc']}</loc>")
            xml_lines.append(f"    <lastmod>{e['lastmod']}</lastmod>")
            xml_lines.append(f"    <changefreq>{e['changefreq']}</changefreq>")
            xml_lines.append(f"    <priority>{e['priority']}</priority>")
            xml_lines.append("  </url>")
        xml_lines.append("</urlset>")

        return "\n".join(xml_lines)

    @staticmethod
    def get_canonical_base_url() -> str:
        """Return public production/staging domain for sitemap and robots directives."""
        from app.core.config import settings
        frontend = getattr(settings, "frontend_url", None)
        if frontend and not any(h in frontend for h in ("localhost", "127.0.0.1", "testserver")):
            return frontend.rstrip("/")
        return "https://sulocraft.com"

    @staticmethod
    def generate_robots_txt(base_url: str | None = None) -> str:
        """Generate production robots.txt file with disallowed private routes and canonical sitemap."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        return (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            "Disallow: /account/\n"
            "Disallow: /cart\n"
            "Disallow: /checkout\n"
            "Disallow: /wishlist\n"
            "Disallow: /auth/\n"
            "Disallow: /api/\n"
            "\n"
            f"Sitemap: {clean_base}/sitemap.xml\n"
        )
