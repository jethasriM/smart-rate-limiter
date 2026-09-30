import time
import requests


BASE_URL = "http://127.0.0.1:8000"


def send_request(path):
    try:
        response = requests.get(f"{BASE_URL}{path}")
        print(f"{path:<30} -> {response.status_code}")
    except Exception as e:
        print(f"{path:<30} -> ERROR: {e}")


print("\n==============================")
print("PHASE 1: NORMAL TRAFFIC")
print("==============================")

# Normal user behavior:
# Same endpoint, slower requests, successful responses.

for i in range(3):
    send_request("/api/data")
    time.sleep(5)


print("\nWaiting briefly before suspicious traffic...")
time.sleep(2)


print("\n==============================")
print("PHASE 2: RAPID / VARIED TRAFFIC")
print("==============================")

# Rapid requests to different endpoints.
# Some intentionally produce 404s, increasing behavioral variation.

paths = [
    "/api/data",
    "/health",
    "/unknown1",
    "/unknown2",
    "/unknown3",
]

for path in paths:
    send_request(path)
    time.sleep(0.2)


print("\n==============================")
print("LIVE TRAFFIC TEST COMPLETE")
print("==============================")