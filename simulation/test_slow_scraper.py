from app.ml.anomaly_detector import AnomalyDetector


detector = AnomalyDetector()


normal_user = {
    "requests_per_second": 8 / 60,
    "requests_per_minute": 8,
    "unique_paths": 2,
    "path_entropy": 0.8,
    "error_rate": 0.01,
    "avg_payload_size": 500,
    "avg_processing_time": 0.05,
    "avg_inter_request_time": 8.5
}


slow_scraper = {
    "requests_per_second": 8 / 60,
    "requests_per_minute": 8,
    "unique_paths": 8,
    "path_entropy": 3.0,
    "error_rate": 0.25,
    "avg_payload_size": 8000,
    "avg_processing_time": 0.02,
    "avg_inter_request_time": 8.5
}


print("\n==============================")
print("NORMAL USER")
print("==============================")

print(
    detector.predict(normal_user)
)


print("\n==============================")
print("SLOW SCRAPER")
print("==============================")

print(
    detector.predict(slow_scraper)
)