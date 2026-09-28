import time

from app.ml.feature_builder import (
    build_features,
    calculate_path_entropy,
    calculate_inter_request_time
)


def test_path_entropy_repeated_path():
    paths = [
        "/api/data",
        "/api/data",
        "/api/data"
    ]

    assert calculate_path_entropy(paths) == 0.0


def test_path_entropy_multiple_paths():
    paths = [
        "/api/data",
        "/health"
    ]

    assert calculate_path_entropy(paths) > 0


def test_inter_request_time():
    now = time.time()

    timestamps = [
        now,
        now + 1,
        now + 2
    ]

    result = calculate_inter_request_time(timestamps)

    assert result == 1.0


def test_build_features():

    now = time.time()

    records = [
        {
            "timestamp": now - 2,
            "client_ip": "127.0.0.1",
            "method": "GET",
            "path": "/api/data",
            "payload_size": 0,
            "status_code": 200,
            "processing_time": 0.01
        },
        {
            "timestamp": now - 1,
            "client_ip": "127.0.0.1",
            "method": "GET",
            "path": "/health",
            "payload_size": 0,
            "status_code": 200,
            "processing_time": 0.02
        }
    ]

    features = build_features(records)

    assert features["request_count"] == 2
    assert features["unique_paths"] == 2
    assert features["error_rate"] == 0
    assert features["path_entropy"] > 0