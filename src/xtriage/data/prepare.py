"""Preparation: time-ordered splits, sampling, investigator oracle and background sets.

Paper Section IV-B/C. All splits are by time: the detector and background sets come from the
earliest window, rule induction and tuning use the middle window, testing uses the latest.

Two split strategies are provided:
  * ``time``    -- contiguous fit / tune / test windows by time fraction (NetFlow v3 corpora);
  * ``blocked`` -- fit window up to ``fit_until``; the remaining timeline is cut into blocks of
                   ``block_minutes`` that alternate between tune and test. Needed for corpora such
                   as CIC-IDS2017 where each attack class occupies a single time block, so a
                   contiguous split would leave the tune window without the classes in the test
                   window. Blocks are contiguous in time, so no flow is shuffled across a block.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from .loaders import FlowTable

log = logging.getLogger(__name__)


@dataclass
class Prepared:
    name: str
    feature_names: list[str]
    fit_X: np.ndarray  # benign flows for detector training
    cal_X: np.ndarray  # held-out benign flows for score percentiles
    backgrounds: list[np.ndarray]  # benign background sets B_1..B_n
    background_pool: np.ndarray
    tune: FlowTable
    test: FlowTable
    pool_meta: pd.DataFrame = field(default_factory=pd.DataFrame)  # ts of background_pool rows
    info: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ io
    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        np.save(path / "fit_X.npy", self.fit_X)
        np.save(path / "cal_X.npy", self.cal_X)
        np.save(path / "background_pool.npy", self.background_pool)
        for i, b in enumerate(self.backgrounds):
            np.save(path / f"background_{i}.npy", b)
        for split in ("tune", "test"):
            t: FlowTable = getattr(self, split)
            t.X.to_parquet(path / f"{split}_X.parquet", index=False)
            t.meta.to_parquet(path / f"{split}_meta.parquet", index=False)
        self.pool_meta.to_parquet(path / "pool_meta.parquet", index=False)
        with open(path / "prepared.json", "w", encoding="utf-8") as fh:
            json.dump({"name": self.name, "feature_names": self.feature_names,
                       "n_backgrounds": len(self.backgrounds), "info": self.info}, fh, indent=2, default=str)

    def subset(self, features: list[str]) -> "Prepared":
        """Same splits restricted to ``features`` (used by the shortcut-removal probe)."""
        idx = [self.feature_names.index(f) for f in features]
        return Prepared(
            self.name, list(features), self.fit_X[:, idx], self.cal_X[:, idx],
            [b[:, idx] for b in self.backgrounds], self.background_pool[:, idx],
            FlowTable(self.tune.name, self.tune.X[features].copy(), self.tune.meta),
            FlowTable(self.test.name, self.test.X[features].copy(), self.test.meta),
            self.pool_meta, dict(self.info),
        )

    @classmethod
    def load(cls, path: str | Path) -> "Prepared":
        path = Path(path)
        with open(path / "prepared.json", encoding="utf-8") as fh:
            head = json.load(fh)
        tabs = {}
        for split in ("tune", "test"):
            tabs[split] = FlowTable(head["name"], pd.read_parquet(path / f"{split}_X.parquet"),
                                    pd.read_parquet(path / f"{split}_meta.parquet"))
        return cls(
            name=head["name"],
            feature_names=head["feature_names"],
            fit_X=np.load(path / "fit_X.npy"),
            cal_X=np.load(path / "cal_X.npy"),
            backgrounds=[np.load(path / f"background_{i}.npy") for i in range(head["n_backgrounds"])],
            background_pool=np.load(path / "background_pool.npy"),
            tune=tabs["tune"],
            test=tabs["test"],
            pool_meta=pd.read_parquet(path / "pool_meta.parquet"),
            info=head["info"],
        )


# ---------------------------------------------------------------------------
# oracle
# ---------------------------------------------------------------------------


def oracle_priority(labels: pd.Series, priority_map: dict) -> np.ndarray:
    """Map attack classes to P1/P2/P3 by likely impact (benign -> P3)."""
    p1 = {str(c).lower() for c in priority_map.get("P1", [])}
    p2 = {str(c).lower() for c in priority_map.get("P2", [])}
    default = priority_map.get("default_attack", "P2")
    out = []
    for lab in labels.astype(str):
        low = lab.lower()
        if low == "benign":
            out.append("P3")
        elif low in p1:
            out.append("P1")
        elif low in p2:
            out.append("P2")
        else:
            out.append(default)
    return np.array(out, dtype=object)


def noisy_oracle(priority: np.ndarray, eta: float, seed: int) -> np.ndarray:
    """Flip a fraction ``eta`` of decisions to a different priority, simulating analyst error."""
    rng = np.random.default_rng(seed + 7919)
    out = np.asarray(priority, dtype=object).copy()
    if eta <= 0:
        return out
    flip = rng.random(len(out)) < eta
    choices = np.array(["P1", "P2", "P3"], dtype=object)
    for i in np.where(flip)[0]:
        out[i] = rng.choice(choices[choices != out[i]])
    return out


# ---------------------------------------------------------------------------
# splitting and sampling
# ---------------------------------------------------------------------------


def _parse_cut(value, ts: np.ndarray) -> int:
    if value is None:
        return int(np.quantile(ts, 0.4))
    if isinstance(value, (int, float)) and 0 < float(value) < 1:
        return int(np.quantile(ts, float(value)))
    return int(pd.Timestamp(value).value // 1_000_000)


def split_windows(meta: pd.DataFrame, split_cfg: dict) -> np.ndarray:
    """Return an array with values 'fit' | 'tune' | 'test' for each row."""
    ts = meta["ts"].to_numpy()
    out = np.empty(len(ts), dtype=object)
    if split_cfg["strategy"] == "time":
        f_fit, f_tune, _ = split_cfg["fractions"]
        order = np.argsort(ts, kind="stable")
        n = len(ts)
        a, b = int(n * f_fit), int(n * (f_fit + f_tune))
        out[order[:a]] = "fit"
        out[order[a:b]] = "tune"
        out[order[b:]] = "test"
    elif split_cfg["strategy"] == "blocked":
        cut = _parse_cut(split_cfg.get("fit_until"), ts)
        block_ms = int(split_cfg.get("block_minutes", 20)) * 60_000
        out[ts < cut] = "fit"
        rest = ts >= cut
        block = (ts[rest] - cut) // block_ms
        out[rest] = np.where(block % 2 == 0, "tune", "test")
    else:
        raise ValueError(f"unknown split strategy {split_cfg['strategy']}")
    return out


def _sample_split(table: FlowTable, idx: np.ndarray, scfg: dict, rng: np.random.Generator) -> np.ndarray:
    labels = table.meta["label"].to_numpy()[idx]
    keep = []
    benign = idx[labels == "Benign"]
    frac = float(scfg.get("benign_fraction", 1.0))
    if frac < 1.0:
        benign = rng.choice(benign, int(round(len(benign) * frac)), replace=False)
    keep.append(benign)
    cap = scfg.get("attack_cap_per_class")
    for cls in np.unique(labels[labels != "Benign"]):
        cidx = idx[labels == cls]
        if cap is not None and len(cidx) > cap:
            cidx = rng.choice(cidx, int(cap), replace=False)
        keep.append(cidx)
    out = np.concatenate(keep) if keep else np.array([], dtype=int)
    max_rows = scfg.get("max_rows")
    if max_rows is not None and len(out) > max_rows:
        out = rng.choice(out, int(max_rows), replace=False)
    ts = table.meta["ts"].to_numpy()[out]
    return out[np.lexsort((out, ts))]  # time order, stable by original position


def hash_array(arr: np.ndarray, feature_names: list[str] | None = None) -> str:
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(arr, dtype=np.float64).tobytes())
    h.update(str(arr.shape).encode())
    if feature_names:
        h.update(json.dumps(feature_names).encode())
    return h.hexdigest()


def prepare(table: FlowTable, cfg: dict) -> Prepared:
    seed = int(cfg.get("seed", 0))
    rng = np.random.default_rng(seed)
    meta = table.meta
    window = split_windows(meta, cfg["split"])
    is_benign = (meta["label"] == "Benign").to_numpy()
    s = cfg["sample"]

    fit_benign = np.where((window == "fit") & is_benign)[0]
    rng.shuffle(fit_benign)
    n_fit = min(int(s["fit_benign"]), int(len(fit_benign) * 0.6))
    n_cal = min(int(s["calibration"]), int(len(fit_benign) * 0.25))
    n_pool = min(int(s["background_pool"]), len(fit_benign) - n_fit - n_cal)
    if n_fit < 100 or n_cal < 100 or n_pool < 10:
        raise ValueError(f"fit window has too few benign flows ({len(fit_benign)})")
    fit_idx = np.sort(fit_benign[:n_fit])
    cal_idx = np.sort(fit_benign[n_fit:n_fit + n_cal])
    pool_idx = np.sort(fit_benign[n_fit + n_cal:n_fit + n_cal + n_pool])

    X = table.X.to_numpy(dtype=np.float32)
    pool = X[pool_idx]
    bsize = int(cfg["explain"]["background_size"])
    backgrounds = []
    for b in range(int(cfg["explain"]["n_backgrounds"])):
        brng = np.random.default_rng(1000 + b)
        backgrounds.append(pool[brng.choice(len(pool), min(bsize, len(pool)), replace=False)])

    tune_idx = _sample_split(table, np.where(window == "tune")[0], s["tune"], rng)
    test_idx = _sample_split(table, np.where(window == "test")[0], s["test"], rng)
    tune, test = table.take(tune_idx), table.take(test_idx)
    for t in (tune, test):
        t.meta["priority"] = oracle_priority(t.meta["label"], cfg["priority_map"])

    info = {
        "windows": {w: int((window == w).sum()) for w in ("fit", "tune", "test")},
        "fit_benign": n_fit,
        "calibration": n_cal,
        "background_pool": n_pool,
        "tune_rows": len(tune),
        "test_rows": len(test),
        "tune_classes": tune.meta["label"].value_counts().to_dict(),
        "test_classes": test.meta["label"].value_counts().to_dict(),
        "tune_priorities": pd.Series(tune.meta["priority"]).value_counts().to_dict(),
        "test_priorities": pd.Series(test.meta["priority"]).value_counts().to_dict(),
        "background_hashes": [hash_array(b, table.feature_names) for b in backgrounds],
        "split": cfg["split"],
        "sample": s,
    }
    log.info("prepared %s: %s", cfg["name"], {k: info[k] for k in ("windows", "tune_rows", "test_rows")})
    return Prepared(cfg["name"], table.feature_names, X[fit_idx], X[cal_idx], backgrounds, pool,
                    tune, test, pool_meta=meta.iloc[pool_idx][["flow_uid", "ts"]].reset_index(drop=True),
                    info=info)
