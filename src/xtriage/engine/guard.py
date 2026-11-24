"""S5: disagreement guard.

A decision is *contested* (sent to manual review, tier P2) when
  (i)  only the default (catch-all) rule fired, or
  (ii) the rule's priority conflicts with the score: a P3 (dismiss) rule on a flow with
       q(s) >= p3_max_q, or a P1 (escalate) rule on a flow in the low score band.
Within each tier alerts are ranked by q(s).

What a contested case does to the queue is set by ``mode``:
  * ``conservative`` (default) -- the guard may only *raise* attention: a contested dismissal or a
    catch-all decision becomes P2 (review), but a contested escalation stays P1 and is flagged.
    The guard therefore never hides a potentially severe event behind its own doubt.
  * ``review`` -- every contested case is placed in tier P2, as in the original formulation.
    Kept as an ablation: it demotes true P1 events whenever an escalation rule fires on a
    low-band score.
  * ``calibrated`` -- replaces the fixed triggers (i)/(ii) by an estimated risk. For every
    (rule, score band) cell the tune window gives the share of oracle-P1 events among the alerts
    the cell decided; smoothed towards the overall P1 share,
        leak = (n_P1 + a * prior) / (n + a).
    A non-escalation decision is contested (raised to P2) when leak >= ``tau``; escalation rules on
    low-band scores are flagged as before but keep P1. The table is learned in
    :func:`guard_stats` and stored with the rule set, so replay reproduces it.
"""

from __future__ import annotations

import numpy as np

TIER_RANK = {"P1": 0, "P2": 1, "P3": 2}


def _cell(rule_id, band) -> str:
    return f"{rule_id}|{band}"


def guard_stats(rule_id: np.ndarray, band: np.ndarray, y: np.ndarray) -> dict:
    """Per (rule, band) cell: [alerts, oracle-P1 alerts] on the tune window, plus the P1 prior."""
    y = np.asarray(y, dtype=object)
    cells: dict[str, list[int]] = {}
    for r, b, t in zip(rule_id, band, y):
        c = cells.setdefault(_cell(r, b), [0, 0])
        c[0] += 1
        c[1] += int(t == "P1")
    return {"cells": cells, "prior": float(np.mean(y == "P1")) if len(y) else 0.0}


def leak_risk(rule_id: np.ndarray, band: np.ndarray, gcfg: dict) -> np.ndarray:
    st = gcfg.get("stats") or {"cells": {}, "prior": 0.0}
    a, prior = float(gcfg.get("smoothing", 20.0)), float(st["prior"])
    out = np.empty(len(rule_id))
    for i, (r, b) in enumerate(zip(rule_id, band)):
        n, p1 = st["cells"].get(_cell(r, b), (0, 0))
        out[i] = (p1 + a * prior) / (n + a) if n + a > 0 else prior  # unseen cell -> prior
    return out


def apply_guard(rule_priority: np.ndarray, is_default: np.ndarray, q: np.ndarray, band: np.ndarray,
                gcfg: dict, rule_id: np.ndarray | None = None):
    rule_priority = np.asarray(rule_priority, dtype=object)
    n = len(rule_priority)
    reason = np.full(n, "", dtype=object)
    if not gcfg.get("enabled", True):
        return rule_priority.copy(), np.zeros(n, dtype=bool), reason
    if gcfg.get("mode") == "calibrated":
        assert rule_id is not None, "calibrated guard needs the fired rule ids"
        leak = leak_risk(rule_id, band, gcfg)
        risky = (rule_priority != "P1") & (leak >= float(gcfg.get("tau", 0.01)))
        p1_conflict = (rule_priority == "P1") & (np.asarray(band) == "low")
        reason[risky] = "p1-leak-risk"
        reason[p1_conflict] = "escalate-rule-on-low-score"
        tier = np.where(risky, "P2", rule_priority).astype(object)
        return tier, risky | p1_conflict, reason
    default_hit = np.asarray(is_default, dtype=bool)
    p3_conflict = (rule_priority == "P3") & (np.asarray(q) >= gcfg.get("p3_max_q", 0.99))
    p1_conflict = (rule_priority == "P1") & (np.asarray(band) == "low")
    reason[default_hit] = "default-rule"
    reason[p3_conflict] = "dismiss-rule-on-high-score"
    reason[p1_conflict] = "escalate-rule-on-low-score"
    contested = default_hit | p3_conflict | p1_conflict
    if gcfg.get("mode", "conservative") == "review":
        tier = np.where(contested, "P2", rule_priority).astype(object)
    else:
        raise_ = contested & (rule_priority != "P1")
        tier = np.where(raise_, "P2", rule_priority).astype(object)
    return tier, contested, reason


def queue_order(tier: np.ndarray, q: np.ndarray, s: np.ndarray | None = None) -> np.ndarray:
    """Alert indices in review order: tier P1 > P2 > P3, then descending q(s).

    q(s) saturates at 1.0 for flows scoring above every calibration flow, so the raw score s
    breaks ties.
    """
    ranks = np.array([TIER_RANK.get(t, 1) for t in tier])
    s = np.zeros(len(ranks)) if s is None else np.asarray(s)
    return np.lexsort((-s, -np.asarray(q), ranks))
