# XTriage — explainable anomaly detection for digital forensic triage

Implementation of the framework in `docs/Phase2.tex`: an anomaly detector (S1) whose alerts are
explained with SHAP (S2), turned into a SHAP-augmented representation (S3), triaged by induced
IF–THEN rules (S4), checked by a disagreement guard (S5), and written to a hash-chained forensic
ledger (S6). The repository also contains the streaming replay testbed, the evaluation harness
(baselines B1–B5, ablations, stability, limitation probes, accountability), the XFT-Bench exporter,
and a Streamlit analyst dashboard.

## Layout

```
src/xtriage/
  data/loaders.py      NetFlow v3, CICFlowMeter and synthetic loaders (Parquet cache)
  data/prepare.py      time-ordered splits, sampling, investigator oracle (+ noise), background sets
  engine/detector.py   S1  isolation forest | autoencoder | XGBoost (reference); percentile q(s)
  engine/explain.py    S2  interventional TreeSHAP, KernelSHAP, LIME; background hash
  engine/represent.py  S3  z(x) = [quantile bins, SHAP predicates pi_j, score band]
  engine/rules.py      S4  ordered RIPPER (wittgenstein), tree surrogate, Anchors-style local rules
  engine/guard.py      S5  contested cases (default rule / rule-score conflict)
  engine/ledger.py     S6  append-only Parquet ledger, h_i = SHA256(h_{i-1} || canonical(r_i))
  engine/pipeline.py   engine, artifacts (model / background / rule-set versions), exact replay
  testbed/replay.py    sensor threads -> JSON batches -> queue -> engine -> ledger writer
  eval/                metrics, experiments (RQ1/RQ3), stability (RQ2), probes (RQ4),
                       accountability (RQ5), harness + report
  bench/export.py      XFT-Bench export + datasheet
dashboard/app.py       Streamlit: alert queue, explanation view, integrity and metrics
configs/               smoke (synthetic), cic2017, nf_unsw_nb15_v3, nf_cse_cic_ids2018_v3
tests/                 pytest suite
```

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e .[dev]      # Windows (use .venv/bin on Linux/macOS)
.venv/Scripts/python -m pytest -q
```

## Running

```bash
xtriage evaluate --config configs/smoke.yaml        # ~3 min, synthetic data, whole pipeline
xtriage prepare  --config configs/cic2017.yaml      # load + cache + split CIC-IDS2017
xtriage evaluate --config configs/cic2017.yaml      # all experiments, 5 seeds
xtriage evaluate --config configs/cic2017.yaml --only main,stability   # a subset
xtriage stream   --config configs/cic2017.yaml      # testbed -> ledger only
xtriage verify   --ledger runs/cic2017/ledger
xtriage replay   --run runs/cic2017 --n 200
xtriage cross    --train configs/nf_unsw_nb15_v3.yaml --test configs/nf_cse_cic_ids2018_v3.yaml
xtriage dashboard --run runs/cic2017
```

Outputs go to `runs/<name>/`: `results/summary.md` (all tables), CSVs per experiment, figures
(`fig_workload`, `fig_stability`, `fig_noise`), `ledger/`, `artifacts/`, `accountability.json`
and `xft-bench/`.

## Data

| Config | Corpus | Status |
|---|---|---|
| `cic2017` | CIC-IDS2017, CICFlowMeter CSVs (original release) | runs from the local copy |
| `nf_unsw_nb15_v3` | NF-UNSW-NB15-v3 (UQ NetFlow v3) | manual download (see below) |
| `nf_cse_cic_ids2018_v3` | NF-CSE-CIC-IDS2018-v3 | manual download (see below) |

The NetFlow v3 files are on UQ Research Data Manager (links on
<https://staff.itee.uq.edu.au/marius/NIDS_datasets/>), which requires signing in. Put the CSVs directly in
`data/raw/` as `NF-UNSW-NB15-v3.csv` and `NF-CICIDS2018-v3.csv` (the names in the UQ download). The loader takes the identifier
columns (`IPV4_*_ADDR`, `L4_SRC_PORT`, `FLOW_*_MILLISECONDS`) and labels (`Label`, `Attack`) by name;
every other numeric column is a model feature.

For the corrected CIC-IDS2017 labels of Engelen et al., point `configs/cic2017.yaml` at those CSVs;
nothing else changes.

## Design decisions and deviations from the Phase 2 text

* **Isolation-forest score.** s(x) = −E[h(x)] (negative mean isolation depth), a strictly monotone
  transform of scikit-learn's anomaly score, so TreeSHAP is exact: φ₀ + Σφ = s (tested).
* **Background sets.** SHAP is interventional over B (100 benign flows from the fit window);
  B's SHA-256 is stored with every decision.
* **Blocked split for CIC-IDS2017.** Every attack in this corpus occupies one time block of one day,
  so a contiguous tune/test split would put different attack classes in each window. Monday (benign
  only) is the fit window; Tuesday–Friday is cut into 20-minute blocks that alternate between tune
  and test. Some classes still fall on one side only (e.g. DoS GoldenEye appears only in test,
  SQL injection only in tune), which tests unseen classes.
* **Multi-class RIPPER.** wittgenstein's RIPPER is binary, so it is applied JRip-style: classes from
  rarest to most frequent, and the most frequent class becomes the default (catch-all) rule.
* **Guard mode.** The Phase 2 text sends every contested case to manual review (tier P2). Doing so
  demotes true P1 events whenever an escalation rule fires on a low-band score. The default is now
  `conservative`: the guard may only raise attention (contested dismissals and catch-all decisions
  go to P2, contested escalations stay P1 and are flagged). The paper's version is kept as the
  ablation `Abl-guard-review-tier`.
* **Fidelity.** The share of a rule's positively referenced features that are among the alert's
  top-k SHAP features. `fidelity_traffic_conds` counts only conditions on traffic values, because
  SHAP predicates match by construction.
* **Anchors.** Re-implemented over the discrete z space (greedy search for the shortest anchor with
  precision ≥ 0.9 on tune alerts), rather than through the alibi library.
* **Workload@90** counts the P1 events the detector actually alerted on. Detector-level P1 recall
  is reported separately (`det_p1_alerted`). Recall@b is measured against all P1 events in the test
  window.
* **Statistics.** With 5 seeds a Wilcoxon signed-rank test cannot reach p < 0.05 two-sided (minimum
  0.0625). The harness reports both two-sided and one-sided p-values. Use more seeds, or pool
  seeds × datasets, to make significance claims.
* **Evasion probe** perturbs features only (padding, timing, port choice within protocol limits).
  Derived features are adjusted to first order; no traffic is generated.
