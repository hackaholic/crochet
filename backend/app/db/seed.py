"""Catalogue seed script conforming to Section 10 & 13 of the Multi-Agent Specification."""

import re
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.catalogue import (
    Category,
    Occasion,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    Tag,
)
from app.models.storefront import BrandSettings, HomepageCampaign
from app.models.user import User, UserIdentity



def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def img(photo_id: str, w: int = 600, h: int = 600) -> str:
    return f"https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&auto=format"


# -----------------------------------------------------------------------------
# Section 10: Hierarchical Categories Taxonomy
# -----------------------------------------------------------------------------
TAXONOMY_TREE = [
    {
        "name": "Flowers",
        "slug": "flowers",
        "description": "Handcrafted permanent blooms, bouquets, and stems",
        "image": img("photo-1700171394718-2457b1190444", 500, 600),
        "children": [
            {"name": "Roses", "slug": "roses"},
            {"name": "Tulips", "slug": "tulips"},
            {"name": "Sunflowers", "slug": "sunflowers"},
            {"name": "Daisies", "slug": "daisies"},
            {"name": "Flower Bouquets", "slug": "flower-bouquets"},
        ],
    },
    {
        "name": "Baby",
        "slug": "baby",
        "description": "Soft cotton booties, rattles, blankets, and nursery décor",
        "image": img("photo-1629019317873-3f603b269723", 500, 600),
        "children": [
            {"name": "Booties", "slug": "booties"},
            {"name": "Rattles", "slug": "rattles"},
            {"name": "Baby Toys", "slug": "baby-toys"},
            {"name": "Baby Gift Sets", "slug": "baby-gift-sets"},
        ],
    },
    {
        "name": "Amigurumi",
        "slug": "amigurumi",
        "description": "Hand-stitched plush toys, animals, and miniature keepsakes",
        "image": img("photo-1753370241607-5d48d8aaa70e", 500, 600),
        "children": [
            {"name": "Teddy Bear", "slug": "teddy-bear"},
            {"name": "Bunny", "slug": "bunny"},
            {"name": "Panda", "slug": "panda"},
            {"name": "Miniatures", "slug": "miniatures"},
        ],
    },
    {
        "name": "Keychains",
        "slug": "keychains",
        "description": "Charming small gifts, flower charms, and mini animals",
        "image": img("photo-1700171458554-46cfd3f2a87a", 500, 600),
        "children": [
            {"name": "Flower Keychains", "slug": "flower-keychains"},
            {"name": "Animal Keychains", "slug": "animal-keychains"},
            {"name": "Personalized Keychains", "slug": "personalized-keychains"},
        ],
    },
    {
        "name": "Home Decor",
        "slug": "home-decor",
        "description": "Crochet wall hangings, planters, coasters, and festive garlands",
        "image": img("photo-1618574760337-2750f6251d20", 500, 600),
        "children": [
            {"name": "Coasters", "slug": "coasters"},
            {"name": "Wall Hangings", "slug": "wall-hangings"},
            {"name": "Plant Decor", "slug": "plant-decor"},
            {"name": "Garlands & Torans", "slug": "garlands-torans"},
        ],
    },
    {
        "name": "Special Gifts",
        "slug": "special-gifts",
        "description": "Curated gifts based on occasions, intention, and celebrations",
        "image": img("photo-1646182504823-a02b768e28b5", 500, 600),
        "children": [
            {"name": "Birthday Gifts", "slug": "birthday-gifts"},
            {"name": "Anniversary Gifts", "slug": "anniversary-gifts"},
            {"name": "Wedding Gifts", "slug": "wedding-gifts"},
            {"name": "Valentine's Gifts", "slug": "valentines-gifts"},
            {"name": "Housewarming Gifts", "slug": "housewarming-gifts"},
        ],
    },
    {
        "name": "Pooja Items",
        "slug": "pooja-items",
        "description": "Devotional garlands, malas, torans, and temple décor",
        "image": img("photo-1700170447159-9d2d0da133a5", 500, 600),
        "children": [
            {"name": "Devotional Garlands", "slug": "devotional-garlands"},
            {"name": "Toran", "slug": "toran"},
            {"name": "Temple Decor", "slug": "temple-decor"},
            {"name": "Festival Decor", "slug": "festival-decor"},
        ],
    },
]

