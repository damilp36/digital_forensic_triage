import json

import numpy as np
import pandas as pd
import pytest

from xtriage.config import load_config
from xtriage.data.loaders import load_dataset, normalise_label, parse_cic2017_time
from xtriage.data.prepare import noisy_oracle, oracle_priority, prepare, split_windows
from xtriage.engine.explain import Explainer, top_k
from xtriage.engine.guard import apply_guard, queue_order
from xtriage.engine.ledger import Ledger, canonical
from xtriage.engine.pipeline import XTriageEngine, fit_detector, replay_record, score_and_explain
from xtriage.engine.represent import Representation
from xtriage.engine.rules import OrderedRipper, TreeSurrogate, cond_features
from xtriage.eval.metrics import ndcg, triage_metrics


@pytest.fixture(scope="module")
def cfg():
    return load_config("configs/smoke.yaml", {"dataset": {"synthetic": {"n": 12000}},
                                              "sample": {"fit_benign": 2000, "calibration": 1000,
                                                         "background_pool": 500},
                                              "explain": {"background_size": 30, "n_jobs": 1},
                                              "rules": {"max_train": 1500, "k": 1}})


@pytest.fixture(scope="module")
def prep(cfg):
    return prepare(load_dataset(cfg), cfg)


@pytest.fixture(scope="module")
def engine(prep, cfg):
    return XTriageEngine.fit(prep, cfg, seed=0)


# ------------------------------------------------------------------ data


def test_cic2017_afternoon_hours_are_pm():
    ts = parse_cic2017_time(pd.Series(["7/7/2017 3:30", "7/7/2017 9:15", "03/07/2017 08:55:58"]))
    hours = pd.to_datetime(ts, unit="ms").hour
    assert list(hours) == [15, 9, 8]


def test_label_normalisation():
    assert normalise_label("Web Attack \x96 Sql Injection") == "Web Attack - Sql Injection"


def test_benign_subsample_is_deterministic_and_chunk_free():
    from xtriage.data.loaders import keep_benign_row

    rows = np.arange(200_000)
    whole = keep_benign_row(rows, 0.1)
    chunked = np.concatenate([keep_benign_row(rows[i:i + 7_000], 0.1) for i in range(0, len(rows), 7_000)])
    assert (whole == chunked).all()
    assert 0.095 < whole.mean() < 0.105


def test_time_split_is_ordered(prep):
    assert prep.tune.meta["ts"].max() <= prep.test.meta["ts"].min()
    assert prep.tune.meta["ts"].is_monotonic_increasing


def test_blocked_split_alternates():
    meta = pd.DataFrame({"ts": np.arange(0, 6 * 60_000 * 20, 60_000)})
    w = split_windows(meta, {"strategy": "blocked", "fit_until": 0.25, "block_minutes": 20})
    assert set(w) == {"fit", "tune", "test"}
    assert (w[meta["ts"] < np.quantile(meta["ts"], 0.25)] == "fit").all()


def test_oracle_and_noise():
    pr = oracle_priority(pd.Series(["Benign", "Exploits", "DoS", "Other"]), {"P1": ["exploits"], "P2": ["DoS"]})
    assert list(pr) == ["P3", "P1", "P2", "P2"]
    base = np.array(["P1"] * 10000, dtype=object)
    flipped = (noisy_oracle(base, 0.2, 0) != base).mean()
    assert 0.18 < flipped < 0.22


# -------------------------------------------------------------- engine


def test_shap_is_additive_for_isolation_forest(prep, cfg):
    det = fit_detector(prep, cfg, 0)
    ex = Explainer.from_config(det, prep.backgrounds[0], prep.feature_names, cfg["explain"], n_jobs=1)
    X = prep.test.X.to_numpy(dtype=np.float32)[:50]
    phi, phi0 = ex.explain(X, parallel=False)
    assert np.allclose(phi0 + phi.sum(1), det.score(X), atol=1e-6)


def test_top_k_orders_by_magnitude():
    phi = np.array([[0.1, -3.0, 2.0, 0.0]])
    assert list(top_k(phi, 2)[0]) == [1, 2]


