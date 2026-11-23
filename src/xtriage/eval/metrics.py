"""Metrics for RQ1-RQ5 (paper Table II)."""

from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

RELEVANCE = {"P1": 2, "P2": 1, "P3": 0}


# ----------------------------------------------------------------- detection


def detection_metrics(s: np.ndarray, alert: np.ndarray, is_attack: np.ndarray, priority: np.ndarray) -> dict:
    is_attack = np.asarray(is_attack, dtype=bool)
    p1 = np.asarray(priority) == "P1"
    out = {
        "flows": int(len(s)),
        "alerts": int(alert.sum()),
        "alert_rate": float(alert.mean()),
        "alert_precision": float(is_attack[alert].mean()) if alert.any() else float("nan"),
        "attack_recall": float(alert[is_attack].mean()) if is_attack.any() else float("nan"),
        "p1_alerted": float(alert[p1].mean()) if p1.any() else float("nan"),
        "benign_alerts": int((alert & ~is_attack).sum()),
    }
    if 0 < is_attack.sum() < len(is_attack):
        out["auroc"] = float(roc_auc_score(is_attack, s))
        out["auprc"] = float(average_precision_score(is_attack, s))
    if 0 < p1.sum() < len(p1):
        out["auroc_p1"] = float(roc_auc_score(p1, s))
        out["auprc_p1"] = float(average_precision_score(p1, s))
    return out


# -------------------------------------------------------------------- triage


def ndcg(relevance_in_order: np.ndarray, k: int | None = None) -> float:
    rel = np.asarray(relevance_in_order, dtype=float)
    ideal = np.sort(rel)[::-1]
    if k is not None:
        rel, ideal = rel[:k], ideal[:k]
    disc = 1.0 / np.log2(np.arange(2, len(rel) + 2))
    idcg = float(np.sum((2 ** ideal - 1) * disc))
    return float(np.sum((2 ** rel - 1) * disc) / idcg) if idcg > 0 else float("nan")


def triage_metrics(order: np.ndarray, alert_priority: np.ndarray, total_p1: int, budgets=(100, 500, 1000, 5000),
                   target: float = 0.9) -> dict:
    """``order``: alert indices in review order; ``alert_priority``: ground-truth priority per alert."""
    pr = np.asarray(alert_priority)[order]
    is_p1 = pr == "P1"
    cum = np.cumsum(is_p1)
    n_alert_p1 = int(is_p1.sum())
    out = {"alerts": int(len(order)), "p1_alerts": n_alert_p1}
    for b in budgets:
        found = int(cum[min(b, len(cum)) - 1]) if len(cum) else 0
        out[f"recall@{b}"] = found / total_p1 if total_p1 else float("nan")
    if n_alert_p1:
        need = int(np.ceil(target * n_alert_p1))
        w = int(np.searchsorted(cum, need) + 1)
        out["workload@90"] = w
        out["workload@90_frac"] = w / len(order)
        # mean rank of P1 alerts (lower is better)
        out["p1_mean_rank_frac"] = float(np.mean(np.where(is_p1)[0]) / len(order))
    else:
        out["workload@90"] = float("nan")
        out["workload@90_frac"] = float("nan")
    rel = np.array([RELEVANCE[p] for p in pr])
    out["ndcg"] = ndcg(rel)
    out["ndcg@1000"] = ndcg(rel, 1000)
    return out


def workload_curve(order: np.ndarray, alert_priority: np.ndarray) -> np.ndarray:
    pr = np.asarray(alert_priority)[order]
    cum = np.cumsum(pr == "P1")
    return cum / max(1, cum[-1]) if len(cum) else cum


# --------------------------------------------------------------------- rules


def rule_metrics(tier: np.ndarray, rule_priority: np.ndarray, truth: np.ndarray, is_default: np.ndarray,
                 rule_features: list[list[str]], top_sets: list[set], q: np.ndarray, bands: list[float],
                 contested: np.ndarray, n_rules: int, mean_len: float) -> dict:
    truth = np.asarray(truth)
    labels = ["P1", "P2", "P3"]
    fired = ~np.asarray(is_default, dtype=bool)
    fid = [len(set(f) & t) / len(f) for f, t, ok in zip(rule_features, top_sets, fired) if ok and f]
    rp = np.asarray(rule_priority)
    q = np.asarray(q)
    band_ok = np.where(rp == "P1", q >= bands[0], np.where(rp == "P3", q < bands[1], True))
    err = rp != truth
    severe = (truth == "P1") & (rp == "P3")
    contested = np.asarray(contested, dtype=bool)
    return {
        "macro_f1": float(f1_score(truth, tier, labels=labels, average="macro", zero_division=0)),
        "macro_f1_rules": float(f1_score(truth, rp, labels=labels, average="macro", zero_division=0)),
        "p1_f1": float(f1_score(truth, tier, labels=["P1"], average="macro", zero_division=0)),
        "accuracy": float(np.mean(tier == truth)),
        "coverage": float(fired.mean()) if len(fired) else float("nan"),
        "fidelity": float(np.mean(fid)) if fid else 0.0,
        "band_consistency": float(np.mean(band_ok)) if len(band_ok) else float("nan"),
        "n_rules": int(n_rules),
        "mean_rule_len": float(mean_len),
        "contested_rate": float(contested.mean()) if len(contested) else float("nan"),
        "rule_error_rate": float(err.mean()) if len(err) else float("nan"),
        "guard_catch_rate": float(contested[err].mean()) if err.any() else float("nan"),
        "guard_precision": float(err[contested].mean()) if contested.any() else float("nan"),
        "severe_errors": int(severe.sum()),
        "severe_caught": float(contested[severe].mean()) if severe.any() else float("nan"),
    }


# ----------------------------------------------------------------- stability


def topk_sets(phi: np.ndarray, k: int) -> list[set]:
    from ..engine.explain import top_k

    return [set(r) for r in top_k(phi, k)] if len(phi) else []


def jaccard_rows(a: np.ndarray, b: np.ndarray, k: int) -> np.ndarray:
    sa, sb = topk_sets(a, k), topk_sets(b, k)
    return np.array([len(x & y) / len(x | y) for x, y in zip(sa, sb)])


def kendall_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.empty(len(a))
    for i in range(len(a)):
        t = kendalltau(a[i], b[i]).statistic
        out[i] = 0.0 if np.isnan(t) else t
    return out


def deletion_curve(score_fn, X: np.ndarray, orders: np.ndarray, baseline: np.ndarray, steps: int = 10) -> np.ndarray:
    """Normalised score after replacing the first m features (m = 0..steps) by benign baseline values.

    Returns an (n, steps + 1) array; 1 = unchanged score, 0 = score of the all-baseline flow.
    A faithful attribution order makes the curve fall quickly (small area).
    """
    X = np.asarray(X, dtype=np.float32)
    s_full = score_fn(X)
    s_base = float(score_fn(baseline[None, :].astype(np.float32))[0])
    denom = np.where(np.abs(s_full - s_base) < 1e-12, 1e-12, s_full - s_base)
    out = np.ones((len(X), steps + 1))
    Xm = X.copy()
    rows = np.arange(len(X))
    for m in range(1, steps + 1):
        j = orders[:, m - 1]
        Xm[rows, j] = baseline[j]
        out[:, m] = (score_fn(Xm) - s_base) / denom
    return out