OCCASIONS_DATA = [
    {"id": "birthday", "name": "Birthday", "icon": "🎂", "image_url": img("photo-1602773984044-3ecbed81556d", 400, 300)},
    {"id": "anniversary", "name": "Anniversary", "icon": "💍", "image_url": img("photo-1700171518313-5dd219beaaa6", 400, 300)},
    {"id": "valentine", "name": "Valentine's Day", "icon": "❤️", "image_url": img("photo-1646182504823-a02b768e28b5", 400, 300)},
    {"id": "wedding", "name": "Wedding", "icon": "💐", "image_url": img("photo-1700171394718-2457b1190444", 400, 300)},
    {"id": "babyshower", "name": "Baby Shower", "icon": "🍼", "image_url": img("photo-1629019317873-3f603b269723", 400, 300)},
    {"id": "housewarming", "name": "Housewarming", "icon": "🏠", "image_url": img("photo-1618574760337-2750f6251d20", 400, 300)},
    {"id": "rakhi", "name": "Rakhi", "icon": "🪡", "image_url": img("photo-1700170447159-9d2d0da133a5", 400, 300)},
    {"id": "diwali", "name": "Diwali", "icon": "🪔", "image_url": img("photo-1700171458554-46cfd3f2a87a", 400, 300)},
    {"id": "mother", "name": "Mother's Day", "icon": "🌷", "image_url": img("photo-1608825154649-2e9bb4cd4211", 400, 300)},
    {"id": "justbecause", "name": "Just Because", "icon": "🎁", "image_url": img("photo-1602773974733-b56200c8653f", 400, 300)},
]

