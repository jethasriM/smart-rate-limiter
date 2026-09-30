import json
import time

from app.redis.client import redis_client


SECURITY_EVENTS_KEY = "guardflow:security_events"


def store_security_event(
    client_ip: str,
    decision: str,
    anomaly: dict | None,
    features: dict
):
    event = {
        "timestamp": time.time(),
        "client_ip": client_ip,
        "decision": decision,
        "score": (
            anomaly["score"]
            if anomaly
            else None
        ),
        "is_anomaly": (
            anomaly["is_anomaly"]
            if anomaly
            else False
        ),
        "requests_per_minute": features.get(
            "requests_per_minute",
            0
        ),
        "unique_paths": features.get(
            "unique_paths",
            0
        ),
        "error_rate": features.get(
            "error_rate",
            0
        ),
        "path_entropy": features.get(
            "path_entropy",
            0
        )
    }

    redis_client.lpush(
        SECURITY_EVENTS_KEY,
        json.dumps(event)
    )

    # Keep the latest 100 events
    redis_client.ltrim(
        SECURITY_EVENTS_KEY,
        0,
        99
    )

    # Events older than 1 hour are removed automatically
    redis_client.expire(
        SECURITY_EVENTS_KEY,
        3600
    )


def get_security_events(limit: int = 50):

    records = redis_client.lrange(
        SECURITY_EVENTS_KEY,
        0,
        limit - 1
    )

    return [
        json.loads(record)
        for record in records
    ]