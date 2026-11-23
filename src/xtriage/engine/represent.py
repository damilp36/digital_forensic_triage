"""S3: SHAP-augmented representation.

z(x) = [ disc(x), pi_1(x), ..., pi_d(x), band(q(s)) ]

* disc   -- each feature assigned to a quantile bin (Q1..Qn), edges learned on tune-window alerts;
* pi_j   -- 'T' when feature j is in the top-k attributions AND pushed the score up (phi_j > 0);
* band   -- score percentile mapped to low / medium / high.

All columns are categorical strings so the rule learners treat them as symbols.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .explain import top_k

BANDS = ("low", "medium", "high")


def band_of(q: np.ndarray, edges: list[float]) -> np.ndarray:
    q = np.asarray(q)
    return np.where(q < edges[0], "low", np.where(q < edges[1], "medium", "high")).astype(object)


class Representation:
    def __init__(self, feature_names: list[str], n_bins: int = 5, bands=(0.99, 0.999), top_k: int = 5,
                 parts=("disc", "why", "band")):
        self.feature_names = list(feature_names)
        self.n_bins = n_bins
        self.bands = list(bands)
        self.k = top_k
        self.parts = tuple(parts)
        self.edges: list[np.ndarray] = []

    # ------------------------------------------------------------------
    def fit(self, X: np.ndarray) -> "Representation":
        qs = np.linspace(0, 1, self.n_bins + 1)[1:-1]
        X = np.asarray(X, dtype=np.float64)
        self.edges = [np.unique(np.quantile(X[:, j], qs)) for j in range(X.shape[1])]
        return self

    def disc(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        out = np.empty(X.shape, dtype=object)
        for j, e in enumerate(self.edges):
            b = np.searchsorted(e, X[:, j], side="right")
            out[:, j] = np.array([f"Q{i + 1}" for i in range(len(e) + 1)], dtype=object)[b]
        return out

    def why(self, phi: np.ndarray) -> np.ndarray:
        out = np.full(phi.shape, "F", dtype=object)
        if phi.shape[0] == 0:
            return out
        idx = top_k(phi, self.k)
        rows = np.arange(phi.shape[0])[:, None]
        pos = np.take_along_axis(phi, idx, axis=1) > 0
        sel = np.where(pos, idx, -1)
        for r, cols in zip(rows[:, 0], sel):
            out[r, cols[cols >= 0]] = "T"
        return out

    def transform(self, X: np.ndarray, phi: np.ndarray | None, q: np.ndarray,
                  parts: tuple[str, ...] | None = None) -> pd.DataFrame:
        parts = parts or self.parts
        cols = {}
        if "disc" in parts:
            D = self.disc(X)
            for j, f in enumerate(self.feature_names):
                cols[f"x:{f}"] = D[:, j]
        if "why" in parts:
            assert phi is not None, "SHAP predicates need attributions"
            W = self.why(phi)
            for j, f in enumerate(self.feature_names):
                cols[f"why:{f}"] = W[:, j]
        if "band" in parts:
            cols["band"] = band_of(q, self.bands)
        return pd.DataFrame(cols)

    # ------------------------------------------------------------------
    def describe_condition(self, col: str, op: str, val: str) -> str:
        """Readable text for a rule condition, e.g. 'Destination Port >= 1024'."""
        if col == "band":
            return f"band {op} {val}"
        if col.startswith("why:"):
            f = col[4:]
            yes = (val == "T") == (op == "==")
            return f"SHAP[{f}] in top-{self.k}, positive" if yes else f"NOT SHAP[{f}] in top-{self.k}, positive"
        if col.startswith("x:"):
            f = col[2:]
            j = self.feature_names.index(f)
            e = self.edges[j]
            b = int(val[1:]) - 1
            lo = -np.inf if b == 0 else e[b - 1]
            hi = np.inf if b >= len(e) else e[b]
            rng = f"[{lo:.4g}, {hi:.4g})"
            return f"{f} {'in' if op == '==' else 'not in'} {val} {rng}"
        return f"{col} {op} {val}"

    def to_dict(self) -> dict:
        return {"feature_names": self.feature_names, "n_bins": self.n_bins, "bands": self.bands,
                "k": self.k, "parts": list(self.parts), "edges": [e.tolist() for e in self.edges]}

    @classmethod
    def from_dict(cls, d: dict) -> "Representation":
        r = cls(d["feature_names"], d["n_bins"], d["bands"], d["k"], d["parts"])
        r.edges = [np.asarray(e) for e in d["edges"]]
        return r
