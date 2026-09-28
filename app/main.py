from fastapi import FastAPI
from app.redis.client import check_redis_connection
from app.middleware.rate_limiter import RateLimitMiddleware

from fastapi import Request
from app.redis.feature_store import get_recent_features

from app.ml.feature_builder import build_features
from app.redis.feature_store import get_recent_features

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

@app.get("/")
async def root():
    return {
        "service": "API GuardFlow",
        "status": "running"
    }
    
@app.get("/api/data")
async def get_data():
    return {
        "message": "This is protected API data"
    }
    
@app.get("/health")
async def health():
    redis_status = check_redis_connection()
    
    return {
        "api": "healthy",
        "redis": "connected" if redis_status else "disconnected"
    }
    
@app.get("/debug/features")
async def debug_features(request: Request):

    client_ip = request.client.host

    features = get_recent_features(client_ip)

    return {
        "client_ip": client_ip,
        "request_count": len(features),
        "features": features
    }
    
@app.get("/debug/aggregated-features")
async def aggregated_features(request: Request):

    client_ip = request.client.host

    records = get_recent_features(
        client_ip,
        limit=100
    )

    features = build_features(records)

    return {
        "client_ip": client_ip,
        "features": features
    }
    
@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    return {
        "product_id": product_id,
        "name": f"Product {product_id}"
    }