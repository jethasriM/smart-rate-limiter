import hashlib
import os


CLIENT_ID_SALT = os.getenv(
    "CLIENT_ID_SALT",
    "local-development-salt"
)


def get_client_id(client_ip: str) -> str:
    value = f"{CLIENT_ID_SALT}:{client_ip}"

    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return f"client_{digest[:8]}"