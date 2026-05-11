from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.models.models import User
from app.schemas.schemas import UserLogin, Token, UserRegister
import uuid


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # === FIXED: Use hash_password ===
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create access token
    token = create_access_token({
        'sub': str(new_user.id), 
        'role': 'customer'
    })
    
    return Token(access_token=token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # Find user by email
    stmt = User.__table__.select().where(User.email == credentials.email)
    result = await db.execute(stmt)
    user_row = result.first()

    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    user = user_row[0]  # Unpack the result

    #verify password
    if not verify_password(credentials.password, user_row.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    #create access token
    token = create_access_token({'sub': str(user.id), 'role': 'customer'})

    return Token(access_token=token, token_type="bearer")


@router.post('/geust-token', response_model=Token)
async def guest_token():
    """Provides a temporary token for guest carts"""
    guest_id = str(uuid.uuid4())
    token = create_access_token({'sub': guest_id, 'role': 'guest'})
    return  {"access_token": token, "token_type": "bearer"}