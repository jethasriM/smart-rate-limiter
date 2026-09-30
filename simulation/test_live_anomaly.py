import time

from app.ml.detector_service import DetectorService


detector = DetectorService()

client_ip = "192.168.1.100"

print("\n==============================")
print("LIVE ANOMALY TEST")
print("==============================")

print("\nSending simulated normal traffic...")

for i in range(3):
    print(f"Normal request {i + 1}")
    time.sleep(2)

print("\nAnalyzing normal client...")

result = detector.analyze(client_ip)

print(result)


print("\n==============================")
print("SIMULATED SLOW SCRAPER")
print("==============================")

scraper_ip = "192.168.1.200"

for i in range(3):
    print(f"Scraper request {i + 1}")
    time.sleep(0.2)

print("\nAnalyzing scraper...")

result = detector.analyze(scraper_ip)

print(result)