# -----------------------------------------------------------------------------
# Products with Multiple Categories, Variants, and Unique SKUs
# -----------------------------------------------------------------------------
PRODUCTS_DATA = [
    {
        "id": 1,
        "name": "Forever Crochet Rose Bouquet",
        "slug": "forever-crochet-rose-bouquet",
        "price": 2599,
        "rating": 4.9,
        "reviews": 128,
        "image": img("photo-1700171518313-5dd219beaaa6"),
        "images": [
            img("photo-1700171518313-5dd219beaaa6"),
            img("photo-1700171394718-2457b1190444"),
            img("photo-1700170447159-9d2d0da133a5"),
            img("photo-1700171458554-46cfd3f2a87a"),
        ],
        "category_slugs": ["flowers", "roses", "flower-bouquets", "anniversary-gifts", "valentines-gifts"],
        "badge": "Bestseller",
        "tags": ["romantic", "anniversary", "valentine", "handmade", "roses"],
        "description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.",
        "customizable": True,
        "variants": [
            {"sku": "FLR-ROSE-RED-5S", "name": "5 Roses / Deep Crimson", "price": 2599, "stock": 15, "attributes": {"color": "Deep Crimson", "stems": 5}},
            {"sku": "FLR-ROSE-PNK-5S", "name": "5 Roses / Soft Pink", "price": 2599, "stock": 12, "attributes": {"color": "Soft Pink", "stems": 5}},
        ],
    },
    {
        "id": 2,
        "name": "Crochet Tulip Bouquet",
        "slug": "crochet-tulip-bouquet",
        "price": 1599,
        "rating": 4.8,
        "reviews": 96,
        "image": img("photo-1700171394718-2457b1190444"),
        "category_slugs": ["flowers", "tulips", "flower-bouquets", "birthday-gifts"],
        "badge": "New",
        "tags": ["romantic", "birthday", "tulips", "handmade"],
        "customizable": True,
        "variants": [
            {"sku": "FLR-TULIP-MIX-3S", "name": "3 Tulips / Pastel Mix", "price": 1599, "stock": 20, "attributes": {"color": "Pastel Mix", "stems": 3}},
        ],
    },
    {
        "id": 3,
        "name": "Heart Bear",
        "slug": "heart-bear",
        "price": 1799,
        "rating": 4.9,
        "reviews": 84,
        "image": img("photo-1602773984044-3ecbed81556d"),
        "category_slugs": ["amigurumi", "teddy-bear", "special-gifts", "valentines-gifts"],
        "badge": "Bestseller",
        "tags": ["romantic", "valentine", "birthday", "amigurumi"],
        "customizable": False,
        "variants": [
            {"sku": "AMG-BEAR-HRT-BRN", "name": "Standard / Warm Brown", "price": 1799, "stock": 10, "attributes": {"color": "Warm Brown"}},
        ],
    },
    {
        "id": 4,
        "name": "Couple Bunny Set",
        "slug": "couple-bunny-set",
        "price": 3299,
        "rating": 5.0,
        "reviews": 52,
        "image": img("photo-1629019317873-3f603b269723"),
        "category_slugs": ["amigurumi", "bunny", "wedding-gifts", "anniversary-gifts"],
        "badge": "Limited",
        "tags": ["romantic", "anniversary", "wedding", "amigurumi"],
        "customizable": True,
        "variants": [
            {"sku": "AMG-BUNNY-CPL-SET", "name": "Pair Set (Boy & Girl)", "price": 3299, "stock": 8, "attributes": {"set": "Pair"}},
        ],
    },
    {
        "id": 5,
        "name": "Mini Panda Amigurumi",
        "slug": "mini-panda-amigurumi",
        "price": 1299,
        "rating": 4.7,
        "reviews": 73,
        "image": img("photo-1602773974733-b56200c8653f"),
        "category_slugs": ["amigurumi", "panda", "miniatures", "baby-toys"],
        "badge": "Handmade",
        "tags": ["baby", "birthday", "amigurumi", "panda"],
        "customizable": False,
        "variants": [
            {"sku": "AMG-PANDA-MINI-01", "name": "Standard Mini Panda", "price": 1299, "stock": 18, "attributes": {"size": "Mini"}},
        ],
    },
    {
        "id": 6,
        "name": "Crochet Bunny",
        "slug": "crochet-bunny",
        "price": 1199,
        "rating": 4.8,
        "reviews": 61,
        "image": img("photo-1753370241607-5d48d8aaa70e"),
        "category_slugs": ["amigurumi", "bunny", "baby-toys"],
        "tags": ["baby", "birthday", "amigurumi", "bunny"],
        "customizable": False,
        "variants": [
            {"sku": "AMG-BUNNY-SNG-WHT", "name": "Single Bunny / White", "price": 1199, "stock": 25, "attributes": {"color": "White"}},
        ],
    },
    {
        "id": 7,
        "name": "Crochet Marigold Garland",
        "slug": "crochet-marigold-garland",
        "price": 1999,
        "rating": 4.9,
        "reviews": 45,
        "image": img("photo-1700170447159-9d2d0da133a5"),
        "category_slugs": ["pooja-items", "devotional-garlands", "festival-decor", "garlands-torans"],
        "badge": "Bestseller",
        "tags": ["pooja", "diwali", "festive", "marigold", "garland"],
        "customizable": True,
        "variants": [
            {"sku": "PJA-GARL-MARI-5FT", "name": "5 Feet Garland / Yellow & Orange", "price": 1999, "stock": 30, "attributes": {"length": "5ft"}},
        ],
    },
    {
        "id": 8,
        "name": "Sunflower Bouquet",
        "slug": "sunflower-bouquet",
        "price": 2199,
        "rating": 4.8,
        "reviews": 88,
        "image": img("photo-1700171458554-46cfd3f2a87a"),
        "category_slugs": ["flowers", "sunflowers", "flower-bouquets", "housewarming-gifts"],
        "badge": "Bestseller",
        "tags": ["birthday", "housewarming", "sunflowers"],
        "customizable": True,
        "variants": [
            {"sku": "FLR-SUNF-BQT-3S", "name": "3 Sunflowers + Foliage", "price": 2199, "stock": 14, "attributes": {"stems": 3}},
        ],
    },
    {
        "id": 9,
        "name": "Crochet Hanging Planter",
        "slug": "crochet-hanging-planter",
        "price": 1499,
        "rating": 4.6,
        "reviews": 39,
        "image": img("photo-1550376026-7375b92bb318"),
        "category_slugs": ["home-decor", "plant-decor", "housewarming-gifts"],
        "tags": ["housewarming", "home", "planter", "decor"],
        "customizable": False,
        "variants": [
            {"sku": "HME-PLNT-HANG-NAT", "name": "Natural Cotton Finish", "price": 1499, "stock": 15, "attributes": {"material": "Cotton"}},
        ],
    },
    {
        "id": 10,
        "name": "Boho Wall Hanging",
        "slug": "boho-wall-hanging",
        "price": 2999,
        "rating": 4.7,
        "reviews": 54,
        "image": img("photo-1618574760337-2750f6251d20"),
        "category_slugs": ["home-decor", "wall-hangings", "housewarming-gifts"],
        "tags": ["housewarming", "home", "boho", "wall-hanging"],
        "customizable": True,
        "variants": [
            {"sku": "HME-WALL-BOHO-MED", "name": "Medium (30x60cm)", "price": 2999, "stock": 8, "attributes": {"size": "Medium"}},
        ],
    },
    {
        "id": 11,
        "name": "Love Letter Crochet Set",
        "slug": "love-letter-crochet-set",
        "price": 3499,
        "rating": 4.9,
        "reviews": 34,
        "image": img("photo-1646182504823-a02b768e28b5"),
        "category_slugs": ["special-gifts", "valentines-gifts", "anniversary-gifts"],
        "badge": "New",
        "tags": ["romantic", "valentine", "anniversary", "personalized"],
        "customizable": True,
        "variants": [
            {"sku": "GFT-LOVE-LETR-SET", "name": "Box Set with Envelope & Flowers", "price": 3499, "stock": 10, "attributes": {"custom_message": True}},
        ],
    },
    {
        "id": 12,
        "name": "Mini Rose Box",
        "slug": "mini-rose-box",
        "price": 1899,
        "rating": 4.8,
        "reviews": 67,
        "image": img("photo-1608825154649-2e9bb4cd4211"),
        "category_slugs": ["flowers", "roses", "special-gifts"],
        "tags": ["romantic", "birthday", "mother", "roses"],
        "customizable": True,
        "variants": [
            {"sku": "FLR-ROSE-BOX-MINI", "name": "Compact Gift Box (4 Roses)", "price": 1899, "stock": 16, "attributes": {"count": 4}},
        ],
    },
    {
        "id": 13,
        "name": "Lotus Mala",
        "slug": "lotus-mala",
        "price": 999,
        "rating": 4.7,
        "reviews": 28,
        "image": img("photo-1700171518313-5dd219beaaa6"),
        "category_slugs": ["pooja-items", "devotional-garlands", "temple-decor"],
        "tags": ["pooja", "festive", "lotus"],
        "customizable": False,
        "variants": [
            {"sku": "PJA-MALA-LOTS-1M", "name": "1 Metre Single Strand", "price": 999, "stock": 25, "attributes": {"length": "1m"}},
        ],
    },
    {
        "id": 14,
        "name": "Crochet Toran",
        "slug": "crochet-toran",
        "price": 1799,
        "rating": 4.8,
        "reviews": 41,
        "image": img("photo-1700171394718-2457b1190444"),
        "category_slugs": ["pooja-items", "toran", "festival-decor", "garlands-torans"],
        "badge": "Bestseller",
        "tags": ["pooja", "diwali", "housewarming", "toran"],
        "customizable": True,
        "variants": [
            {"sku": "PJA-TORN-MAIN-3FT", "name": "3 Feet Standard Door Frame", "price": 1799, "stock": 14, "attributes": {"length": "3ft"}},
        ],
    },
    {
        "id": 15,
        "name": "Daisy Coaster Set",
        "slug": "daisy-coaster-set",
        "price": 899,
        "rating": 4.5,
        "reviews": 93,
        "image": img("photo-1700170447159-9d2d0da133a5"),
        "category_slugs": ["home-decor", "coasters", "housewarming-gifts"],
        "badge": "Bestseller",
        "tags": ["home", "housewarming", "coasters", "daisies"],
        "customizable": False,
        "variants": [
            {"sku": "HME-COAS-DASY-4PK", "name": "Set of 4 Coasters", "price": 899, "stock": 40, "attributes": {"pack": 4}},
        ],
    },
    {
        "id": 16,
        "name": "Mini Teddy Bear",
        "slug": "mini-teddy-bear",
        "price": 1099,
        "rating": 4.6,
        "reviews": 112,
        "image": img("photo-1602773974733-b56200c8653f"),
        "category_slugs": ["amigurumi", "teddy-bear", "miniatures", "baby-toys"],
        "badge": "Bestseller",
        "tags": ["baby", "birthday", "teddy", "amigurumi"],
        "customizable": False,
        "variants": [
            {"sku": "AMG-TEDY-MINI-01", "name": "Classic Honey Teddy", "price": 1099, "stock": 20, "attributes": {"color": "Honey"}},
        ],
    },
]

