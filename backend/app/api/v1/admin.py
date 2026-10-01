"""Admin API router conforming to Sections 18, 20, 34, and Milestone 9 of Specification."""

import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_admin
from app.db.session import get_db
from app.services.notification import dispatch_order_status_background
from app.services.storage import get_storage_provider
from app.models.catalogue import (
    Category,
    Product,
    ProductImage,
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
)
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
    AdminCategoryCreate,
    AdminCategoryOut,
    AdminCategoryUpdate,
    AdminInventoryAdjustRequest,
    AdminLowStockItem,
    AdminOrderDetailOut,
    AdminOrderItemOut,
    AdminOrderListOut,
    AdminOrderStatusUpdate,
    AdminProductCreate,
    AdminProductListOut,
    AdminProductOut,
    AdminProductUpdate,
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
        categoryIds=[c.id for c in p.categories],
        categoryNames=[c.name for c in p.categories],
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
        image=c.image,
        icon=c.icon,
        displayOrder=c.display_order or 0,
        isActive=c.is_active,
        productsCount=len(c.products) if c.products else 0,
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
            joinedload(Product.categories),
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

    # Attach categories
    if payload.category_ids:
        categories = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()
        product.categories.extend(categories)

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
            joinedload(Product.categories),
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
            joinedload(Product.categories),
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

    if payload.category_ids is not None:
        product.categories = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()

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

    category = Category(
        name=payload.name,
        slug=slug,
        parent_id=payload.parent_id,
        description=payload.description,
        image=payload.image,
        icon=payload.icon,
        display_order=payload.display_order,
        is_active=payload.is_active,
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
    """Update taxonomy category details."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if payload.name is not None:
        category.name = payload.name
    if payload.slug is not None:
        category.slug = payload.slug
    if payload.parent_id is not None:
        category.parent_id = payload.parent_id
    if payload.description is not None:
        category.description = payload.description
    if payload.image is not None:
        category.image = payload.image
    if payload.icon is not None:
        category.icon = payload.icon
    if payload.display_order is not None:
        category.display_order = payload.display_order
    if payload.is_active is not None:
        category.is_active = payload.is_active

    db.commit()
    db.refresh(category)
    return _category_to_admin_out(category)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a taxonomy category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"status": "ok", "message": f"Category '{category.name}' deleted successfully"}


# -----------------------------------------------------------------------------
# Orders Administration & Lifecycle Transitions
# -----------------------------------------------------------------------------


@router.get("/orders", response_model=AdminOrderListOut)
def list_admin_orders(
    status: str | None = Query(default=None, description="Filter by OrderStatus"),
    payment_status: str | None = Query(default=None, alias="paymentStatus", description="Filter by PaymentStatus"),
    q: str | None = Query(default=None, description="Search by orderNumber, customer name, email, or phone"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: Session = Depends(get_db),
) -> AdminOrderListOut:
    """List all orders across customers with status filters and search."""
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

    if q:
        search_fmt = f"%{q.strip()}%"
        query = query.filter(
            (Order.order_number.ilike(search_fmt))
            | (Order.customer_name.ilike(search_fmt))
            | (Order.customer_phone.ilike(search_fmt))
            | (Order.customer_email.ilike(search_fmt))
        )

    total = query.distinct().count()
    orders = (
        query.distinct()
        .order_by(Order.created_at.desc())
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
            owner_name="Anupama",
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
    allowed_types = {"category_grid", "product_collection", "promo_banner", "review_section", "image_text"}
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

    allowed_types = {"category_grid", "product_collection", "promo_banner", "review_section", "image_text"}
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




