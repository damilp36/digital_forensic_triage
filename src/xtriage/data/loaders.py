"""Dataset loaders.

Every loader returns a :class:`FlowTable` with
  * ``X``    -- numeric model features (float32); identifiers are never included,
  * ``meta`` -- identifiers and provenance kept for the evidence record:
               flow_uid, ts (epoch ms), label (attack class, "Benign" for benign),
               is_attack, source_file, source_row, source_sha256 and the raw id columns.

Supported formats
  * ``netflow_v3``  -- UQ NetFlow v3 datasets (NF-UNSW-NB15-v3, NF-CSE-CIC-IDS2018-v3, 53 features)
  * ``cicflowmeter`` -- CICFlowMeter CSVs (CIC-IDS2017 original or corrected, CSE-CIC-IDS2018)
  * ``synthetic``   -- small NetFlow-like generator used by the tests and the smoke config
"""

from __future__ import annotations

import glob
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

NETFLOW_V3_IDS = [
    "IPV4_SRC_ADDR",
    "IPV4_DST_ADDR",
    "L4_SRC_PORT",
    "FLOW_START_MILLISECONDS",
    "FLOW_END_MILLISECONDS",
]


@dataclass
class FlowTable:
    name: str
    X: pd.DataFrame
    meta: pd.DataFrame

    @property
    def feature_names(self) -> list[str]:
        return list(self.X.columns)

    def __len__(self) -> int:
        return len(self.X)

    def take(self, idx) -> "FlowTable":
        idx = np.asarray(idx)
        return FlowTable(
            self.name,
            self.X.iloc[idx].reset_index(drop=True),
            self.meta.iloc[idx].reset_index(drop=True),
        )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def sha256_file(path: str | Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _resolve_files(ds: dict) -> list[Path]:
    base = Path(ds.get("base_dir", "."))
    out: list[Path] = []
    for pattern in ds.get("files", []):
        matches = sorted(glob.glob(str(base / pattern)))
        if not matches:
            raise FileNotFoundError(f"No files match {base / pattern}")
        out.extend(Path(m) for m in matches)
    return out


def normalise_label(value) -> str:
    text = str(value)
    text = text.replace("\x96", "-").replace("–", "-").replace("�", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _to_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.apply(pd.to_numeric, errors="coerce")
    arr = out.to_numpy(dtype=np.float64)
    arr[~np.isfinite(arr)] = np.nan
    out = pd.DataFrame(arr, columns=out.columns)
    # Undefined values (e.g. CICFlowMeter rates for zero-duration flows) become -1.
    out = out.fillna(-1.0)
    return out.astype(np.float32)


def parse_cic2017_time(series: pd.Series) -> np.ndarray:
    """CIC-IDS2017 timestamps: day-first dates, 12-hour clock without AM/PM.

    The capture ran 08:00-17:00 local time, so hours 1-7 are afternoon hours.
    Monday's file carries seconds, the other days only minutes.
    """
    text = series.astype(str).str.strip()
    parsed = pd.to_datetime(text, format="%d/%m/%Y %H:%M:%S", errors="coerce")
    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(text[missing], format="%d/%m/%Y %H:%M", errors="coerce")
    hours = parsed.dt.hour
    parsed = parsed + pd.to_timedelta(np.where(hours < 8, 12, 0), unit="h")
    return (parsed.astype("int64") // 1_000_000).to_numpy()


def _parse_time(series: pd.Series, fmt: str | None) -> np.ndarray:
    if fmt == "cic2017":
        return parse_cic2017_time(series)
    if fmt == "ms":
        return pd.to_numeric(series, errors="coerce").fillna(0).astype("int64").to_numpy()
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return (parsed.astype("int64") // 1_000_000).to_numpy()


# ---------------------------------------------------------------------------
# loaders
# ---------------------------------------------------------------------------


def keep_benign_row(rows: np.ndarray, fraction: float) -> np.ndarray:
    """Deterministic benign subsample: a row is kept iff a fixed hash of its file row number falls
    below ``fraction``. Independent of chunk boundaries, so the kept set is reproducible."""
    h = (rows.astype(np.uint64) * np.uint64(2654435761) + np.uint64(97)) % np.uint64(1 << 32)
    return h.astype(np.float64) / float(1 << 32) < fraction


def _read_chunks(path: Path, ds: dict):
    max_rows = ds.get("max_rows")
    chunk_rows = int(ds.get("chunk_rows", 1_000_000))
    reader = pd.read_csv(path, encoding="latin-1", low_memory=False, nrows=max_rows, chunksize=chunk_rows)
    start = 0
    for df in reader:
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~pd.Index(df.columns).duplicated()]
        df["__row"] = np.arange(start, start + len(df))
        start += len(df)
        yield df


def _load_csv_files(name: str, ds: dict, label_col: str, attack_col: str | None,
                    time_col: str | None, time_format: str | None, id_cols: list[str]) -> FlowTable:
    """Read CSVs in chunks (float32 features), optionally keeping only a deterministic fraction
    ``benign_keep`` of benign rows. All attack rows are always kept."""
    files = _resolve_files(ds)
    benign = {normalise_label(b).lower() for b in ds.get("benign_labels", [])}
    drop_cols = set(ds.get("drop_cols", []))
    benign_keep = ds.get("benign_keep")
    frames_x, frames_m = [], []
    for path in files:
        log.info("loading %s", path)
        digest = sha256_file(path)
        n_read, k0 = 0, len(frames_m)
        for df in _read_chunks(path, ds):
            n_read += len(df)
            lab_src = attack_col if attack_col and attack_col in df.columns else label_col
            df = df[df[lab_src].notna()]
            labels = df[lab_src].map(normalise_label)
            is_benign = labels.str.lower().isin(benign)
            if benign_keep is not None and benign_keep < 1:
                keep = ~is_benign.to_numpy() | keep_benign_row(df["__row"].to_numpy(), float(benign_keep))
                df, labels, is_benign = df[keep], labels[keep], is_benign[keep]
            df = df.reset_index(drop=True)
            labels = labels.where(~is_benign, "Benign").reset_index(drop=True)
            meta = pd.DataFrame({
                "source_file": path.name,
                "source_row": df["__row"].to_numpy(),
                "label": labels.to_numpy(),
                "is_attack": (~is_benign).to_numpy(),
            })
            meta["source_sha256"] = digest
            meta["ts"] = _parse_time(df[time_col], time_format) if time_col else df["__row"].to_numpy()
            for col in id_cols:
                if col in df.columns:
                    meta["id:" + col] = df[col].astype(str).to_numpy()
            excluded = set(id_cols) | {label_col, "__row"} | drop_cols
            if attack_col:
                excluded.add(attack_col)
            if time_col:
                excluded.add(time_col)
            feat = df[[c for c in df.columns if c not in excluded]]
            frames_x.append(_to_numeric_features(feat))
            frames_m.append(meta)
        log.info("  %s: read %d rows, kept %d", path.name, n_read, sum(len(m) for m in frames_m[k0:]))
    X = pd.concat(frames_x, ignore_index=True)
    meta = pd.concat(frames_m, ignore_index=True)
    # Drop columns that are not numeric anywhere (all sentinel) -- typically stray text.
    all_missing = (X == -1.0).all(axis=0)
    if all_missing.any():
        log.info("dropping non-numeric columns: %s", list(X.columns[all_missing]))
        X = X.loc[:, ~all_missing]
    bad_ts = meta["ts"] < 0
    if bad_ts.any():
        log.warning("dropping %d rows with unparseable timestamps", int(bad_ts.sum()))
        X, meta = X[~bad_ts].reset_index(drop=True), meta[~bad_ts].reset_index(drop=True)
    meta["flow_uid"] = name + ":" + meta["source_file"] + ":" + meta["source_row"].astype(str)
    return FlowTable(name, X, meta)


def load_cicflowmeter(name: str, ds: dict) -> FlowTable:
    id_cols = ds.get("id_cols") or ["Flow ID", "Source IP", "Source Port", "Destination IP",
                                     "Src IP", "Src Port", "Dst IP"]
    return _load_csv_files(name, ds, ds.get("label_col", "Label"), ds.get("attack_col"),
                           ds.get("time_col", "Timestamp"), ds.get("time_format"), id_cols)


def load_netflow_v3(name: str, ds: dict) -> FlowTable:
    id_cols = ds.get("id_cols") or NETFLOW_V3_IDS
    return _load_csv_files(name, ds, ds.get("label_col", "Label"), ds.get("attack_col") or "Attack",
                           ds.get("time_col") or "FLOW_START_MILLISECONDS", ds.get("time_format") or "ms",
                           [c for c in id_cols if c != (ds.get("time_col") or "FLOW_START_MILLISECONDS")])


SYNTH_FEATURES = [
    "L4_DST_PORT", "PROTOCOL", "IN_BYTES", "OUT_BYTES", "IN_PKTS", "OUT_PKTS",
    "FLOW_DURATION_MILLISECONDS", "MIN_TTL", "MAX_TTL", "LONGEST_FLOW_PKT", "SHORTEST_FLOW_PKT",
    "SRC_TO_DST_IAT_AVG", "DST_TO_SRC_IAT_AVG", "TCP_FLAGS", "NUM_PKTS_UP_TO_128_BYTES",
    "RETRANSMITTED_IN_PKTS",
]


def load_synthetic(name: str, ds: dict, seed: int = 0) -> FlowTable:
    """NetFlow-like synthetic traffic with five attack classes appearing after 30% of the timeline."""
    n = int(ds.get("synthetic", {}).get("n", 60000))
    rng = np.random.default_rng(seed)
    ts = np.sort(rng.integers(1_600_000_000_000, 1_600_000_000_000 + 7 * 86_400_000, n))
    common_ports = np.array([80, 443, 53, 22, 25, 123, 8080])
    feats = {
        "L4_DST_PORT": rng.choice(common_ports, n, p=[0.35, 0.35, 0.15, 0.05, 0.04, 0.03, 0.03]).astype(float),
        "PROTOCOL": rng.choice([6, 17], n, p=[0.8, 0.2]).astype(float),
        "IN_PKTS": rng.poisson(12, n) + 1.0,
        "OUT_PKTS": rng.poisson(10, n) + 1.0,
        "FLOW_DURATION_MILLISECONDS": rng.lognormal(6, 1.2, n),
        "MIN_TTL": rng.choice([64, 128], n).astype(float),
        "LONGEST_FLOW_PKT": rng.normal(1200, 150, n).clip(60, 1514),
        "SHORTEST_FLOW_PKT": rng.normal(60, 5, n).clip(40, 200),
        "SRC_TO_DST_IAT_AVG": rng.lognormal(3, 0.7, n),
        "DST_TO_SRC_IAT_AVG": rng.lognormal(3, 0.7, n),
        "TCP_FLAGS": rng.choice([27, 31, 24, 26], n).astype(float),
        "RETRANSMITTED_IN_PKTS": rng.poisson(0.2, n).astype(float),
    }
    feats["IN_BYTES"] = feats["IN_PKTS"] * rng.normal(500, 80, n).clip(60)
    feats["OUT_BYTES"] = feats["OUT_PKTS"] * rng.normal(700, 120, n).clip(60)
    feats["MAX_TTL"] = feats["MIN_TTL"]
    feats["NUM_PKTS_UP_TO_128_BYTES"] = np.floor(feats["IN_PKTS"] * rng.uniform(0.1, 0.4, n))
    X = pd.DataFrame(feats)[SYNTH_FEATURES]
    labels = np.array(["Benign"] * n, dtype=object)
    late = np.where(ts >= np.quantile(ts, 0.3))[0]
    n_att = int(0.08 * n)
    att_idx = rng.choice(late, n_att, replace=False)
    classes = rng.choice(["Exploits", "Backdoor", "Reconnaissance", "DoS", "Fuzzers"], n_att,
                         p=[0.15, 0.1, 0.3, 0.3, 0.15])
    labels[att_idx] = classes
    for cls in np.unique(classes):
        idx = att_idx[classes == cls]
        m = len(idx)
        if cls == "Exploits":
            X.loc[idx, "OUT_BYTES"] = rng.lognormal(12, 0.5, m)
            X.loc[idx, "L4_DST_PORT"] = rng.choice([445, 139, 3389], m)
        elif cls == "Backdoor":
            X.loc[idx, "L4_DST_PORT"] = rng.integers(20000, 60000, m)
            X.loc[idx, "FLOW_DURATION_MILLISECONDS"] = rng.lognormal(11, 0.5, m)
        elif cls == "Reconnaissance":
            X.loc[idx, "L4_DST_PORT"] = rng.integers(1, 1024, m)
            X.loc[idx, ["IN_PKTS", "OUT_PKTS"]] = 1.0
            X.loc[idx, "IN_BYTES"] = 44.0
            X.loc[idx, "OUT_BYTES"] = 40.0
            X.loc[idx, "FLOW_DURATION_MILLISECONDS"] = rng.uniform(0, 2, m)
            X.loc[idx, "TCP_FLAGS"] = 2.0
        elif cls == "DoS":
            X.loc[idx, "IN_PKTS"] = rng.poisson(400, m)
            X.loc[idx, "IN_BYTES"] = X.loc[idx, "IN_PKTS"] * 60
            X.loc[idx, "SRC_TO_DST_IAT_AVG"] = rng.uniform(0, 0.5, m)
        elif cls == "Fuzzers":
            X.loc[idx, "LONGEST_FLOW_PKT"] = rng.uniform(1400, 1514, m)
            X.loc[idx, "SHORTEST_FLOW_PKT"] = rng.uniform(1, 30, m)
            X.loc[idx, "RETRANSMITTED_IN_PKTS"] = rng.poisson(5, m)
    meta = pd.DataFrame({
        "source_file": "synthetic.csv",
        "source_row": np.arange(n),
        "label": labels,
        "is_attack": labels != "Benign",
        "source_sha256": hashlib.sha256(f"synthetic-{seed}-{n}".encode()).hexdigest(),
        "ts": ts,
        "id:IPV4_SRC_ADDR": [f"10.0.{i % 250}.{(i * 7) % 250}" for i in range(n)],
        "id:IPV4_DST_ADDR": [f"192.168.{(i * 3) % 250}.{i % 200}" for i in range(n)],
    })
    meta["flow_uid"] = name + ":synthetic.csv:" + meta["source_row"].astype(str)
    return FlowTable(name, X.astype(np.float32), meta)


LOADERS = {"cicflowmeter": load_cicflowmeter, "netflow_v3": load_netflow_v3}


def load_dataset(cfg: dict, use_cache: bool = True) -> FlowTable:
    """Load (and cache as Parquet) the dataset described by ``cfg['dataset']``."""
    ds = cfg["dataset"]
    name = cfg["name"]
    if ds["loader"] == "synthetic":
        return load_synthetic(name, ds, seed=cfg.get("seed", 0))
    cache_dir = Path(ds.get("cache_dir", "data/cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(json.dumps(ds, sort_keys=True, default=str).encode()).hexdigest()[:10]
    xf, mf = cache_dir / f"{name}-{key}-X.parquet", cache_dir / f"{name}-{key}-meta.parquet"
    if use_cache and xf.exists() and mf.exists():
        return FlowTable(name, pd.read_parquet(xf), pd.read_parquet(mf))
    table = LOADERS[ds["loader"]](name, ds)
    table.X.to_parquet(xf, index=False)
    table.meta.to_parquet(mf, index=False)
    log.info("cached %s rows x %s features to %s", len(table), table.X.shape[1], cache_dir)
    return table


def describe(table: FlowTable) -> dict:
    t0, t1 = int(table.meta["ts"].min()), int(table.meta["ts"].max())
    return {
        "rows": len(table),
        "features": table.X.shape[1],
        "attack_rate": float(table.meta["is_attack"].mean()),
        "classes": table.meta["label"].value_counts().to_dict(),
        "time_span": [datetime.utcfromtimestamp(t0 / 1000).isoformat(),
                      datetime.utcfromtimestamp(t1 / 1000).isoformat()],
    }
