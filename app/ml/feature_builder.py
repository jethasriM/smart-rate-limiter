import math
import time
from collections import Counter


def calculate_path_entropy(paths: list[str]) -> float:
    """
    Calculating Shannon entropy of requested API paths.
    Higher entropy generally means more diversity in paths.
    """

    if not paths:
        return 0.0

    counts = Counter(paths)
    total = len(paths)

    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    return round(entropy, 4)


def calculate_inter_request_time(timestamps: list[float]) -> float:
    """
    Calculating average time between consecutive requests.
    """

    if len(timestamps) < 2:
        return 0.0

    timestamps = sorted(timestamps)

    intervals = [
        timestamps[i] - timestamps[i - 1]
        for i in range(1, len(timestamps))
    ]

    return round(sum(intervals) / len(intervals), 4)


def build_features(
    records: list[dict],
    window_seconds: int = 60
) -> dict:

    now = time.time()

    recent_records = [
        record
        for record in records
        if now - record["timestamp"] <= window_seconds
    ]

    if not recent_records:
        return {
            "request_count": 0,
            "requests_per_second": 0.0,
            "requests_per_minute": 0.0,
            "unique_paths": 0,
            "path_entropy": 0.0,
            "error_rate": 0.0,
            "avg_payload_size": 0.0,
            "avg_processing_time": 0.0,
            "avg_inter_request_time": 0.0
        }

    request_count = len(recent_records)

    paths = [
        record["path"]
        for record in recent_records
    ]

    timestamps = [
        record["timestamp"]
        for record in recent_records
    ]

    payload_sizes = [
        record["payload_size"]
        for record in recent_records
    ]

    processing_times = [
        record["processing_time"]
        for record in recent_records
    ]

    errors = [
        record
        for record in recent_records
        if record["status_code"] >= 400
    ]

    error_rate = len(errors) / request_count

    return {
        "request_count": request_count,

        "requests_per_second": round(
            request_count / window_seconds,
            4
        ),

        "requests_per_minute": round(
            request_count * 60 / window_seconds,
            4
        ),

        "unique_paths": len(set(paths)),

        "path_entropy": calculate_path_entropy(paths),

        "error_rate": round(
            error_rate,
            4
        ),

        "avg_payload_size": round(
            sum(payload_sizes) / len(payload_sizes),
            4
        ),

        "avg_processing_time": round(
            sum(processing_times) / len(processing_times),
            6
        ),

        "avg_inter_request_time": calculate_inter_request_time(
            timestamps
        )
    }