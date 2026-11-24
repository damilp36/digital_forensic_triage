"""RQ4: limitation probes -- conditions under which explainable triage fails."""

from __future__ import annotations

import copy
import itertools
import logging
import re

import numpy as np
import pandas as pd

from ..data.prepare import Prepared
from ..engine.explain import Explainer
from ..engine.pipeline import XTriageEngine, fit_detector, score_and_explain
from ..engine.represent import band_of
from .experiments import VARIANTS, _restrict, _subsample_alerts, evaluate_engine, resolve_overrides
from .metrics import detection_metrics, jaccard_rows, kendall_rows

EVASION_METHODS = ("XTriage", "Fix-SHAP-gated-bins", "Fix-no-port-bins", "Fix-calibrated-guard")
NOISE_METHODS = ("XTriage", "Fix-label-filter")

log = logging.getLogger(__name__)


def _match(names: list[str], patterns: list[str]) -> list[int]:
    out = []
    for j, n in enumerate(names):
        if any(re.fullmatch(p, n, flags=re.IGNORECASE) for p in patterns):
            out.append(j)
    return out


# ----------------------------------------------------------------- background


def probe_background(prep: Prepared, cfg: dict, cache: dict, idx: np.ndarray, phi_ref: np.ndarray) -> pd.DataFrame:
    """Vary size, time window and traffic mix of B; compare attributions and fired rules with B_0."""
    det, eng = cache["detector"], cache["engines"]["XTriage"]
    k = cfg["explain"]["top_k"]
    X = prep.test.X.to_numpy(dtype=np.float32)[idx]
    q = det.percentile(det.score(X))
    ref = eng.triage(X, phi_ref, q)
    pool = prep.background_pool
    pts = prep.pool_meta["ts"].to_numpy()
    rng = np.random.default_rng(99)
    size = int(cfg["explain"]["background_size"])
    variants = {}
    for n in cfg["eval"]["background_sizes"]:
        variants[f"size={n}"] = pool[rng.choice(len(pool), min(n, len(pool)), replace=False)]
    order = np.argsort(pts)
    half = len(order) // 2
    variants["window=early-fit"] = pool[rng.choice(order[:half], min(size, half), replace=False)]
    variants["window=late-fit"] = pool[rng.choice(order[half:], min(size, len(order) - half), replace=False)]
    Xtu = prep.tune.X.to_numpy(dtype=np.float32)
    ben_tu = np.where(prep.tune.meta["label"].to_numpy() == "Benign")[0]
    variants["mix=tune-benign"] = Xtu[rng.choice(ben_tu, min(size, len(ben_tu)), replace=False)]
    variants["mix=tune-all-traffic"] = Xtu[rng.choice(len(Xtu), min(size, len(Xtu)), replace=False)]
    att_tu = np.where(prep.tune.meta["is_attack"].to_numpy())[0]
    if len(att_tu):
        m = np.concatenate([rng.choice(ben_tu, size // 2, replace=False),
                            rng.choice(att_tu, min(size // 2, len(att_tu)), replace=False)])
        variants["mix=50%-attack"] = Xtu[m]
    rows = []
    for name, bg in variants.items():
        ex = Explainer.from_config(det, bg, prep.feature_names, cfg["explain"], seed=0)
        phi, phi0 = ex.explain(X)
        tr = eng.triage(X, phi, q)
        rows.append({"probe": "background", "variant": name, "n_background": len(bg), "phi0": phi0,
                     "jaccard_vs_ref": float(jaccard_rows(phi, phi_ref, k).mean()),
                     "kendall_vs_ref": float(kendall_rows(phi, phi_ref).mean()),
                     "rule_change": float(np.mean(tr.rule_id != ref.rule_id)),
                     "tier_change": float(np.mean(tr.tier != ref.tier)),
                     "p1_tier_lost": float(np.mean((ref.tier == "P1") & (tr.tier != "P1")))})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------- shortcut


def probe_shortcut(prep: Prepared, cfg: dict, cache: dict, seed: int = 0) -> pd.DataFrame:
    """Remove port and TTL-like features; do detection and explanations collapse together?"""
    drop = [f for f in cfg.get("shortcut_features", []) if f in prep.feature_names]
    if not drop:
        return pd.DataFrame()
    keep = [f for f in prep.feature_names if f not in drop]
    budgets = cfg["eval"]["budgets"]
    truth = prep.test.meta["priority"].to_numpy()
    total_p1 = int((truth == "P1").sum())
    att = prep.test.meta["is_attack"].to_numpy()
    rows = []
    # reliance of the full model on the shortcut features
    sc = cache["test"]
    drop_idx = [prep.feature_names.index(f) for f in drop]
    top1 = np.argmax(sc.phi, axis=1) if len(sc.phi) else np.array([], dtype=int)
    share = np.abs(sc.phi[:, drop_idx]).sum(1) / np.maximum(np.abs(sc.phi).sum(1), 1e-12)
    for label, p in (("full", prep), ("without-shortcuts", prep.subset(keep))):
        if label == "full":
            det, eng, tsc = cache["detector"], cache["engines"]["XTriage"], sc
        else:
            det = fit_detector(p, cfg, seed)
            ex = Explainer.from_config(det, p.backgrounds[0], p.feature_names, cfg["explain"], seed=seed)
            tsc = score_and_explain(det, ex, p.test.X.to_numpy(dtype=np.float32), cfg["alert"]["theta"])
            eng = XTriageEngine.fit(p, cfg, seed, detector=det, explainer=ex)
        dm = detection_metrics(tsc.s, tsc.alert, att, truth)
        m, _ = evaluate_engine(eng, p.test.X.to_numpy(dtype=np.float32), tsc, truth, total_p1, budgets)
        row = {"probe": "shortcut", "variant": label, "dropped": ";".join(drop), **dm,
               **{k: m[k] for k in ("workload@90", "workload@90_frac", "ndcg", "macro_f1", "coverage", "n_rules",
                                    "fidelity") if k in m}}
        if label == "full":
            row["top1_is_shortcut"] = float(np.isin(top1, drop_idx).mean()) if len(top1) else float("nan")
            row["shortcut_attr_share"] = float(share.mean()) if len(share) else float("nan")
            labels = prep.test.meta["label"].to_numpy()[sc.alert_idx]
            for cls in pd.unique(labels):
                msk = labels == cls
                row[f"shortcut_share[{cls}]"] = float(share[msk].mean())
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------- shift


def probe_shift_time(prep: Prepared, cfg: dict, cache: dict) -> pd.DataFrame:
    """Early vs late half of the test window, same models."""
    eng, sc = cache["engines"]["XTriage"], cache["test"]
    budgets = cfg["eval"]["budgets"]
    X = prep.test.X.to_numpy(dtype=np.float32)
    truth = prep.test.meta["priority"].to_numpy()
    ts = prep.test.meta["ts"].to_numpy()
    cut = np.median(ts)
    ai = sc.alert_idx
    rows = []
    for name, sel in (("early-test", ts < cut), ("late-test", ts >= cut)):
        pos = np.where(sel[ai])[0]
        total_p1 = int(((truth == "P1") & sel).sum())
        dm = detection_metrics(sc.s[sel], sc.alert[sel], prep.test.meta["is_attack"].to_numpy()[sel], truth[sel])
        m, _ = evaluate_engine(eng, X, sc, truth, total_p1, budgets, alert_subset=pos)
        rows.append({"probe": "shift-time", "variant": name, **dm,
                     **{k: m[k] for k in ("workload@90_frac", "ndcg", "macro_f1", "coverage", "contested_rate",
                                          "rule_error_rate") if k in m},
                     "classes": ";".join(sorted(pd.unique(prep.test.meta["label"].to_numpy()[sel])))})
    return pd.DataFrame(rows)


def probe_cross_corpus(train: Prepared, test: Prepared, cfg: dict, seed: int = 0) -> pd.DataFrame:
    """Train detector + rules on one corpus, test on another with the same feature set."""
    common = [f for f in train.feature_names if f in test.feature_names]
    a, b = train.subset(common), test.subset(common)
    budgets = cfg["eval"]["budgets"]
    det = fit_detector(a, cfg, seed)
    ex = Explainer.from_config(det, a.backgrounds[0], common, cfg["explain"], seed=seed)
    eng = XTriageEngine.fit(a, cfg, seed, detector=det, explainer=ex)
    rows = []
    for name, p in (("in-corpus", a), ("cross-corpus", b)):
        X = p.test.X.to_numpy(dtype=np.float32)
        truth = p.test.meta["priority"].to_numpy()
        sc = score_and_explain(det, ex, X, cfg["alert"]["theta"])
        dm = detection_metrics(sc.s, sc.alert, p.test.meta["is_attack"].to_numpy(), truth)
        m, _ = evaluate_engine(eng, X, sc, truth, int((truth == "P1").sum()), budgets)
        rows.append({"probe": "shift-corpus", "variant": f"{name}:{a.name}->{p.name}", **dm, **m})
    return pd.DataFrame(rows)


# -------------------------------------------------------------------- evasion


def perturb(X: np.ndarray, names: list[str], ecfg: dict, kind: str, value) -> np.ndarray:
    """Feature-space perturbation of attacker-controllable features (within protocol limits)."""
    Xp = X.copy()
    if kind == "padding":
        for j in _match(names, ecfg.get("padding_len_regex", [])):
            Xp[:, j] = np.minimum(Xp[:, j] + value * (Xp[:, j] > 0), 1514)
        for tot, cnt in ecfg.get("padding_total", {}).items():
            if tot in names and cnt in names:
                Xp[:, names.index(tot)] += value * X[:, names.index(cnt)]
    elif kind == "timing":
        for j in _match(names, ecfg.get("timing_mult_regex", [])):
            Xp[:, j] = Xp[:, j] * value
        for j in _match(names, ecfg.get("timing_div_regex", [])):
            Xp[:, j] = np.where(Xp[:, j] > 0, Xp[:, j] / value, Xp[:, j])
    elif kind == "port":
        for f in ecfg.get("port_features", []):
            if f in names:
                Xp[:, names.index(f)] = value
    return Xp


def probe_evasion(prep: Prepared, cfg: dict, cache: dict, n: int = 2000, seed: int = 0) -> pd.DataFrame:
    """Do rules stop firing faster than the score changes?  (Feature-space sensitivity only.)
    Run for XTriage and for the representation / guard fixes, on the same perturbed flows."""
    det, ex, sc = cache["detector"], cache["explainer"], cache["test"]
    truth = prep.test.meta["priority"].to_numpy()
    ai = sc.alert_idx
    att = np.where(truth[ai] != "P3")[0]
    if len(att) == 0:
        return pd.DataFrame()
    pos = att[_subsample_alerts(truth[ai][att], n, seed)]
    idx = ai[pos]
    X = prep.test.X.to_numpy(dtype=np.float32)[idx]
    ecfg = cfg["evasion"]
    variants = [("padding", v) for v in ecfg.get("padding_bytes", [])] + \
               [("timing", v) for v in ecfg.get("timing_factors", [])] + \
               [("port", v) for v in ecfg.get("ports", []) if ecfg.get("port_features")]
    perturbed = {}
    for kind, v in variants:
        Xp = perturb(X, prep.feature_names, ecfg, kind, v)
        if np.allclose(Xp, X):
            continue
        s = det.score(Xp)
        q = det.percentile(s)
        phi, _ = ex.explain(Xp)
        perturbed[(kind, v)] = (Xp, s, q, phi)
    rows = []
    for method in EVASION_METHODS:
        eng = cache["engines"].get(method)
        if eng is None:
            continue
        ref = eng.triage(X, sc.phi[pos], sc.q[idx])
        p1 = ref.tier == "P1"
        for (kind, v), (Xp, s, q, phi) in perturbed.items():
            still = q >= cfg["alert"]["theta"]
            tr = eng.triage(Xp, phi, q)
            rows.append({
                "probe": "evasion", "method": method, "variant": f"{kind}={v}", "n": len(idx),
                "mean_abs_dq": float(np.mean(np.abs(q - sc.q[idx]))),
                "mean_ds": float(np.mean(s - sc.s[idx])),
                "evaded_detection": float(np.mean(~still)),
                "rule_changed": float(np.mean(tr.rule_id != ref.rule_id)),
                "tier_changed": float(np.mean(tr.tier != ref.tier)),
                "tier_changed_still_alerted": float(np.mean((tr.tier != ref.tier)[still])) if still.any() else np.nan,
                "p1_downgraded": float(np.mean(tr.tier[p1] != "P1")) if p1.any() else np.nan,
                "became_contested": float(np.mean(tr.contested & ~ref.contested)),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- oracle noise


def probe_noise(prep: Prepared, cfg: dict, cache: dict, seed: int) -> pd.DataFrame:
    det, ex, tsc, sc = cache["detector"], cache["explainer"], cache["tune"], cache["test"]
    truth = prep.test.meta["priority"].to_numpy()
    X = prep.test.X.to_numpy(dtype=np.float32)
    rows = []
    for method, eta in itertools.product(NOISE_METHODS, cfg["eval"]["eta_sweep"]):
        parts, learner, guard, ov = VARIANTS[method]
        eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=tsc, eta=eta,
                                parts=parts, learner=learner, guard=guard, overrides=resolve_overrides(ov, cfg))
        m, _ = evaluate_engine(eng, X, sc, truth, int((truth == "P1").sum()), cfg["eval"]["budgets"])
        rows.append({"probe": "oracle-noise", "method": method, "variant": f"eta={eta}", "eta": eta, "seed": seed,
                     "labels_filtered": getattr(eng.rules, "filtered", 0),
                     **{k: m[k] for k in ("macro_f1", "macro_f1_rules", "p1_f1", "coverage", "n_rules", "mean_rule_len",
                                          "fidelity", "workload@90_frac", "ndcg", "contested_rate", "guard_catch_rate")}})
    return pd.DataFrame(rows)


# ------------------------------------------------------------- guard trade-off


def probe_guard(prep: Prepared, cfg: dict, cache: dict) -> pd.DataFrame:
    """W3: contested rate vs. severe errors caught as the calibrated guard's tau varies, with the
    fixed-trigger guard and no guard as reference points."""
    sc = cache["test"]
    truth = prep.test.meta["priority"].to_numpy()
    X = prep.test.X.to_numpy(dtype=np.float32)
    total_p1 = int((truth == "P1").sum())
    keep = ("workload@90_frac", "ndcg", "macro_f1", "p1_f1", "contested_rate", "guard_catch_rate",
            "guard_precision", "severe_errors", "severe_caught")
    rows = []
    for name in ("Abl-no-guard", "XTriage"):
        if name in cache["engines"]:
            m, _ = evaluate_engine(cache["engines"][name], X, sc, truth, total_p1, cfg["eval"]["budgets"])
            rows.append({"probe": "guard", "variant": name, "tau": np.nan, **{k: m.get(k) for k in keep}})
    cal = cache["engines"].get("Fix-calibrated-guard")
    if cal is not None:
        for tau in cfg["eval"]["guard_taus"]:
            eng = copy.copy(cal)
            eng.guard_cfg = {**cal.guard_cfg, "tau": tau}
            m, _ = evaluate_engine(eng, X, sc, truth, total_p1, cfg["eval"]["budgets"])
            rows.append({"probe": "guard", "variant": "calibrated", "tau": tau, **{k: m.get(k) for k in keep}})
    return pd.DataFrame(rows)


# ------------------------------------------------------------ alert threshold


def probe_theta(prep: Prepared, cfg: dict, cache: dict, seed: int) -> pd.DataFrame:
    """W1: how many P1 events reach triage at all, and what triage does with them, as theta varies.
    SHAP is computed once at the lowest theta and restricted for the higher ones."""
    det, ex = cache["detector"], cache["explainer"]
    thetas = sorted(cfg["eval"]["theta_sweep"])
    Xtu = prep.tune.X.to_numpy(dtype=np.float32)
    Xte = prep.test.X.to_numpy(dtype=np.float32)
    truth = prep.test.meta["priority"].to_numpy()
    att = prep.test.meta["is_attack"].to_numpy()
    tsc = score_and_explain(det, ex, Xtu, thetas[0])
    esc = score_and_explain(det, ex, Xte, thetas[0])
    rows = []
    for th in thetas:
        t_sc = _restrict(tsc, np.where(tsc.q[tsc.alert_idx] >= th)[0])
        e_sc = _restrict(esc, np.where(esc.q[esc.alert_idx] >= th)[0])
        dm = detection_metrics(e_sc.s, e_sc.alert, att, truth)
        eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=t_sc,
                                overrides={"alert": {"theta": th}})
        m, _ = evaluate_engine(eng, Xte, e_sc, truth, int((truth == "P1").sum()), cfg["eval"]["budgets"])
        rows.append({"probe": "theta", "variant": f"theta={th}", "theta": th, "seed": seed,
                     "alerts": int(e_sc.alert.sum()), "det_p1_alerted": dm.get("p1_alerted"),
                     **{k: m.get(k) for k in ("recall@1000", "workload@90", "workload@90_frac", "ndcg",
                                              "macro_f1", "p1_f1", "contested_rate")}})
    return pd.DataFrame(rows)


# -------------------------------------------------- detector size vs stability


def probe_forest_size(prep: Prepared, cfg: dict, idx: np.ndarray) -> pd.DataFrame:
    """W6: does a larger isolation forest make SHAP explanations agree across retraining seeds?"""
    if cfg["detector"]["type"] != "iforest":
        return pd.DataFrame()
    X = prep.test.X.to_numpy(dtype=np.float32)[idx]
    k = cfg["explain"]["top_k"]
    seeds = cfg["eval"]["stability_seeds"]
    rows = []
    for n_est in cfg["eval"]["forest_sizes"]:
        c = copy.deepcopy(cfg)
        c["detector"]["n_estimators"] = int(n_est)
        phis, qs = {}, {}
        for sd in seeds:
            det = fit_detector(prep, c, sd)
            ex = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, c["explain"], seed=sd)
            phis[sd], _ = ex.explain(X)
            qs[sd] = det.percentile(det.score(X))
        pairs = list(itertools.combinations(seeds, 2))
        jac = np.mean([jaccard_rows(phis[a], phis[b], k) for a, b in pairs], axis=0)
        tau = np.mean([kendall_rows(phis[a], phis[b]) for a, b in pairs], axis=0)
        dq = np.mean([np.abs(qs[a] - qs[b]) for a, b in pairs], axis=0)
        band = band_of(qs[seeds[0]], cfg["represent"]["bands"])
        row = {"probe": "forest-size", "n_estimators": int(n_est), "n": len(idx),
               "jaccard_seed": float(jac.mean()), "kendall_seed": float(tau.mean()),
               "mean_abs_dq_seed": float(dq.mean())}
        for b in ("low", "medium", "high"):
            if (band == b).any():
                row[f"jaccard_seed[{b}]"] = float(jac[band == b].mean())
        rows.append(row)
        log.info("forest size %d: seed Jaccard %.3f", n_est, row["jaccard_seed"])
    return pd.DataFrame(rows)
