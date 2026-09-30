FEATURE_NAMES = [
    "requests_per_second",
    "unique_paths",
    "path_entropy",
    "error_rate",
    "avg_payload_size",
    "avg_processing_time",
    "avg_inter_request_time",
]


def features_to_vector(features: dict) -> list[float]:
    return [features[name] for name in FEATURE_NAMES]