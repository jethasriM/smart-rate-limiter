import json
import time

from app.redis.client import redis_client


def store_request_features(features: dict):
    client_ip = features["client_ip"]

    key = f"request_features:{client_ip}"

    redis_client.lpush(
        key,
        json.dumps(features)
    )

    # Only the latest 100 requests are kept
    redis_client.ltrim(key, 0, 99)

    # Inactive clients automatically removed
    redis_client.expire(key, 3600)


def get_recent_features(client_ip: str, limit: int = 100):
    key = f"request_features:{client_ip}"

    records = redis_client.lrange(
        key,
        0,
        limit - 1
    )

    return [
        json.loads(record)
        for record in records
    ]