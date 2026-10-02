"""Admin API router conforming to Sections 18, 20, 34, and Milestone 9 of Specification."""

import re
from typing import Any
from datetime import datetime, timedelta, timezone
import secrets
import uuid
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_admin
from app.db.session import get_db
from app.services.notification import dispatch_order_status_background, dispatch_welcome_background
from app.services.payment.factory import get_payment_provider
from app.services.storage import get_storage_provider
from app.models.catalogue import (
    Category,
    Collection,
    Occasion,
    Product,
    ProductCategory,
    ProductCollection,
    ProductImage,
    ProductOccasion,
    ProductVariant,
    Review,
    Tag,
)
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    PaymentStatus,
    RefundStatus,
    ReturnRequest,
    ReturnStatus,
)
from app.models.payment import Payment, PaymentRecordStatus
from app.models.promotion import Coupon
from app.models.storefront import BrandSettings, HomepageCampaign, HomepageSection
from app.models.user import User
from app.schemas.storefront import (
    AdminHomepageCampaignCreate,
    AdminHomepageCampaignOut,
    AdminHomepageCampaignUpdate,
    AdminHomepageSectionCreate,
    AdminHomepageSectionOut,
    AdminHomepageSectionUpdate,
    BrandSettingsOut,
    BrandSettingsUpdate,
)

from app.schemas.admin import (
    AdminAnalyticsOut,
    AdminAttentionItem,
    AdminAttentionListOut,
    AdminCategoryCreate,
    AdminCategoryOut,
    AdminCategoryUpdate,
    AdminCollectionAssignProducts,
    AdminCollectionCreate,
    AdminCollectionOut,
    AdminCollectionUpdate,
    AdminDashboardComparison,
    AdminDashboardSummaryOut,
    AdminFinanceSalesBucket,
    AdminFinanceSeriesOut,
    AdminFinanceSummaryOut,
    AdminGlobalSearchOut,
    AdminInventoryAdjustRequest,
    AdminLowStockItem,
    AdminOccasionIn,
    AdminOccasionOut,
    AdminOccasionUpdateIn,
    AdminOrderDetailOut,
    AdminOrderItemOut,
    AdminOrderListOut,
    AdminOrderStatusUpdate,
    AdminProductCreate,
    AdminProductListOut,
    AdminProductOut,
    AdminProductUpdate,
    AdminReturnCreateIn,
    AdminReturnDetailOut,
    AdminReturnItemIn,
    AdminReturnItemOut,
    AdminReturnListOut,
    AdminReturnRefundIn,
    AdminReturnStatusUpdateIn,
    AdminSalesBucket,
    AdminSalesSeriesOut,
    AdminSearchResultItem,
    AdminSendWelcomeRequest,
    AdminTopSellingProduct,
    AdminVariantCreate,
    AdminVariantOut,
    AdminVariantUpdate,
)
from app.schemas.promotion import (
    AdminCouponCreate,
    AdminCouponOut,
    AdminCouponUpdate,
)
from app.schemas.review import AdminReviewOut

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