REVIEWS_DATA = [
    {
        "id": 1,
        "name": "Priya Sharma",
        "location": "Mumbai",
        "rating": 5,
        "text": "Bought the Forever Rose bouquet for our anniversary and it looked even better than the pictures! My husband was completely surprised. The quality is exceptional.",
        "product_name": "Forever Crochet Rose Bouquet",
        "avatar_url": "https://i.pravatar.cc/60?img=47",
        "date": "15 Aug 2026",
    },
    {
        "id": 2,
        "name": "Ananya Krishnan",
        "location": "Bangalore",
        "rating": 5,
        "text": "Ordered the Marigold Garland for Ganesh Chaturthi. It was absolutely stunning on our mandir! Everyone who visited asked where I got it from.",
        "product_name": "Crochet Marigold Garland",
        "avatar_url": "https://i.pravatar.cc/60?img=44",
        "date": "2 Sep 2026",
    },
    {
        "id": 3,
        "name": "Ritu Agarwal",
        "location": "Delhi",
        "rating": 5,
        "text": "The Couple Bunny Set was the perfect wedding gift. The packaging was so beautiful — I almost didn't want to give it away! Sulocraft is truly special.",
        "product_name": "Couple Bunny Set",
        "avatar_url": "https://i.pravatar.cc/60?img=41",
        "date": "20 Sep 2026",
    },
    {
        "id": 4,
        "name": "Meera Pillai",
        "location": "Chennai",
        "rating": 5,
        "text": "My daughter absolutely loves her mini panda! The craftsmanship is incredible. You can see the love that goes into every stitch. Will definitely order again.",
        "product_name": "Mini Panda Amigurumi",
        "avatar_url": "https://i.pravatar.cc/60?img=49",
        "date": "8 Sep 2026",
    },
]


