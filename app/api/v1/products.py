from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.schemas.schemas import ProductOut
from app.core.database import get_db
from app.models import Product, ProductVariant, Category



router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductOut])
async def get_products(
    db:AsyncSession = Depends(get_db),
    gender: str = Query(None,description="Filter by men, women, kids"),
    category_slug: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    search : str = Query(None,),
    skip: int = 0,
    limit: int = 20
    ):
    stmt = select(Product).where(Product.isactive == True, Product.isdleted == False)

    if gender:
        stmt = stmt.where(Product.gender == gender)

    if category_slug:
        stmt = stmt.join(Product.categories).where(Category.slug == category_slug )

    if min_price is not None or max_price is not None:
        stmt = stmt.where(Product.base_price.between(min_price, max_price))

    if search:
        stmt = stmt.where(or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))

    stmt = stmt.offset(skip).limit(limit).distinct()
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.slug == slug, Product.is_active == True)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product