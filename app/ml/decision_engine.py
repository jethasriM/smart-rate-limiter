class DecisionEngine:
    def __init__(
        self,
        block_threshold: float = -0.04
    ):
        self.block_threshold = block_threshold

    def decide(self, anomaly_result: dict, features: dict | None = None):

        score = anomaly_result["score"]
        is_anomaly = anomaly_result["is_anomaly"]

        # Strong behavioral abuse indicators
        if features:
            error_rate = features.get("error_rate", 0)
            unique_paths = features.get("unique_paths", 0)
            path_entropy = features.get("path_entropy", 0)
            avg_inter_request_time = features.get(
                "avg_inter_request_time", 0
            )

            # Strong scraping / probing behavior
            if (
                error_rate >= 0.5
                and unique_paths >= 5
                and path_entropy >= 2.0
            ):
                return "BLOCK"

            # Very rapid endpoint probing
            if (
                avg_inter_request_time < 0.2
                and unique_paths >= 5
            ):
                return "THROTTLE"

        # ML anomaly decision
        if is_anomaly:
            if score <= self.block_threshold:
                return "BLOCK"

            return "THROTTLE"

        return "ALLOW"