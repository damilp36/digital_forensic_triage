"""RQ5: accountability -- streaming testbed run, chain integrity, replay, tamper detection, cost."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.prepare import Prepared, noisy_oracle
from ..engine.ledger import Ledger
from ..engine.pipeline import XTriageEngine, replay_record
from ..testbed.replay import run_testbed

log = logging.getLogger(__name__)


def run_accountability(prep: Prepared, cfg: dict, eng: XTriageEngine, out: Path, seed: int = 0) -> dict:
    out = Path(out)
    ledger_dir = out / "ledger"
    if ledger_dir.exists():
        shutil.rmtree(ledger_dir)
    artifacts = out / "artifacts"
    eng.save_artifacts(artifacts)
    ledger = Ledger(ledger_dir)
    tb = cfg["testbed"]
    table = prep.test
    if tb.get("max_flows") and len(table) > tb["max_flows"]:
        rng = np.random.default_rng(seed)
        keep = np.sort(rng.choice(len(table), int(tb["max_flows"]), replace=False))
        table = table.take(keep)
    responses = dict(zip(table.meta["flow_uid"], noisy_oracle(table.meta["priority"].to_numpy(),
                                                               cfg["oracle"]["eta"], seed)))
    stats = run_testbed(eng, table, ledger, responses, n_sensors=tb["n_sensors"], batch_size=tb["batch_size"],
                        queue_max=tb["queue_max"], run_id=f"{cfg['name']}-seed{seed}")
    ver = ledger.verify()
    df = ledger.read()
    n = len(df)
    recs = [json.loads(p) for p in df["payload"]]
    rng = np.random.default_rng(seed + 3)
    pick = rng.choice(n, min(n, int(cfg["eval"]["replay_sample"])), replace=False) if n else []
    cache: dict = {}
    checks = [replay_record(recs[i], artifacts, cache) for i in pick]
    replay = pd.DataFrame(checks)

    # tamper test on a copy: alter one score, then check that verification pinpoints it
    tamper = {}
    if n > 2:
        tdir = out / "ledger_tampered"
        if tdir.exists():
            shutil.rmtree(tdir)
        shutil.copytree(ledger_dir, tdir)
        tl = Ledger(tdir)
        head = json.loads((tdir / "head.json").read_text())
        first = pd.read_parquet(tdir / head["parts"][0])
        victim = len(first) // 2
        rec = json.loads(first.at[victim, "payload"])
        rec["tier"] = "P3" if rec["tier"] != "P3" else "P1"
        from ..engine.ledger import canonical

        first.at[victim, "payload"] = canonical(rec)
        first.to_parquet(tdir / head["parts"][0], index=False)
        tv = tl.verify()
        tamper = {"tampered_seq": int(first.at[victim, "seq"]), "detected": not tv["ok"],
                  "first_bad_seq": tv["first_bad_seq"]}
        shutil.rmtree(tdir)

    result = {
        "testbed": stats,
        "chain_ok": ver["ok"],
        "records": n,
        "bytes_per_record": ledger.size_bytes() / n if n else float("nan"),
        "contested_rate": float(df["contested"].astype(float).mean()) if n else float("nan"),
        "tier_counts": df["tier"].value_counts().to_dict() if n else {},
        "replay_n": int(len(replay)),
        "replay_success_rate": float(replay["ok"].mean()) if len(replay) else float("nan"),
        "replay_checks": {c: float(replay[c].mean()) for c in replay.columns} if len(replay) else {},
        "tamper": tamper,
        "artifacts": str(artifacts),
        "ledger": str(ledger_dir),
    }
    with open(out / "accountability.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=str)
    log.info("accountability: chain_ok=%s replay=%.3f bytes/record=%.0f", ver["ok"], result["replay_success_rate"],
             result["bytes_per_record"])
    return result
