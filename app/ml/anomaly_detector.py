import joblib
import pandas as pd

from app.ml.features import FEATURE_NAMES


MODEL_PATH = "app/ml/isolation_forest.joblib"


class AnomalyDetector:

    def __init__(self, model_path=MODEL_PATH):

        self.model = joblib.load(model_path)

    def predict(self, features: dict):

        vector = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        dataframe = pd.DataFrame(
            [vector],
            columns=FEATURE_NAMES
        )

        prediction = self.model.predict(
            dataframe
        )[0]

        decision_score = self.model.decision_function(
            dataframe
        )[0]

        return {
            "prediction": int(prediction),
            "score": float(decision_score),
            "is_anomaly": bool(prediction == -1)
        }