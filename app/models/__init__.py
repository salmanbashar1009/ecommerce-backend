"""Model package exports.

API modules import models from `app.models`, e.g.:

    from app.models import Product, ProductVariant, Category

So we re-export the SQLAlchemy model classes defined in `app.models.models`.
"""

# app/models/__init__.py

from .models import (
    User,
    Address,
    Category,
    Product,
    ProductVariant,
    ProductImage,
    ProductCategory,
    Review,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    Coupon,
    ShippingZone,
    AdminActivityLog,
    Base,          # if you need it elsewhere
)

