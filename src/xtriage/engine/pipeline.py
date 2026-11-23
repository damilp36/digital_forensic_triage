"""The XTriage engine: S1-S6 wired together, with artifact storage and exact replay."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .. import PRIORITY_ACTION
from ..data.prepare import Prepared, noisy_oracle
from .detector import Detector, build_detector
from .explain import Explainer, top_k
from .guard import apply_guard
from .represent import Representation, band_of
from .rules import RuleList, build_rules, rules_from_dict

log = logging.getLogger(__name__)


@dataclass
class Scored:
    """Detector output for a set of flows plus attributions for the alerts."""

    s: np.ndarray
    q: np.ndarray
    alert: np.ndarray  # bool mask over flows
    phi: np.ndarray  # (n_alerts, d)
    phi0: float
    seconds: dict = field(default_factory=dict)

    @property
    def alert_idx(self) -> np.ndarray:
        return np.where(self.alert)[0]


@dataclass
class Triage:
    rule_priority: np.ndarray
    rule_id: np.ndarray
    is_default: np.ndarray
    band: np.ndarray
    tier: np.ndarray
    contested: np.ndarray
    reason: np.ndarray
    seconds: float = 0.0


class XTriageEngine:
    def __init__(self, cfg: dict, feature_names: list[str], detector: Detector, explainer: Explainer,
                 rep: Representation, rules, parts: tuple[str, ...], guard_cfg: dict, theta: float):
        self.cfg = cfg
        self.feature_names = feature_names
        self.detector = detector
        self.explainer = explainer
        self.rep = rep
        self.rules = rules
        self.parts = tuple(parts)
        self.guard_cfg = dict(guard_cfg)
        self.theta = float(theta)

    # ================================================================ fitting
    @classmethod
    def fit(cls, prep: Prepared, cfg: dict, seed: int, *, detector: Detector | None = None,
            background_idx: int = 0, parts=None, learner: str | None = None, guard: bool | str | None = None,
            explain_method: str | None = None, eta: float | None = None, tune_scored: Scored | None = None,
            explainer: Explainer | None = None):
        """Train S1 (unless given), then S3/S4 on tune-window alerts labelled by the oracle."""
        theta = cfg["alert"]["theta"]
        if detector is None:
            detector = fit_detector(prep, cfg, seed)
        if explainer is None:
            explainer = Explainer.from_config(detector, prep.backgrounds[background_idx], prep.feature_names,
                                              cfg["explain"], method=explain_method, seed=seed)
        Xt = prep.tune.X.to_numpy(dtype=np.float32)
        if tune_scored is None:
            tune_scored = score_and_explain(detector, explainer, Xt, theta)
        ai = tune_scored.alert_idx
        rep = Representation(prep.feature_names, cfg["represent"]["n_bins"], cfg["represent"]["bands"],
                             cfg["explain"]["top_k"], parts or cfg["represent"]["parts"])
        rep.fit(Xt[ai])
        y_clean = prep.tune.meta["priority"].to_numpy()[ai]
        y = noisy_oracle(y_clean, cfg["oracle"]["eta"] if eta is None else eta, seed)
        Z = rep.transform(Xt[ai], tune_scored.phi, tune_scored.q[ai])
        rules = build_rules(cfg["rules"], seed, learner)
        rules.fit(Z, y)
        gcfg = dict(cfg["guard"])
        if isinstance(guard, str):  # a guard mode, e.g. "review"
            gcfg["enabled"], gcfg["mode"] = True, guard
        elif guard is not None:
            gcfg["enabled"] = guard
        eng = cls(cfg, prep.feature_names, detector, explainer, rep, rules, rep.parts, gcfg, theta)
        eng.tune_scored = tune_scored
        eng.tune_labels = y
        return eng

    # ============================================================== inference
    def score(self, X: np.ndarray, parallel: bool = True) -> Scored:
        return score_and_explain(self.detector, self.explainer, X, self.theta, parallel=parallel)

    def triage(self, X_alerts: np.ndarray, phi: np.ndarray, q_alerts: np.ndarray) -> Triage:
        t0 = time.perf_counter()
        Z = self.rep.transform(X_alerts, phi, q_alerts, self.parts)
        prio, rid, is_def = self.rules.apply(Z)
        band = band_of(q_alerts, self.rep.bands)
        tier, contested, reason = apply_guard(prio, is_def, q_alerts, band, self.guard_cfg)
        return Triage(prio, rid, is_def, band, tier, contested, reason, time.perf_counter() - t0)

    def process(self, X: np.ndarray, parallel: bool = True):
        sc = self.score(X, parallel=parallel)
        ai = sc.alert_idx
        tr = self.triage(X[ai], sc.phi, sc.q[ai])
        return sc, tr

    # ================================================================ records
    @property
    def ruleset_version(self) -> str:
        blob = json.dumps({"rules": self.rules.to_dict(), "rep": self.rep.to_dict(), "parts": self.parts,
                           "guard": self.guard_cfg, "theta": self.theta}, sort_keys=True, default=str)
        return f"{self.rules.learner}-{hashlib.sha256(blob.encode()).hexdigest()[:12]}"

    def make_records(self, X: np.ndarray, meta: pd.DataFrame, sc: Scored, tr: Triage,
                     responses: np.ndarray | None = None, responder: str = "oracle",
                     run_id: str = "run") -> list[dict]:
        ai = sc.alert_idx
        k = self.rep.k
        tops = top_k(sc.phi, k) if len(ai) else np.zeros((0, k), dtype=int)
        now = datetime.now(timezone.utc).isoformat()
        id_cols = [c for c in meta.columns if c.startswith("id:")]
        out = []
        for r, i in enumerate(ai):
            m = meta.iloc[i]
            resp = None if responses is None else responses[r]
            rec = {
                "record_type": "triage",
                "alert_id": f"{run_id}:{m['flow_uid']}",
                "flow_uid": m["flow_uid"],
                "event_ts": int(m["ts"]),
                "identifiers": {c[3:]: m[c] for c in id_cols},
                "source_ref": {"file": m["source_file"], "row": int(m["source_row"]),
                               "sha256": m["source_sha256"]},
                "features": dict(zip(self.feature_names, map(float, X[i]))),
                "s": float(sc.s[i]),
                "q": float(sc.q[i]),
                "band": tr.band[r],
                "phi0": float(sc.phi0),
                "phi": [float(v) for v in sc.phi[r]],
                "top_features": [{"feature": self.feature_names[j], "phi": float(sc.phi[r, j])} for j in tops[r]],
                "explainer": self.explainer.algorithm,
                "background_hash": self.explainer.background_hash,
                "rule_id": tr.rule_id[r],
                "rule_text": self.rules.text_of(tr.rule_id[r], self.rep),
                "rule_priority": tr.rule_priority[r],
                "is_default_rule": bool(tr.is_default[r]),
                "contested": bool(tr.contested[r]),
                "guard_reason": tr.reason[r],
                "tier": tr.tier[r],
                "action": PRIORITY_ACTION[tr.tier[r]],
                "model_version": self.detector.version,
                "ruleset_version": self.ruleset_version,
                "processed_at": now,
                "investigator_response": None if resp is None else PRIORITY_ACTION.get(resp, resp),
                "responder": responder if resp is not None else None,
            }
            out.append(rec)
        return out

    # ============================================================== artifacts
    def save_artifacts(self, root: str | Path) -> dict:
        root = Path(root)
        for sub in ("models", "backgrounds", "rulesets"):
            (root / sub).mkdir(parents=True, exist_ok=True)
        mfile = root / "models" / f"{self.detector.version}.joblib"
        if not mfile.exists():
            joblib.dump(self.detector, mfile)
        bfile = root / "backgrounds" / f"{self.explainer.background_hash}.npy"
        if not bfile.exists():
            np.save(bfile, self.explainer.background)
        rfile = root / "rulesets" / f"{self.ruleset_version}.json"
        with open(rfile, "w", encoding="utf-8") as fh:
            json.dump({"rules": self.rules.to_dict(), "rep": self.rep.to_dict(), "parts": list(self.parts),
                       "guard": self.guard_cfg, "theta": self.theta, "explainer": self.explainer.algorithm,
                       "explain_cfg": {k: self.cfg["explain"][k] for k in ("chunk", "top_k")},
                       "ruleset_version": self.ruleset_version}, fh, indent=1, default=str)
        return {"model": str(mfile), "background": str(bfile), "ruleset": str(rfile)}

    @classmethod
    def from_artifacts(cls, root: str | Path, model_version: str, background_hash: str, ruleset_version: str):
        root = Path(root)
        det = joblib.load(root / "models" / f"{model_version}.joblib")
        bg = np.load(root / "backgrounds" / f"{background_hash}.npy")
        with open(root / "rulesets" / f"{ruleset_version}.json", encoding="utf-8") as fh:
            rs = json.load(fh)
        rep = Representation.from_dict(rs["rep"])
        rules: RuleList = rules_from_dict(rs["rules"])
        method = "lime" if rs["explainer"] == "LIME" else "shap"
        ex = Explainer(det, bg, rep.feature_names, method=method, n_jobs=1)
        cfg = {"explain": {"top_k": rep.k}}
        return cls(cfg, rep.feature_names, det, ex, rep, rules, tuple(rs["parts"]), rs["guard"], rs["theta"])


# ===================================================================== helpers


def fit_detector(prep: Prepared, cfg: dict, seed: int, dtype: str | None = None) -> Detector:
    dcfg = dict(cfg["detector"])
    if dtype:
        dcfg["type"] = dtype
    Xs = ys = None
    if dcfg["type"] == "xgboost":
        Xs = prep.tune.X.to_numpy(dtype=np.float32)
        ys = prep.tune.meta["is_attack"].to_numpy().astype(int)
    det = build_detector(dcfg, seed, prep.fit_X, prep.cal_X, Xs, ys)
    return det


def score_and_explain(detector: Detector, explainer: Explainer, X: np.ndarray, theta: float,
                      parallel: bool = True) -> Scored:
    t0 = time.perf_counter()
    s = detector.score(X)
    q = detector.percentile(s)
    alert = q >= theta
    t1 = time.perf_counter()
    phi, phi0 = explainer.explain(X[alert], parallel=parallel)
    t2 = time.perf_counter()
    return Scored(s, q, alert, phi, phi0, {"score": t1 - t0, "explain": t2 - t1})


def replay_record(record: dict, artifacts: str | Path, cache: dict | None = None, rtol: float = 1e-6) -> dict:
    """Re-derive score, attribution, rule and guard decision from a stored record."""
    key = (record["model_version"], record["background_hash"], record["ruleset_version"])
    cache = {} if cache is None else cache
    if key not in cache:
        cache[key] = XTriageEngine.from_artifacts(artifacts, *key)
    eng: XTriageEngine = cache[key]
    x = np.array([[record["features"][f] for f in eng.feature_names]], dtype=np.float32)
    s = eng.detector.score(x)
    q = eng.detector.percentile(s)
    phi, _ = eng.explainer.explain(x, parallel=False)
    tr = eng.triage(x, phi, q)
    checks = {
        "score": bool(np.isclose(s[0], record["s"], rtol=rtol, atol=1e-9)),
        "percentile": bool(np.isclose(q[0], record["q"], atol=1e-12)),
        "attribution": bool(np.allclose(phi[0], np.asarray(record["phi"]), rtol=1e-5, atol=1e-7)),
        "rule": tr.rule_id[0] == record["rule_id"],
        "tier": tr.tier[0] == record["tier"],
    }
    checks["ok"] = all(checks.values())
    return checks
