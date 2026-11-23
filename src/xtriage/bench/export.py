"""XFT-Bench export: the explained-triage dataset released with the paper.

Layout of ``<run>/xft-bench/``:
    flows.parquet        every test flow: ids, provenance, label, oracle priority (clean + noisy),
                         score s, percentile q, alert flag, rule fired, tier, guard status
    shap.parquet         long format: flow_uid, detector_seed, background, phi_0 .. phi_{d-1}
                         (all alerts of the seed-0 detector x 3 seeds x 5 background sets)
    features.parquet     raw model features of every test flow
    splits.json          split strategy, windows, sample sizes, background hashes
    rulesets/            rule sets (JSON) of every exported configuration
    datasheet.md         datasheet (Gebru et al. style)
    regenerate.md        how to rebuild the benchmark from the upstream corpora
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .. import __version__
from ..data.prepare import Prepared, noisy_oracle
from ..engine.explain import Explainer
from ..engine.pipeline import fit_detector

log = logging.getLogger(__name__)


def export_bench(prep: Prepared, cfg: dict, cache: dict, out: Path, config_path: str | None = None) -> Path:
    out = Path(out) / "xft-bench"
    out.mkdir(parents=True, exist_ok=True)
    det, eng, sc = cache["detector"], cache["engines"]["XTriage"], cache["test"]
    X = prep.test.X.to_numpy(dtype=np.float32)
    meta = prep.test.meta
    ai = sc.alert_idx
    tr = eng.triage(X[ai], sc.phi, sc.q[ai])

    flows = meta.copy()
    flows["priority_noisy"] = noisy_oracle(meta["priority"].to_numpy(), cfg["oracle"]["eta"], 0)
    flows["s"], flows["q"], flows["alert"] = sc.s, sc.q, sc.alert
    for col, vals in (("rule_id", tr.rule_id), ("rule_priority", tr.rule_priority), ("tier", tr.tier),
                      ("contested", tr.contested), ("guard_reason", tr.reason), ("band", tr.band)):
        full = np.full(len(flows), None, dtype=object)
        full[ai] = vals
        flows[col] = full
    flows["rule_text"] = [eng.rules.text_of(r, eng.rep) if r is not None else None for r in flows["rule_id"]]
    flows["model_version"] = det.version
    flows["ruleset_version"] = eng.ruleset_version
    flows.to_parquet(out / "flows.parquet", index=False)
    prep.test.X.assign(flow_uid=meta["flow_uid"].to_numpy()).to_parquet(out / "features.parquet", index=False)

    # SHAP stability grid for every alert
    frames = []
    phi_cols = [f"phi:{f}" for f in prep.feature_names]
    for sd in cfg["eval"]["stability_seeds"]:
        d = det if sd == det.seed else fit_detector(prep, cfg, sd)
        for b, bg in enumerate(prep.backgrounds):
            if sd == det.seed and b == 0:
                phi, phi0 = sc.phi, sc.phi0
            else:
                ex = Explainer.from_config(d, bg, prep.feature_names, cfg["explain"], seed=sd)
                phi, phi0 = ex.explain(X[ai])
            f = pd.DataFrame(phi.astype(np.float32), columns=phi_cols)
            f.insert(0, "phi0", np.float32(phi0))
            f.insert(0, "background_hash", prep.info["background_hashes"][b])
            f.insert(0, "background", b)
            f.insert(0, "detector_seed", sd)
            f.insert(0, "s", d.score(X[ai]).astype(np.float32))
            f.insert(0, "flow_uid", meta["flow_uid"].to_numpy()[ai])
            frames.append(f)
            log.info("xft-bench: seed %d background %d done", sd, b)
    pd.concat(frames, ignore_index=True).to_parquet(out / "shap.parquet", index=False)

    (out / "rulesets").mkdir(exist_ok=True)
    for name, e in cache["engines"].items():
        with open(out / "rulesets" / f"{name}.json", "w", encoding="utf-8") as fh:
            json.dump({"method": name, "ruleset_version": e.ruleset_version, "rules": e.rules.to_dict(),
                       "readable": [e.rules.text(r, e.rep) for r in getattr(e.rules, "rules", [])],
                       "representation": e.rep.to_dict(), "guard": e.guard_cfg}, fh, indent=1, default=str)
    with open(out / "splits.json", "w", encoding="utf-8") as fh:
        json.dump(prep.info, fh, indent=2, default=str)
    if config_path:
        shutil.copy(config_path, out / "config.yaml")
    _write_datasheet(out, prep, cfg, flows, sc)
    log.info("xft-bench exported to %s", out)
    return out


def _write_datasheet(out: Path, prep: Prepared, cfg: dict, flows: pd.DataFrame, sc) -> None:
    pri = flows["priority"].value_counts().to_dict()
    alerts = int(flows["alert"].sum())
    classes = flows["label"].value_counts().to_dict()
    text = f"""# XFT-Bench datasheet -- {prep.name}

Generated {datetime.now(timezone.utc).date().isoformat()} by xtriage {__version__}.

## Motivation
XFT-Bench is an *explained-triage* dataset: for every test flow of an upstream intrusion-detection
corpus it records the anomaly score, SHAP attributions under several background sets and
detector seeds, the triage rule that fired, the guard decision and the oracle priority. It exists so
that the faithfulness, stability and actionability of explanations can be compared across studies
on identical alerts.

## Composition
* Upstream corpus: `{cfg['dataset']['loader']}` files {cfg['dataset'].get('files')}
* Test flows: {len(flows)}; alerts (q >= {cfg['alert']['theta']}): {alerts}
* Classes: {classes}
* Oracle priorities (clean): {pri}
* Features: {len(prep.feature_names)} (identifiers excluded from the model input)
* SHAP grid: {len(cfg['eval']['stability_seeds'])} detector seeds x {len(prep.backgrounds)} background sets of
  {cfg['explain']['background_size']} benign flows (hashes in `splits.json`).

## Collection and preprocessing
Split strategy `{cfg['split']['strategy']}`; windows {prep.info.get('windows')}. Undefined feature values
(NaN, +-inf) are replaced by -1. Benign traffic in the tune/test windows is sampled at
{cfg['sample']['test'].get('benign_fraction')}; attack classes are capped at
{cfg['sample']['test'].get('attack_cap_per_class')} flows per class. The detector is
`{cfg['detector']['type']}` trained only on benign flows from the earliest window.

## Labels
`label` is the upstream attack class. `priority` is a documented oracle mapping (P1 escalate, P2 review,
P3 dismiss): {cfg['priority_map']}. `priority_noisy` flips a fraction eta = {cfg['oracle']['eta']} at random to
simulate analyst error. The oracle only approximates human judgement.

## Uses and limitations
Intended for research on explanation stability, rule fidelity and triage workload. Lab corpora may not
reflect production networks; flow records carry no payloads; upstream labelling errors are inherited.
Not suitable for training production detectors.

## Licence
Derived data; subject to the licence of the upstream corpus. Regenerate with `regenerate.md`.
"""
    (out / "datasheet.md").write_text(text, encoding="utf-8")
    (out / "regenerate.md").write_text(
        "# Regenerating XFT-Bench\n\n"
        "1. Obtain the upstream corpus files listed in `config.yaml` (`dataset.files`).\n"
        "2. `pip install -e .` in the xtriage repository.\n"
        "3. `xtriage evaluate --config config.yaml --only main,bench`\n\n"
        "Splits, samples and background sets are deterministic given `seed` in the config.\n",
        encoding="utf-8")
