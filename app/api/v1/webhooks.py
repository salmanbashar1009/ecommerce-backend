import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Payment, Order,OrderStatusHistory
from uuid import UUID
import json

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_API_KEY

@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    if event["type"] == "payment_intent.succeeded":
        intent_data = event["data"]["object"]
        stripe_pi_id = intent_data["id"]

        #find payment 
        stmt = Payment.__table__.select().where(Payment.stripe_payment_intent_id == stripe_pi_id)
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "succeeded"

            # Update order status to "paid"
            stmt_order = Order.__table__.select().where(Order.id == payment.order_id)
            result_order = await db.execute(stmt_order)
            order = result_order.scalar_one_or_none()

            order.status = "confirmed"

            # log order status change
            history = OrderStatusHistory(
                order_id=order.id,
                previous_status=order.status,
                new_status="confirmed",
                changed_by = None, # system triggered
            )

            db.add(history)
            await db.commit()
    
    elif event['type'] == 'payment_intent.payment_failed':
        intent_data = event['data']['object']
        stripe_pi_id = intent_data['id']
        stmt = Payment.__table__.select().where(Payment.stripe_payment_intent_id == stripe_pi_id)
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()
        if payment:
            payment.status = "failed"
            stmt_order = Order.__table__.select().where(Order.id == payment.order_id)
            order_result = await db.execute(stmt_order)
            order = order_result.scalar_one()
            order.status = "cancelled"
            await db.commit()

    return {"status": "success"}
