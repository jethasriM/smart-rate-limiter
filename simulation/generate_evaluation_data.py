import random

import pandas as pd


def generate_normal(n=200):

    records = []

    for _ in range(n):

        rps = random.uniform(0.01, 0.5)

        records.append({
            "requests_per_second": rps,
            "requests_per_minute": rps * 60,
            "unique_paths": random.randint(1, 5),
            "path_entropy": random.uniform(0, 2.3),
            "error_rate": random.uniform(0, 0.08),
            "avg_payload_size": random.uniform(0, 2000),
            "avg_processing_time": random.uniform(0.001, 0.2),
            "avg_inter_request_time": random.uniform(0.5, 10)
        })

    return records


def generate_suspicious(n=100):

    records = []

    for _ in range(n):

        rps = random.uniform(0.5, 1.5)

        records.append({
            "requests_per_second": rps,
            "requests_per_minute": rps * 60,
            "unique_paths": random.randint(20, 100),
            "path_entropy": random.uniform(3, 7),
            "error_rate": random.uniform(0.15, 0.6),
            "avg_payload_size": random.uniform(5000, 30000),
            "avg_processing_time": random.uniform(0.001, 0.05),
            "avg_inter_request_time": random.uniform(0.05, 0.5)
        })

    return records


if __name__ == "__main__":

    normal = generate_normal()
    suspicious = generate_suspicious()

    normal_df = pd.DataFrame(normal)
    suspicious_df = pd.DataFrame(suspicious)

    normal_df.to_csv(
        "simulation/evaluation_normal.csv",
        index=False
    )

    suspicious_df.to_csv(
        "simulation/evaluation_suspicious.csv",
        index=False
    )

    print("Evaluation datasets generated.")