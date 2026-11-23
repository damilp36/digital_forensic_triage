"""S6: forensic triage record -- an append-only, hash-chained ledger stored as Parquet.

Each record r_i is serialised as canonical JSON (sorted keys, no whitespace) and chained:
    h_i = SHA256( h_{i-1} || canonical(r_i) ),   h_0 = 64 * "0"
Any change to an earlier record, its order, or a deletion breaks every later hash.

Layout of a ledger directory:
    head.json            -- {"n": int, "last_hash": str, "parts": [file, ...]}
    part-000000.parquet  -- seq, prev_hash, hash, record_type, payload (+ query columns)
    .lock                -- exclusive lock while appending (engine and dashboard may both write)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

GENESIS = "0" * 64
QUERY_COLUMNS = ["alert_id", "flow_uid", "event_ts", "s", "q", "tier", "rule_id", "contested",
                 "investigator_response", "responder"]


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_clean(v) for v in o.tolist()]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def canonical(record: dict) -> str:
    return json.dumps(_clean(record), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def chain_hash(prev: str, payload: str) -> str:
    return hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.head_file = self.path / "head.json"
        if not self.head_file.exists():
            self._write_head({"n": 0, "last_hash": GENESIS, "parts": []})

    # ------------------------------------------------------------------ head
    def _read_head(self) -> dict:
        with open(self.head_file, encoding="utf-8") as fh:
            return json.load(fh)

    def _write_head(self, head: dict) -> None:
        tmp = self.head_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(head, fh)
        os.replace(tmp, self.head_file)

    @contextmanager
    def _lock(self, timeout: float = 30.0):
        lock = self.path / ".lock"
        start = time.time()
        while True:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError:
                if time.time() - start > timeout:
                    raise TimeoutError(f"ledger lock held: {lock}")
                time.sleep(0.02)
        try:
            yield
        finally:
            os.close(fd)
            os.remove(lock)

    # ---------------------------------------------------------------- append
    def append(self, records: list[dict]) -> list[str]:
        if not records:
            return []
        with self._lock():
            head = self._read_head()
            prev, seq0 = head["last_hash"], head["n"]
            rows, hashes = [], []
            for i, rec in enumerate(records):
                payload = canonical(rec)
                h = chain_hash(prev, payload)
                row = {"seq": seq0 + i, "prev_hash": prev, "hash": h,
                       "record_type": rec.get("record_type", "triage"), "payload": payload}
                for c in QUERY_COLUMNS:
                    v = rec.get(c)
                    row[c] = None if v is None else (v if isinstance(v, (int, float, bool)) else str(v))
                rows.append(row)
                hashes.append(h)
                prev = h
            part = f"part-{len(head['parts']):06d}.parquet"
            df = pd.DataFrame(rows)
            for c in ("s", "q"):
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df["contested"] = df["contested"].astype("boolean")
            df.to_parquet(self.path / part, index=False)
            head["parts"].append(part)
            head["n"] = seq0 + len(records)
            head["last_hash"] = prev
            self._write_head(head)
        return hashes

    # ------------------------------------------------------------------ read
    def read(self, payloads: bool = True) -> pd.DataFrame:
        head = self._read_head()
        if not head["parts"]:
            return pd.DataFrame(columns=["seq", "prev_hash", "hash", "record_type", "payload"] + QUERY_COLUMNS)
        cols = None if payloads else ["seq", "prev_hash", "hash", "record_type"] + QUERY_COLUMNS
        frames = [pd.read_parquet(self.path / p, columns=cols) for p in head["parts"]]
        return pd.concat(frames, ignore_index=True)

    def records(self) -> list[dict]:
        return [json.loads(p) for p in self.read()["payload"]]

    def verify(self) -> dict:
        """Recompute the chain. Returns {'ok', 'n', 'first_bad_seq', 'last_hash'}."""
        head = self._read_head()
        df = self.read()
        prev = GENESIS
        for i, (seq, ph, h, payload) in enumerate(zip(df["seq"], df["prev_hash"], df["hash"], df["payload"])):
            if seq != i or ph != prev or chain_hash(prev, payload) != h:
                return {"ok": False, "n": len(df), "first_bad_seq": int(i), "last_hash": prev}
            prev = h
        ok = prev == head["last_hash"] and len(df) == head["n"]
        return {"ok": bool(ok), "n": len(df), "first_bad_seq": None if ok else len(df), "last_hash": prev}

    def size_bytes(self) -> int:
        return sum((self.path / p).stat().st_size for p in self._read_head()["parts"])

    def __len__(self) -> int:
        return self._read_head()["n"]