def _seed_taxonomy_and_products(db: Session) -> None:
    """Seed Occasions, Categories, Tags, Products, Variants, and Reviews."""
    # 1. Seed Occasions
    for occ in OCCASIONS_DATA:
        existing = db.query(Occasion).filter_by(id=occ["id"]).first()
        if not existing:
            db.add(Occasion(**occ))

    # 2. Seed Hierarchical Categories
    category_slug_map: dict[str, Category] = {}
    for parent_idx, parent_data in enumerate(TAXONOMY_TREE):
        parent_cat = db.query(Category).filter_by(slug=parent_data["slug"]).first()
        if not parent_cat:
            parent_cat = Category(
                name=parent_data["name"],
                slug=parent_data["slug"],
                description=parent_data.get("description"),
                image=parent_data.get("image"),
                display_order=parent_idx,
                is_active=True,
            )
            db.add(parent_cat)
            db.flush()
        category_slug_map[parent_data["slug"]] = parent_cat

        for child_idx, child_data in enumerate(parent_data.get("children", [])):
            child_cat = db.query(Category).filter_by(slug=child_data["slug"]).first()
            if not child_cat:
                child_cat = Category(
                    name=child_data["name"],
                    slug=child_data["slug"],
                    parent_id=parent_cat.id,
                    display_order=child_idx,
                    is_active=True,
                )
                db.add(child_cat)
                db.flush()
            category_slug_map[child_data["slug"]] = child_cat

    # 3. Seed Tags
    tag_map: dict[str, Tag] = {}
    for p in PRODUCTS_DATA:
        for t_name in p.get("tags", []):
            if t_name not in tag_map:
                existing = db.query(Tag).filter_by(name=t_name).first()
                if not existing:
                    t = Tag(name=t_name)
                    db.add(t)
                    db.flush()
                    tag_map[t_name] = t
                else:
                    tag_map[t_name] = existing

    # 4. Seed Products and Variants
    for p_data in PRODUCTS_DATA:
        product = Product(
            id=p_data["id"],
            name=p_data["name"],
            slug=p_data["slug"],
            description=p_data.get("description"),
            short_description=p_data.get("description", "")[:120],
            primary_image=p_data["image"],
            badge=p_data.get("badge"),
            customizable=p_data.get("customizable", False),
            rating=p_data.get("rating", 5.0),
            reviews_count=p_data.get("reviews", 0),
            status="ACTIVE",
            brand="Sulocraft",
            metadata_json={"customizable": p_data.get("customizable", False)},
        )

        # Attach categories
        for c_slug in p_data.get("category_slugs", []):
            if c_slug in category_slug_map:
                product.categories.append(category_slug_map[c_slug])

        # Attach tags
        for t_name in p_data.get("tags", []):
            if t_name in tag_map:
                product.tags.append(tag_map[t_name])

        # Attach gallery images
        for idx, img_url in enumerate(p_data.get("images", [p_data["image"]])):
            product.images.append(
                ProductImage(
                    url=img_url,
                    sort_order=idx,
                    is_primary=(idx == 0),
                )
            )

        # Attach variants
        for v_data in p_data.get("variants", []):
            product.variants.append(
                ProductVariant(
                    sku=v_data["sku"],
                    name=v_data["name"],
                    price=v_data["price"],
                    stock_quantity=v_data.get("stock", 10),
                    status="ACTIVE",
                    attributes_json=v_data.get("attributes", {}),
                )
            )

        db.add(product)

    db.flush()

    # 5. Seed Reviews
    for r in REVIEWS_DATA:
        matching_product = db.query(Product).filter(Product.name.ilike(f"%{r['product_name']}%")).first()
        db.add(
            Review(
                id=r["id"],
                product_id=matching_product.id if matching_product else None,
                product_name=r["product_name"],
                author_name=r["name"],
                location=r["location"],
                rating=r["rating"],
                text=r["text"],
                avatar_url=r["avatar_url"],
                date=r["date"],
            )
        )

