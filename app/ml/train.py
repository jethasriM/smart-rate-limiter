import os

import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest


DATA_PATH = "simulation/normal_traffic.csv"
MODEL_PATH = "app/ml/isolation_forest.joblib"


def train_model():

    df = pd.read_csv(DATA_PATH)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,
        random_state=42,
        n_jobs=-1
    )

    model.fit(df)

    os.makedirs(
        os.path.dirname(MODEL_PATH),
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print("Model trained successfully.")
    print(f"Training samples: {len(df)}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()