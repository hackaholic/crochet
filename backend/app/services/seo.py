"""Service for Dynamic SEO Metadata Resolution, XML Sitemap generation, and Robots.txt."""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse
from xml.sax.saxutils import escape as xml_escape
from sqlalchemy.orm import Session

from app.core.images import build_image_url
from app.models.catalogue import Category, Collection, Product, ProductCategory
from app.models.storefront import BrandSettings
from app.schemas.seo import (
    SeoBreadcrumb,
    SeoFaqItem,
    SeoMetadataOut,
    SeoReturnPolicy,
    SeoShippingInfo,
)

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
                title=f"{brand_name} | Handcrafted Crochet Gifts, Flower Bouquets & Amigurumi in India",
                description="Discover 100% handcrafted heirloom crochet creations, forever flower bouquets, cute amigurumi keepsakes, and home decor lovingly made with premium milk cotton yarn.",
                canonicalPath="/",
                robots="index,follow",
                imageUrl=build_image_url("hero/heritage.png"),
                imageAlt=f"{brand_name} handcrafted crochet creations in India",
                pageType="website",
                breadcrumbs=[],
                faqs=[
                    SeoFaqItem(
                        question="Are all Sulocraft products 100% handmade?",
                        answer="Yes, every single piece at Sulocraft is handcrafted stitch by stitch in small batches by skilled artisans using premium, durable milk cotton yarn.",
                    ),
                    SeoFaqItem(
                        question="Do you ship across India and provide order tracking?",
                        answer="Yes, we provide tracked express shipping across all states in India with free delivery on orders above ₹999.",
                    ),
                    SeoFaqItem(
                        question="How do crochet flowers compare to real flowers?",
                        answer="Sulocraft crochet flowers never wilt, shed petals, or trigger pollen allergies. They are washable, eco-friendly, and serve as everlasting keepsakes.",
                    ),
                ],
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        # 3. Static Public Pages
        if path == "/about":
            return SeoMetadataOut(
                title="Our Story | Handcrafted Artisan Heritage | Sulocraft",
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
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        if path == "/contact":
            return SeoMetadataOut(
                title="Contact Us | Sulocraft Customer Support & Custom Orders",
                description="Get in touch with Sulocraft for custom orders, artisanal crochet inquiries, and dedicated customer support.",
                canonicalPath="/contact",
                robots="index,follow",
                imageUrl=None,
                imageAlt=None,
                pageType="website",
                breadcrumbs=[
                    SeoBreadcrumb(name="Home", path="/"),
                    SeoBreadcrumb(name="Contact", path="/contact"),
                ],
                shippingInfo=SeoShippingInfo(),
                returnPolicy=SeoReturnPolicy(),
            )

        # 4. Shop Page (no filter)
        if path == "/shop" and not query_params.get("category") and not query_params.get("collection"):
            return SeoMetadataOut(
                title="Shop Handcrafted Crochet Creations | Sulocraft",
                description="Explore our full catalogue of handcrafted crochet flowers, amigurumi toys, baby accessories, and pooja essentials with free shipping over ₹999.",
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
                desc = category.description or f"Discover our collection of handcrafted crochet {category.name.lower()} made with love by Sulocraft artisans. Free shipping on orders over ₹999."
                if len(desc) > 160:
                    desc = desc[:157] + "..."
                return SeoMetadataOut(
                    title=f"Handcrafted Crochet {category.name} | Buy Online India | Sulocraft",
                    description=desc,
                    canonicalPath=f"/categories/{category.slug}",
                    robots="index,follow",
                    imageUrl=img_url,
                    imageAlt=f"Handcrafted crochet {category.name} collection by Sulocraft",
                    pageType="collection",
                    breadcrumbs=breadcrumbs,
                    faqs=[
                        SeoFaqItem(
                            question=f"What makes Sulocraft crochet {category.name.lower()} unique?",
                            answer=f"Our {category.name.lower()} are 100% hand-knitted with soft, durable milk cotton yarn. They never wilt or fade and make thoughtful everlasting gifts.",
                        ),
                        SeoFaqItem(
                            question=f"How quickly do orders for {category.name.lower()} ship?",
                            answer="In-stock creations are dispatched within 24 to 48 hours and typically arrive within 3-5 business days across India.",
                        ),
                    ],
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
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
                desc = collection.description or f"Explore the {collection.name} handcrafted collection at Sulocraft. Limited edition heirloom crochet gifts."
                if len(desc) > 160:
                    desc = desc[:157] + "..."
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
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
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

                cat_label = prim_cat.name if prim_cat else "Creation"
                desc = product.short_description or product.description or f"Buy {product.name} handcrafted with premium yarn by Sulocraft."
                desc_meta = f"Handcrafted {product.name}. 100% handmade heirloom crochet in premium milk cotton yarn. {desc}".strip()
                if len(desc_meta) > 160:
                    desc_meta = desc_meta[:157] + "..."

                return SeoMetadataOut(
                    title=f"{product.name} - Handcrafted Crochet {cat_label} | Sulocraft",
                    description=desc_meta,
                    canonicalPath=f"/products/{product.slug}",
                    robots="index,follow",
                    imageUrl=build_image_url(product.primary_image),
                    imageAlt=f"Handcrafted {product.name} in premium milk cotton yarn by Sulocraft",
                    pageType="product",
                    breadcrumbs=breadcrumbs,
                    faqs=[
                        SeoFaqItem(
                            question=f"How do I clean and care for {product.name}?",
                            answer=f"Gently spot-clean {product.name} with a soft damp cloth and mild liquid detergent. Reshape gently while slightly damp and allow to air-dry completely in shade.",
                        ),
                        SeoFaqItem(
                            question=f"What materials are used to make {product.name}?",
                            answer=f"{product.name} is lovingly handmade with hypoallergenic, super-soft milk cotton yarn, reinforced internal wiring/stuffing, and durable color-fast dyes.",
                        ),
                        SeoFaqItem(
                            question="What is the return and refund policy for this item?",
                            answer="Sulocraft provides a 7-day hassle-free return window for any damaged, defective, or incorrect items with quick replacement or full refund.",
                        ),
                    ],
                    shippingInfo=SeoShippingInfo(),
                    returnPolicy=SeoReturnPolicy(),
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
        """Generate dynamic XML sitemap conforming to sitemaps.org standards with Google Image sitemap tags."""
        clean_base = (base_url or SeoService.get_canonical_base_url()).rstrip("/")
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        entries: list[dict[str, Any]] = []

        # 1. Static Public Pages
        entries.append({
            "loc": f"{clean_base}/",
            "lastmod": now_date,
            "changefreq": "daily",
            "priority": "1.0",
            "images": [{"loc": build_image_url("hero/heritage.png"), "title": "Sulocraft Handcrafted Crochet"}],
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
            "images": [{"loc": build_image_url("sections/artisan-story.jpg"), "title": "Sulocraft Artisan Story"}],
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
            images = []
            if cat.image_url:
                images.append({"loc": build_image_url(cat.image_url), "title": f"Crochet {cat.name}"})
            entries.append({
                "loc": f"{clean_base}/categories/{cat.slug}",
                "lastmod": mod_date,
                "changefreq": "weekly",
                "priority": "0.8",
                "images": images,
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
                images = []
                if col.image_url:
                    images.append({"loc": build_image_url(col.image_url), "title": col.name})
                entries.append({
                    "loc": f"{clean_base}/collections/{col.slug}",
                    "lastmod": mod_date,
                    "changefreq": "weekly",
                    "priority": "0.8",
                    "images": images,
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
            images = []
            if prod.primary_image:
                images.append({"loc": build_image_url(prod.primary_image), "title": prod.name})
            for img in prod.images:
                if img.url and img.url != prod.primary_image:
                    images.append({"loc": build_image_url(img.url), "title": img.alt_text or f"{prod.name} gallery image"})
            entries.append({
                "loc": f"{clean_base}/products/{prod.slug}",
                "lastmod": mod_date,
                "changefreq": "daily",
                "priority": "0.9",
                "images": images,
            })

        # Build XML
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        ]
        for e in entries:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{xml_escape(str(e['loc']))}</loc>")
            xml_lines.append(f"    <lastmod>{xml_escape(str(e['lastmod']))}</lastmod>")
            xml_lines.append(f"    <changefreq>{xml_escape(str(e['changefreq']))}</changefreq>")
            xml_lines.append(f"    <priority>{xml_escape(str(e['priority']))}</priority>")
            for img in e.get("images", []):
                xml_lines.append("    <image:image>")
                xml_lines.append(f"      <image:loc>{xml_escape(str(img['loc']))}</image:loc>")
                if img.get("title"):
                    xml_lines.append(f"      <image:title>{xml_escape(str(img['title']))}</image:title>")
                xml_lines.append("    </image:image>")
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
