"""Streaming replay testbed (paper Section IV-A, Fig. 3).

Time-ordered test windows are replayed as a live stream:

  sensor threads --JSON batches--> message queue --> engine (S1-S5) --> ledger writer (S6)

* Flows are partitioned across ``n_sensors`` emulated sensors (by destination address when it
  is available, else by flow id). A shared simulated clock advances in ticks; on each tick every
  sensor publishes the flows it observed in that tick, in fixed-size JSON batches. Alerts
  therefore reach the engine in the order they would arrive in practice, interleaved across
  sensors.
* The engine records the per-stage latencies t1 (scoring + attribution), t2 (rules + guard) and
  t3 (record write), plus end-to-end latency from publication to ledger commit.
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
import zlib

import numpy as np
import pandas as pd

from ..data.loaders import FlowTable
from ..engine.ledger import Ledger
from ..engine.pipeline import XTriageEngine

log = logging.getLogger(__name__)
_STOP = object()


def _partition(meta: pd.DataFrame, n: int) -> np.ndarray:
    key_col = next((c for c in ("id:Destination IP", "id:IPV4_DST_ADDR", "id:Dst IP") if c in meta.columns),
                   "flow_uid")
    return np.array([zlib.crc32(str(v).encode()) % n for v in meta[key_col]])


class Sensor(threading.Thread):
    def __init__(self, sid: int, rows: np.ndarray, ticks: np.ndarray, table: FlowTable, out: queue.Queue,
                 barrier: threading.Barrier, n_ticks: int, batch_size: int):
        super().__init__(daemon=True, name=f"sensor-{sid}")
        self.sid, self.rows, self.ticks, self.table = sid, rows, ticks, table
        self.out, self.barrier, self.n_ticks, self.batch_size = out, barrier, n_ticks, batch_size
        self.published = 0

    def run(self):
        feats = self.table.feature_names
        X = self.table.X.to_numpy(dtype=np.float32)
        uid = self.table.meta["flow_uid"].to_numpy()
        ts = self.table.meta["ts"].to_numpy()
        pos, seq = 0, 0
        for tick in range(self.n_ticks):
            end = pos
            while end < len(self.rows) and self.ticks[end] <= tick:
                end += 1
            for b in range(pos, end, self.batch_size):
                idx = self.rows[b:min(end, b + self.batch_size)]
                msg = json.dumps({"sensor": self.sid, "seq": seq, "published": time.perf_counter(),
                                  "features": feats,
                                  "flows": [{"flow_uid": uid[i], "ts": int(ts[i]), "row": int(i),
                                             "x": X[i].tolist()} for i in idx]})
                self.out.put(msg)
                seq += 1
                self.published += len(idx)
            pos = end
            self.barrier.wait()


def run_testbed(engine: XTriageEngine, table: FlowTable, ledger: Ledger, responses: dict | None = None,
                n_sensors: int = 4, batch_size: int = 256, tick_seconds: float = 60.0, queue_max: int = 64,
                run_id: str = "testbed", flush_every: int = 2000) -> dict:
    ts = table.meta["ts"].to_numpy()
    tick = ((ts - ts.min()) // int(tick_seconds * 1000)).astype(int)
    n_ticks = int(tick.max()) + 1
    part = _partition(table.meta, n_sensors)
    q_in: queue.Queue = queue.Queue(maxsize=queue_max)
    q_rec: queue.Queue = queue.Queue()
    barrier = threading.Barrier(n_sensors)
    sensors = []
    for sid in range(n_sensors):
        rows = np.where(part == sid)[0]
        rows = rows[np.argsort(ts[rows], kind="stable")]
        sensors.append(Sensor(sid, rows, tick[rows], table, q_in, barrier, n_ticks, batch_size))

    lat = {"t1": [], "t2": [], "t3": [], "e2e": [], "alerts_per_batch": []}
    stats = {"batches": 0, "flows": 0, "alerts": 0}
    meta = table.meta
    X_all = table.X.to_numpy(dtype=np.float32)

    def writer():
        buf, pubs = [], []
        while True:
            item = q_rec.get()
            if item is not _STOP:
                recs, published = item
                buf.extend(recs)
                pubs.extend([published] * len(recs))
            if buf and (item is _STOP or len(buf) >= flush_every):
                t0 = time.perf_counter()
                ledger.append(buf)
                t3 = time.perf_counter() - t0
                lat["t3"].append(t3 / len(buf))
                done = time.perf_counter()
                lat["e2e"].extend(done - p for p in pubs)
                buf, pubs = [], []
            if item is _STOP:
                return

    def engine_loop():
        finished = 0
        while finished < n_sensors:
            msg = q_in.get()
            if msg is _STOP:
                finished += 1
                continue
            batch = json.loads(msg)
            rows = np.array([f["row"] for f in batch["flows"]], dtype=int)
            X = np.array([f["x"] for f in batch["flows"]], dtype=np.float32)
            t0 = time.perf_counter()
            sc = engine.score(X, parallel=False)
            t1 = time.perf_counter() - t0
            ai = sc.alert_idx
            tr = engine.triage(X[ai], sc.phi, sc.q[ai])
            stats["batches"] += 1
            stats["flows"] += len(rows)
            stats["alerts"] += len(ai)
            lat["t1"].append(t1 / max(1, len(rows)))
            lat["alerts_per_batch"].append(len(ai))
            if len(ai):
                lat["t2"].append(tr.seconds / len(ai))
                resp = None if responses is None else np.array(
                    [responses.get(meta["flow_uid"].iat[rows[i]]) for i in ai], dtype=object)
                sub_meta = meta.iloc[rows].reset_index(drop=True)
                recs = engine.make_records(X_all[rows], sub_meta, sc, tr, resp, run_id=run_id)
                q_rec.put((recs, batch["published"]))

    def sensor_done(s: Sensor):
        s.join()
        q_in.put(_STOP)

    wt = threading.Thread(target=writer, daemon=True)
    et = threading.Thread(target=engine_loop, daemon=True)
    start = time.perf_counter()
    wt.start()
    et.start()
    for s in sensors:
        s.start()
    closers = [threading.Thread(target=sensor_done, args=(s,), daemon=True) for s in sensors]
    for c in closers:
        c.start()
    for c in closers:
        c.join()
    et.join()
    q_rec.put(_STOP)
    wt.join()
    wall = time.perf_counter() - start

    def pct(v, p):
        return float(np.percentile(v, p) * 1000) if len(v) else float("nan")

    out = {
        **stats,
        "sensors": n_sensors,
        "published": int(sum(s.published for s in sensors)),
        "wall_seconds": wall,
        "flows_per_second": stats["flows"] / wall if wall else float("nan"),
        "t1_ms_per_flow_mean": float(np.mean(lat["t1"]) * 1000) if lat["t1"] else float("nan"),
        "t1_ms_per_flow_p95": pct(lat["t1"], 95),
        "mean_alerts_per_batch": float(np.mean(lat["alerts_per_batch"])) if lat["alerts_per_batch"] else 0.0,
        "t2_ms_per_alert_mean": float(np.mean(lat["t2"]) * 1000) if lat["t2"] else float("nan"),
        "t3_ms_per_record_mean": float(np.mean(lat["t3"]) * 1000) if lat["t3"] else float("nan"),
        "e2e_ms_p50": pct(lat["e2e"], 50),
        "e2e_ms_p95": pct(lat["e2e"], 95),
    }
    log.info("testbed: %s", out)
    return out
