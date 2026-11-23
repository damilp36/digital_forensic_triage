"""Evaluation harness: runs RQ1-RQ5 over seeds and writes tables, figures and a summary."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import run_dir
from ..data.loaders import describe, load_dataset
from ..data.prepare import Prepared, prepare
from .accountability import run_accountability
from .experiments import run_detectors, run_main, summarise, wilcoxon_table
from .probes import probe_background, probe_evasion, probe_noise, probe_shift_time, probe_shortcut
from .stability import attribution_grid, faithfulness, stability_sample, stability_tables

log = logging.getLogger(__name__)

ALL_PARTS = ("main", "stability", "probes", "detectors", "accountability", "bench")
MAIN_METRICS = ["det_auroc", "det_auprc", "det_p1_alerted", "alerts", "recall@100", "recall@500", "recall@1000",
                "recall@5000", "workload@90", "workload@90_frac", "ndcg", "ndcg@1000", "macro_f1", "p1_f1",
                "coverage", "fidelity", "fidelity_traffic_conds", "band_consistency", "n_rules", "mean_rule_len", "contested_rate",
                "rule_error_rate", "guard_catch_rate", "severe_errors", "severe_caught"]
TESTS = {"workload@90_frac": "lower", "ndcg": "higher", "recall@1000": "higher", "macro_f1": "higher",
         "fidelity": "higher", "n_rules": "lower"}


def get_prepared(cfg: dict, refresh: bool = False) -> Prepared:
    path = run_dir(cfg) / "prepared"
    if path.exists() and not refresh:
        return Prepared.load(path)
    table = load_dataset(cfg)
    info = describe(table)
    log.info("dataset %s: %s", cfg["name"], {k: info[k] for k in ("rows", "features", "attack_rate", "time_span")})
    prep = prepare(table, cfg)
    prep.info["dataset"] = info
    prep.save(path)
    return prep


def _write(df: pd.DataFrame, path: Path) -> None:
    if df is not None and len(df):
        df.to_csv(path, index=False)


def _figures(res: Path, curves: dict, stab: pd.DataFrame | None, noise: pd.DataFrame | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if curves:
        fig, ax = plt.subplots(figsize=(5, 3.4))
        for name in ("B1-score-only", "B2-xgboost-shap", "B3-raw-rules", "B4-tree-surrogate", "XTriage"):
            if name in curves and len(curves[name]):
                c = curves[name]
                ax.plot(np.arange(1, len(c) + 1) / len(c), c, label=name, lw=2 if name == "XTriage" else 1.2)
        ax.axhline(0.9, color="grey", ls=":", lw=0.8)
        ax.set_xlabel("fraction of alerts reviewed")
        ax.set_ylabel("fraction of P1 alerts found")
        ax.legend(fontsize=7, frameon=False)
        ax.set_xlim(0, 1)
        fig.tight_layout()
        fig.savefig(res / "fig_workload.pdf")
        fig.savefig(res / "fig_workload.png", dpi=160)
        plt.close(fig)
    if stab is not None and len(stab):
        fig, ax = plt.subplots(figsize=(5, 3.2))
        bins = np.linspace(stab["q"].min(), 1.0, 8)
        stab = stab.assign(qbin=pd.cut(stab["q"], bins, include_lowest=True))
        g = stab.groupby("qbin", observed=True)[["jaccard_bg", "jaccard_seed"]].mean()
        x = [iv.mid for iv in g.index]
        ax.plot(x, g["jaccard_bg"], marker="o", label="across background sets")
        ax.plot(x, g["jaccard_seed"], marker="s", label="across detector seeds")
        ax.set_xlabel("score percentile q(s)")
        ax.set_ylabel("top-k Jaccard")
        ax.set_ylim(0, 1.02)
        ax.legend(fontsize=7, frameon=False)
        fig.tight_layout()
        fig.savefig(res / "fig_stability.pdf")
        fig.savefig(res / "fig_stability.png", dpi=160)
        plt.close(fig)
    if noise is not None and len(noise):
        fig, ax = plt.subplots(figsize=(5, 3.2))
        g = noise.groupby("eta")[["macro_f1", "fidelity", "coverage"]].agg(["mean", "std"])
        for m in ("macro_f1", "fidelity", "coverage"):
            ax.errorbar(g.index, g[(m, "mean")], yerr=g[(m, "std")], marker="o", capsize=3, label=m)
        ax.set_xlabel(r"oracle noise $\eta$")
        ax.set_ylim(0, 1.02)
        ax.legend(fontsize=7, frameon=False)
        fig.tight_layout()
        fig.savefig(res / "fig_noise.pdf")
        fig.savefig(res / "fig_noise.png", dpi=160)
        plt.close(fig)


def evaluate(cfg: dict, parts=ALL_PARTS, refresh: bool = False, config_path: str | None = None) -> Path:
    t_start = time.perf_counter()
    out = run_dir(cfg)
    res = out / "results"
    res.mkdir(exist_ok=True)
    prep = get_prepared(cfg, refresh)
    seeds = list(cfg["seeds"])
    with open(res / "data_summary.json", "w", encoding="utf-8") as fh:
        json.dump(prep.info, fh, indent=2, default=str)

    # ---------------------------------------------------------------- RQ1/RQ3
    rows, cache0, curves = [], None, {}
    if any(p in parts for p in ("main", "stability", "probes", "accountability", "bench")):
        run_seeds = seeds if "main" in parts else seeds[:1]
        for sd in run_seeds:
            r, cache = run_main(prep, cfg, sd, curves=curves if sd == seeds[0] else None)
            rows.extend(r)
            if sd == seeds[0]:
                cache0 = cache
            pd.DataFrame(rows).to_csv(res / "main_per_seed.csv", index=False)
        main = pd.DataFrame(rows)
        metrics = [m for m in MAIN_METRICS if m in main.columns]
        _write(summarise(main, ["method"], metrics), res / "main_summary.csv")
        _write(wilcoxon_table(main, "XTriage", TESTS), res / "stats_wilcoxon.csv")

    # -------------------------------------------------------------------- RQ2
    stab = None
    if "stability" in parts or "probes" in parts:
        idx = stability_sample(prep, cache0, int(cfg["eval"]["stability_sample"]))
        grid = attribution_grid(prep, cfg, idx, cache0["detector"])
        X = prep.test.X.to_numpy(dtype=np.float32)[idx]
        q = cache0["test"].q[idx]
        s = cache0["test"].s[idx]
        stab, stab_sum = stability_tables(prep, cfg, idx, grid, cache0["engines"]["XTriage"], q, s)
        _write(stab, res / "stability_per_flow.csv")
        _write(stab_sum, res / "stability_summary.csv")
        if "stability" in parts:
            _write(faithfulness(prep, cfg, cache0["detector"], idx, grid[(seeds[0], 0)]), res / "faithfulness.csv")

    # -------------------------------------------------------------------- RQ4
    noise = None
    if "probes" in parts:
        _write(probe_background(prep, cfg, cache0, idx, grid[(seeds[0], 0)]), res / "probe_background.csv")
        _write(probe_shortcut(prep, cfg, cache0, seeds[0]), res / "probe_shortcut.csv")
        _write(probe_shift_time(prep, cfg, cache0), res / "probe_shift.csv")
        _write(probe_evasion(prep, cfg, cache0), res / "probe_evasion.csv")
        main = pd.DataFrame(rows)
        guard_cols = ["seed", "method", "rule_error_rate", "contested_rate", "guard_catch_rate", "guard_precision",
                      "severe_errors", "severe_caught"]
        _write(main[main["method"].isin(["XTriage", "Abl-no-guard", "B4-tree-surrogate"])][
            [c for c in guard_cols if c in main.columns]], res / "probe_rule_infidelity.csv")
        frames = []
        for sd in cfg["eval"].get("probe_seeds", seeds[:3]):
            if sd == seeds[0]:
                c = cache0
            else:
                _, c = run_main_light(prep, cfg, sd)
            frames.append(probe_noise(prep, cfg, c, sd))
        noise = pd.concat(frames, ignore_index=True)
        _write(noise, res / "probe_noise.csv")

    # -------------------------------------------------------------- detectors
    if "detectors" in parts:
        drows = []
        for sd in cfg["eval"].get("detector_seeds", seeds[:3]):
            drows.extend(run_detectors(prep, cfg, sd))
        det = pd.DataFrame(drows)
        _write(det, res / "detectors_per_seed.csv")
        m = [c for c in ["det_auroc", "det_auprc", "alerts", "alerts_explained", "workload@90_frac", "ndcg",
                         "recall@1000", "macro_f1", "fidelity", "n_rules", "seconds"] if c in det.columns]
        _write(summarise(det, ["detector", "method"], m), res / "detectors_summary.csv")

    # -------------------------------------------------------------------- RQ5
    if "accountability" in parts:
        run_accountability(prep, cfg, cache0["engines"]["XTriage"], out, seed=seeds[0])

    if "bench" in parts:
        from ..bench.export import export_bench

        export_bench(prep, cfg, cache0, out, config_path)

    _figures(res, curves, stab, noise)
    write_report(out, cfg)
    log.info("evaluation finished in %.1f min -> %s", (time.perf_counter() - t_start) / 60, res)
    return res


def run_main_light(prep: Prepared, cfg: dict, seed: int):
    """Detector, SHAP and the XTriage engine only (for probes on extra seeds)."""
    from ..engine.explain import Explainer
    from ..engine.pipeline import XTriageEngine, fit_detector, score_and_explain

    det = fit_detector(prep, cfg, seed)
    ex = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], seed=seed)
    theta = cfg["alert"]["theta"]
    tsc = score_and_explain(det, ex, prep.tune.X.to_numpy(dtype=np.float32), theta)
    esc = score_and_explain(det, ex, prep.test.X.to_numpy(dtype=np.float32), theta)
    eng = XTriageEngine.fit(prep, cfg, seed, detector=det, explainer=ex, tune_scored=tsc)
    return None, {"detector": det, "explainer": ex, "tune": tsc, "test": esc, "engines": {"XTriage": eng}}


# ---------------------------------------------------------------------- report


def _md(df: pd.DataFrame, cols: list[str] | None = None, floatfmt: str = ".3f") -> str:
    if df is None or not len(df):
        return "_(not run)_\n"
    if cols:
        df = df[[c for c in cols if c in df.columns]]

    def fmt(v):
        if isinstance(v, float):
            return "" if np.isnan(v) else format(v, floatfmt)
        return str(v)

    head = "| " + " | ".join(map(str, df.columns)) + " |\n"
    sep = "|" + "|".join("---" for _ in df.columns) + "|\n"
    body = "".join("| " + " | ".join(fmt(v) for v in row) + " |\n" for row in df.itertuples(index=False))
    return head + sep + body


def _read(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def write_report(out: Path, cfg: dict) -> Path:
    res = out / "results"
    parts = [f"# XTriage results -- {cfg['name']}\n"]
    info_path = res / "data_summary.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        parts.append("## Data\n")
        parts.append(f"* windows: {info.get('windows')}\n* tune rows: {info.get('tune_rows')}, "
                     f"test rows: {info.get('test_rows')}\n* test priorities: {info.get('test_priorities')}\n"
                     f"* test classes: {info.get('test_classes')}\n")
    ms = _read(res / "main_summary.csv")
    parts.append("\n## RQ1 triage effectiveness and RQ3 rule quality (mean ± s.d. over seeds)\n\n")
    parts.append(_md(ms, ["method", "det_auroc", "alerts", "recall@1000", "workload@90_frac", "ndcg", "macro_f1",
                          "p1_f1", "coverage", "fidelity", "fidelity_traffic_conds", "n_rules", "mean_rule_len",
                          "contested_rate", "severe_caught"]))
    st = _read(res / "stats_wilcoxon.csv")
    parts.append("\n### Paired Wilcoxon signed-rank tests, XTriage vs. each method (over seeds)\n\n"
                 "With n = 5 seeds the smallest attainable p-value is 0.0625 two-sided and 0.03125 one-sided.\n\n")
    parts.append(_md(st))
    parts.append("\n## RQ2 explanation reliability\n\n")
    parts.append(_md(_read(res / "stability_summary.csv")))
    parts.append("\nDeletion-curve faithfulness (lower AUC = more faithful):\n\n")
    parts.append(_md(_read(res / "faithfulness.csv")))
    parts.append("\n## RQ4 limitation probes\n\n### Background set\n\n")
    parts.append(_md(_read(res / "probe_background.csv")))
    parts.append("\n### Shortcut features\n\n")
    parts.append(_md(_read(res / "probe_shortcut.csv")))
    parts.append("\n### Distribution shift (time)\n\n")
    parts.append(_md(_read(res / "probe_shift.csv")))
    parts.append("\n### Feature-space evasion\n\n")
    parts.append(_md(_read(res / "probe_evasion.csv")))
    parts.append("\n### Rule infidelity and the guard\n\n")
    parts.append(_md(_read(res / "probe_rule_infidelity.csv")))
    nz = _read(res / "probe_noise.csv")
    if nz is not None:
        nz = nz.groupby("eta").mean(numeric_only=True).reset_index().drop(columns=["seed"], errors="ignore")
    parts.append("\n### Oracle noise (mean over probe seeds)\n\n")
    parts.append(_md(nz))
    parts.append("\n## Detector robustness\n\n")
    parts.append(_md(_read(res / "detectors_summary.csv")))
    acc = out / "accountability.json"
    parts.append("\n## RQ5 accountability\n\n")
    if acc.exists():
        a = json.loads(acc.read_text())
        tb = a["testbed"]
        parts.append(
            f"* records: {a['records']}, chain verified: {a['chain_ok']}, tamper detected: "
            f"{a['tamper'].get('detected')} (first bad seq {a['tamper'].get('first_bad_seq')})\n"
            f"* replay success: {a['replay_success_rate']:.3f} over {a['replay_n']} records {a['replay_checks']}\n"
            f"* bytes per record: {a['bytes_per_record']:.0f}; contested rate: {a['contested_rate']:.3f}\n"
            f"* testbed: {tb['sensors']} sensors, {tb['flows']} flows, {tb['alerts']} alerts, "
            f"{tb['flows_per_second']:.0f} flows/s; t1 {tb['t1_ms_per_flow_mean']:.3f} ms/flow, "
            f"t2 {tb['t2_ms_per_alert_mean']:.3f} ms/alert, t3 {tb['t3_ms_per_record_mean']:.3f} ms/record, "
            f"publish-to-ledger latency incl. queueing under max-rate replay p50 {tb['e2e_ms_p50']:.0f} ms / p95 {tb['e2e_ms_p95']:.0f} ms\n")
    else:
        parts.append("_(not run)_\n")
    path = res / "summary.md"
    path.write_text("".join(parts), encoding="utf-8")
    return path
