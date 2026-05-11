# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import only existing routers
from app.api.v1 import auth, products, orders
# from app.api.v1.users import router as users_router  # Uncomment when ready

app = FastAPI(
    title="Clothing E-commerce Backend API",
    version="1.0.0",
    description="Complete backend for Men, Women, and Kids clothing store",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers - IMPORTANT: No trailing slash in prefix
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")

# app.include_router(users_router, prefix="/api/v1")   # when you create users.py

# Health Check
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "message": "API is up and running!"}


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )