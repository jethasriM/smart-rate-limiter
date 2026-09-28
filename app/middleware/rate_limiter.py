import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.redis.client import redis_client
from app.middleware.feature_extractor import extract_request_features
from app.redis.feature_store import store_request_features


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        max_requests: int = 10,
        window_seconds: int = 60
    ):
        super().__init__(app)

        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):

        start_time = time.time()

        client_ip = request.client.host

        current_time = int(time.time())

        window = current_time // self.window_seconds

        redis_key = f"rate_limit:{client_ip}:{window}"

        request_count = redis_client.incr(redis_key)

        if request_count == 1:
            redis_client.expire(
                redis_key,
                self.window_seconds
            )

        if request_count > self.max_requests:

            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "Rate limit exceeded"
                }
            )

        else:

            response = await call_next(request)

        features = await extract_request_features(
            request,
            response.status_code,
            start_time
        )

        
        store_request_features(features)

        return response