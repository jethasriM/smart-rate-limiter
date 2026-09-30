import json
import time

from app.redis.client import redis_client


STATE_TTL = 60


def set_client_state(
    client_ip: str,
    decision: str,
    anomaly: dict | None
):
    state = {
        "decision": decision,
        "score": (
            anomaly["score"]
            if anomaly
            else None
        ),
        "updated_at": time.time()
    }

    key = f"guardflow:client_state:{client_ip}"

    redis_client.set(
        key,
        json.dumps(state),
        ex=STATE_TTL
    )


def get_client_state(client_ip: str):

    key = f"guardflow:client_state:{client_ip}"

    value = redis_client.get(key)

    if not value:
        return None

    return json.loads(value)


def clear_client_state(client_ip: str):

    key = f"guardflow:client_state:{client_ip}"

    redis_client.delete(key)