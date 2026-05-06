from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import OrderOut, OrderCreate
from uuid import UUID
from app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model= OrderOut)
async def place_orders(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db) 
    # current_user: User = Depends(get_current_user) #Implement in production
):
    try:
        # pass actual user_id from jwt token in production
        mock_user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        order = await create_order(db, payload, mock_user_id)
        return order
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
