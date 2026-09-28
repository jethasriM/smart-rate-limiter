import time
from starlette.requests import Request

async def extract_request_features(
    request: Request,
    response_status: int,
    start_time: float
):
    
    processing_time = time.time() - start_time
    
    content_length = request.headers.get("content-length", "0")
    
    try:
        payload_size = int(content_length)
    except ValueError:
        payload_size = 0
        
    return {
        "timestamp": time.time(),
        "client_ip": request.client.host,
        "method": request.method,
        "path": request.url.path,
        "payload_size": payload_size,
        "status_code": response_status,
        "processing_time": round(processing_time, 6)
    }
        