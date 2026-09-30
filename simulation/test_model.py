from app.ml.anomaly_detector import AnomalyDetector


detector = AnomalyDetector()


normal_traffic = {
    "requests_per_second": 0.15,
    "requests_per_minute": 9.0,
    "unique_paths": 2,
    "path_entropy": 1.0,
    "error_rate": 0.01,
    "avg_payload_size": 500,
    "avg_processing_time": 0.05,
    "avg_inter_request_time": 6.0
}


suspicious_traffic = {
    "requests_per_second": 0.9,
    "requests_per_minute": 54.0,
    "unique_paths": 45,
    "path_entropy": 5.2,
    "error_rate": 0.35,
    "avg_payload_size": 15000,
    "avg_processing_time": 0.01,
    "avg_inter_request_time": 0.2
}


print("NORMAL TRAFFIC")
print(
    detector.predict(normal_traffic)
)


print("\nSUSPICIOUS TRAFFIC")
print(
    detector.predict(suspicious_traffic)
)