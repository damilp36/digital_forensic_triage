"""RQ1 / RQ3: XTriage against baselines B1-B5 and ablations, per seed."""

from __future__ import annotations

import logging
import time

import numpy as np
import pandas as pd

from ..data.prepare import Prepared
from ..engine.explain import Explainer
from ..engine.guard import queue_order
from ..engine.pipeline import Scored, XTriageEngine, fit_detector, score_and_explain
from .metrics import detection_metrics, rule_metrics, topk_sets, triage_metrics, workload_curve

log = logging.getLogger(__name__)

FULL = ("disc", "why", "band")
VARIANTS = {
    # name: (parts, learner, guard, overrides)
    "XTriage": (FULL, "ripper", True, None),
    "B3-raw-rules": (("disc",), "ripper", False, None),
    "B4-tree-surrogate": (FULL, "tree", True, None),
    "Abl-no-SHAP-predicates": (("disc", "band"), "ripper", True, None),
    "Abl-no-score-band": (("disc", "why"), "ripper", True, None),
    "Abl-no-guard": (FULL, "ripper", False, None),
    "Abl-guard-review-tier": (FULL, "ripper", "review", None),
    # follow-ups to the CIC-IDS2017 limitation findings (docs/notes.txt W2-W5)
    "Fix-calibrated-guard": (FULL, "ripper", "calibrated", None),
    "Fix-SHAP-gated-bins": (FULL, "ripper", True, {"represent": {"gate_disc": True}}),
    "Fix-no-port-bins": (FULL, "ripper", True, {"represent": {"exclude": "$port_features"}}),
    "Fix-label-filter": (FULL, "ripper", True, {"rules": {"label_filter": True}}),
}


def resolve_overrides(overrides, cfg: dict):
    """Substitute config references such as "$port_features" (cfg['evasion']['port_features'])."""
    if not overrides:
        return overrides
    out = {}
    for k, v in overrides.items():
        if isinstance(v, dict):
            out[k] = resolve_overrides(v, cfg)
        elif v == "$port_features":
            out[k] = list(cfg["evasion"].get("port_features", []))
        else:
            out[k] = v
    return out


def evaluate_engine(eng: XTriageEngine, X: np.ndarray, sc: Scored, truth: np.ndarray, total_p1: int,
                    budgets, alert_subset: np.ndarray | None = None) -> tuple[dict, np.ndarray]:
    """Triage the alerts in ``sc`` (optionally a subset of positions) and compute RQ1 + RQ3 metrics."""
    ai = sc.alert_idx
    pos = np.arange(len(ai)) if alert_subset is None else alert_subset
    idx = ai[pos]
    phi = sc.phi[pos]
    tr = eng.triage(X[idx], phi, sc.q[idx])
    order = queue_order(tr.tier, sc.q[idx], sc.s[idx])
    t = truth[idx]
    m = triage_metrics(order, t, total_p1, budgets)
    feats = [eng.rules.features_of(r) for r in tr.rule_id]
    tops = [{eng.feature_names[j] for j in s} for s in topk_sets(phi, eng.rep.k)]
    m.update(rule_metrics(tr.tier, tr.rule_priority, t, tr.is_default, feats, tops,
                          sc.q[idx], eng.rep.bands, tr.contested, eng.rules.n_rules, eng.rules.mean_length))
    # fidelity counting only conditions on traffic values (SHAP predicates match by construction)
    disc = [eng.rules.features_of(r, disc_only=True) for r in tr.rule_id]
    fd = [len(set(f) & s) / len(f) for f, s, d in zip(disc, tops, tr.is_default) if f and not d]
    m["fidelity_traffic_conds"] = float(np.mean(fd)) if fd else float("nan")
    m["triage_seconds"] = tr.seconds
    return m, order


def score_only(sc: Scored, truth: np.ndarray, total_p1: int, budgets, alert_subset=None) -> tuple[dict, np.ndarray]:
    ai = sc.alert_idx
    pos = np.arange(len(ai)) if alert_subset is None else alert_subset
    idx = ai[pos]
    order = np.lexsort((-sc.s[idx], -sc.q[idx]))
    return triage_metrics(order, truth[idx], total_p1, budgets), order


