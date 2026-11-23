"""Command-line interface.

  xtriage prepare   --config C            load data, build splits / oracle / background sets
  xtriage evaluate  --config C [--only main,stability,probes,detectors,accountability,bench]
  xtriage stream    --config C [--seed S] replay the test window through the testbed into a ledger
  xtriage verify    --ledger DIR           re-check the hash chain
  xtriage replay    --run DIR [--n N]      re-derive N ledger decisions from stored artifacts
  xtriage cross     --train C1 --test C2   cross-corpus shift probe (shared feature set)
  xtriage report    --config C             rebuild summary.md from existing results
  xtriage dashboard --run DIR              launch the Streamlit dashboard
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np


def _cfg(args):
    from .config import load_config

    overrides = json.loads(args.set) if getattr(args, "set", None) else None
    return load_config(args.config, overrides)


def cmd_prepare(args):
    from .eval.harness import get_prepared

    cfg = _cfg(args)
    prep = get_prepared(cfg, refresh=True)
    print(json.dumps({k: prep.info[k] for k in ("windows", "tune_rows", "test_rows", "tune_priorities",
                                                 "test_priorities")}, indent=2, default=str))


def cmd_evaluate(args):
    from .eval.harness import ALL_PARTS, evaluate

    cfg = _cfg(args)
    parts = tuple(args.only.split(",")) if args.only else ALL_PARTS
    res = evaluate(cfg, parts, refresh=args.refresh, config_path=args.config)
    print(f"results in {res}")


def cmd_stream(args):
    from .config import run_dir
    from .eval.accountability import run_accountability
    from .eval.harness import get_prepared
    from .engine.pipeline import XTriageEngine

    cfg = _cfg(args)
    prep = get_prepared(cfg)
    eng = XTriageEngine.fit(prep, cfg, args.seed)
    out = run_dir(cfg)
    res = run_accountability(prep, cfg, eng, out, seed=args.seed)
    print(json.dumps(res, indent=2, default=str))


def cmd_verify(args):
    from .engine.ledger import Ledger

    print(json.dumps(Ledger(args.ledger).verify(), indent=2))


def cmd_replay(args):
    from .engine.ledger import Ledger
    from .engine.pipeline import replay_record

    run = Path(args.run)
    recs = [r for r in Ledger(run / "ledger").records() if r.get("record_type") == "triage"]
    rng = np.random.default_rng(0)
    pick = rng.choice(len(recs), min(args.n, len(recs)), replace=False)
    cache = {}
    checks = [replay_record(recs[i], run / "artifacts", cache) for i in pick]
    ok = sum(c["ok"] for c in checks)
    print(f"replayed {len(checks)} records: {ok} reproduced exactly")


def cmd_cross(args):
    from .config import load_config, run_dir
    from .eval.harness import get_prepared
    from .eval.probes import probe_cross_corpus

    a, b = load_config(args.train), load_config(args.test)
    df = probe_cross_corpus(get_prepared(a), get_prepared(b), a, seed=0)
    out = run_dir(a) / "results" / f"probe_cross_{b['name']}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string())


def cmd_report(args):
    from .config import run_dir
    from .eval.harness import write_report

    cfg = _cfg(args)
    print(write_report(run_dir(cfg), cfg))


def cmd_dashboard(args):
    app = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app), "--", "--run", args.run], check=False)


def main(argv=None):
    p = argparse.ArgumentParser(prog="xtriage")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def with_cfg(sp):
        sp.add_argument("--config", required=True)
        sp.add_argument("--set", help='JSON overrides, e.g. \'{"seeds": [0]}\'')
        return sp

    with_cfg(sub.add_parser("prepare")).set_defaults(fn=cmd_prepare)
    e = with_cfg(sub.add_parser("evaluate"))
    e.add_argument("--only")
    e.add_argument("--refresh", action="store_true")
    e.set_defaults(fn=cmd_evaluate)
    s = with_cfg(sub.add_parser("stream"))
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=cmd_stream)
    v = sub.add_parser("verify")
    v.add_argument("--ledger", required=True)
    v.set_defaults(fn=cmd_verify)
    r = sub.add_parser("replay")
    r.add_argument("--run", required=True)
    r.add_argument("--n", type=int, default=200)
    r.set_defaults(fn=cmd_replay)
    c = sub.add_parser("cross")
    c.add_argument("--train", required=True)
    c.add_argument("--test", required=True)
    c.set_defaults(fn=cmd_cross)
    with_cfg(sub.add_parser("report")).set_defaults(fn=cmd_report)
    d = sub.add_parser("dashboard")
    d.add_argument("--run", required=True)
    d.set_defaults(fn=cmd_dashboard)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    for noisy in ("shap", "matplotlib", "numba", "PIL"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    args.fn(args)


if __name__ == "__main__":
    main()
