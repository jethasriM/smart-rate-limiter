import asyncio
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.redis.client import redis_client
from app.middleware.feature_extractor import extract_request_features
from app.redis.feature_store import store_request_features
from app.ml.detector_service import DetectorService

from app.redis.security_events import store_security_event

from app.redis.client_state import get_client_state
from app.redis.client_state import set_client_state


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        max_requests: int = 10,
        window_seconds: int = 60,
        throttle_delay: float = 1.5
    ):
        super().__init__(app)

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.throttle_delay = throttle_delay
        self.detector_service = DetectorService()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        client_ip = request.client.host
        
        if request.url.path.startswith((
            "/dashboard",
            "/debug"
       )):
            return await call_next(request)
        
        existing_state = get_client_state(client_ip)

        if existing_state:
            decision = existing_state["decision"]
            if decision == "BLOCK":
                return JSONResponse(
                    status_code=403,
                    content={
                "error": "Request blocked",
                "message": "Client temporarily blocked due to suspicious behavior",
                "client_ip": client_ip,
                "reason": "cached_behavioral_anomaly"
                   }
                )
                
            if decision == "THROTTLE":
                await asyncio.sleep(
                    self.throttle_delay
                )
        current_time = int(time.time())

        window = current_time // self.window_seconds

        redis_key = f"rate_limit:{client_ip}:{window}"

        request_count = redis_client.incr(redis_key)

        if request_count == 1:
            redis_client.expire(
                redis_key,
                self.window_seconds
            )

        # Fixed-window rate limiting
        if request_count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "Rate limit exceeded"
                }
            )

        # Allow request to reach the API
        response = await call_next(request)

        # Extract request behavior features
        features = await extract_request_features(
            request,
            response.status_code,
            start_time
        )

        # Store features in Redis
        store_request_features(features)

        # Run ML anomaly detection
        ml_result = self.detector_service.analyze(client_ip)

        if ml_result["anomaly"]:
            score = ml_result["anomaly"]["score"]
        else:
            score = "N/A"
            
        store_security_event(
            client_ip=client_ip,
            decision=ml_result["decision"],
            anomaly=ml_result["anomaly"],
            features=ml_result["features"]
        )
        
        if ml_result["decision"] in (
            "THROTTLE",
            "BLOCK"
        ):
            set_client_state(
                client_ip=client_ip,
                decision=ml_result["decision"],
                anomaly=ml_result["anomaly"]
            )

        print(
            f"[ML] {client_ip} -> "
            f"{ml_result['decision']} "
            f"score={score}"
        )
        
        # ML enforcement
        if ml_result["decision"] == "BLOCK":
            return JSONResponse(
                status_code=403,
                content={
                "error": "Request blocked",
                "message": "Suspicious behavior detected",
                "client_ip": client_ip,
                "reason": "behavioral_anomaly"
                 } 
            )
        if ml_result["decision"] == "THROTTLE":
            await asyncio.sleep(
                self.throttle_delay
            )

        return response