def _slugify(text: str) -> str:
    """Helper to convert string into URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def _variant_to_admin_out(v: ProductVariant) -> AdminVariantOut:
    """Convert ProductVariant ORM to AdminVariantOut."""
    return AdminVariantOut(
        id=v.id,
        productId=v.product_id,
        sku=v.sku,
        name=v.name,
        price=v.price,
        pricePaise=v.price * 100,
        compareAtPrice=v.compare_at_price,
        compareAtPricePaise=v.compare_at_price * 100 if v.compare_at_price else None,
        cost=v.cost,
        stockQuantity=v.stock_quantity,
        weight=v.weight,
        status=v.status,
        attributes=v.attributes_json or {},
        createdAt=v.created_at,
        updatedAt=v.updated_at,
    )


def _product_to_admin_out(p: Product) -> AdminProductOut:
    """Convert Product ORM to comprehensive AdminProductOut."""
    active_variants = [v for v in p.variants if v.status == "ACTIVE"]
    variants_for_calc = active_variants if active_variants else p.variants

    total_stock = sum(v.stock_quantity for v in variants_for_calc)
    min_price = min((v.price for v in variants_for_calc), default=0)

    prim_cat = p.primary_category
    primary_category_id = prim_cat.id if prim_cat else None

    return AdminProductOut(
        id=p.id,
        name=p.name,
        slug=p.slug,
        shortDescription=p.short_description,
        description=p.description,
        status=p.status,
        brand=p.brand or "Sulocraft",
        primaryImage=p.primary_image,
        badge=p.badge,
        customizable=p.customizable,
        rating=p.rating or 5.0,
        reviewsCount=p.reviews_count or 0,
        primaryCategoryId=primary_category_id,
        categoryIds=[c.id for c in p.categories],
        categoryNames=[c.name for c in p.categories],
        collectionIds=[c.id for c in p.collections],
        collectionNames=[c.name for c in p.collections],
        tagIds=[t.id for t in p.tags],
        tagNames=[t.name for t in p.tags],
        galleryImages=[img.url for img in p.images],
        variants=[_variant_to_admin_out(v) for v in p.variants],
        totalStock=total_stock,
        minPrice=min_price,
        minPricePaise=min_price * 100,
        createdAt=p.created_at,
        updatedAt=p.updated_at,
    )


def _category_to_admin_out(c: Category) -> AdminCategoryOut:
    """Convert Category ORM to AdminCategoryOut."""
    return AdminCategoryOut(
        id=c.id,
        name=c.name,
        slug=c.slug,
        parentId=c.parent_id,
        description=c.description,
        imageKey=c.image_key,
        image=c.image_url,
        imageUrl=c.image_url,
        icon=c.icon,
        displayOrder=c.display_order or 0,
        isActive=c.is_active,
        showWhenEmpty=c.show_when_empty,
        seoTitle=c.seo_title,
        seoDescription=c.seo_description,
        productsCount=len(c.products) if c.products else 0,
        createdAt=c.created_at,
        updatedAt=c.updated_at,
    )


def _collection_to_admin_out(col: Collection) -> AdminCollectionOut:
    """Convert Collection ORM to AdminCollectionOut."""
    return AdminCollectionOut(
        id=col.id,
        name=col.name,
        slug=col.slug,
        description=col.description,
        imageKey=col.image_key,
        imageUrl=col.image_url,
        collectionType=col.collection_type,
        displayOrder=col.display_order or 0,
        isActive=col.is_active,
        startsAt=col.starts_at,
        endsAt=col.ends_at,
        seoTitle=col.seo_title,
        seoDescription=col.seo_description,
        productsCount=len(col.products) if col.products else 0,
        createdAt=col.created_at,
        updatedAt=col.updated_at,
    )


def _order_to_admin_detail(order: Order) -> AdminOrderDetailOut:
    """Convert Order ORM to full AdminOrderDetailOut."""
    items_out = [
        AdminOrderItemOut(
            id=item.id,
            productId=item.product_id,
            variantId=item.product_variant_id,
            productName=item.product_name,
            productSlug=item.product_slug,
            sku=item.sku,
            variantName=item.variant_name,
            productImage=item.product_image,
            unitPrice=item.unit_price,
            unitPricePaise=item.unit_price * 100,
            quantity=item.quantity,
            lineTotal=item.line_total,
            lineTotalPaise=item.line_total * 100,
            personalization=item.personalization_json or {},
        )
        for item in order.items
    ]

    history_out = [
        {
            "id": h.id,
            "status": h.status,
            "note": h.note,
            "timestamp": h.timestamp.isoformat() if h.timestamp else None,
        }
        for h in order.status_history
    ]

    return AdminOrderDetailOut(
        id=order.id,
        orderNumber=order.order_number,
        customerName=order.customer_name,
        customerPhone=order.customer_phone,
        customerEmail=order.customer_email,
        status=order.status,
        paymentStatus=order.payment_status,
        paymentMethod=order.payment_method,
        currency=order.currency or "INR",
        subtotal=order.subtotal,
        subtotalPaise=order.subtotal * 100,
        shippingFee=order.shipping_fee,
        shippingFeePaise=order.shipping_fee * 100,
        discountAmount=order.discount_amount,
        discountAmountPaise=order.discount_amount * 100,
        taxAmount=order.tax_amount,
        taxAmountPaise=order.tax_amount * 100,
        totalAmount=order.total_amount,
        totalAmountPaise=order.total_amount * 100,
        shippingAddress=order.shipping_address_json or {},
        billingAddress=order.billing_address_json,
        trackingNumber=order.tracking_number,
        courierName=order.courier_name,
        notes=order.notes,
        items=items_out,
        statusHistory=history_out,
        createdAt=order.created_at,
        updatedAt=order.updated_at,
    )


def _parse_ist_date_range(
    from_str: str | None,
    to_str: str | None,
    default_days: int = 30,
) -> tuple[datetime, datetime, str, str]:
    """Parse calendar date strings in Asia/Kolkata (IST) and return UTC boundaries with effective IST dates."""
    now_ist = datetime.now(IST)
    if to_str:
        try:
            to_clean = to_str.strip().split("T")[0]
            to_d = datetime.strptime(to_clean, "%Y-%m-%d").date()
        except ValueError:
            to_d = now_ist.date()
    else:
        to_d = now_ist.date()

    if from_str:
        try:
            from_clean = from_str.strip().split("T")[0]
            from_d = datetime.strptime(from_clean, "%Y-%m-%d").date()
        except ValueError:
            from_d = to_d - timedelta(days=default_days)
    else:
        from_d = to_d - timedelta(days=default_days)

    if from_d > to_d:
        from_d, to_d = to_d, from_d

    from_ist_dt = datetime(from_d.year, from_d.month, from_d.day, 0, 0, 0, tzinfo=IST)
    to_ist_dt = datetime(to_d.year, to_d.month, to_d.day, 23, 59, 59, 999999, tzinfo=IST)

    from_utc = from_ist_dt.astimezone(timezone.utc).replace(tzinfo=None)
    to_utc = to_ist_dt.astimezone(timezone.utc).replace(tzinfo=None)

    return from_utc, to_utc, from_d.isoformat(), to_d.isoformat()


def _return_to_admin_out(r: ReturnRequest) -> AdminReturnDetailOut:
    """Convert ReturnRequest ORM to AdminReturnDetailOut."""
    items = []
    for it in (r.items_json or []):
        items.append(
            AdminReturnItemOut(
                orderItemId=it.get("order_item_id") or it.get("orderItemId") or 0,
                productName=it.get("product_name") or it.get("productName") or "Product",
                sku=it.get("sku") or "",
                quantity=it.get("quantity") or 1,
                unitPrice=it.get("unit_price") or it.get("unitPrice") or 0,
                lineTotal=it.get("line_total") or it.get("lineTotal") or 0,
            )
        )
    order = r.order
    return AdminReturnDetailOut(
        id=r.id,
        returnNumber=r.return_number,
        orderId=r.order_id,
        orderNumber=order.order_number if order else "",
        customerName=order.customer_name if order else "Customer",
        customerEmail=order.customer_email if order else None,
        customerPhone=order.customer_phone if order else "",
        status=r.status,
        reason=r.reason,
        reasonDetails=r.reason_details,
        items=items,
        refundAmount=r.refund_amount,
        refundAmountPaise=r.refund_amount_paise or (r.refund_amount * 100),
        refundStatus=r.refund_status,
        adminNotes=r.admin_notes,
        history=r.history_json or [],
        createdAt=r.created_at or datetime.now(timezone.utc),
        updatedAt=r.updated_at or datetime.now(timezone.utc),
    )


# -----------------------------------------------------------------------------
# Products Administration
# -----------------------------------------------------------------------------


@router.get("/products", response_model=AdminProductListOut)
def list_admin_products(
    q: str | None = Query(default=None, description="Search term in name, description, or SKU"),
    status: str | None = Query(default=None, description="Filter by status: ACTIVE, DRAFT, ARCHIVED"),
    category_id: int | None = Query(default=None, alias="categoryId"),
    low_stock: bool | None = Query(default=None, alias="lowStock", description="Filter products with low stock (<=5)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminProductListOut:
    """List products for store administration with search and filtering."""
    query = (
        db.query(Product)
        .options(
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
    )

    if status:
        query = query.filter(Product.status == status)

    if category_id:
        query = query.filter(Product.categories.any(Category.id == category_id))

    if q:
        search_fmt = f"%{q.strip()}%"
        query = query.filter(
            (Product.name.ilike(search_fmt))
            | (Product.description.ilike(search_fmt))
            | (Product.variants.any(ProductVariant.sku.ilike(search_fmt)))
        )

    if low_stock:
        query = query.filter(Product.variants.any(ProductVariant.stock_quantity <= 5))

    total = query.distinct().count()
    products = (
        query.distinct()
        .order_by(Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AdminProductListOut(
        items=[_product_to_admin_out(p) for p in products],
        total=total,
        page=page,
        pageSize=page_size,
    )


@router.post("/products", response_model=AdminProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: AdminProductCreate,
    db: Session = Depends(get_db),
) -> AdminProductOut:
    """Create a new product with optional initial variants and gallery images."""
    slug = payload.slug or _slugify(payload.name)
    existing_slug = db.query(Product).filter(Product.slug == slug).first()
    if existing_slug:
        slug = f"{slug}-{int(datetime.now(timezone.utc).timestamp())}"

    product = Product(
        name=payload.name,
        slug=slug,
        short_description=payload.short_description or (payload.description[:120] if payload.description else None),
        description=payload.description,
        brand=payload.brand,
        primary_image=payload.primary_image,
        badge=payload.badge,
        customizable=payload.customizable,
        status="ACTIVE",
        metadata_json=payload.metadata_json,
    )

    # Attach categories with primary indication
    cat_ids = list(payload.category_ids)
    prim_id = payload.primary_category_id or (cat_ids[0] if cat_ids else None)
    if prim_id and prim_id not in cat_ids:
        cat_ids.append(prim_id)
    for idx, cid in enumerate(cat_ids):
        product.product_categories.append(
            ProductCategory(
                category_id=cid,
                is_primary=(cid == prim_id),
                display_order=idx,
            )
        )

    # Attach collections
    if payload.collection_ids:
        for idx, col_id in enumerate(payload.collection_ids):
            product.product_collections.append(
                ProductCollection(
                    collection_id=col_id,
                    display_order=idx,
                )
            )

    # Attach tags
    if payload.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
        product.tags.extend(tags)

    # Attach gallery images
    all_images = [payload.primary_image] + [img for img in payload.gallery_images if img != payload.primary_image]
    for idx, img_url in enumerate(all_images):
        product.images.append(
            ProductImage(
                url=img_url,
                sort_order=idx,
                is_primary=(idx == 0),
            )
        )

    # Attach variants
    if payload.variants:
        for v in payload.variants:
            existing_sku = db.query(ProductVariant).filter(ProductVariant.sku == v.sku).first()
            if existing_sku:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SKU '{v.sku}' is already in use by another product variant.",
                )
            product.variants.append(
                ProductVariant(
                    sku=v.sku,
                    name=v.name,
                    price=v.price,
                    compare_at_price=v.compare_at_price,
                    cost=v.cost,
                    stock_quantity=v.stock_quantity,
                    weight=v.weight,
                    status="ACTIVE",
                    attributes_json=v.attributes_json,
                )
            )
    else:
        # Default single variant
        product.variants.append(
            ProductVariant(
                sku=f"SKU-{slug.upper()[:10]}-DEF",
                name="Standard",
                price=999,
                stock_quantity=10,
                status="ACTIVE",
            )
        )

    db.add(product)
    db.commit()
    db.refresh(product)
    return _product_to_admin_out(product)


@router.get("/products/{product_id}", response_model=AdminProductOut)
def get_admin_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> AdminProductOut:
    """Retrieve full product details for administration."""
    product = (
        db.query(Product)
        .options(
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return _product_to_admin_out(product)


@router.patch("/products/{product_id}", response_model=AdminProductOut)
def update_product(
    product_id: int,
    payload: AdminProductUpdate,
    db: Session = Depends(get_db),
) -> AdminProductOut:
    """Update product fields, taxonomy associations, and images."""
    product = (
        db.query(Product)
        .options(
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if payload.name is not None:
        product.name = payload.name
    if payload.slug is not None:
        product.slug = payload.slug
    if payload.short_description is not None:
        product.short_description = payload.short_description
    if payload.description is not None:
        product.description = payload.description
    if payload.status is not None:
        product.status = payload.status
    if payload.brand is not None:
        product.brand = payload.brand
    if payload.primary_image is not None:
        product.primary_image = payload.primary_image
    if payload.badge is not None:
        product.badge = payload.badge
    if payload.customizable is not None:
        product.customizable = payload.customizable
    if payload.metadata_json is not None:
        product.metadata_json = payload.metadata_json

    if payload.category_ids is not None or payload.primary_category_id is not None:
        cat_ids = list(payload.category_ids) if payload.category_ids is not None else [c.id for c in product.categories]
        prim_id = payload.primary_category_id or (product.primary_category.id if product.primary_category else (cat_ids[0] if cat_ids else None))
        if prim_id and prim_id not in cat_ids:
            cat_ids.append(prim_id)
        product.product_categories.clear()
        for idx, cid in enumerate(cat_ids):
            product.product_categories.append(
                ProductCategory(
                    product_id=product.id,
                    category_id=cid,
                    is_primary=(cid == prim_id),
                    display_order=idx,
                )
            )

    if payload.collection_ids is not None:
        product.product_collections.clear()
        for idx, col_id in enumerate(payload.collection_ids):
            product.product_collections.append(
                ProductCollection(
                    product_id=product.id,
                    collection_id=col_id,
                    display_order=idx,
                )
            )

    if payload.tag_ids is not None:
        product.tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()

    if payload.gallery_images is not None:
        product.images.clear()
        all_imgs = [product.primary_image] + [url for url in payload.gallery_images if url != product.primary_image]
        for idx, url in enumerate(all_imgs):
            product.images.append(
                ProductImage(
                    url=url,
                    sort_order=idx,
                    is_primary=(idx == 0),
                )
            )

    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    return _product_to_admin_out(product)


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Soft delete product by transitioning its status to ARCHIVED."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.status = "ARCHIVED"
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok", "message": f"Product '{product.name}' archived successfully"}


# -----------------------------------------------------------------------------
# Variants & Inventory Management
# -----------------------------------------------------------------------------


@router.post("/products/{product_id}/variants", response_model=AdminVariantOut, status_code=status.HTTP_201_CREATED)
def create_variant(
    product_id: int,
    payload: AdminVariantCreate,
    db: Session = Depends(get_db),
) -> AdminVariantOut:
    """Add a new sellable variant to a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_sku = db.query(ProductVariant).filter(ProductVariant.sku == payload.sku).first()
    if existing_sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{payload.sku}' is already in use.")

    variant = ProductVariant(
        product_id=product_id,
        sku=payload.sku,
        name=payload.name,
        price=payload.price,
        compare_at_price=payload.compare_at_price,
        cost=payload.cost,
        stock_quantity=payload.stock_quantity,
        weight=payload.weight,
        status="ACTIVE",
        attributes_json=payload.attributes_json,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return _variant_to_admin_out(variant)


@router.patch("/variants/{variant_id}", response_model=AdminVariantOut)
def update_variant(
    variant_id: int,
    payload: AdminVariantUpdate,
    db: Session = Depends(get_db),
) -> AdminVariantOut:
    """Update variant details (price, compare_at_price, cost, name, sku, attributes)."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    if payload.sku is not None and payload.sku != variant.sku:
        existing = db.query(ProductVariant).filter(ProductVariant.sku == payload.sku).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{payload.sku}' is already in use.")
        variant.sku = payload.sku

    if payload.name is not None:
        variant.name = payload.name
    if payload.price is not None:
        variant.price = payload.price
    if payload.compare_at_price is not None:
        variant.compare_at_price = payload.compare_at_price
    if payload.cost is not None:
        variant.cost = payload.cost
    if payload.stock_quantity is not None:
        variant.stock_quantity = payload.stock_quantity
    if payload.weight is not None:
        variant.weight = payload.weight
    if payload.status is not None:
        variant.status = payload.status
    if payload.attributes_json is not None:
        variant.attributes_json = payload.attributes_json

    variant.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(variant)
    return _variant_to_admin_out(variant)


@router.patch("/variants/{variant_id}/inventory", response_model=AdminVariantOut)
def adjust_variant_inventory(
    variant_id: int,
    payload: AdminInventoryAdjustRequest,
    db: Session = Depends(get_db),
) -> AdminVariantOut:
    """Adjust variant inventory level by absolute amount or delta."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    if payload.stock_quantity is not None:
        variant.stock_quantity = payload.stock_quantity
    elif payload.adjustment is not None:
        new_quantity = variant.stock_quantity + payload.adjustment
        if new_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resulting stock quantity cannot be negative")
        variant.stock_quantity = new_quantity
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide stock_quantity or adjustment")

    variant.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(variant)
    return _variant_to_admin_out(variant)


@router.delete("/variants/{variant_id}")
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a variant if multiple variants exist on the product."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    db.delete(variant)
    db.commit()
    return {"status": "ok", "message": f"Variant '{variant.sku}' deleted successfully"}


# -----------------------------------------------------------------------------
# Categories Administration
# -----------------------------------------------------------------------------


@router.get("/categories", response_model=list[AdminCategoryOut])
def list_admin_categories(
    db: Session = Depends(get_db),
) -> list[AdminCategoryOut]:
    """List all categories for admin inspection including inactive and empty."""
    categories = db.query(Category).order_by(Category.display_order, Category.id).all()
    return [_category_to_admin_out(c) for c in categories]


@router.post("/categories", response_model=AdminCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: AdminCategoryCreate,
    db: Session = Depends(get_db),
) -> AdminCategoryOut:
    """Create a new taxonomy category."""
    slug = payload.slug or _slugify(payload.name)
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category slug '{slug}' is already taken.")

    if payload.parent_id is not None:
        parent = db.query(Category).filter(Category.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent category {payload.parent_id} does not exist.")

    category = Category(
        name=payload.name,
        slug=slug,
        parent_id=payload.parent_id,
        description=payload.description,
        image_key=payload.image_key,
        image=payload.image or payload.image_key,
        icon=payload.icon,
        display_order=payload.display_order,
        is_active=payload.is_active,
        show_when_empty=payload.show_when_empty,
        seo_title=payload.seo_title,
        seo_description=payload.seo_description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return _category_to_admin_out(category)


@router.patch("/categories/{category_id}", response_model=AdminCategoryOut)
def update_category(
    category_id: int,
    payload: AdminCategoryUpdate,
    db: Session = Depends(get_db),
) -> AdminCategoryOut:
    """Update taxonomy category details with cycle prevention."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if payload.parent_id is not None:
        if payload.parent_id == category.id or category.would_create_cycle(payload.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Moving category would create a circular parent reference.",
            )
        parent = db.query(Category).filter(Category.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent category {payload.parent_id} does not exist.")
        category.parent_id = payload.parent_id
    elif payload.parent_id is None and "parentId" in payload.model_fields_set:
        category.parent_id = None

    if payload.name is not None:
        category.name = payload.name
    if payload.slug is not None:
        category.slug = payload.slug
    if payload.description is not None:
        category.description = payload.description
    if payload.image_key is not None:
        category.image_key = payload.image_key
        category.image = payload.image_key
    elif payload.image is not None:
        category.image = payload.image
    if payload.icon is not None:
        category.icon = payload.icon
    if payload.display_order is not None:
        category.display_order = payload.display_order
    if payload.is_active is not None:
        category.is_active = payload.is_active
    if payload.show_when_empty is not None:
        category.show_when_empty = payload.show_when_empty
    if payload.seo_title is not None:
        category.seo_title = payload.seo_title
    if payload.seo_description is not None:
        category.seo_description = payload.seo_description

    category.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(category)
    return _category_to_admin_out(category)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Safe delete a taxonomy category rejecting if subcategories or products are attached."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    has_children = db.query(Category).filter(Category.parent_id == category.id).count() > 0
    if has_children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category '{category.name}' because it contains subcategories. Move or delete child categories first.",
        )

    has_products = len(category.products) > 0
    if has_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category '{category.name}' because products are assigned to it. Reassign products first.",
        )

    db.delete(category)
    db.commit()
    return {"status": "ok", "message": f"Category '{category.name}' deleted successfully"}


# -----------------------------------------------------------------------------
# Collections Administration
# -----------------------------------------------------------------------------


@router.get("/collections", response_model=list[AdminCollectionOut])
def list_admin_collections(
    db: Session = Depends(get_db),
) -> list[AdminCollectionOut]:
    """List all collections for store administration."""
    collections = db.query(Collection).order_by(Collection.display_order, Collection.id).all()
    return [_collection_to_admin_out(col) for col in collections]


@router.post("/collections", response_model=AdminCollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: AdminCollectionCreate,
    db: Session = Depends(get_db),
) -> AdminCollectionOut:
    """Create a new merchandising or evergreen collection."""
    slug = payload.slug or _slugify(payload.name)
    existing = db.query(Collection).filter(Collection.slug == slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection slug '{slug}' is already taken.")

    collection = Collection(
        name=payload.name,
        slug=slug,
        description=payload.description,
        image_key=payload.image_key,
        collection_type=payload.collection_type,
        display_order=payload.display_order,
        is_active=payload.is_active,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        seo_title=payload.seo_title,
        seo_description=payload.seo_description,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return _collection_to_admin_out(collection)


@router.get("/collections/{collection_id}", response_model=AdminCollectionOut)
def get_admin_collection(
    collection_id: int,
    db: Session = Depends(get_db),
) -> AdminCollectionOut:
    """Get single collection by ID."""
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return _collection_to_admin_out(col)


@router.patch("/collections/{collection_id}", response_model=AdminCollectionOut)
def update_collection(
    collection_id: int,
    payload: AdminCollectionUpdate,
    db: Session = Depends(get_db),
) -> AdminCollectionOut:
    """Update collection fields."""
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    if payload.name is not None:
        col.name = payload.name
    if payload.slug is not None:
        col.slug = payload.slug
    if payload.description is not None:
        col.description = payload.description
    if payload.image_key is not None:
        col.image_key = payload.image_key
    if payload.collection_type is not None:
        col.collection_type = payload.collection_type
    if payload.display_order is not None:
        col.display_order = payload.display_order
    if payload.is_active is not None:
        col.is_active = payload.is_active
    if payload.starts_at is not None:
        col.starts_at = payload.starts_at
    if payload.ends_at is not None:
        col.ends_at = payload.ends_at
    if payload.seo_title is not None:
        col.seo_title = payload.seo_title
    if payload.seo_description is not None:
        col.seo_description = payload.seo_description

    col.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(col)
    return _collection_to_admin_out(col)


@router.delete("/collections/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a collection and detach associated products."""
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    db.query(ProductCollection).filter(ProductCollection.collection_id == collection_id).delete()
    db.delete(col)
    db.commit()
    return {"status": "ok", "message": f"Collection '{col.name}' deleted successfully"}


@router.post("/collections/{collection_id}/products")
def assign_collection_products(
    collection_id: int,
    payload: AdminCollectionAssignProducts,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Assign products to a collection, replacing existing memberships."""
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    db.query(ProductCollection).filter(ProductCollection.collection_id == collection_id).delete()
    for idx, pid in enumerate(payload.product_ids):
        db.add(ProductCollection(collection_id=collection_id, product_id=pid, display_order=idx))

    col.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok", "collectionId": collection_id, "productCount": len(payload.product_ids)}


# -----------------------------------------------------------------------------
# Orders Administration & Lifecycle Transitions
# -----------------------------------------------------------------------------


@router.get("/orders", response_model=AdminOrderListOut)
def list_admin_orders(
    status: str | None = Query(default=None, description="Filter by OrderStatus"),
    payment_status: str | None = Query(default=None, alias="paymentStatus", description="Filter by PaymentStatus"),
    from_date: str | None = Query(default=None, alias="from", description="Filter from date (YYYY-MM-DD)"),
    to_date: str | None = Query(default=None, alias="to", description="Filter to date (YYYY-MM-DD)"),
    country: str | None = Query(default=None, description="Filter by shipping country"),
    min_total: int | None = Query(default=None, alias="minTotal", ge=0, description="Minimum order total in rupees"),
    max_total: int | None = Query(default=None, alias="maxTotal", ge=0, description="Maximum order total in rupees"),
    sku: str | None = Query(default=None, description="Filter orders containing variant SKU"),
    sort_by: str = Query(
        default="created_at_desc",
        alias="sortBy",
        description="Sort by: created_at_desc, created_at_asc, total_desc, total_asc, order_number_asc, order_number_desc",
    ),
    q: str | None = Query(default=None, description="Search by orderNumber, customer name, email, or phone"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminOrderListOut:
    """List all orders across customers with date, status, country, price, SKU filters, and sorting."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
    )

    if status:
        query = query.filter(Order.status == status)

    if payment_status:
        query = query.filter(Order.payment_status == payment_status)

    if from_date or to_date:
        from_utc, to_utc, _, _ = _parse_ist_date_range(from_date, to_date)
        if from_date:
            query = query.filter(Order.created_at >= from_utc)
        if to_date:
            query = query.filter(Order.created_at <= to_utc)

    if min_total is not None:
        query = query.filter(Order.total_amount >= min_total)

    if max_total is not None:
        query = query.filter(Order.total_amount <= max_total)

    if country:
        query = query.filter(
            func.lower(func.coalesce(sa.cast(Order.shipping_address_json, sa.String), "")).contains(country.lower())
        )

    if sku:
        query = query.filter(Order.items.any(OrderItem.sku.ilike(f"%{sku.strip()}%")))

    if q:
        search_fmt = f"%{q.strip()}%"
        query = query.filter(
            (Order.order_number.ilike(search_fmt))
            | (Order.customer_name.ilike(search_fmt))
            | (Order.customer_phone.ilike(search_fmt))
            | (Order.customer_email.ilike(search_fmt))
        )

    # Sorting
    if sort_by == "created_at_asc":
        query = query.order_by(Order.created_at.asc())
    elif sort_by == "total_desc":
        query = query.order_by(Order.total_amount.desc())
    elif sort_by == "total_asc":
        query = query.order_by(Order.total_amount.asc())
    elif sort_by == "order_number_asc":
        query = query.order_by(Order.order_number.asc())
    elif sort_by == "order_number_desc":
        query = query.order_by(Order.order_number.desc())
    else:
        query = query.order_by(Order.created_at.desc())

    total = query.distinct().count()
    orders = (
        query.distinct()
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AdminOrderListOut(
        items=[_order_to_admin_detail(o) for o in orders],
        total=total,
        page=page,
        pageSize=page_size,
    )


@router.get("/orders/{order_number_or_id}", response_model=AdminOrderDetailOut)
def get_admin_order(
    order_number_or_id: str,
    db: Session = Depends(get_db),
) -> AdminOrderDetailOut:
    """Retrieve full order details for administrative inspection."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
    )
    if order_number_or_id.isdigit():
        order = query.filter((Order.id == int(order_number_or_id)) | (Order.order_number == order_number_or_id)).first()
    else:
        order = query.filter(Order.order_number == order_number_or_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return _order_to_admin_detail(order)


@router.patch("/orders/{order_number_or_id}/status", response_model=AdminOrderDetailOut)
def update_order_status(
    order_number_or_id: str,
    payload: AdminOrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AdminOrderDetailOut:
    """Transition order status, update courier tracking info, and restore inventory if cancelled."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
    )
    if order_number_or_id.isdigit():
        order = query.filter((Order.id == int(order_number_or_id)) | (Order.order_number == order_number_or_id)).first()
    else:
        order = query.filter(Order.order_number == order_number_or_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Validate target status against known OrderStatus values
    valid_statuses = {s.value for s in OrderStatus}
    target_status = payload.status.upper().strip()
    if target_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Must be one of: {sorted(list(valid_statuses))}",
        )

    previous_status = order.status
    order.status = target_status

    if payload.tracking_number is not None:
        order.tracking_number = payload.tracking_number
    if payload.courier_name is not None:
        order.courier_name = payload.courier_name

    # If transitioning to SHIPPED and no courier set, allow tracking
    if target_status == OrderStatus.SHIPPED.value and not order.courier_name:
        order.courier_name = "Bluedart / Delhivery"

    # If transitioning to CANCELLED and was not already cancelled, restore inventory
    if target_status == OrderStatus.CANCELLED.value and previous_status != OrderStatus.CANCELLED.value:
        for item in order.items:
            if item.product_variant_id:
                variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
                if variant:
                    variant.stock_quantity += item.quantity

    note = payload.note or f"Order status updated from {previous_status} to {target_status} by admin"
    history_entry = OrderStatusHistory(
        order_id=order.id,
        status=target_status,
        note=note,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(history_entry)
    order.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order)
    background_tasks.add_task(
        dispatch_order_status_background,
        order.id,
        target_status,
        order.courier_name,
        order.tracking_number,
    )
    return _order_to_admin_detail(order)


# -----------------------------------------------------------------------------
# Store Analytics & KPI Dashboard
# -----------------------------------------------------------------------------


@router.get("/analytics", response_model=AdminAnalyticsOut)
def get_admin_analytics(
    db: Session = Depends(get_db),
) -> AdminAnalyticsOut:
    """Aggregate business KPIs, sales revenue, low stock alerts, and top products."""
    # 1. Orders count & status breakdown
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value, OrderStatus.READY_TO_SHIP.value])
    ).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED.value).count()
    cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED.value).count()

    # 2. Revenue calculation (paid or confirmed/shipped/delivered non-cancelled orders)
    revenue_sum = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(
            (Order.payment_status == PaymentStatus.PAID.value)
            | (Order.status.in_([
                OrderStatus.CONFIRMED.value,
                OrderStatus.PROCESSING.value,
                OrderStatus.READY_TO_SHIP.value,
                OrderStatus.SHIPPED.value,
                OrderStatus.OUT_FOR_DELIVERY.value,
                OrderStatus.DELIVERED.value,
            ]))
        )
        .scalar()
        or 0
    )

    # 3. Customer & product totals
    total_customers = db.query(User).filter(User.role == "CUSTOMER").count()
    total_products = db.query(Product).filter(Product.status == "ACTIVE").count()

    # 4. Low stock inventory alerts (<=5)
    low_stock_variants = (
        db.query(ProductVariant)
        .options(joinedload(ProductVariant.product))
        .filter(ProductVariant.stock_quantity <= 5, ProductVariant.status == "ACTIVE")
        .all()
    )
    low_stock_items = [
        AdminLowStockItem(
            variantId=v.id,
            productId=v.product_id,
            productName=v.product.name if v.product else "Unknown Product",
            sku=v.sku,
            variantName=v.name,
            stockQuantity=v.stock_quantity,
        )
        for v in low_stock_variants
    ]

    # 5. Recent 5 orders
    recent_orders = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.status_history))
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    # 6. Top selling products
    top_selling_raw = (
        db.query(
            OrderItem.product_id,
            OrderItem.product_name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("total_sold"),
            func.coalesce(func.sum(OrderItem.line_total), 0).label("total_revenue"),
        )
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    top_selling_products = [
        AdminTopSellingProduct(
            productId=r[0] or 0,
            productName=r[1],
            totalSold=int(r[2]),
            totalRevenue=int(r[3]),
            totalRevenuePaise=int(r[3]) * 100,
        )
        for r in top_selling_raw
    ]

    return AdminAnalyticsOut(
        totalRevenue=int(revenue_sum),
        totalRevenuePaise=int(revenue_sum) * 100,
        totalOrders=total_orders,
        pendingOrders=pending_orders,
        deliveredOrders=delivered_orders,
        cancelledOrders=cancelled_orders,
        totalCustomers=total_customers,
        totalProducts=total_products,
        lowStockCount=len(low_stock_items),
        lowStockItems=low_stock_items,
        recentOrders=[_order_to_admin_detail(o) for o in recent_orders],
        topSellingProducts=top_selling_products,
    )


# -----------------------------------------------------------------------------
# Dashboard Analytics & Sales Series
# -----------------------------------------------------------------------------


def _compute_attention_count(db: Session) -> int:
    """Return count of actionable items requiring admin attention."""
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff_48h = now_utc - timedelta(hours=48)
    cutoff_24h = now_utc - timedelta(hours=24)

    unshipped = (
        db.query(Order)
        .filter(
            Order.status.in_([OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value, OrderStatus.READY_TO_SHIP.value]),
            Order.created_at <= cutoff_48h,
        )
        .count()
    )
    stale_pay = (
        db.query(Order)
        .filter(Order.status == OrderStatus.PENDING_PAYMENT.value, Order.created_at <= cutoff_24h)
        .count()
    )
    pending_returns = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.status == ReturnStatus.REQUESTED.value)
        .count()
    )
    low_stock = (
        db.query(ProductVariant)
        .filter(ProductVariant.stock_quantity <= 2, ProductVariant.status == "ACTIVE")
        .count()
    )
    return unshipped + stale_pay + pending_returns + low_stock


