import numpy as np
import pandas as pd

from app.routes.predict import predict_frame


def test_predict_frame_serializes_batch_predictions_and_probabilities():
    class FakePipeline:
        named_steps = {"estimator": type("Estimator", (), {"classes_": np.array(["no", "yes"])})()}

        def predict(self, frame):
            return np.array(["no", "yes"])

        def predict_proba(self, frame):
            return np.array([[0.8, 0.2], [0.1, 0.9]])

    results = predict_frame(
        {"task_type": "classification"},
        pd.DataFrame({"age": [20, 30]}),
        FakePipeline(),
    )

    assert results == [
        {"prediction": "no", "probabilities": {"no": 0.8, "yes": 0.2}},
        {"prediction": "yes", "probabilities": {"no": 0.1, "yes": 0.9}},
    ]
