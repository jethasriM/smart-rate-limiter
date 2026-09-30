import numpy as np
import pandas as pd


np.random.seed(42)

NUM_SAMPLES = 3000

data = []

for _ in range(NUM_SAMPLES):

    # ---------------------------------------------------------
    # 1. Request frequency
    # ---------------------------------------------------------
    requests_per_second = np.random.uniform(0.01, 0.5)

    # ---------------------------------------------------------
    # 2. Number of endpoints used
    # ---------------------------------------------------------
    unique_paths = np.random.randint(1, 8)

    # ---------------------------------------------------------
    # 3. Path entropy
    # ---------------------------------------------------------
    path_entropy = np.random.uniform(0.0, 2.0)

    # ---------------------------------------------------------
    # 4. Error rate
    # ---------------------------------------------------------
    error_rate = np.random.uniform(0.0, 0.08)

    # ---------------------------------------------------------
    # 5. Payload size
    #
    # GET requests commonly have zero request-body payload.
    # ---------------------------------------------------------
    if np.random.random() < 0.45:
        avg_payload_size = 0.0
    else:
        avg_payload_size = np.random.uniform(50, 2000)

    # ---------------------------------------------------------
    # 6. Processing time
    # ---------------------------------------------------------
    avg_processing_time = np.random.uniform(0.001, 0.2)

    # ---------------------------------------------------------
    # 7. Inter-request time
    #
    # Legitimate users can make rapid bursts.
    # ---------------------------------------------------------
    traffic_pattern = np.random.choice(
        ["burst", "normal", "slow"],
        p=[0.25, 0.55, 0.20]
    )

    if traffic_pattern == "burst":
        avg_inter_request_time = np.random.uniform(0.03, 0.5)

    elif traffic_pattern == "normal":
        avg_inter_request_time = np.random.uniform(0.5, 5.0)

    else:
        avg_inter_request_time = np.random.uniform(5.0, 15.0)

    data.append({
        "requests_per_second": requests_per_second,
        "unique_paths": unique_paths,
        "path_entropy": path_entropy,
        "error_rate": error_rate,
        "avg_payload_size": avg_payload_size,
        "avg_processing_time": avg_processing_time,
        "avg_inter_request_time": avg_inter_request_time,
    })


df = pd.DataFrame(data)

output_path = "simulation/normal_traffic.csv"

df.to_csv(output_path, index=False)

print(f"Generated {len(df)} normal traffic samples")
print(f"Saved to: {output_path}")
print()
print(df.describe())