def _gather_attention_items(db: Session) -> list[AdminAttentionItem]:
    """Gather and prioritize all actionable attention items from real data."""
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff_48h = now_utc - timedelta(hours=48)
    cutoff_24h = now_utc - timedelta(hours=24)
    items: list[AdminAttentionItem] = []

    # 1. Unshipped orders > 48h
    unshipped = (
        db.query(Order)
        .filter(
            Order.status.in_([OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value, OrderStatus.READY_TO_SHIP.value]),
            Order.created_at <= cutoff_48h,
        )
        .order_by(Order.created_at.asc())
        .all()
    )
    for o in unshipped:
        hours = int((now_utc - o.created_at).total_seconds() // 3600)
        items.append(
            AdminAttentionItem(
                id=f"att_unshipped_{o.id}",
                severity="HIGH",
                rule="unshipped_over_48h",
                title=f"Order {o.order_number} unshipped for {hours}h",
                message=f"Order placed by {o.customer_name} is awaiting fulfillment/shipping.",
                orderNumber=o.order_number,
                orderId=o.id,
                createdAt=o.created_at,
                actionUrl=f"/admin/orders/{o.order_number}",
            )
        )

    # 2. Stale pending payments > 24h
    stale_pay = (
        db.query(Order)
        .filter(Order.status == OrderStatus.PENDING_PAYMENT.value, Order.created_at <= cutoff_24h)
        .order_by(Order.created_at.asc())
        .all()
    )
    for o in stale_pay:
        items.append(
            AdminAttentionItem(
                id=f"att_pending_pay_{o.id}",
                severity="WARNING",
                rule="stale_pending_payment",
                title=f"Pending payment on order {o.order_number}",
                message=f"Order payment has remained pending for over 24 hours.",
                orderNumber=o.order_number,
                orderId=o.id,
                createdAt=o.created_at,
                actionUrl=f"/admin/orders/{o.order_number}",
            )
        )

    # 3. Pending return reviews
    pending_returns = (
        db.query(ReturnRequest)
        .options(joinedload(ReturnRequest.order))
        .filter(ReturnRequest.status == ReturnStatus.REQUESTED.value)
        .order_by(ReturnRequest.created_at.asc())
        .all()
    )
    for r in pending_returns:
        items.append(
            AdminAttentionItem(
                id=f"att_return_{r.id}",
                severity="HIGH",
                rule="pending_return_review",
                title=f"Return request {r.return_number} awaiting review",
                message=f"Customer requested return for '{r.reason}'. Review and decide action.",
                orderNumber=r.order.order_number if r.order else None,
                orderId=r.order_id,
                createdAt=r.created_at,
                actionUrl=f"/admin/returns/{r.return_number}",
            )
        )

    # 4. Critical low stock
    critical_stock = (
        db.query(ProductVariant)
        .options(joinedload(ProductVariant.product))
        .filter(ProductVariant.stock_quantity <= 2, ProductVariant.status == "ACTIVE")
        .order_by(ProductVariant.stock_quantity.asc())
        .all()
    )
    for v in critical_stock:
        sev = "CRITICAL" if v.stock_quantity == 0 else "WARNING"
        items.append(
            AdminAttentionItem(
                id=f"att_stock_{v.id}",
                severity=sev,
                rule="critical_low_stock",
                title=f"Low stock: {v.sku} ({v.stock_quantity} left)",
                message=f"Product '{v.product.name if v.product else 'Product'}' variant '{v.name}' has low inventory.",
                variantId=v.id,
                productId=v.product_id,
                createdAt=v.updated_at,
                actionUrl=f"/admin/products/{v.product_id}",
            )
        )

    return items


def _build_sales_buckets(
    eff_from: str,
    eff_to: str,
    interval: str,
    orders: list[Order],
) -> list[AdminSalesBucket]:
    """Generate calendar buckets in IST with zero-filled gaps."""
    from_d = datetime.strptime(eff_from, "%Y-%m-%d").date()
    to_d = datetime.strptime(eff_to, "%Y-%m-%d").date()

    orders_by_date: dict[str, list[Order]] = {}
    for o in orders:
        if o.created_at:
            o_ist = o.created_at.replace(tzinfo=timezone.utc).astimezone(IST)
            key = o_ist.date().isoformat()
            orders_by_date.setdefault(key, []).append(o)

    buckets: list[AdminSalesBucket] = []

    if interval == "monthly":
        curr = datetime(from_d.year, from_d.month, 1).date()
        while curr <= to_d:
            key_prefix = curr.strftime("%Y-%m")
            matching_orders = [
                o for d_str, o_list in orders_by_date.items() if d_str.startswith(key_prefix) for o in o_list
            ]
            sales = sum(o.total_amount for o in matching_orders)
            ts = datetime(curr.year, curr.month, 1, 0, 0, 0, tzinfo=IST).isoformat()
            buckets.append(
                AdminSalesBucket(
                    date=key_prefix,
                    timestamp=ts,
                    sales=sales,
                    salesPaise=sales * 100,
                    orderCount=len(matching_orders),
                )
            )
            if curr.month == 12:
                curr = datetime(curr.year + 1, 1, 1).date()
            else:
                curr = datetime(curr.year, curr.month + 1, 1).date()
    elif interval == "weekly":
        curr = from_d
        while curr <= to_d:
            week_end = min(curr + timedelta(days=6), to_d)
            matching_orders = []
            d_walk = curr
            while d_walk <= week_end:
                matching_orders.extend(orders_by_date.get(d_walk.isoformat(), []))
                d_walk += timedelta(days=1)
            sales = sum(o.total_amount for o in matching_orders)
            ts = datetime(curr.year, curr.month, curr.day, 0, 0, 0, tzinfo=IST).isoformat()
            buckets.append(
                AdminSalesBucket(
                    date=curr.isoformat(),
                    timestamp=ts,
                    sales=sales,
                    salesPaise=sales * 100,
                    orderCount=len(matching_orders),
                )
            )
            curr += timedelta(days=7)
    else:  # daily
        curr = from_d
        while curr <= to_d:
            matching_orders = orders_by_date.get(curr.isoformat(), [])
            sales = sum(o.total_amount for o in matching_orders)
            ts = datetime(curr.year, curr.month, curr.day, 0, 0, 0, tzinfo=IST).isoformat()
            buckets.append(
                AdminSalesBucket(
                    date=curr.isoformat(),
                    timestamp=ts,
                    sales=sales,
                    salesPaise=sales * 100,
                    orderCount=len(matching_orders),
                )
            )
            curr += timedelta(days=1)

    return buckets


def _build_finance_buckets(
    eff_from: str,
    eff_to: str,
    interval: str,
    orders: list[Order],
    returns: list[ReturnRequest],
) -> list[AdminFinanceSalesBucket]:
    """Generate finance buckets in IST reconciling to summary totals."""
    from_d = datetime.strptime(eff_from, "%Y-%m-%d").date()
    to_d = datetime.strptime(eff_to, "%Y-%m-%d").date()

    orders_by_date: dict[str, list[Order]] = {}
    for o in orders:
        if o.created_at:
            o_ist = o.created_at.replace(tzinfo=timezone.utc).astimezone(IST)
            key = o_ist.date().isoformat()
            orders_by_date.setdefault(key, []).append(o)

    returns_by_date: dict[str, list[ReturnRequest]] = {}
    for r in returns:
        dt = r.updated_at or r.created_at
        if dt:
            r_ist = dt.replace(tzinfo=timezone.utc).astimezone(IST)
            key = r_ist.date().isoformat()
            returns_by_date.setdefault(key, []).append(r)

    buckets: list[AdminFinanceSalesBucket] = []

    curr = from_d
    step_days = 7 if interval == "weekly" else 1

    while curr <= to_d:
        if interval == "monthly":
            key_prefix = curr.strftime("%Y-%m")
            b_orders = [o for d_str, o_list in orders_by_date.items() if d_str.startswith(key_prefix) for o in o_list]
            b_returns = [r for d_str, r_list in returns_by_date.items() if d_str.startswith(key_prefix) for r in r_list]
            ts = datetime(curr.year, curr.month, 1, 0, 0, 0, tzinfo=IST).isoformat()
            label = key_prefix
        else:
            end_step = min(curr + timedelta(days=step_days - 1), to_d)
            b_orders = []
            b_returns = []
            d_walk = curr
            while d_walk <= end_step:
                b_orders.extend(orders_by_date.get(d_walk.isoformat(), []))
                b_returns.extend(returns_by_date.get(d_walk.isoformat(), []))
                d_walk += timedelta(days=1)
            ts = datetime(curr.year, curr.month, curr.day, 0, 0, 0, tzinfo=IST).isoformat()
            label = curr.isoformat()

        gross = sum(o.subtotal + o.discount_amount for o in b_orders)
        discounts = sum(o.discount_amount for o in b_orders)
        refunds = sum(r.refund_amount for r in b_returns)
        shipping = sum(o.shipping_fee for o in b_orders)
        tax = sum(o.tax_amount for o in b_orders)
        net = gross - discounts + shipping + tax - refunds

        buckets.append(
            AdminFinanceSalesBucket(
                date=label,
                timestamp=ts,
                grossSales=gross,
                discounts=discounts,
                refunds=refunds,
                netRevenue=net,
                orderCount=len(b_orders),
            )
        )

        if interval == "monthly":
            if curr.month == 12:
                curr = datetime(curr.year + 1, 1, 1).date()
            else:
                curr = datetime(curr.year, curr.month + 1, 1).date()
        else:
            curr += timedelta(days=step_days)

    return buckets


@router.get("/dashboard/summary", response_model=AdminDashboardSummaryOut)
def get_admin_dashboard_summary(
    from_date: str | None = Query(default=None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(default=None, alias="to", description="End date (YYYY-MM-DD)"),
    compare_from: str | None = Query(default=None, alias="compareFrom", description="Comparison start date"),
    compare_to: str | None = Query(default=None, alias="compareTo", description="Comparison end date"),
    db: Session = Depends(get_db),
) -> AdminDashboardSummaryOut:
    """Aggregate business KPIs, net revenue, status counts, recent orders, and stock alerts."""
    from_utc, to_utc, eff_from, eff_to = _parse_ist_date_range(from_date, to_date)

    orders_query = (
        db.query(Order)
        .filter(Order.created_at >= from_utc, Order.created_at <= to_utc)
    )

    all_orders = orders_query.all()
    order_count = len(all_orders)

    eligible_orders = [o for o in all_orders if o.status != OrderStatus.CANCELLED.value]
    total_sales = sum(o.total_amount for o in eligible_orders)

    refunds_sum = (
        db.query(func.coalesce(func.sum(ReturnRequest.refund_amount), 0))
        .filter(
            ReturnRequest.refund_status == RefundStatus.COMPLETED.value,
            ReturnRequest.updated_at >= from_utc,
            ReturnRequest.updated_at <= to_utc,
        )
        .scalar()
        or 0
    )

    net_revenue = max(0, total_sales - int(refunds_sum))
    aov = round(total_sales / order_count, 2) if order_count > 0 else 0.0

    status_counts = {st.value: 0 for st in OrderStatus}
    for o in all_orders:
        if o.status in status_counts:
            status_counts[o.status] += 1

    comparison = None
    if compare_from and compare_to:
        comp_from_utc, comp_to_utc, _, _ = _parse_ist_date_range(compare_from, compare_to)
        prev_orders = (
            db.query(Order)
            .filter(Order.created_at >= comp_from_utc, Order.created_at <= comp_to_utc)
            .all()
        )
        prev_count = len(prev_orders)
        prev_sales = sum(o.total_amount for o in prev_orders if o.status != OrderStatus.CANCELLED.value)

        sales_growth = round(((total_sales - prev_sales) / prev_sales) * 100, 2) if prev_sales > 0 else None
        order_growth = round(((order_count - prev_count) / prev_count) * 100, 2) if prev_count > 0 else None

        comparison = AdminDashboardComparison(
            previousTotalSales=prev_sales,
            previousTotalSalesPaise=prev_sales * 100,
            previousOrderCount=prev_count,
            salesGrowthPercent=sales_growth,
            orderGrowthPercent=order_growth,
        )

    recent_orders = (
        orders_query
        .options(joinedload(Order.items), joinedload(Order.status_history))
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    )

    low_stock_variants = (
        db.query(ProductVariant)
        .options(joinedload(ProductVariant.product))
        .filter(ProductVariant.stock_quantity <= 5, ProductVariant.status == "ACTIVE")
        .all()
    )
    low_stock_items = [
        AdminLowStockItem(
            variantId=v.id,
            productId=v.product_id,
            productName=v.product.name if v.product else "Unknown Product",
            sku=v.sku,
            variantName=v.name,
            stockQuantity=v.stock_quantity,
        )
        for v in low_stock_variants
    ]

    attention_count = _compute_attention_count(db)

    return AdminDashboardSummaryOut(
        effectiveRange={"from": eff_from, "to": eff_to},
        totalSales=total_sales,
        totalSalesPaise=total_sales * 100,
        netRevenue=net_revenue,
        netRevenuePaise=net_revenue * 100,
        orderCount=order_count,
        averageOrderValue=aov,
        averageOrderValuePaise=int(aov * 100),
        comparison=comparison,
        statusCounts=status_counts,
        recentOrders=[_order_to_admin_detail(o) for o in recent_orders],
        inventoryAlerts={
            "lowStockCount": len(low_stock_items),
            "lowStockItems": low_stock_items,
        },
        attentionCount=attention_count,
    )


@router.get("/dashboard/sales", response_model=AdminSalesSeriesOut)
def get_admin_dashboard_sales(
    from_date: str | None = Query(default=None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(default=None, alias="to", description="End date (YYYY-MM-DD)"),
    interval: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
) -> AdminSalesSeriesOut:
    """Return ordered sales time series buckets with zero-filled gaps in Asia/Kolkata timezone."""
    from_utc, to_utc, eff_from, eff_to = _parse_ist_date_range(from_date, to_date)
    orders = (
        db.query(Order)
        .filter(
            Order.created_at >= from_utc,
            Order.created_at <= to_utc,
            Order.status != OrderStatus.CANCELLED.value,
        )
        .order_by(Order.created_at.asc())
        .all()
    )

    buckets = _build_sales_buckets(eff_from, eff_to, interval, orders)
    return AdminSalesSeriesOut(
        interval=interval,
        effectiveRange={"from": eff_from, "to": eff_to},
        buckets=buckets,
    )


@router.get("/dashboard/attention", response_model=AdminAttentionListOut)
def get_admin_attention(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminAttentionListOut:
    """Retrieve actionable items requiring administrator intervention."""
    items = _gather_attention_items(db)
    total = len(items)
    paged = items[(page - 1) * page_size : page * page_size]
    return AdminAttentionListOut(items=paged, total=total, page=page, pageSize=page_size)


# -----------------------------------------------------------------------------
# Finance Summary & Breakdown
# -----------------------------------------------------------------------------


@router.get("/finance/summary", response_model=AdminFinanceSummaryOut)
def get_admin_finance_summary(
    from_date: str | None = Query(default=None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(default=None, alias="to", description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> AdminFinanceSummaryOut:
    """Financial accounting summary reconciling gross sales, discounts, shipping, stored tax, and refunds."""
    from_utc, to_utc, eff_from, eff_to = _parse_ist_date_range(from_date, to_date)

    orders = (
        db.query(Order)
        .filter(Order.created_at >= from_utc, Order.created_at <= to_utc, Order.status != OrderStatus.CANCELLED.value)
        .all()
    )

    gross_sales = sum(o.subtotal + o.discount_amount for o in orders)
    discounts = sum(o.discount_amount for o in orders)
    shipping_collected = sum(o.shipping_fee for o in orders)
    stored_tax = sum(o.tax_amount for o in orders)

    completed_returns = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.refund_status == RefundStatus.COMPLETED.value,
            ReturnRequest.updated_at >= from_utc,
            ReturnRequest.updated_at <= to_utc,
        )
        .all()
    )
    refunds = sum(r.refund_amount for r in completed_returns)
    refund_count = len(completed_returns)

    net_revenue = gross_sales - discounts + shipping_collected + stored_tax - refunds
    taxable_sales = gross_sales - discounts

    return AdminFinanceSummaryOut(
        effectiveRange={"from": eff_from, "to": eff_to},
        grossSales=gross_sales,
        grossSalesPaise=gross_sales * 100,
        discounts=discounts,
        discountsPaise=discounts * 100,
        shippingCollected=shipping_collected,
        shippingCollectedPaise=shipping_collected * 100,
        storedTax=stored_tax,
        storedTaxPaise=stored_tax * 100,
        refunds=refunds,
        refundsPaise=refunds * 100,
        gatewayFees=None,
        gatewayFeesAvailable=False,
        adjustments=0,
        adjustmentsPaise=0,
        netRevenue=net_revenue,
        netRevenuePaise=net_revenue * 100,
        taxableSales=taxable_sales,
        taxableSalesPaise=taxable_sales * 100,
        orderCount=len(orders),
        refundCount=refund_count,
    )


@router.get("/finance/sales", response_model=AdminFinanceSeriesOut)
def get_admin_finance_sales(
    from_date: str | None = Query(default=None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(default=None, alias="to", description="End date (YYYY-MM-DD)"),
    interval: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
) -> AdminFinanceSeriesOut:
    """Finance trend series reconciling with summary."""
    from_utc, to_utc, eff_from, eff_to = _parse_ist_date_range(from_date, to_date)
    orders = (
        db.query(Order)
        .filter(
            Order.created_at >= from_utc,
            Order.created_at <= to_utc,
            Order.status != OrderStatus.CANCELLED.value,
        )
        .order_by(Order.created_at.asc())
        .all()
    )
    returns = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.refund_status == RefundStatus.COMPLETED.value,
            ReturnRequest.updated_at >= from_utc,
            ReturnRequest.updated_at <= to_utc,
        )
        .all()
    )

    buckets = _build_finance_buckets(eff_from, eff_to, interval, orders, returns)
    return AdminFinanceSeriesOut(
        interval=interval,
        effectiveRange={"from": eff_from, "to": eff_to},
        buckets=buckets,
    )


# -----------------------------------------------------------------------------
# Global Admin Search
# -----------------------------------------------------------------------------


@router.get("/search", response_model=AdminGlobalSearchOut)
def admin_global_search(
    q: str = Query(..., min_length=1, description="Search term for order, product, variant, or customer"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminGlobalSearchOut:
    """Global admin search across orders, products, variants, and customers."""
    term = f"%{q.strip()}%"
    results: list[AdminSearchResultItem] = []

    # 1. Orders
    orders = (
        db.query(Order)
        .filter(
            (Order.order_number.ilike(term))
            | (Order.customer_name.ilike(term))
            | (Order.customer_email.ilike(term))
            | (Order.customer_phone.ilike(term))
        )
        .limit(20)
        .all()
    )
    for o in orders:
        results.append(
            AdminSearchResultItem(
                kind="order",
                id=str(o.id),
                title=f"Order {o.order_number}",
                subtitle=f"{o.customer_name} • ₹{o.total_amount} • {o.status}",
                badge=o.status,
                url=f"/admin/orders/{o.order_number}",
                metadata={"orderNumber": o.order_number, "totalAmount": o.total_amount, "phone": o.customer_phone},
            )
        )

    # 2. Products
    products = (
        db.query(Product)
        .filter((Product.name.ilike(term)) | (Product.slug.ilike(term)) | (Product.brand.ilike(term)))
        .limit(20)
        .all()
    )
    for p in products:
        results.append(
            AdminSearchResultItem(
                kind="product",
                id=str(p.id),
                title=p.name,
                subtitle=f"{p.brand or 'Sulocraft'} • {p.status}",
                badge=p.badge or p.status,
                url=f"/admin/products/{p.id}",
                metadata={"slug": p.slug, "primaryImage": p.primary_image},
            )
        )

    # 3. Variants
    variants = (
        db.query(ProductVariant)
        .options(joinedload(ProductVariant.product))
        .filter((ProductVariant.sku.ilike(term)) | (ProductVariant.name.ilike(term)))
        .limit(20)
        .all()
    )
    for v in variants:
        results.append(
            AdminSearchResultItem(
                kind="variant",
                id=str(v.id),
                title=f"SKU: {v.sku}",
                subtitle=f"{v.product.name if v.product else ''} - {v.name} • Stock: {v.stock_quantity}",
                badge=f"₹{v.price}",
                url=f"/admin/products/{v.product_id}",
                metadata={"sku": v.sku, "productId": v.product_id, "stockQuantity": v.stock_quantity},
            )
        )

    # 4. Customers
    users = (
        db.query(User)
        .filter(
            (User.name.ilike(term))
            | (User.email.ilike(term))
            | (User.phone.ilike(term))
        )
        .limit(20)
        .all()
    )
    for u in users:
        results.append(
            AdminSearchResultItem(
                kind="customer",
                id=str(u.id),
                title=u.name or "Customer",
                subtitle=f"{u.email or ''} • {u.phone or ''}",
                badge=u.role,
                url=f"/admin/customers/{u.id}",
                metadata={"email": u.email, "phone": u.phone},
            )
        )

    total = len(results)
    paged = results[(page - 1) * page_size : page * page_size]
    return AdminGlobalSearchOut(query=q, total=total, items=paged, page=page, pageSize=page_size)


# -----------------------------------------------------------------------------
# Returns & Refunds Administration
# -----------------------------------------------------------------------------


@router.get("/returns", response_model=AdminReturnListOut)
def list_admin_returns(
    status: str | None = Query(default=None, description="Filter by ReturnStatus"),
    order_number: str | None = Query(default=None, alias="orderNumber", description="Filter by order number"),
    order_num_alt: str | None = Query(default=None, alias="order_number", include_in_schema=False),
    from_date: str | None = Query(default=None, alias="from", description="Filter from date"),
    to_date: str | None = Query(default=None, alias="to", description="Filter to date"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminReturnListOut:
    """List return requests with status, order, and date filters."""
    query = db.query(ReturnRequest).options(joinedload(ReturnRequest.order))

    if status:
        query = query.filter(ReturnRequest.status == status)

    target_order_num = order_number or order_num_alt
    if target_order_num:
        query = query.filter(ReturnRequest.order.has(Order.order_number.ilike(f"%{target_order_num.strip()}%")))

    if from_date or to_date:
        from_utc, to_utc, _, _ = _parse_ist_date_range(from_date, to_date)
        if from_date:
            query = query.filter(ReturnRequest.created_at >= from_utc)
        if to_date:
            query = query.filter(ReturnRequest.created_at <= to_utc)

    total = query.count()
    returns = (
        query.order_by(ReturnRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AdminReturnListOut(
        items=[_return_to_admin_out(r) for r in returns],
        total=total,
        page=page,
        pageSize=page_size,
    )


@router.get("/returns/{return_id_or_number}", response_model=AdminReturnDetailOut)
def get_admin_return(
    return_id_or_number: str,
    db: Session = Depends(get_db),
) -> AdminReturnDetailOut:
    """Retrieve full details of a specific return request."""
    ret = (
        db.query(ReturnRequest)
        .options(joinedload(ReturnRequest.order))
        .filter(
            (ReturnRequest.return_number == return_id_or_number)
            | (ReturnRequest.id == int(return_id_or_number) if return_id_or_number.isdigit() else False)
        )
        .first()
    )
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return request not found")
    return _return_to_admin_out(ret)


@router.post("/returns", response_model=AdminReturnDetailOut, status_code=status.HTTP_201_CREATED)
def create_admin_return(
    payload: AdminReturnCreateIn,
    db: Session = Depends(get_db),
) -> AdminReturnDetailOut:
    """Create a return request for an order."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.order_number == payload.order_number)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{payload.order_number}' not found")

    items_to_return = []
    total_refund = 0
    order_items_by_id = {item.id: item for item in order.items}

    if payload.items:
        for it in payload.items:
            order_item = order_items_by_id.get(it.order_item_id)
            if not order_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order item ID {it.order_item_id} does not belong to order {order.order_number}",
                )
            qty = min(it.quantity, order_item.quantity)
            line_tot = order_item.unit_price * qty
            items_to_return.append({
                "order_item_id": order_item.id,
                "product_name": order_item.product_name,
                "sku": order_item.sku,
                "quantity": qty,
                "unit_price": order_item.unit_price,
                "line_total": line_tot,
            })
            total_refund += line_tot
    else:
        for order_item in order.items:
            items_to_return.append({
                "order_item_id": order_item.id,
                "product_name": order_item.product_name,
                "sku": order_item.sku,
                "quantity": order_item.quantity,
                "unit_price": order_item.unit_price,
                "line_total": order_item.line_total,
            })
            total_refund += order_item.line_total

    return_num = f"RET-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
    new_return = ReturnRequest(
        return_number=return_num,
        order_id=order.id,
        user_id=order.user_id,
        status=ReturnStatus.REQUESTED.value,
        reason=payload.reason,
        reason_details=payload.reason_details,
        items_json=items_to_return,
        refund_amount=total_refund,
        refund_amount_paise=total_refund * 100,
        refund_status=RefundStatus.PENDING.value,
        admin_notes=payload.admin_notes,
        history_json=[{
            "status": ReturnStatus.REQUESTED.value,
            "actor": "admin",
            "note": f"Return created for order {order.order_number} (reason: {payload.reason})",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    )
    db.add(new_return)
    db.commit()
    db.refresh(new_return)
    return _return_to_admin_out(new_return)


@router.patch("/returns/{return_id_or_number}/status", response_model=AdminReturnDetailOut)
def update_admin_return_status(
    return_id_or_number: str,
    payload: AdminReturnStatusUpdateIn,
    db: Session = Depends(get_db),
) -> AdminReturnDetailOut:
    """Transition return request lifecycle status (APPROVED, REJECTED, ITEMS_RECEIVED, CANCELLED)."""
    ret = (
        db.query(ReturnRequest)
        .options(joinedload(ReturnRequest.order))
        .filter(
            (ReturnRequest.return_number == return_id_or_number)
            | (ReturnRequest.id == int(return_id_or_number) if return_id_or_number.isdigit() else False)
        )
        .first()
    )
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return request not found")

    allowed_statuses = {
        ReturnStatus.APPROVED.value,
        ReturnStatus.REJECTED.value,
        ReturnStatus.ITEMS_RECEIVED.value,
        ReturnStatus.CANCELLED.value,
    }
    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target status '{payload.status}'. Allowed: {', '.join(sorted(allowed_statuses))}",
        )

    prev_status = ret.status
    ret.status = payload.status
    ret.updated_at = datetime.now(timezone.utc)

    history = list(ret.history_json or [])
    history.append({
        "status": payload.status,
        "actor": "admin",
        "note": payload.note or f"Return status updated from {prev_status} to {payload.status}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    ret.history_json = history

    db.commit()
    db.refresh(ret)
    return _return_to_admin_out(ret)


@router.post("/returns/{return_id_or_number}/refund", response_model=AdminReturnDetailOut)
def process_return_refund(
    return_id_or_number: str,
    payload: AdminReturnRefundIn,
    db: Session = Depends(get_db),
) -> AdminReturnDetailOut:
    """Execute refund through payment provider and update return & order states upon confirmation."""
    ret = (
        db.query(ReturnRequest)
        .options(joinedload(ReturnRequest.order).joinedload(Order.payments))
        .filter(
            (ReturnRequest.return_number == return_id_or_number)
            | (ReturnRequest.id == int(return_id_or_number) if return_id_or_number.isdigit() else False)
        )
        .first()
    )
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return request not found")

    if ret.refund_status == RefundStatus.COMPLETED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund has already been completed for this return")

    if ret.status not in (ReturnStatus.APPROVED.value, ReturnStatus.ITEMS_RECEIVED.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot refund return in status '{ret.status}'. Must be APPROVED or ITEMS_RECEIVED.",
        )

    refund_amt = payload.amount or ret.refund_amount
    if refund_amt <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund amount must be greater than zero")

    order = ret.order
    successful_payment = next((p for p in order.payments if p.status in ("SUCCESS", "PAID")), None)
    provider_name = successful_payment.provider if successful_payment else "mock"
    provider = get_payment_provider(provider_name)

    dummy_payment = successful_payment or Payment(
        order_id=order.id,
        provider=provider_name,
        amount=refund_amt,
        amount_paise=refund_amt * 100,
        status="SUCCESS",
    )
    res = provider.refund_payment(dummy_payment, refund_amt, payload.note or ret.reason)
    if not res.get("success"):
        ret.refund_status = RefundStatus.FAILED.value
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payment provider rejected the refund")

    # Record confirmed refund payment record
    refund_payment = Payment(
        order_id=order.id,
        provider=provider_name,
        provider_payment_id=res.get("refund_id"),
        amount=-refund_amt,
        amount_paise=-refund_amt * 100,
        currency="INR",
        status=PaymentRecordStatus.REFUNDED.value,
        payment_method_detail=f"Refund: {res.get('refund_id')}",
    )
    db.add(refund_payment)

    ret.refund_amount = refund_amt
    ret.refund_amount_paise = refund_amt * 100
    ret.refund_status = RefundStatus.COMPLETED.value
    ret.status = ReturnStatus.REFUNDED.value
    ret.updated_at = datetime.now(timezone.utc)

    history = list(ret.history_json or [])
    history.append({
        "status": ReturnStatus.REFUNDED.value,
        "actor": "admin",
        "note": f"Refund of ₹{refund_amt} completed successfully (Ref: {res.get('refund_id')}). {payload.note or ''}".strip(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    ret.history_json = history

    total_refunded = (
        db.query(func.coalesce(func.sum(ReturnRequest.refund_amount), 0))
        .filter(
            ReturnRequest.order_id == order.id,
            ReturnRequest.refund_status == RefundStatus.COMPLETED.value,
        )
        .scalar()
        or 0
    )

    if total_refunded >= order.total_amount:
        order.payment_status = PaymentStatus.REFUNDED.value
        order.status = OrderStatus.REFUNDED.value
        db.add(
            OrderStatusHistory(
                order_id=order.id,
                status=OrderStatus.REFUNDED.value,
                note=f"Order fully refunded via return {ret.return_number}",
                timestamp=datetime.now(timezone.utc),
            )
        )

    db.commit()
    db.refresh(ret)
    return _return_to_admin_out(ret)


# -----------------------------------------------------------------------------
# Coupon / Promotion Management Endpoints
# -----------------------------------------------------------------------------


@router.get("/coupons", response_model=list[AdminCouponOut])
def list_admin_coupons(
    active_only: bool = Query(False, description="Filter only active coupons"),
    search: str | None = Query(None, description="Search by code or description"),
    db: Session = Depends(get_db),
) -> list[AdminCouponOut]:
    """List promotional coupons with optional active status and search filters."""
    query = db.query(Coupon)
    if active_only:
        query = query.filter(Coupon.is_active.is_(True))
    if search:
        s = f"%{search.strip()}%"
        query = query.filter((Coupon.code.ilike(s)) | (Coupon.description.ilike(s)))
    return query.order_by(Coupon.created_at.desc()).all()


@router.post("/coupons", response_model=AdminCouponOut, status_code=status.HTTP_201_CREATED)
def create_admin_coupon(
    payload: AdminCouponCreate,
    db: Session = Depends(get_db),
) -> AdminCouponOut:
    """Create a new promotional coupon code."""
    code_clean = payload.code.strip().upper()
    existing = db.query(Coupon).filter(Coupon.code == code_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon code '{code_clean}' already exists",
        )
    if payload.discount_type not in ["PERCENTAGE", "FLAT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount type must be either 'PERCENTAGE' or 'FLAT'",
        )

    coupon = Coupon(
        code=code_clean,
        description=payload.description,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        min_order_amount=payload.min_order_amount,
        max_discount_amount=payload.max_discount_amount,
        usage_limit=payload.usage_limit,
        usage_count=0,
        valid_until=payload.valid_until,
        is_active=payload.is_active,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.get("/coupons/{id}", response_model=AdminCouponOut)
def get_admin_coupon(
    id: int,
    db: Session = Depends(get_db),
) -> AdminCouponOut:
    """Retrieve coupon details by ID."""
    coupon = db.query(Coupon).filter(Coupon.id == id).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    return coupon


@router.patch("/coupons/{id}", response_model=AdminCouponOut)
def update_admin_coupon(
    id: int,
    payload: AdminCouponUpdate,
    db: Session = Depends(get_db),
) -> AdminCouponOut:
    """Update coupon fields (e.g. toggle active, adjust discount, extend validity)."""
    coupon = db.query(Coupon).filter(Coupon.id == id).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "discount_type" in update_data and update_data["discount_type"] not in ["PERCENTAGE", "FLAT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount type must be either 'PERCENTAGE' or 'FLAT'",
        )

    for field, val in update_data.items():
        setattr(coupon, field, val)

    coupon.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/coupons/{id}")
def delete_admin_coupon(
    id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a promo coupon permanently."""
    coupon = db.query(Coupon).filter(Coupon.id == id).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    code = coupon.code
    db.delete(coupon)
    db.commit()
    return {"message": f"Coupon '{code}' deleted successfully"}


# -----------------------------------------------------------------------------
# Customer Review Moderation Endpoints
# -----------------------------------------------------------------------------


@router.get("/reviews", response_model=list[AdminReviewOut])
def list_admin_reviews(
    product_id: int | None = Query(None, description="Filter by product ID"),
    min_rating: int | None = Query(None, ge=1, le=5, description="Filter by minimum star rating"),
    db: Session = Depends(get_db),
) -> list[AdminReviewOut]:
    """List customer reviews for moderation with optional product and rating filters."""
    query = db.query(Review).options(joinedload(Review.product))
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if min_rating:
        query = query.filter(Review.rating >= min_rating)
    reviews = query.order_by(Review.id.desc()).all()

    out = []
    for r in reviews:
        out.append(
            AdminReviewOut(
                id=r.id,
                productId=r.product_id,
                productName=r.product_name or (r.product.name if r.product else None),
                productSlug=r.product.slug if r.product else None,
                authorName=r.author_name,
                location=r.location,
                rating=r.rating,
                text=r.text,
                avatarUrl=r.avatar_url,
                date=r.date,
            )
        )
    return out


@router.delete("/reviews/{id}")
def delete_admin_review(
    id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete or moderate customer review, automatically recalculating product average rating."""
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    product = db.query(Product).filter(Product.id == review.product_id).first() if review.product_id else None

    db.delete(review)
    db.flush()

    if product:
        remaining_reviews = db.query(Review).filter(Review.product_id == product.id).all()
        if remaining_reviews:
            product.rating = round(sum(r.rating for r in remaining_reviews) / len(remaining_reviews), 1)
        else:
            product.rating = 5.0
        product.reviews_count = max(0, (product.reviews_count or 1) - 1)
    db.commit()
    return {"message": "Review deleted successfully"}


# -----------------------------------------------------------------------------
# Asset & Product Image Storage (Cloudflare R2)
# -----------------------------------------------------------------------------

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/avif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/images/upload")
async def upload_product_image(
    file: UploadFile = File(...),
) -> dict[str, str | int]:
    """Upload product image to Cloudflare R2 object storage and return CDN URL."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: '{file.content_type}'. Allowed: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed 5 MB limit",
        )

    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "webp"
    unique_key = f"products/{uuid.uuid4().hex[:12]}.{ext}"

    storage = get_storage_provider()
    cdn_url = storage.upload_file(
        file_bytes=file_bytes,
        destination_path=unique_key,
        content_type=file.content_type,
    )

    return {
        "url": cdn_url,
        "key": unique_key,
        "contentType": file.content_type,
        "size": len(file_bytes),
    }


# ---------------------------------------------------------------------------
# Storefront Brand Settings & Homepage Campaigns Management
# ---------------------------------------------------------------------------

@router.get("/storefront/brand", response_model=BrandSettingsOut)
def get_admin_brand_settings(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> BrandSettingsOut:
    """Retrieve storewide brand settings."""
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand = BrandSettings(
            name="Sulocraft",
            owner_name="Anupama Sharma",
            instagram_url="https://instagram.com/sulocraft",
            whatsapp_url="https://wa.me/919876543210",
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
    return BrandSettingsOut.model_validate(brand)


@router.put("/storefront/brand", response_model=BrandSettingsOut)
def update_admin_brand_settings(
    payload: BrandSettingsUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> BrandSettingsOut:
    """Update storewide brand settings."""
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand = BrandSettings(id=1)
        db.add(brand)

    if payload.name is not None:
        brand.name = payload.name
    if payload.owner_name is not None:
        brand.owner_name = payload.owner_name
    if payload.instagram_url is not None:
        brand.instagram_url = payload.instagram_url
    if payload.whatsapp_url is not None:
        brand.whatsapp_url = payload.whatsapp_url

    brand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(brand)
    return BrandSettingsOut.model_validate(brand)


@router.get("/storefront/campaigns", response_model=list[AdminHomepageCampaignOut])
def list_admin_campaigns(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> list[AdminHomepageCampaignOut]:
    """List all homepage campaigns (including inactive or scheduled) ordered by priority."""
    campaigns = (
        db.query(HomepageCampaign)
        .order_by(HomepageCampaign.priority.asc(), HomepageCampaign.id.asc())
        .all()
    )
    return [AdminHomepageCampaignOut.model_validate(c) for c in campaigns]


@router.post("/storefront/campaigns", response_model=AdminHomepageCampaignOut, status_code=status.HTTP_201_CREATED)
def create_admin_campaign(
    payload: AdminHomepageCampaignCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminHomepageCampaignOut:
    """Create a new homepage campaign."""
    now = datetime.now(timezone.utc)
    campaign = HomepageCampaign(
        title=payload.title,
        emphasis=payload.emphasis,
        description=payload.description,
        eyebrow=payload.eyebrow,
        image_url=payload.image_url,
        image_alt=payload.image_alt,
        destination=payload.destination,
        priority=payload.priority,
        is_active=payload.is_active,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        created_at=now,
        updated_at=now,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return AdminHomepageCampaignOut.model_validate(campaign)


@router.put("/storefront/campaigns/{campaign_id}", response_model=AdminHomepageCampaignOut)
def update_admin_campaign(
    campaign_id: int,
    payload: AdminHomepageCampaignUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminHomepageCampaignOut:
    """Update an existing homepage campaign."""
    campaign = db.query(HomepageCampaign).filter(HomepageCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if payload.title is not None:
        campaign.title = payload.title
    if payload.emphasis is not None:
        campaign.emphasis = payload.emphasis
    if payload.description is not None:
        campaign.description = payload.description
    if payload.eyebrow is not None:
        campaign.eyebrow = payload.eyebrow
    if payload.image_url is not None:
        campaign.image_url = payload.image_url
    if payload.image_alt is not None:
        campaign.image_alt = payload.image_alt
    if payload.destination is not None:
        campaign.destination = payload.destination
    if payload.priority is not None:
        campaign.priority = payload.priority
    if payload.is_active is not None:
        campaign.is_active = payload.is_active
    if payload.starts_at is not None:
        campaign.starts_at = payload.starts_at
    if payload.ends_at is not None:
        campaign.ends_at = payload.ends_at

    campaign.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(campaign)
    return AdminHomepageCampaignOut.model_validate(campaign)


@router.delete("/storefront/campaigns/{campaign_id}")
def delete_admin_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> dict[str, str | int]:
    """Delete a homepage campaign."""
    campaign = db.query(HomepageCampaign).filter(HomepageCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return {"status": "ok", "message": "Campaign deleted successfully", "id": campaign_id}


# -----------------------------------------------------------------------------
# Storefront Homepage Sections Management
# -----------------------------------------------------------------------------

@router.get("/storefront/sections", response_model=list[AdminHomepageSectionOut])
def list_admin_homepage_sections(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> list[AdminHomepageSectionOut]:
    """List all configured homepage sections ordered by display_order."""
    sections = db.query(HomepageSection).order_by(HomepageSection.display_order.asc(), HomepageSection.id.asc()).all()
    return [AdminHomepageSectionOut.model_validate(s) for s in sections]


@router.post("/storefront/sections", response_model=AdminHomepageSectionOut, status_code=status.HTTP_201_CREATED)
def create_admin_homepage_section(
    payload: AdminHomepageSectionCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminHomepageSectionOut:
    """Create a new controlled homepage section."""
    allowed_types = {"category_grid", "product_collection", "promo_banner", "review_section", "image_text", "occasion_grid"}
    if payload.section_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sectionType '{payload.section_type}'. Must be one of: {', '.join(sorted(allowed_types))}",
        )

    section = HomepageSection(
        section_type=payload.section_type,
        title=payload.title,
        eyebrow=payload.eyebrow,
        description=payload.description,
        image_url=payload.image_url,
        image_alt=payload.image_alt,
        image_position=payload.image_position or "left",
        cta_text=payload.cta_text,
        cta_url=payload.cta_url,
        collection_slug=payload.collection_slug,
        item_limit=payload.item_limit or 4,
        display_order=payload.display_order,
        is_enabled=payload.is_enabled,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        metadata_json=payload.metadata_json or {},
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return AdminHomepageSectionOut.model_validate(section)


@router.get("/storefront/sections/{section_id}", response_model=AdminHomepageSectionOut)
def get_admin_homepage_section(
    section_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminHomepageSectionOut:
    """Retrieve details for a single homepage section."""
    section = db.query(HomepageSection).filter(HomepageSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return AdminHomepageSectionOut.model_validate(section)


@router.put("/storefront/sections/{section_id}", response_model=AdminHomepageSectionOut)
def update_admin_homepage_section(
    section_id: int,
    payload: AdminHomepageSectionUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminHomepageSectionOut:
    """Update attributes, ordering, or visibility for a homepage section."""
    section = db.query(HomepageSection).filter(HomepageSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    allowed_types = {"category_grid", "product_collection", "promo_banner", "review_section", "image_text", "occasion_grid"}
    if payload.section_type is not None:
        if payload.section_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid sectionType '{payload.section_type}'. Must be one of: {', '.join(sorted(allowed_types))}",
            )
        section.section_type = payload.section_type

    if payload.title is not None:
        section.title = payload.title
    if payload.eyebrow is not None:
        section.eyebrow = payload.eyebrow
    if payload.description is not None:
        section.description = payload.description
    if payload.image_url is not None:
        section.image_url = payload.image_url
    if payload.image_alt is not None:
        section.image_alt = payload.image_alt
    if payload.image_position is not None:
        section.image_position = payload.image_position
    if payload.cta_text is not None:
        section.cta_text = payload.cta_text
    if payload.cta_url is not None:
        section.cta_url = payload.cta_url
    if payload.collection_slug is not None:
        section.collection_slug = payload.collection_slug
    if payload.item_limit is not None:
        section.item_limit = payload.item_limit
    if payload.display_order is not None:
        section.display_order = payload.display_order
    if payload.is_enabled is not None:
        section.is_enabled = payload.is_enabled
    if payload.starts_at is not None:
        section.starts_at = payload.starts_at
    if payload.ends_at is not None:
        section.ends_at = payload.ends_at
    if payload.metadata_json is not None:
        section.metadata_json = payload.metadata_json

    section.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(section)
    return AdminHomepageSectionOut.model_validate(section)


@router.delete("/storefront/sections/{section_id}")
def delete_admin_homepage_section(
    section_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> dict[str, str | int]:
    """Delete a homepage section."""
    section = db.query(HomepageSection).filter(HomepageSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    db.delete(section)
    db.commit()
    return {"status": "ok", "message": "Section deleted successfully", "id": section_id}


@router.post("/customers/send-welcome")
def admin_send_welcome_email(
    payload: AdminSendWelcomeRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(get_current_admin),
) -> dict[str, str]:
    """Admin endpoint to dispatch a branded welcome email to any customer.

    Supports an optional custom note/message from the founder.
    """
    background_tasks.add_task(
        dispatch_welcome_background,
        to_email=payload.email,
        customer_name=payload.name,
        custom_message=payload.custom_message,
    )
    return {
        "status": "queued",
        "message": f"Welcome email queued for {payload.email}",
        "recipient": payload.email,
    }


# ============================================================================
# Admin Occasion Management Endpoints
# ============================================================================

def _build_admin_occasion_out(occasion: Occasion, db: Session) -> AdminOccasionOut:
    product_ids = [
        po.product_id
        for po in db.query(ProductOccasion)
        .filter(ProductOccasion.occasion_id == occasion.id)
        .order_by(ProductOccasion.display_order.asc(), ProductOccasion.product_id.asc())
        .all()
    ]
    return AdminOccasionOut(
        id=occasion.id,
        name=occasion.name,
        icon=occasion.icon,
        image_key=occasion.image_key,
        image_url=occasion.image_url,
        description=occasion.description,
        display_order=occasion.display_order,
        is_enabled=occasion.is_enabled,
        is_evergreen=occasion.is_evergreen,
        starts_at=occasion.starts_at,
        ends_at=occasion.ends_at,
        product_count=len(product_ids),
        product_ids=product_ids,
        created_at=occasion.created_at,
        updated_at=occasion.updated_at,
    )


@router.get("/occasions", response_model=list[AdminOccasionOut])
def list_admin_occasions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> list[AdminOccasionOut]:
    """List all curated occasions with product associations and display order."""
    occasions = db.query(Occasion).order_by(Occasion.display_order.asc(), Occasion.id.asc()).all()
    return [_build_admin_occasion_out(occ, db) for occ in occasions]


@router.post("/occasions", response_model=AdminOccasionOut, status_code=status.HTTP_201_CREATED)
def create_admin_occasion(
    payload: AdminOccasionIn,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminOccasionOut:
    """Create a new curated occasion with optional product associations."""
    slug = re.sub(r"[^a-z0-9_-]", "", payload.id.lower().strip())
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Occasion ID must be a valid alphanumeric slug",
        )

    existing = db.query(Occasion).filter(Occasion.id == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Occasion with id '{slug}' already exists",
        )

    # Distinct artwork validation
    target_key = (payload.image_key or "").strip()
    if target_key:
        duplicate = db.query(Occasion).filter(Occasion.image_key == target_key).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image key '{target_key}' is already assigned to occasion '{duplicate.id}'. Please provide distinct artwork for each occasion.",
            )

    target_url = (payload.image_url or "").strip()
    if target_url:
        duplicate_url = db.query(Occasion).filter(Occasion._legacy_image_url == target_url).first()
        if duplicate_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image URL '{target_url}' is already assigned to occasion '{duplicate_url.id}'. Please provide distinct artwork for each occasion.",
            )

    occasion = Occasion(
        id=slug,
        name=payload.name,
        icon=payload.icon,
        image_key=payload.image_key,
        _legacy_image_url=payload.image_url,
        description=payload.description,
        display_order=payload.display_order,
        is_enabled=payload.is_enabled,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
    )
    db.add(occasion)
    db.flush()

    if payload.product_ids:
        existing_pids = {p[0] for p in db.query(Product.id).filter(Product.id.in_(payload.product_ids)).all()}
        for order_idx, pid in enumerate(payload.product_ids):
            if pid in existing_pids:
                db.add(ProductOccasion(product_id=pid, occasion_id=slug, display_order=order_idx))

    db.commit()
    db.refresh(occasion)
    return _build_admin_occasion_out(occasion, db)


@router.get("/occasions/{occasion_id}", response_model=AdminOccasionOut)
def get_admin_occasion(
    occasion_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminOccasionOut:
    """Get details of a single curated occasion."""
    occasion = db.query(Occasion).filter(Occasion.id == occasion_id).first()
    if not occasion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")
    return _build_admin_occasion_out(occasion, db)


@router.put("/occasions/{occasion_id}", response_model=AdminOccasionOut)
@router.patch("/occasions/{occasion_id}", response_model=AdminOccasionOut)
def update_admin_occasion(
    occasion_id: str,
    payload: AdminOccasionUpdateIn,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> AdminOccasionOut:
    """Update occasion metadata, distinct image, active dates, or product associations."""
    occasion = db.query(Occasion).filter(Occasion.id == occasion_id).first()
    if not occasion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")

    if occasion.is_evergreen:
        if payload.is_enabled is not None and not payload.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evergreen occasions cannot be disabled. They remain active year-round.",
            )
        if ("starts_at" in payload.model_fields_set and payload.starts_at is not None) or (
            "ends_at" in payload.model_fields_set and payload.ends_at is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evergreen occasions cannot have seasonal schedule dates. They remain active year-round.",
            )

    if payload.image_key is not None and payload.image_key != occasion.image_key:
        target_key = payload.image_key.strip()
        if target_key:
            duplicate = (
                db.query(Occasion)
                .filter(Occasion.image_key == target_key, Occasion.id != occasion_id)
                .first()
            )
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image key '{target_key}' is already assigned to occasion '{duplicate.id}'. Please provide distinct artwork for each occasion.",
                )
        occasion.image_key = payload.image_key

    if payload.image_url is not None and payload.image_url != occasion._legacy_image_url:
        target_url = payload.image_url.strip()
        if target_url:
            duplicate_url = (
                db.query(Occasion)
                .filter(Occasion._legacy_image_url == target_url, Occasion.id != occasion_id)
                .first()
            )
            if duplicate_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image URL '{target_url}' is already assigned to occasion '{duplicate_url.id}'. Please provide distinct artwork for each occasion.",
                )
        occasion._legacy_image_url = payload.image_url

    if payload.name is not None:
        occasion.name = payload.name
    if payload.icon is not None:
        occasion.icon = payload.icon
    if payload.description is not None:
        occasion.description = payload.description
    if payload.display_order is not None:
        occasion.display_order = payload.display_order
    if payload.is_enabled is not None:
        occasion.is_enabled = payload.is_enabled
    if "starts_at" in payload.model_fields_set:
        occasion.starts_at = payload.starts_at
    if "ends_at" in payload.model_fields_set:
        occasion.ends_at = payload.ends_at

    if payload.product_ids is not None:
        db.query(ProductOccasion).filter(ProductOccasion.occasion_id == occasion_id).delete(synchronize_session=False)
        existing_pids = {p[0] for p in db.query(Product.id).filter(Product.id.in_(payload.product_ids)).all()}
        for order_idx, pid in enumerate(payload.product_ids):
            if pid in existing_pids:
                db.add(ProductOccasion(product_id=pid, occasion_id=occasion_id, display_order=order_idx))

    occasion.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(occasion)
    return _build_admin_occasion_out(occasion, db)


@router.delete("/occasions/{occasion_id}")
def delete_admin_occasion(
    occasion_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
) -> dict[str, str]:
    """Delete an occasion and its associations."""
    occasion = db.query(Occasion).filter(Occasion.id == occasion_id).first()
    if not occasion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")

    if occasion.is_evergreen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evergreen occasions cannot be deleted.",
        )

    db.delete(occasion)
    db.commit()
    return {"status": "ok", "message": f"Occasion '{occasion_id}' deleted successfully"}
