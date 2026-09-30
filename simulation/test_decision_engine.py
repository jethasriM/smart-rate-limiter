from app.ml.decision_engine import DecisionEngine


engine = DecisionEngine()


test_cases = [
    {
        "name": "Normal traffic",
        "score": 0.0191,
        "is_anomaly": False,
    },
    {
        "name": "Moderate anomaly",
        "score": -0.02,
        "is_anomaly": True,
    },
    {
        "name": "Strong anomaly",
        "score": -0.062,
        "is_anomaly": True,
    },
]


for case in test_cases:
    result = engine.decide({
        "score": case["score"],
        "is_anomaly": case["is_anomaly"],
    })

    print(
        f"{case['name']:<20} "
        f"score={case['score']:<8} "
        f"anomaly={case['is_anomaly']:<5} "
        f"-> {result}"
    )