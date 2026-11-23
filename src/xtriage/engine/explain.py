"""S2: event-level attribution.

phi_j(x) is the contribution of feature j to the detector output, relative to the expected output
phi_0 over a benign background set B:  s(x) = phi_0 + sum_j phi_j(x).

* tree detectors (isolation forest, XGBoost): exact interventional TreeSHAP over B;
* autoencoder: KernelSHAP over a fixed subsample of B;
* LIME: local linear surrogate (comparison method, baseline B5).

The hash of B is part of every explanation, because phi depends on it.
"""

from __future__ import annotations

import warnings

import numpy as np
from joblib import Parallel, delayed

from ..data.prepare import hash_array


def top_k(phi: np.ndarray, k: int) -> np.ndarray:
    """Indices of the k features with the largest |phi| per row, most important first."""
    k = min(k, phi.shape[1])
    idx = np.argpartition(-np.abs(phi), k - 1, axis=1)[:, :k]
    order = np.argsort(-np.take_along_axis(np.abs(phi), idx, axis=1), axis=1)
    return np.take_along_axis(idx, order, axis=1)


def _tree_chunk(detector, background, X):
    import shap

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ex = shap.TreeExplainer(detector.model, data=background, feature_perturbation="interventional")
        sv = np.asarray(ex.shap_values(X, check_additivity=False))
        ev = float(np.ravel(ex.expected_value)[0])
    if detector.kind == "iforest":  # shap explains E[h]; our score is -E[h]
        return -sv, -ev
    return sv, ev


def _kernel_chunk(detector, background, X, nsamples, seed):
    import shap

    np.random.seed(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ex = shap.KernelExplainer(detector.score, background)
        sv = np.asarray(ex.shap_values(X, nsamples=nsamples, silent=True))
    return sv, float(np.ravel(ex.expected_value)[0])


def _lime_chunk(detector, background, X, feature_names, num_samples, seed):
    from lime.lime_tabular import LimeTabularExplainer

    ex = LimeTabularExplainer(np.asarray(background, dtype=np.float64), mode="regression",
                              feature_names=feature_names, discretize_continuous=True,
                              random_state=seed)
    d = X.shape[1]
    out = np.zeros((len(X), d))
    for i, x in enumerate(X):
        exp = ex.explain_instance(np.asarray(x, dtype=np.float64), detector.score, num_features=d,
                                  num_samples=num_samples)
        for j, w in exp.as_map()[next(iter(exp.as_map()))]:
            out[i, j] = w
    return out, float(np.mean(detector.score(background)))


class Explainer:
    def __init__(self, detector, background: np.ndarray, feature_names: list[str], method: str = "shap",
                 n_jobs: int = -1, chunk: int = 400, kernel_background: int = 50, kernel_nsamples: int = 200,
                 lime_num_samples: int = 1000, seed: int = 0):
        self.detector = detector
        self.background = np.asarray(background, dtype=np.float32)
        self.feature_names = feature_names
        self.method = method
        self.n_jobs = n_jobs
        self.chunk = chunk
        self.kernel_background = kernel_background
        self.kernel_nsamples = kernel_nsamples
        self.lime_num_samples = lime_num_samples
        self.seed = seed
        self.background_hash = hash_array(self.background, feature_names)
        if method == "shap":
            self.algorithm = "TreeSHAP" if detector.kind in ("iforest", "xgboost") else "KernelSHAP"
        else:
            self.algorithm = "LIME"

    @classmethod
    def from_config(cls, detector, background, feature_names, ecfg: dict, method: str | None = None,
                    seed: int = 0, n_jobs: int | None = None):
        return cls(detector, background, feature_names, method=method or ecfg["method"],
                   n_jobs=ecfg["n_jobs"] if n_jobs is None else n_jobs, chunk=ecfg["chunk"],
                   kernel_background=ecfg["kernel_background"], kernel_nsamples=ecfg["kernel_nsamples"],
                   lime_num_samples=ecfg["lime_num_samples"], seed=seed)

    def __getstate__(self):
        state = dict(self.__dict__)
        state.pop("_tree_cache", None)  # never ship the cached shap object to worker processes
        return state

    def _tree_sequential(self, X):
        """TreeSHAP with a cached explainer (building one costs ~0.25 s, too slow per stream batch)."""
        import shap

        ex = self.__dict__.get("_tree_cache")
        if ex is None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ex = shap.TreeExplainer(self.detector.model, data=self.background,
                                        feature_perturbation="interventional")
            self._tree_cache = ex
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sv = np.asarray(ex.shap_values(X, check_additivity=False))
        ev = float(np.ravel(ex.expected_value)[0])
        return (-sv, -ev) if self.detector.kind == "iforest" else (sv, ev)

    def _task(self, X, i, sequential=False):
        if self.algorithm == "TreeSHAP":
            if sequential:
                return self._tree_sequential(X)
            return _tree_chunk(self.detector, self.background, X)
        if self.algorithm == "KernelSHAP":
            return _kernel_chunk(self.detector, self.background[: self.kernel_background], X,
                                 self.kernel_nsamples, self.seed + i)
        return _lime_chunk(self.detector, self.background, X, self.feature_names,
                           self.lime_num_samples, self.seed + i)

    def explain(self, X: np.ndarray, parallel: bool = True) -> tuple[np.ndarray, float]:
        X = np.asarray(X, dtype=np.float32)
        d = len(self.feature_names)
        if len(X) == 0:
            return np.zeros((0, d)), float("nan")
        chunks = [X[i:i + self.chunk] for i in range(0, len(X), self.chunk)]
        if parallel and len(chunks) > 1 and self.n_jobs != 1:
            res = Parallel(n_jobs=self.n_jobs)(delayed(self._task)(c, i) for i, c in enumerate(chunks))
        else:
            res = [self._task(c, i, sequential=True) for i, c in enumerate(chunks)]
        phi = np.vstack([r[0] for r in res]).astype(np.float64)
        return phi, res[0][1]
