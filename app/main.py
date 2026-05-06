from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import auth, products, orders, users


app = FastAPI(
    title="Clothing E-commerce Backend API",
    version="1.0.0",
    description="Complete backend for Men, Women, and Kids clothing store",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

#CORS configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    alow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# versioned API routes
app.include_router(auth.router, prefix="/api/v1/")
app.include_router(products.router, prefix="/api/v1/")
app.include_router(orders.router, prefix="/api/v1/")

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "message": "API is up and running!"}