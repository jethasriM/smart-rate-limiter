from app.ml.anomaly_detector import AnomalyDetector
from app.ml.decision_engine import DecisionEngine
from app.ml.feature_builder import build_features
from app.redis.feature_store import get_recent_features


class DetectorService:

    def __init__(self):
        self.detector = AnomalyDetector()
        self.decision_engine = DecisionEngine()

    def analyze(self, client_ip: str):

        records = get_recent_features(
            client_ip,
            limit=100
        )

        features = build_features(records)

    
        if features["request_count"] < 3:
            return {
                "decision": "ALLOW",
                "reason": "insufficient_data",
                "features": features,
                "anomaly": None
            }

        anomaly = self.detector.predict(features)

        decision = self.decision_engine.decide(
            anomaly,
            features
        )

        return {
            "decision": decision,
            "reason": "behavior_analysis",
            "features": features,
            "anomaly": anomaly
        }