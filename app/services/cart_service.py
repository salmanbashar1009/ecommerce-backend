from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from app.models import ProductVariant, CartItem


async def add_to_cart(db:AsyncSession, variant_id:UUID, quantity:int, user_id:UUID = None, guest_session_id:str = None):
    # Validate variant exists and has stock
    variant = await db.get(ProductVariant, variant_id)
    if not variant:
        raise ValueError("Product variant not found")
    
    # Determine filter
    filter_kwargs = {"variant_id": variant_id}
    if user_id:
        filter_kwargs['user_id'] = user_id
    else:
        filter_kwargs['guest_session_id'] = guest_session_id

    stmt = select(CartItem).filter_by(**filter_kwargs)
    result = await db.execute(stmt)
    cart_item = result.scalar_one_or_none()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(**filter_kwargs, quantity=quantity)
        db.add(cart_item)
    await db.commit()
    return cart_item


async def merge_guest_cart(db:AsyncSession, guest_session_id:str, user_id:UUID):
    """Transfers guest cart items to user cart on login"""
    stmt = select(CartItem).filter_by(guest_session_id=guest_session_id)
    result = await db.execute(stmt)
    guest_cart_items = result.scalars().all()

    for guest_item in guest_cart_items:
        # Check if user already has this variant in cart
        user_stmt = select(CartItem).filter_by(user_id=user_id, variant_id=guest_item.variant_id)
        user_result = await db.execute(user_stmt)
        existing_item = user_result.scalar_one_or_none()

        if existing_item:
            existing_item.quantity += guest_item.quantity
            db.delete(guest_item)  # Remove guest item after merging
        else:
            guest_item.user_id = user_id
            guest_item.guest_session_id = None  # Clear guest session association
       
    await db.commit()