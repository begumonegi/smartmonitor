import numpy as np
import os
import pickle
from sklearn.ensemble import IsolationForest

MODEL_PATH = os.path.join(os.path.dirname(__file__), "anomaly_model.pkl")

THRESHOLDS = {
    "temperature": {"min": 10, "max": 35},
    "humidity":    {"min": 10, "max": 95},
    "co2":         {"min": 300, "max": 1500},
}

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.buffer = []
        self.min_samples = 100
        self.trained = False

    def _to_features(self, data):
        return [data.get("temperature", 20), data.get("humidity", 50), data.get("co2", 500)]

    def load_or_train(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            self.trained = True
            print("Anomali modeli yuklendi")
        else:
            print("Model egitiliyor...")
            X = self._generate_synthetic_normal()
            self._train(X)
            print("Model hazir")

    def _generate_synthetic_normal(self):
        np.random.seed(42)
        n = 500
        return np.column_stack([
            np.random.normal(21, 2, n),
            np.random.normal(50, 8, n),
            np.random.normal(550, 80, n),
        ])

    def _train(self, X):
        self.model = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
        self.model.fit(X)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        self.trained = True

    def predict(self, data):
        for metric, limits in THRESHOLDS.items():
            val = data.get(metric)
            if val is not None:
                if val < limits["min"] or val > limits["max"]:
                    return True
        if self.trained and self.model:
            features = np.array([self._to_features(data)])
            return self.model.predict(features)[0] == -1
        self.buffer.append(self._to_features(data))
        if len(self.buffer) >= self.min_samples:
            self._train(np.array(self.buffer))
            self.buffer = []
        return False
