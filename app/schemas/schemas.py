from pydantic import BaseModel, EmailStr
from typing import Optional,List
from uuid import UUID

#Auth
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# Product
class ProductVariantOut(BaseModel):
    id: UUID
    sku: str
    size:Optional[str]
    color: Optional[str]
    price_override: Optional[float]
    stock_quantity: int
    stock: int

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: UUID
    name: str
    slug: str
    gendger:str
    base_price: float
    variants: List[ProductVariantOut]
    
    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_variant_id: UUID
    quantity: int = 1

class CartItemOut(BaseModel):
    id: UUID
    variant_id: UUID
    quantity: int
    product_name: str
    variant_sku: str
    current_price: float

    class Config:
        from_attributes = True