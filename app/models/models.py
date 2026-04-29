import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Text, DateTime, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

Base = declarative_base()

class user(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid = True),primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True,) #nullable for social login
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(Enum('admin', 'customer', name = 'user_roles'), default = 'customer')
    is_verified = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    addresses = relationship('Address', back_populates= "user", cascade = 'all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='user',)
    orders = relationship('Order', back_populates='user',)
    reviews = relationship('Review', back_populates='user',)
    wishlist = relationship('Wishlist', back_populates='user',)




class Address(Base):
    __tablename__ = 'addresses'
    id = Column(UUID(as_uuid=True), primary_key=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    label = Column(String(50),) # e.g., Home, Work
    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    phone = Column(String(20))
    is_default_shipping  = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)

    # Relationships
    user = relationship('User', back_populates='addresses')




class Category(Base):
    __tablename__ = 'categories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    children = relationship("Category", backref="parent", remote_side=[id])
    products = relationship("Product",secondary="product_categories", back_populates="categories")


# Junction table for products and categories (many to many)
class ProductCategory(Base):
    __tanblename__ = 'product_categories'
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), primary_key=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255),unique=True, nullable=False, index=True)
    description = Column(Text)
    gender = Column(Enum('men', 'women','kids','unisex',name='gender_enum' ), nullable=False)
    base_price = Column(Float(precision=2),nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False) #soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    categories = relationship('Category',secondary='product_categories', back_populates='products')
    variants = relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')
    images = relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='product', cascade='all, delete-orphan')

class ProductVariant(Base):
    __tablename__ = 'product_variants'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    size = Column(String(50), ) # S, M, L, XL, 8, 9 etc.
    color = Column(String(50))
    price_override = Column(Float(precision=2),) # if null, use product's base price
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_low_stock = Column(Boolean, default=False) # flag for admin alerts
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint('product_id', 'size', 'color', name='uq_variant_matrix'),)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    display_order = Column(Integer, default=0)
    is_main = Column(Boolean, default=False)
    
    product = relationship("Product", back_populates="images")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    is_approved = Column(Boolean, default=False) # Moderation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Null for guests
    guest_session_id = Column(String(255), nullable=True, index=True) # For guests
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='uq_wishlist'),)
    user = relationship("User", back_populates="wishlist")

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Nullable for guest checkout
    guest_email = Column(String(255), nullable=True)
    status = Column(Enum("pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "returned", name="order_status"), default="pending")
    total_amount = Column(Float(precision=2), nullable=False)
    discount_amount = Column(Float(precision=2), default=0.0)
    shipping_cost = Column(Float(precision=2), default=0.0)
    tax_amount = Column(Float(precision=2), default=0.0)
    shipping_address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"))
    billing_address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"))
    tracking_number = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float(precision=2), nullable=False) # Snapshot price
    
    order = relationship("Order", back_populates="items")
    variant = relationship("ProductVariant", back_populates="order_items")

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    status = Column(String(50), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id")) # Admin who changed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="status_history")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True)
    amount = Column(Float(precision=2), nullable=False)
    currency = Column(String(10), default="usd")
    status = Column(Enum("pending", "succeeded", "failed", "refunded", name="payment_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="payments")

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(Enum("percentage", "fixed", name="discount_type"), nullable=False)
    discount_value = Column(Float(precision=2), nullable=False)
    min_order_amount = Column(Float(precision=2), default=0.0)
    max_uses = Column(Integer, nullable=True)
    times_used = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class ShippingZone(Base):
    __tablename__ = "shipping_zones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False) # e.g., "North America", "Local"
    countries = Column(Text) # JSON array of country codes
    flat_rate = Column(Float(precision=2), default=0.0)

class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(255), nullable=False) # e.g., "UPDATE_PRODUCT", "CANCEL_ORDER"
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    details = Column(Text) # JSON string of changes
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
