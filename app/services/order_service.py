from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Order, OrderItem, ProductVariant, Coupon, Payment
from app.schemas.schemas import OrderCreate
from uuid import UUID
from datetime import datetime

async def create_order(db: AsyncSession, user_id: UUID, payload: OrderCreate):
    # 1. Fetch Cart Items (Assuming cart is cleared after this)
    # In real app, fetch from CartItem where user_id=user_id
    
    # Mock fetching cart items for demonstration
    cart_items = [{"variant_id": payload.stripe_payment_intent_id, "quantity": 1}] # Replace with actual cart fetch
    
    total_amount = 0.0
    order_items_to_create = []
    
    # 2. Validate and Lock Inventory (Using with_for_update() to prevent race conditions)
    for item in cart_items:
        stmt = select(ProductVariant).filter(ProductVariant.id == item["variant_id"]).with_for_update()
        result = await db.execute(stmt)
        variant = result.scalar_one_or_none()
        
        if not variant or variant.stock_quantity < item["quantity"]:
            await db.rollback()
            raise ValueError(f"Insufficient stock for variant {variant.sku if variant else 'Unknown'}")
        
        # Deduct stock
        variant.stock_quantity -= item["quantity"]
        if variant.stock_quantity <= 5: # Low stock threshold
            variant.is_low_stock = True
            
        price = variant.price_override if variant.price_override else variant.product.base_price
        total_amount += price * item["quantity"]
        
        order_items_to_create.append(OrderItem(
            variant_id=variant.id,
            quantity=item["quantity"],
            price_at_purchase=price
        ))

    # 3. Apply Coupon (Simplified)
    discount = 0.0
    if payload.coupon_code:
        c_stmt = select(Coupon).filter(Coupon.code == payload.coupon_code, Coupon.is_active == True)
        c_result = await db.execute(c_stmt)
        coupon = c_result.scalar_one_or_none()
        if coupon and total_amount >= coupon.min_order_amount:
            if coupon.discount_type == "percentage":
                discount = (coupon.discount_value / 100) * total_amount
            else:
                discount = coupon.discount_value
            coupon.times_used += 1

    final_amount = total_amount - discount

    # 4. Create Order
    new_order = Order(
        user_id=user_id,
        total_amount=final_amount,
        discount_amount=discount,
        shipping_address_id=payload.shipping_address_id,
        billing_address_id=payload.billing_address_id or payload.shipping_address_id,
        status="pending"
    )
    db.add(new_order)
    await db.flush() # Flush to get order ID for order items

    for oi in order_items_to_create:
        oi.order_id = new_order.id
        db.add(oi)
        
    # 5. Create Payment Record
    payment = Payment(
        order_id=new_order.id,
        stripe_payment_intent_id=payload.stripe_payment_intent_id,
        amount=final_amount,
        status="pending"
    )
    db.add(payment)

    await db.commit()
    return new_order