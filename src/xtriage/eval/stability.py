"""RQ2: explanation reliability -- stability across background sets and detector seeds, and
deletion-curve faithfulness of SHAP vs LIME vs random orderings."""

from __future__ import annotations

import itertools
import logging

import numpy as np
import pandas as pd

from ..data.prepare import Prepared
from ..engine.explain import Explainer, top_k
from ..engine.pipeline import XTriageEngine, fit_detector
from ..engine.represent import band_of
from .experiments import _subsample_alerts
from .metrics import deletion_curve, jaccard_rows, kendall_rows

log = logging.getLogger(__name__)


def stability_sample(prep: Prepared, cache: dict, n: int, seed: int = 0) -> np.ndarray:
    """Test-flow indices: a sample of seed-0 alerts stratified by score band."""
    sc = cache["test"]
    bands = band_of(sc.q[sc.alert_idx], cache["engines"]["XTriage"].rep.bands)
    pos = _subsample_alerts(bands, n, seed + 5)
    return sc.alert_idx[pos]


def attribution_grid(prep: Prepared, cfg: dict, idx: np.ndarray, base_detector) -> dict:
    """phi for the flows ``idx`` under every (detector seed, background) pair."""
    X = prep.test.X.to_numpy(dtype=np.float32)[idx]
    grid = {}
    seeds = cfg["eval"]["stability_seeds"]
    for sd in seeds:
        det = base_detector if sd == base_detector.seed else fit_detector(prep, cfg, sd)
        for b, bg in enumerate(prep.backgrounds):
            ex = Explainer.from_config(det, bg, prep.feature_names, cfg["explain"], seed=sd)
            phi, _ = ex.explain(X)
            grid[(sd, b)] = phi
    return grid


def stability_tables(prep: Prepared, cfg: dict, idx: np.ndarray, grid: dict, eng: XTriageEngine,
                     q: np.ndarray, s: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-flow stability (across backgrounds / seeds) and a summary by score band and class."""
    k = cfg["explain"]["top_k"]
    seeds = sorted({sd for sd, _ in grid})
    bgs = sorted({b for _, b in grid})
    s0 = seeds[0]
    pairs_bg = list(itertools.combinations(bgs, 2))
    pairs_sd = list(itertools.combinations(seeds, 2))
    jb = np.mean([jaccard_rows(grid[(s0, a)], grid[(s0, b)], k) for a, b in pairs_bg], axis=0)
    tb = np.mean([kendall_rows(grid[(s0, a)], grid[(s0, b)]) for a, b in pairs_bg], axis=0)
    js = np.mean([jaccard_rows(grid[(a, 0)], grid[(b, 0)], k) for a, b in pairs_sd], axis=0) if pairs_sd else np.nan
    ts = np.mean([kendall_rows(grid[(a, 0)], grid[(b, 0)]) for a, b in pairs_sd], axis=0) if pairs_sd else np.nan
    # do the fired rules change when only the background changes?
    X = prep.test.X.to_numpy(dtype=np.float32)[idx]
    ref = eng.triage(X, grid[(s0, 0)], q)
    rule_change = np.zeros(len(idx))
    tier_change = np.zeros(len(idx))
    for b in bgs[1:]:
        tr = eng.triage(X, grid[(s0, b)], q)
        rule_change += tr.rule_id != ref.rule_id
        tier_change += tr.tier != ref.tier
    rule_change /= max(1, len(bgs) - 1)
    tier_change /= max(1, len(bgs) - 1)
    theta = cfg["alert"]["theta"]
    per_flow = pd.DataFrame({
        "flow_uid": prep.test.meta["flow_uid"].to_numpy()[idx],
        "label": prep.test.meta["label"].to_numpy()[idx],
        "priority": prep.test.meta["priority"].to_numpy()[idx],
        "q": q, "s": s,
        "band": band_of(q, eng.rep.bands),
        "near_threshold": q < max(theta, eng.rep.bands[0]),
        "jaccard_bg": jb, "kendall_bg": tb, "jaccard_seed": js, "kendall_seed": ts,
        "rule_change_bg": rule_change, "tier_change_bg": tier_change,
    })
    cols = ["jaccard_bg", "kendall_bg", "jaccard_seed", "kendall_seed", "rule_change_bg", "tier_change_bg"]
    parts = []
    for key in ("band", "priority"):
        g = per_flow.groupby(key)[cols].mean()
        g.insert(0, "n", per_flow.groupby(key).size())
        g.index = [f"{key}={v}" for v in g.index]
        parts.append(g)
    allrow = per_flow[cols].mean().to_frame().T
    allrow.insert(0, "n", len(per_flow))
    allrow.index = ["all"]
    summary = pd.concat([allrow] + parts)
    return per_flow, summary.reset_index().rename(columns={"index": "group"})


def faithfulness(prep: Prepared, cfg: dict, det, idx: np.ndarray, phi_shap: np.ndarray, seed: int = 0,
                 steps: int = 10) -> pd.DataFrame:
    """Deletion curves: replace top-attributed features by the benign median, watch the score fall."""
    n = min(len(idx), int(cfg["eval"]["faithfulness_sample"]))
    rng = np.random.default_rng(seed + 11)
    pick = np.sort(rng.choice(len(idx), n, replace=False))
    X = prep.test.X.to_numpy(dtype=np.float32)[idx[pick]]
    baseline = np.median(prep.backgrounds[0], axis=0).astype(np.float32)
    d = X.shape[1]
    steps = min(steps, d)
    lime = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], method="lime", seed=seed)
    phi_lime, _ = lime.explain(X)
    orders = {
        "SHAP": top_k(np.maximum(phi_shap[pick], 0) + 1e-12 * phi_shap[pick], d),  # positive contributions first
        "LIME": top_k(np.maximum(phi_lime, 0) + 1e-12 * phi_lime, d),
        "random": np.stack([rng.permutation(d) for _ in range(n)]),
    }
    rows = []
    for name, order in orders.items():
        curve = deletion_curve(det.score, X, order, baseline, steps)
        rows.append({"method": name, "n": n, "deletion_auc": float(np.trapezoid(curve.mean(0)) / steps),
                     **{f"after_{m}": float(curve[:, m].mean()) for m in (1, 3, 5, steps)}})
    return pd.DataFrame(rows)
