"""XTriage analyst dashboard (Streamlit).

    streamlit run dashboard/app.py -- --run runs/cic2017
    # or: xtriage dashboard --run runs/cic2017

Views
  1. Alert queue        -- ordered by tier (P1 > P2 > P3), then score percentile q(s)
  2. Explanation        -- SHAP attributions, the rule that fired, guard status, evidence reference;
                           escalate / review / dismiss decisions are appended to the same ledger
  3. Integrity/metrics  -- hash-chain verification, replay of stored decisions, harness results
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from xtriage import PRIORITY_ACTION  # noqa: E402
from xtriage.engine.ledger import Ledger  # noqa: E402
from xtriage.engine.pipeline import replay_record  # noqa: E402

ACTION_TIER = {v: k for k, v in PRIORITY_ACTION.items()}
TIER_RANK = {"P1": 0, "P2": 1, "P3": 2}


def _args():
    p = argparse.ArgumentParser()
    p.add_argument("--run", default=str(ROOT / "runs" / "cic2017"))
    a, _ = p.parse_known_args()
    return Path(a.run)


RUN = _args()
st.set_page_config(page_title="XTriage", layout="wide")


@st.cache_data(show_spinner=False)
def load_index(ledger_dir: str, n: int) -> pd.DataFrame:
    df = Ledger(ledger_dir).read(payloads=False)
    return df


def queue_frame(df: pd.DataFrame) -> pd.DataFrame:
    tri = df[df["record_type"] == "triage"].copy()
    dec = df[df["record_type"] == "decision"]
    tri["analyst_decision"] = None
    if len(dec):
        last = dec.sort_values("seq").groupby("alert_id").tail(1).set_index("alert_id")
        tri["analyst_decision"] = tri["alert_id"].map(last["investigator_response"])
    tri["effective_tier"] = [ACTION_TIER.get(d, t) if isinstance(d, str) else t
                             for d, t in zip(tri["analyst_decision"], tri["tier"])]
    tri["rank"] = tri["effective_tier"].map(TIER_RANK)
    tri = tri.sort_values(["rank", "q", "s"], ascending=[True, False, False])
    tri["event_time"] = pd.to_datetime(tri["event_ts"].astype("int64"), unit="ms")
    return tri


def payload_of(ledger: Ledger, seq: int) -> dict:
    df = ledger.read()
    return json.loads(df.loc[df["seq"] == seq, "payload"].iloc[0])


available = {p.parent.parent.name: p.parent.parent for p in sorted((ROOT / "runs").glob("*/ledger/head.json"))}
if available:
    names = list(available)
    default = names.index(RUN.name) if RUN.name in names else 0
    RUN = available[st.sidebar.selectbox("Run", names, index=default)]
if not (RUN / "ledger" / "head.json").exists():
    st.error(f"No ledger in {RUN} yet. `xtriage evaluate` writes it at the accountability stage (after the "
             f"seed experiments); `xtriage stream --config ... --set '{{\"name\": \"<run>\"}}'` writes one directly.")
    st.stop()

ledger = Ledger(RUN / "ledger")
index = load_index(str(RUN / "ledger"), len(ledger))
queue = queue_frame(index)

st.title("XTriage — explainable forensic triage")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Alerts", f"{len(queue):,}")
c2.metric("P1 escalate", int((queue["effective_tier"] == "P1").sum()))
c3.metric("Contested", int(queue["contested"].fillna(False).astype(bool).sum()))
c4.metric("Analyst decisions", int((index["record_type"] == "decision").sum()))

tab_q, tab_e, tab_i = st.tabs(["Alert queue", "Explanation", "Integrity and metrics"])

# ------------------------------------------------------------------ queue
with tab_q:
    f1, f2, f3 = st.columns([2, 1, 1])
    tiers = f1.multiselect("Tier", ["P1", "P2", "P3"], default=["P1", "P2", "P3"])
    only_contested = f2.checkbox("Contested only")
    undecided = f3.checkbox("Undecided only")
    view = queue[queue["effective_tier"].isin(tiers)]
    if only_contested:
        view = view[view["contested"].fillna(False).astype(bool)]
    if undecided:
        view = view[view["analyst_decision"].isna()]
    cols = ["seq", "effective_tier", "q", "s", "rule_id", "contested", "event_time", "flow_uid",
            "investigator_response", "analyst_decision"]
    sel = st.dataframe(view[cols].head(2000), hide_index=True, use_container_width=True,
                       on_select="rerun", selection_mode="single-row", key="queue")
    rows = sel.selection.rows if sel and hasattr(sel, "selection") else []
    if rows:
        st.session_state["seq"] = int(view.iloc[rows[0]]["seq"])
        st.info("Selected — open the Explanation tab.")

# ------------------------------------------------------------ explanation
with tab_e:
    default_seq = int(queue["seq"].iloc[0]) if len(queue) else 0
    seq = st.number_input("Ledger sequence number", min_value=0, value=st.session_state.get("seq", default_seq))
    rec = payload_of(ledger, int(seq))
    if rec.get("record_type") != "triage":
        st.warning("This record is an analyst decision; select a triage record.")
    else:
        left, right = st.columns([3, 2])
        with left:
            st.subheader(f"{rec['tier']} — {rec['action']}" + ("  (contested)" if rec["contested"] else ""))
            st.markdown(f"**Rule:** `{rec['rule_text']}`")
            if rec["contested"]:
                st.warning(f"Guard: {rec['guard_reason']} — confirm against evidence before acting.")
            st.markdown(f"**Score** s = {rec['s']:.4f}, percentile q = {rec['q']:.5f} (band {rec['band']}); "
                        f"expected value φ₀ = {rec['phi0']:.4f}; explainer {rec['explainer']}")
            phi = pd.Series(rec["phi"], index=list(rec["features"].keys()))
            top = phi.reindex(phi.abs().sort_values(ascending=False).index[:12])
            chart = pd.DataFrame({"feature": top.index, "SHAP contribution": top.values,
                                  "value": [rec["features"][f] for f in top.index]})
            st.bar_chart(chart.set_index("feature")["SHAP contribution"], horizontal=True)
            st.dataframe(chart, hide_index=True, use_container_width=True)
        with right:
            st.markdown("**Evidence reference**")
            st.json({"flow_uid": rec["flow_uid"], "event_time": str(pd.to_datetime(rec["event_ts"], unit="ms")),
                     "identifiers": rec["identifiers"], "source": rec["source_ref"]})
            st.markdown("**Versions**")
            st.json({"model": rec["model_version"], "ruleset": rec["ruleset_version"],
                     "background_hash": rec["background_hash"][:16] + "…", "processed_at": rec["processed_at"]})
            st.markdown("**Decision**")
            analyst = st.text_input("Analyst", value="analyst-1")
            note = st.text_area("Rationale (stored in the ledger)")
            b1, b2, b3 = st.columns(3)
            choice = None
            if b1.button("Escalate", type="primary"):
                choice = "escalate"
            if b2.button("Review"):
                choice = "review"
            if b3.button("Dismiss"):
                choice = "dismiss"
            if choice:
                row = index[index["seq"] == int(seq)].iloc[0]
                ledger.append([{
                    "record_type": "decision",
                    "alert_id": rec["alert_id"],
                    "flow_uid": rec["flow_uid"],
                    "event_ts": rec["event_ts"],
                    "refers_to_seq": int(seq),
                    "refers_to_hash": row["hash"],
                    "tier": ACTION_TIER[choice],
                    "investigator_response": choice,
                    "responder": analyst,
                    "note": note,
                    "decided_at": datetime.now(timezone.utc).isoformat(),
                }])
                load_index.clear()
                st.success(f"Recorded '{choice}' by {analyst}.")

# -------------------------------------------------------------- integrity
with tab_i:
    a, b = st.columns(2)
    if a.button("Verify hash chain"):
        v = ledger.verify()
        (a.success if v["ok"] else a.error)(f"chain ok = {v['ok']} over {v['n']} records; "
                                            f"first bad seq = {v['first_bad_seq']}")
    n_replay = b.number_input("Records to replay", 1, 500, 25)
    if b.button("Replay decisions from stored inputs"):
        recs = [json.loads(p) for p in ledger.read().query("record_type == 'triage'")["payload"].sample(
            int(n_replay), random_state=0)]
        cache = {}
        checks = pd.DataFrame([replay_record(r, RUN / "artifacts", cache) for r in recs])
        b.write(checks.mean().rename("share reproduced"))
    res = RUN / "results"
    acc = RUN / "accountability.json"
    if acc.exists():
        st.subheader("Testbed and accountability")
        st.json(json.loads(acc.read_text()))
    for fig in ("fig_workload.png", "fig_stability.png", "fig_noise.png"):
        if (res / fig).exists():
            st.image(str(res / fig), caption=fig)
    if (res / "main_summary.csv").exists():
        st.subheader("Main results (mean ± s.d. over seeds)")
        st.dataframe(pd.read_csv(res / "main_summary.csv"), hide_index=True, use_container_width=True)
