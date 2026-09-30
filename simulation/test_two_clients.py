import subprocess
import time


BASE_URL = "http://127.0.0.1:8000"


def request_from_ip(source_ip, path):
    result = subprocess.run(
        [
            "curl.exe",
            "--interface",
            source_ip,
            "-s",
            "-o",
            "NUL",
            "-w",
            "%{http_code}",
            f"{BASE_URL}{path}",
        ],
        capture_output=True,
        text=True,
    )

    print(f"{source_ip} -> {path:<15} -> {result.stdout}")


print("\n======================================")
print("CLIENT A: NORMAL USER")
print("======================================")

normal_paths = [
    "/api/data",
    "/api/data",
    "/health",
    "/api/data",
    "/api/data",
    "/health",
]

for path in normal_paths:
    request_from_ip("127.0.0.2", path)
    time.sleep(4)


print("\n======================================")
print("CLIENT B: SUSPICIOUS SCRAPER")
print("======================================")

scraper_paths = [
    "/api/data",
    "/unknown1",
    "/unknown2",
    "/api/data",
    "/unknown3",
    "/unknown4",
    "/api/data",
    "/unknown5",
]

for path in scraper_paths:
    request_from_ip("127.0.0.3", path)
    time.sleep(0.2)


print("\n======================================")
print("COMPARISON COMPLETE")
print("======================================")