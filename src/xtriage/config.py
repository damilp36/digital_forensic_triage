"""Configuration loading with defaults and deep merge."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "name": "experiment",
    "seed": 0,  # data-preparation seed (splits, samples, background sets)
    "seeds": [0, 1, 2, 3, 4],  # run seeds (detector, oracle noise, rule subsample)
    "run_dir": "runs",
    "dataset": {
        "loader": "netflow_v3",  # netflow_v3 | cicflowmeter | synthetic
        "base_dir": ".",
        "files": [],
        "cache_dir": "data/cache",
        "label_col": "Label",
        "attack_col": None,  # column holding the attack class (NetFlow v3: Attack)
        "time_col": None,
        "time_format": None,  # cic2017 | ms | iso
        "id_cols": [],
        "drop_cols": [],
        "benign_labels": ["BENIGN", "Benign", "benign", "0"],
        "max_rows": None,  # optional cap when loading (debug)
        "chunk_rows": 1000000,  # CSV rows read per chunk
        "benign_keep": None,  # keep this deterministic fraction of benign rows at load (large corpora)
        "synthetic": {"n": 60000},
    },
    "priority_map": {"P1": [], "P2": [], "default_attack": "P2"},
    "split": {
        "strategy": "time",  # time | blocked
        "fractions": [0.4, 0.3, 0.3],  # fit / tune / test (time strategy)
        "fit_until": None,  # timestamp string or fraction (blocked strategy)
        "block_minutes": 20,
    },
    "sample": {
        "fit_benign": 100000,
        "calibration": 50000,
        "background_pool": 20000,
        "tune": {"benign_fraction": 1.0, "attack_cap_per_class": None, "max_rows": None},
        "test": {"benign_fraction": 1.0, "attack_cap_per_class": None, "max_rows": None},
    },
    "detector": {
        "type": "iforest",  # iforest | autoencoder | xgboost
        "n_estimators": 100,
        "max_samples": 256,
        "ae_hidden": [32, 8, 32],
        "ae_max_iter": 60,
        "xgb_n_estimators": 200,
        "xgb_max_depth": 6,
    },
    "explain": {
        "method": "shap",  # shap | lime
        "background_size": 100,
        "n_backgrounds": 5,
        "top_k": 5,
        "n_jobs": -1,
        "chunk": 400,
        "kernel_background": 50,
        "kernel_nsamples": 200,
        "lime_num_samples": 1000,
        "max_alerts_slow": 3000,  # cap for KernelSHAP / LIME runs
    },
    "alert": {"theta": 0.95},
    "represent": {"n_bins": 5, "bands": [0.99, 0.999], "parts": ["disc", "why", "band"],
                  "exclude": [], "gate_disc": False},
    "rules": {
        "learner": "ripper",  # ripper | tree | anchors
        "max_conds": 4,
        "max_rules": 40,
        "max_train": 15000,
        "k": 2,
        "tree_depth": 4,
        "tree_min_leaf": 20,
        "anchor_precision": 0.9,
        "anchor_min_support": 10,
        "label_filter": False,  # drop oracle labels an out-of-fold forest finds unlikely (noise)
        "label_filter_min_prob": 0.2,
    },
    # mode: conservative | review | calibrated (tau and smoothing are used by calibrated only)
    "guard": {"enabled": True, "mode": "conservative", "p3_max_q": 0.99, "tau": 0.01, "smoothing": 20.0},
    "oracle": {"eta": 0.0},
    "shortcut_features": [],
    "evasion": {
        "padding_len_regex": [],  # per-packet size features: + delta bytes (capped at 1514)
        "padding_total": {},  # total-bytes feature -> its packet-count feature: + delta * packets
        "timing_mult_regex": [],  # durations / inter-arrival times: x factor
        "timing_div_regex": [],  # rates (bytes/s, packets/s): / factor
        "port_features": [],
        "padding_bytes": [16, 64, 256],
        "timing_factors": [0.5, 2.0, 5.0],
        "ports": [80, 443],
    },
    "testbed": {"n_sensors": 4, "batch_size": 256, "queue_max": 64, "max_flows": None},
    "eval": {
        "budgets": [100, 500, 1000, 5000],
        "stability_sample": 600,
        "stability_seeds": [0, 1, 2],
        "faithfulness_sample": 300,
        "lime_sample": 1500,
        "anchors_sample": 3000,
        "replay_sample": 500,
        "eta_sweep": [0.0, 0.1, 0.2, 0.3],
        "background_sizes": [10, 50, 100, 500],
        "detectors": ["autoencoder", "xgboost"],
        "export_shap_all_flows": False,
        "guard_taus": [0.002, 0.005, 0.01, 0.02, 0.05, 0.1],
        "theta_sweep": [0.9, 0.95, 0.99],
        "forest_sizes": [100, 300, 1000],
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def load_config(path: str | Path | None = None, overrides: dict | None = None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    if path is not None:
        with open(path, "r", encoding="utf-8") as fh:
            cfg = deep_merge(cfg, yaml.safe_load(fh) or {})
    if overrides:
        cfg = deep_merge(cfg, overrides)
    return cfg


def run_dir(cfg: dict) -> Path:
    path = Path(cfg["run_dir"]) / cfg["name"]
    path.mkdir(parents=True, exist_ok=True)
    return path