def seed_storefront_content(db: Session) -> None:
    """Seed default brand settings and initial 5 homepage campaigns."""
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand = BrandSettings(
            id=1,
            name="Sulocraft",
            owner_name="Anupama",
            instagram_url="https://instagram.com/sulocraft",
            whatsapp_url="https://wa.me/919876543210",
        )
        db.add(brand)
    else:
        if not brand.name:
            brand.name = "Sulocraft"
        if not brand.owner_name:
            brand.owner_name = "Anupama"

    if db.query(HomepageCampaign).count() == 0:
        campaigns_data = [
            {
                "title": "Rooted in Warmth, Woven by Hand",
                "emphasis": "Every loop tells a story",
                "eyebrow": "Our Heritage",
                "description": "Founded by Anupama, Sulocraft preserves traditional crochet artistry through modern heirloom designs crafted in small artisanal batches.",
                "image_url": "https://images.sulocraft.com/products/hero-brand-story.jpg",
                "image_alt": "Artisanal crochet yarn and handmade floral creation",
                "destination": "/about",
                "priority": 1,
                "is_active": True,
            },
            {
                "title": "Thoughtful Gifts for Festive Seasons",
                "emphasis": "Cherished moments",
                "eyebrow": "Festive Collection",
                "description": "Discover handcrafted festive hampers, delicate crochet pooja blooms, and heartwarming gifts crafted to bring joy.",
                "image_url": "https://images.sulocraft.com/products/hero-festive-gifting.jpg",
                "image_alt": "Festive handcrafted crochet gift box with ribbon",
                "destination": "/shop?category=Gifts",
                "priority": 2,
                "is_active": True,
            },
            {
                "title": "Fresh Floral Blooms & Modern Accents",
                "emphasis": "Just arrived in store",
                "eyebrow": "New Releases",
                "description": "Explore our latest collection of eternal potted flowers, handcrafted car charms, and pastel botanical bouquets.",
                "image_url": "https://images.sulocraft.com/products/hero-new-arrivals.jpg",
                "image_alt": "Handmade crochet flowers and miniature potted plants",
                "destination": "/shop",
                "priority": 3,
                "is_active": True,
            },
            {
                "title": "Artisanal Accents for Cozy Living",
                "emphasis": "Bespoke elegance",
                "eyebrow": "Home & Living",
                "description": "Elevate your sanctuary with intricate coasters, bohemian wall hangings, and tactile home accents that radiate warmth.",
                "image_url": "https://images.sulocraft.com/products/hero-home-decor.jpg",
                "image_alt": "Crochet table coaster and boho wall hanging decor",
                "destination": "/shop?category=Home+Decor",
                "priority": 4,
                "is_active": True,
            },
            {
                "title": "Made Specially for Your Special Occasions",
                "emphasis": "Personalized for you",
                "eyebrow": "Custom Orders",
                "description": "From personalized initials to custom colorways and bridal bouquets, collaborate directly with our artisans.",
                "image_url": "https://images.sulocraft.com/products/hero-custom-creations.jpg",
                "image_alt": "Custom colored yarn and bespoke crochet monogram project",
                "destination": "/contact?subject=custom-order",
                "priority": 5,
                "is_active": True,
            },
        ]
        for c in campaigns_data:
            db.add(HomepageCampaign(**c))

    db.commit()


def seed_catalogue(db: Session) -> None:
    """Populate database with hierarchical taxonomy, products, variants, tags, reviews, admin, and storefront."""
    if not db.query(Product).first():
        _seed_taxonomy_and_products(db)

    # Seed Default Admin User
    admin_user = db.query(User).filter(User.phone == "9999900000").first()
    if not admin_user:
        admin_user = User(
            name="Store Admin",
            email="admin@sulocraft.com",
            phone="9999900000",
            role="ADMIN",
            status="ACTIVE",
        )
        db.add(admin_user)
        db.flush()
        db.add(UserIdentity(user_id=admin_user.id, provider="phone", provider_subject="9999900000"))

    seed_storefront_content(db)
    db.commit()




if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_catalogue(session)
        print("Catalogue database seeded successfully!")
