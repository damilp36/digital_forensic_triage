"""S1: anomaly detection.

Every detector exposes ``score(X)`` -- the output that SHAP explains (higher = more anomalous) --
and ``percentile(score)`` -- q(s), the score's percentile among held-out benign traffic.

* IsolationForest: s(x) = -E_t[h_t(x)], the negative mean isolation depth. It is a strictly
  monotone transform of scikit-learn's anomaly score 2^{-E[h]/c(n)}, so rankings are identical,
  and TreeSHAP explains it exactly (phi_0 + sum(phi) == s).
* Autoencoder: mean squared reconstruction error of a bottleneck MLP (scikit-learn), explained
  with KernelSHAP.
* XGBoost: supervised reference (upper bound); s(x) is the attack log-odds margin.
"""

from __future__ import annotations

import hashlib
import io

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


def signed_log(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    return np.sign(X) * np.log1p(np.abs(X))


class Detector:
    kind = "base"
    supervised = False

    def __init__(self, seed: int = 0, **params):
        self.seed = seed
        self.params = params
        self.cal_scores: np.ndarray | None = None
        self.version: str | None = None

    # -- to implement
    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> "Detector":
        raise NotImplementedError

    def score(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    # -- shared
    def calibrate(self, X_cal: np.ndarray) -> "Detector":
        self.cal_scores = np.sort(self.score(X_cal))
        self.version = self._compute_version()
        return self

    def percentile(self, s: np.ndarray) -> np.ndarray:
        assert self.cal_scores is not None, "detector not calibrated"
        return np.searchsorted(self.cal_scores, s, side="right") / len(self.cal_scores)

    def _compute_version(self) -> str:
        buf = io.BytesIO()
        joblib.dump(self._state(), buf)
        return f"{self.kind}-{hashlib.sha256(buf.getvalue()).hexdigest()[:12]}"

    def _state(self):
        return {"kind": self.kind, "seed": self.seed, "params": self.params,
                "model": getattr(self, "model", None), "cal": self.cal_scores}


class IForestDetector(Detector):
    kind = "iforest"

    def fit(self, X, y=None):
        self.model = IsolationForest(
            n_estimators=int(self.params.get("n_estimators", 100)),
            max_samples=self.params.get("max_samples", 256),
            random_state=self.seed,
            n_jobs=-1,
        ).fit(X)
        self._c = None
        return self

    def score(self, X):
        # score_samples = -2^{-E[h]/c}  ->  E[h] = -c * log2(-score_samples)
        from sklearn.ensemble._iforest import _average_path_length

        if getattr(self, "_c", None) is None:
            self._c = float(_average_path_length([self.model.max_samples_])[0])
        ss = -self.model.score_samples(np.asarray(X, dtype=np.float32))
        return self._c * np.log2(ss)  # = -E[h(x)]


class AutoencoderDetector(Detector):
    kind = "autoencoder"

    def fit(self, X, y=None):
        self.scaler = StandardScaler().fit(signed_log(X))
        Z = self.scaler.transform(signed_log(X))
        self.model = MLPRegressor(
            hidden_layer_sizes=tuple(self.params.get("ae_hidden", (32, 8, 32))),
            max_iter=int(self.params.get("ae_max_iter", 60)),
            early_stopping=True,
            random_state=self.seed,
        ).fit(Z, Z)
        return self

    def score(self, X):
        Z = self.scaler.transform(signed_log(X))
        Z = np.clip(Z, -50, 50)
        return np.mean((self.model.predict(Z) - Z) ** 2, axis=1)

    def _state(self):
        st = super()._state()
        st["scaler"] = self.scaler
        return st


class XGBoostDetector(Detector):
    kind = "xgboost"
    supervised = True

    def fit(self, X, y=None):
        import xgboost as xgb

        assert y is not None, "XGBoost reference detector needs labels"
        pos = max(1, int(np.sum(y)))
        self.model = xgb.XGBClassifier(
            n_estimators=int(self.params.get("xgb_n_estimators", 200)),
            max_depth=int(self.params.get("xgb_max_depth", 6)),
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=(len(y) - pos) / pos,
            random_state=self.seed,
            n_jobs=-1,
            tree_method="hist",
        ).fit(X, y)
        return self

    def score(self, X):
        return self.model.predict(np.asarray(X, dtype=np.float32), output_margin=True)


DETECTORS = {"iforest": IForestDetector, "autoencoder": AutoencoderDetector, "xgboost": XGBoostDetector}


def build_detector(dcfg: dict, seed: int, X_fit: np.ndarray, X_cal: np.ndarray,
                   X_sup: np.ndarray | None = None, y_sup: np.ndarray | None = None) -> Detector:
    cls = DETECTORS[dcfg["type"]]
    det = cls(seed=seed, **{k: v for k, v in dcfg.items() if k != "type"})
    if cls.supervised:
        det.fit(X_sup, y_sup)
    else:
        det.fit(X_fit)
    return det.calibrate(X_cal)
