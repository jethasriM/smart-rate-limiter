from fastapi import FastAPI
from app.redis.client import check_redis_connection
from app.middleware.rate_limiter import RateLimitMiddleware
from app.dashboard.routes import router as dashboard_router


app = FastAPI(
    title = "API GuardFlow",
    description = "Adaptive API rate limiting and abuse detection",
    version = "0.1.0"
)


app.add_middleware(
    RateLimitMiddleware,
    max_requests=10,
    window_seconds=60
)

app.include_router(dashboard_router)

@app.get("/")
async def root():
    return {
        "service": "API GuardFlow",
        "status": "running"
    }
    
@app.get("/api/data")
async def get_data():
    return {
        "message": "This is protected API data",
    }
    
@app.get("/health")
async def health():
    redis_status = check_redis_connection()
    
    return {
        "api": "healthy",
        "redis": "connected" if redis_status else "disconnected"
    }  
    
@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    return {
        "product_id": product_id,
        "name": f"Product {product_id}"
    }