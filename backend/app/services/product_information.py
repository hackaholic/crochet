"""Resolve public specification copy without modifying editable product records."""

INFORMATION_FIELDS = (
    "handmade_details", "materials_used", "size_dimensions",
    "processing_time", "care_instructions", "shipping_delivery",
)


def resolve_product_information(product, defaults=None) -> dict[str, str | None]:
    """Use meaningful product text first, then the database-managed default."""
    resolved = {}
    for field in INFORMATION_FIELDS:
        value = getattr(product, field, None)
        if not isinstance(value, str) or not value.strip():
            value = getattr(defaults, field, None)
        resolved[field] = value if isinstance(value, str) and value.strip() else None
    return resolved
