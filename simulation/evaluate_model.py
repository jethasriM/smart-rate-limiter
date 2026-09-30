import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

from app.ml.anomaly_detector import AnomalyDetector
from app.ml.features import FEATURE_NAMES


def evaluate():

    detector = AnomalyDetector()

    normal_df = pd.read_csv(
        "simulation/evaluation_normal.csv"
    )

    suspicious_df = pd.read_csv(
        "simulation/evaluation_suspicious.csv"
    )

    # 0 = normal
    # 1 = suspicious
    normal_df["actual"] = 0
    suspicious_df["actual"] = 1

    df = pd.concat(
        [normal_df, suspicious_df],
        ignore_index=True
    )

    predictions = []

    for _, row in df.iterrows():

        features = {
            name: row[name]
            for name in FEATURE_NAMES
        }

        result = detector.predict(features)

        # Isolation Forest:
        #  1  = normal
        # -1  = anomaly
        predicted = 1 if result["is_anomaly"] else 0

        predictions.append(predicted)

    df["predicted"] = predictions

    y_true = df["actual"]
    y_pred = df["predicted"]

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred
    )

    tn, fp, fn, tp = cm.ravel()

    false_positive_rate = fp / (fp + tn)

    print("\n==============================")
    print("ISOLATION FOREST EVALUATION")
    print("==============================")

    print(f"\nSamples: {len(df)}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            target_names=[
                "Normal",
                "Suspicious"
            ],
            zero_division=0
        )
    )

    print(f"Precision:         {precision:.4f}")
    print(f"Recall:            {recall:.4f}")
    print(f"F1 Score:          {f1:.4f}")
    print(f"False Positive Rate: {false_positive_rate:.4f}")


if __name__ == "__main__":
    evaluate()