def test_representation_predicates():
    rep = Representation(["a", "b", "c"], n_bins=2, top_k=1).fit(np.array([[0, 0, 0], [1, 1, 1]]))
    Z = rep.transform(np.array([[5, 0, 0]]), np.array([[0.9, -2.0, 0.1]]), np.array([0.9991]))
    assert Z.loc[0, "why:a"] == "F"  # top-1 is b, but negative -> not a reason for anomaly
    assert Z.loc[0, "why:b"] == "F"
    assert Z.loc[0, "band"] == "high"
    assert Z.loc[0, "x:a"] == "Q2"


def test_ripper_recovers_planted_rule():
    rng = np.random.default_rng(0)
    n = 1500
    Z = pd.DataFrame({"x:f": rng.choice(["Q1", "Q2"], n), "why:g": rng.choice(["T", "F"], n),
                      "band": rng.choice(["low", "high"], n)})
    y = np.where((Z["why:g"] == "T") & (Z["band"] == "high"), "P1",
                 np.where(Z["x:f"] == "Q1", "P3", "P2")).astype(object)
    r = OrderedRipper(seed=0, k=1).fit(Z, y)
    pred, _, _ = r.apply(Z)
    assert (pred == y).mean() > 0.97


def test_tree_rules_are_exhaustive():
    rng = np.random.default_rng(1)
    Z = pd.DataFrame({"x:f": rng.choice(["Q1", "Q2", "Q3"], 500), "band": rng.choice(["low", "high"], 500)})
    y = np.where(Z["band"] == "high", "P1", "P3").astype(object)
    t = TreeSurrogate(tree_depth=3, tree_min_leaf=5).fit(Z, y)
    _, _, is_default = t.apply(Z)
    assert not is_default.any()


def test_cond_features_ignores_negations():
    conds = [["why:a", "==", "F"], ["why:b", "==", "T"], ["x:c", "==", "Q5"], ["x:d", "!=", "Q1"], ["band", "==", "high"]]
    assert cond_features(conds) == ["b", "c"]
    assert cond_features(conds, disc_only=True) == ["c"]


def test_guard_modes():
    prio = np.array(["P1", "P3", "P2", "P1"], dtype=object)
    is_def = np.array([False, False, True, False])
    q = np.array([0.96, 0.995, 0.97, 0.9995])
    band = np.array(["low", "medium", "low", "high"], dtype=object)
    tier, cont, reason = apply_guard(prio, is_def, q, band, {"enabled": True, "mode": "conservative", "p3_max_q": 0.99})
    assert list(cont) == [True, True, True, False]
    assert list(tier) == ["P1", "P2", "P2", "P1"]  # escalation kept, dismissal raised
    tier, _, _ = apply_guard(prio, is_def, q, band, {"enabled": True, "mode": "review", "p3_max_q": 0.99})
    assert list(tier) == ["P2", "P2", "P2", "P1"]


def test_calibrated_guard_contests_leaky_cells_only():
    from xtriage.engine.guard import guard_stats

    rid = np.array(["R1"] * 100 + ["R2"] * 100, dtype=object)
    band = np.array(["low"] * 200, dtype=object)
    y = np.array(["P3"] * 100 + ["P1"] * 10 + ["P3"] * 90, dtype=object)  # R2 lets 10% P1 through
    g = {"enabled": True, "mode": "calibrated", "tau": 0.05, "smoothing": 0.0, "stats": guard_stats(rid, band, y)}
    prio = np.array(["P3", "P3", "P1"], dtype=object)
    tier, cont, reason = apply_guard(prio, np.zeros(3, bool), np.array([0.96] * 3),
                                     np.array(["low"] * 3, dtype=object), g, np.array(["R1", "R2", "R9"], dtype=object))
    assert list(tier) == ["P3", "P2", "P1"]
    assert list(cont) == [False, True, True] and reason[2] == "escalate-rule-on-low-score"