def _subsample_alerts(truth_alerts: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Stratified (by priority) sample of alert positions, keeping every P1 alert when possible."""
    rng = np.random.default_rng(seed + 31)
    pos = np.arange(len(truth_alerts))
    if len(pos) <= n:
        return pos
    out = []
    classes, counts = np.unique(truth_alerts, return_counts=True)
    budget = n
    for c, k in sorted(zip(classes, counts), key=lambda t: t[1]):
        share = budget // (len(classes) - len(out))
        cpos = pos[truth_alerts == c]
        if len(cpos) > share:
            cpos = rng.choice(cpos, share, replace=False)
        out.append(cpos)
        budget -= len(cpos)
    return np.sort(np.concatenate(out))


def _restrict(sc: Scored, pos: np.ndarray, phi: np.ndarray | None = None) -> Scored:
    """A Scored whose alerts are only the given alert positions (optionally new attributions)."""
    ai = sc.alert_idx[pos]
    mask = np.zeros_like(sc.alert)
    mask[ai] = True
    return Scored(sc.s, sc.q, mask, sc.phi[pos] if phi is None else phi, sc.phi0)


def run_main(prep: Prepared, cfg: dict, seed: int, curves: dict | None = None) -> tuple[list[dict], dict]:
    """All main-table methods for one seed. Returns rows and cached objects for later experiments."""
    budgets = cfg["eval"]["budgets"]
    theta = cfg["alert"]["theta"]
    Xtu = prep.tune.X.to_numpy(dtype=np.float32)
    Xte = prep.test.X.to_numpy(dtype=np.float32)
    truth = prep.test.meta["priority"].to_numpy()
    total_p1 = int((truth == "P1").sum())
    rows: list[dict] = []

    t0 = time.perf_counter()
    det = fit_detector(prep, cfg, seed)
    ex = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], seed=seed)
    tune_sc = score_and_explain(det, ex, Xtu, theta)
    test_sc = score_and_explain(det, ex, Xte, theta)
    log.info("seed %d: detector + SHAP in %.1fs (tune alerts %d, test alerts %d)", seed, time.perf_counter() - t0,
             tune_sc.alert.sum(), test_sc.alert.sum())
    dm = detection_metrics(test_sc.s, test_sc.alert, prep.test.meta["is_attack"].to_numpy(), truth)
    dm["shap_ms_per_alert"] = 1000 * test_sc.seconds["explain"] / max(1, test_sc.alert.sum())
    base = {"seed": seed, **{f"det_{k}": v for k, v in dm.items()}}

    m, order = score_only(test_sc, truth, total_p1, budgets)
    rows.append({**base, "method": "B1-score-only", **m})
    if curves is not None:
        curves["B1-score-only"] = workload_curve(order, truth[test_sc.alert_idx])

    engines = {}
    for name, (parts, learner, guard, overrides) in VARIANTS.items():
        t1 = time.perf_counter()
        eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=tune_sc,
                                parts=parts, learner=learner, guard=guard,
                                overrides=resolve_overrides(overrides, cfg))
        fit_s = time.perf_counter() - t1
        m, order = evaluate_engine(eng, Xte, test_sc, truth, total_p1, budgets)
        rows.append({**base, "method": name, "rule_fit_seconds": fit_s, **m})
        engines[name] = eng
        if curves is not None:
            curves[name] = workload_curve(order, truth[test_sc.alert_idx])
        log.info("seed %d %-24s workload@90=%s macroF1=%.3f rules=%d (%.0fs)", seed, name, m.get("workload@90"),
                 m["macro_f1"], m["n_rules"], fit_s)

    # B2: supervised XGBoost + SHAP, ranking only (its own alert set)
    det_x = fit_detector(prep, cfg, seed, dtype="xgboost")
    ex_x = Explainer.from_config(det_x, prep.backgrounds[0], prep.feature_names, cfg["explain"], seed=seed)
    xs = score_and_explain(det_x, ex_x, Xte, theta)
    m, order = score_only(xs, truth, total_p1, budgets)
    dmx = detection_metrics(xs.s, xs.alert, prep.test.meta["is_attack"].to_numpy(), truth)
    rows.append({"seed": seed, **{f"det_{k}": v for k, v in dmx.items()}, "method": "B2-xgboost-shap", **m})
    if curves is not None:
        curves["B2-xgboost-shap"] = workload_curve(order, truth[xs.alert_idx])

    # B5 (LIME instead of SHAP) and Anchors -- on stratified alert samples, against XTriage on the same sample
    rows.extend(_run_sampled(prep, cfg, seed, det, ex, tune_sc, test_sc, Xtu, Xte, truth, total_p1, base))
    cache = {"detector": det, "explainer": ex, "tune": tune_sc, "test": test_sc, "engines": engines}
    return rows, cache


def _run_sampled(prep, cfg, seed, det, ex, tune_sc, test_sc, Xtu, Xte, truth, total_p1, base) -> list[dict]:
    budgets = cfg["eval"]["budgets"]
    rows = []
    n = int(cfg["eval"]["lime_sample"])
    tu_truth = prep.tune.meta["priority"].to_numpy()[tune_sc.alert_idx]
    te_truth = truth[test_sc.alert_idx]
    tu_pos = _subsample_alerts(tu_truth, n, seed)
    te_pos = _subsample_alerts(te_truth, n, seed + 1)
    t0 = time.perf_counter()
    lime = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], method="lime",
                                 seed=seed)
    phi_tu, _ = lime.explain(Xtu[tune_sc.alert_idx[tu_pos]])
    phi_te, _ = lime.explain(Xte[test_sc.alert_idx[te_pos]])
    log.info("seed %d: LIME on %d + %d alerts in %.0fs", seed, len(tu_pos), len(te_pos), time.perf_counter() - t0)
    sample_p1 = int((te_truth[te_pos] == "P1").sum())
    tag = {"sample": f"stratified-{len(te_pos)}"}
    for name, tsc, tsc_te in (
        ("XTriage@sample", _restrict(tune_sc, tu_pos), _restrict(test_sc, te_pos)),
        ("B5-LIME@sample", _restrict(tune_sc, tu_pos, phi_tu), _restrict(test_sc, te_pos, phi_te)),
    ):
        eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=tsc)
        m, _ = evaluate_engine(eng, Xte, tsc_te, truth, sample_p1, budgets)
        rows.append({**base, "method": name, **tag, **m})
    m, _ = score_only(_restrict(test_sc, te_pos), truth, sample_p1, budgets)
    rows.append({**base, "method": "B1-score-only@sample", **tag, **m})

    # Anchors-style local rules (RQ3) on the same test sample, learned from all tune alerts
    na = int(cfg["eval"]["anchors_sample"])
    te_pos_a = _subsample_alerts(te_truth, na, seed + 2)
    sample_p1 = int((te_truth[te_pos_a] == "P1").sum())
    t0 = time.perf_counter()
    rcfg = dict(cfg)
    rcfg["rules"] = {**cfg["rules"], "max_train": min(int(cfg["rules"]["max_train"]), 5000)}
    eng_a = XTriageEngine.fit(prep, rcfg, seed, detector=det, explainer=ex, tune_scored=tune_sc, learner="anchors")
    m, _ = evaluate_engine(eng_a, Xte, _restrict(test_sc, te_pos_a), truth, sample_p1, budgets)
    rows.append({**base, "method": "Anchors@sample", "sample": f"stratified-{len(te_pos_a)}", **m})
    eng_r = XTriageEngine.fit(prep, rcfg, seed, detector=det, explainer=ex, tune_scored=tune_sc)
    m, _ = evaluate_engine(eng_r, Xte, _restrict(test_sc, te_pos_a), truth, sample_p1, budgets)
    rows.append({**base, "method": "XTriage@anchor-sample", "sample": f"stratified-{len(te_pos_a)}", **m})
    log.info("seed %d: anchors comparison in %.0fs", seed, time.perf_counter() - t0)
    return rows


def run_detectors(prep: Prepared, cfg: dict, seed: int) -> list[dict]:
    """Repeat XTriage vs score-only ranking with the autoencoder (KernelSHAP) and XGBoost detectors."""
    budgets = cfg["eval"]["budgets"]
    theta = cfg["alert"]["theta"]
    Xtu = prep.tune.X.to_numpy(dtype=np.float32)
    Xte = prep.test.X.to_numpy(dtype=np.float32)
    truth = prep.test.meta["priority"].to_numpy()
    rows = []
    for dtype in cfg["eval"]["detectors"]:
        t0 = time.perf_counter()
        det = fit_detector(prep, cfg, seed, dtype=dtype)
        ex = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], seed=seed)
        slow = ex.algorithm != "TreeSHAP"
        s_tu, s_te = det.score(Xtu), det.score(Xte)
        q_tu, q_te = det.percentile(s_tu), det.percentile(s_te)
        a_tu, a_te = q_tu >= theta, q_te >= theta
        dm = detection_metrics(s_te, a_te, prep.test.meta["is_attack"].to_numpy(), truth)
        tu_pos = np.arange(a_tu.sum())
        te_pos = np.arange(a_te.sum())
        if slow:
            cap = int(cfg["explain"]["max_alerts_slow"])
            tu_pos = _subsample_alerts(prep.tune.meta["priority"].to_numpy()[a_tu], cap, seed)
            te_pos = _subsample_alerts(truth[a_te], cap, seed + 1)
        idx_tu, idx_te = np.where(a_tu)[0][tu_pos], np.where(a_te)[0][te_pos]
        phi_tu, phi0 = ex.explain(Xtu[idx_tu])
        phi_te, _ = ex.explain(Xte[idx_te])
        m_tu = np.zeros_like(a_tu)
        m_tu[idx_tu] = True
        m_te = np.zeros_like(a_te)
        m_te[idx_te] = True
        tsc = Scored(s_tu, q_tu, m_tu, phi_tu, phi0)
        esc = Scored(s_te, q_te, m_te, phi_te, phi0)
        total_p1 = int((truth[idx_te] == "P1").sum()) if slow else int((truth == "P1").sum())
        eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=tsc)
        m, _ = evaluate_engine(eng, Xte, esc, truth, total_p1, budgets)
        b1, _ = score_only(esc, truth, total_p1, budgets)
        base = {"seed": seed, "detector": dtype, "explainer": ex.algorithm,
                "alerts_explained": int(len(idx_te)), **{f"det_{k}": v for k, v in dm.items()},
                "seconds": time.perf_counter() - t0}
        rows.append({**base, "method": "XTriage", **m})
        rows.append({**base, "method": "B1-score-only", **b1})
        log.info("detector %s seed %d: XTriage W@90=%s vs B1 %s", dtype, seed, m.get("workload@90"),
                 b1.get("workload@90"))
    return rows


def summarise(df: pd.DataFrame, by: list[str], metrics: list[str]) -> pd.DataFrame:
    g = df.groupby(by, sort=False)[metrics]
    mean, sd = g.mean(), g.std(ddof=1)
    out = mean.copy()
    for c in metrics:
        out[c] = [f"{m:.4g} ± {s:.2g}" if pd.notna(s) else f"{m:.4g}" for m, s in zip(mean[c], sd[c])]
    return out.reset_index()


def wilcoxon_table(df: pd.DataFrame, reference: str, metrics: dict[str, str]) -> pd.DataFrame:
    """Paired Wilcoxon signed-rank tests (over seeds) of ``reference`` against every other method.

    ``metrics`` maps metric -> 'lower' or 'higher' (which direction is better). Note that with
    five seeds the smallest attainable two-sided p-value is 0.0625 (one-sided 0.03125).
    """
    from scipy.stats import wilcoxon

    rows = []
    ref = df[df["method"] == reference].set_index("seed")
    for method in df["method"].unique():
        if method == reference or "@" in method:
            continue
        other = df[df["method"] == method].set_index("seed")
        seeds = ref.index.intersection(other.index)
        for metric, better in metrics.items():
            if metric not in df.columns:
                continue
            a, b = ref.loc[seeds, metric].astype(float), other.loc[seeds, metric].astype(float)
            ok = a.notna() & b.notna()
            a, b = a[ok], b[ok]
            if len(a) < 2 or np.allclose(a, b):
                p2 = p1 = float("nan")
            else:
                alt = "less" if better == "lower" else "greater"
                p2 = float(wilcoxon(a, b).pvalue)
                p1 = float(wilcoxon(a, b, alternative=alt).pvalue)
            rows.append({"reference": reference, "method": method, "metric": metric, "n": int(len(a)),
                         "ref_mean": float(a.mean()) if len(a) else float("nan"),
                         "other_mean": float(b.mean()) if len(b) else float("nan"),
                         "p_two_sided": p2, "p_one_sided": p1})
    return pd.DataFrame(rows)