def test_shap_gated_bins_and_excluded_features():
    rep = Representation(["a", "b", "c"], n_bins=2, top_k=1, exclude=["c"], gate_disc=True)
    rep.fit(np.array([[0, 0, 0], [1, 1, 1]]))
    Z = rep.transform(np.array([[5, 5, 5]]), np.array([[0.9, -2.0, 0.1]]), np.array([0.96]))
    assert "x:c" not in Z.columns
    assert Z.loc[0, "x:a"] == "-" and Z.loc[0, "x:b"] == "-"  # top-1 is b (negative): no reason
    Z = rep.transform(np.array([[5, 5, 5]]), np.array([[0.9, 0.1, 0.0]]), np.array([0.96]))
    assert Z.loc[0, "x:a"] == "Q2" and Z.loc[0, "x:b"] == "-"
    assert Representation.from_dict(rep.to_dict()).gate_disc


def test_label_filter_removes_random_flips():
    from xtriage.engine.rules import filter_noisy_labels

    rng = np.random.default_rng(0)
    Z = pd.DataFrame({"x:f": rng.choice(["Q1", "Q2", "Q3"], 3000), "band": rng.choice(["low", "high"], 3000)})
    clean = np.where(Z["x:f"] == "Q3", "P1", "P3").astype(object)
    noisy = noisy_oracle(clean, 0.1, 0)
    keep = filter_noisy_labels(Z, noisy, seed=0)
    flipped = noisy != clean
    assert keep[flipped].mean() < 0.2 and keep[~flipped].mean() > 0.95


def test_queue_order_tier_then_score():
    order = queue_order(np.array(["P2", "P1", "P1"], dtype=object), np.array([1.0, 0.97, 1.0]), np.array([9, 1, 2]))
    assert list(order) == [2, 1, 0]


# ------------------------------------------------------------- ledger


def test_ledger_chain_and_tamper(tmp_path):
    led = Ledger(tmp_path / "l")
    led.append([{"record_type": "triage", "alert_id": str(i), "q": 0.5 + i / 100} for i in range(5)])
    led.append([{"record_type": "decision", "alert_id": "1", "investigator_response": "dismiss"}])
    assert led.verify()["ok"] and len(led) == 6
    head = json.loads((tmp_path / "l" / "head.json").read_text())
    part = tmp_path / "l" / head["parts"][0]
    df = pd.read_parquet(part)
    rec = json.loads(df.at[2, "payload"])
    rec["q"] = 0.0
    df.at[2, "payload"] = canonical(rec)
    df.to_parquet(part, index=False)
    v = led.verify()
    assert not v["ok"] and v["first_bad_seq"] == 2


# ------------------------------------------------------------ end to end


def test_records_replay_exactly(prep, cfg, engine, tmp_path):
    X = prep.test.X.to_numpy(dtype=np.float32)[:3000]
    sc, tr = engine.process(X, parallel=False)
    assert sc.alert.sum() > 0
    recs = engine.make_records(X, prep.test.meta.iloc[:3000].reset_index(drop=True), sc, tr)
    engine.save_artifacts(tmp_path / "artifacts")
    led = Ledger(tmp_path / "ledger")
    led.append(recs)
    assert led.verify()["ok"]
    cache = {}
    for r in led.records()[:20]:
        assert replay_record(r, tmp_path / "artifacts", cache)["ok"]


def test_metrics():
    pr = np.array(["P3", "P1", "P2", "P1"], dtype=object)
    m = triage_metrics(np.array([1, 3, 2, 0]), pr, total_p1=2, budgets=(1, 2))
    assert m["recall@2"] == 1.0 and m["workload@90"] == 2 and m["ndcg"] == pytest.approx(1.0)
    assert ndcg(np.array([0, 2])) < 1.0


def test_streaming_testbed(prep, engine, tmp_path):
    from xtriage.testbed.replay import run_testbed

    table = prep.test.take(np.arange(1500))
    stats = run_testbed(engine, table, Ledger(tmp_path / "tb"), n_sensors=3, batch_size=64, tick_seconds=3600)
    assert stats["flows"] == 1500 and stats["published"] == 1500
    assert Ledger(tmp_path / "tb").verify()["ok"]
