"""S4: rule induction over z(x).

Three learners share one rule format, ``{"id", "priority", "conds": [[col, op, val], ...],
"support", "precision"}``, and one decision procedure (first matching rule wins):

* ``OrderedRipper``  -- RIPPER (wittgenstein) applied JRip-style to three classes: classes are
  learned from the rarest to the most frequent; the most frequent becomes the default
  (catch-all) rule. At most ``max_conds`` conditions per rule.
* ``TreeSurrogate``  -- depth-limited decision tree in the style of Trustee; every leaf is a rule.
* ``LocalAnchors``   -- Anchors-style per-event rules: greedy search for the shortest set of the
  event's own z-predicates whose matching tune alerts reach ``precision`` for one priority.
  (A re-implementation of the Anchors idea over the discrete z space, not the alibi library.)
"""

from __future__ import annotations

import hashlib
import json
import logging
import warnings

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

DEFAULT_ID = "R-default"


def cond_features(conds, disc_only: bool = False) -> list[str]:
    """Features a rule *positively* references: x-conditions with '==' and SHAP predicates that
    require the feature to be a top-k reason. Negated conditions say what the detector did not use."""
    out = set()
    for col, op, val in conds:
        if col == "band" or ":" not in col:
            continue
        kind, feat = col.split(":", 1)
        if kind == "why":
            if disc_only or (val == "T") != (op == "=="):
                continue
        elif op != "==":
            continue
        out.add(feat)
    return sorted(out)


def _match(Z: pd.DataFrame, conds) -> np.ndarray:
    mask = np.ones(len(Z), dtype=bool)
    for col, op, val in conds:
        if col not in Z.columns:
            return np.zeros(len(Z), dtype=bool)
        eq = Z[col].to_numpy() == val
        mask &= eq if op == "==" else ~eq
    return mask


class RuleList:
    """Ordered rule list with an optional default priority."""

    learner = "rules"

    def __init__(self, rules: list[dict] | None = None, default: str | None = None):
        self.rules = rules or []
        self.default = default

    # ---------------------------------------------------------------- apply
    def apply(self, Z: pd.DataFrame):
        n = len(Z)
        prio = np.full(n, self.default or "P2", dtype=object)
        rule_id = np.full(n, DEFAULT_ID, dtype=object)
        is_default = np.ones(n, dtype=bool)
        free = np.ones(n, dtype=bool)
        for r in self.rules:
            if not free.any():
                break
            m = free & _match(Z, r["conds"])
            prio[m] = r["priority"]
            rule_id[m] = r["id"]
            is_default[m] = False
            free &= ~m
        return prio, rule_id, is_default

    # ---------------------------------------------------------------- stats
    def annotate(self, Z: pd.DataFrame, y: np.ndarray) -> None:
        """Store support and precision of every rule on (Z, y), with first-match semantics."""
        _, rid, _ = self.apply(Z)
        for r in self.rules:
            m = rid == r["id"]
            r["support"] = int(m.sum())
            r["precision"] = float(np.mean(y[m] == r["priority"])) if m.any() else 0.0

    @property
    def n_rules(self) -> int:
        return len(self.rules)

    @property
    def mean_length(self) -> float:
        return float(np.mean([len(r["conds"]) for r in self.rules])) if self.rules else 0.0

    def features_of(self, rule_id: str, disc_only: bool = False) -> list[str]:
        for r in self.rules:
            if r["id"] == rule_id:
                return cond_features(r["conds"], disc_only)
        return []

    def to_dict(self) -> dict:
        return {"learner": self.learner, "default": self.default, "rules": self.rules}

    @property
    def version(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, default=str).encode()
        return f"{self.learner}-{hashlib.sha256(blob).hexdigest()[:12]}"

    def text(self, rule: dict, rep=None) -> str:
        if rep is not None:
            conds = [rep.describe_condition(*c) for c in rule["conds"]]
        else:
            conds = [f"{c[0]} {c[1]} {c[2]}" for c in rule["conds"]]
        return f"IF {' AND '.join(conds) or 'TRUE'} THEN {rule['priority']}"

    def text_of(self, rule_id: str, rep=None) -> str:
        if rule_id == DEFAULT_ID:
            return f"DEFAULT THEN {self.default}"
        for r in self.rules:
            if r["id"] == rule_id:
                return self.text(r, rep)
        return rule_id


def _stratified_cap(y: np.ndarray, cap: int | None, rng: np.random.Generator) -> np.ndarray:
    idx = np.arange(len(y))
    if cap is None or len(y) <= cap:
        return idx
    keep = []
    classes, counts = np.unique(y, return_counts=True)
    # keep rare classes whole, share the remaining budget proportionally
    budget = cap
    for c, n in sorted(zip(classes, counts), key=lambda t: t[1]):
        remaining = len(classes) - len(keep)
        share = max(1, budget // remaining)
        cidx = idx[y == c]
        if len(cidx) > share:
            cidx = rng.choice(cidx, share, replace=False)
        keep.append(cidx)
        budget -= len(cidx)
    return np.sort(np.concatenate(keep))


class OrderedRipper(RuleList):
    learner = "ripper"

    def __init__(self, max_conds=4, max_rules=40, k=2, max_train=15000, seed=0, **_):
        super().__init__()
        self.max_conds, self.max_rules, self.k = max_conds, max_rules, k
        self.max_train, self.seed = max_train, seed

    def fit(self, Z: pd.DataFrame, y: np.ndarray) -> "OrderedRipper":
        import wittgenstein as lw

        y = np.asarray(y, dtype=object)
        rng = np.random.default_rng(self.seed)
        sub = _stratified_cap(y, self.max_train, rng)
        Zs, ys = Z.iloc[sub].reset_index(drop=True), y[sub]
        classes, counts = np.unique(ys, return_counts=True)
        order = [c for _, c in sorted(zip(counts, classes))]
        self.default = order[-1]
        remaining = np.ones(len(ys), dtype=bool)
        rules = []
        for cls in order[:-1]:
            target = (ys == cls) & remaining
            if target.sum() < 2:
                remaining &= ys != cls
                continue
            df = Zs[remaining].copy()
            df["__y"] = (ys[remaining] == cls).astype(int)
            clf = lw.RIPPER(k=self.k, max_rules=self.max_rules, max_rule_conds=self.max_conds,
                            random_state=self.seed)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                clf.fit(df, class_feat="__y", pos_class=1)
            for r in clf.ruleset_.rules:
                conds = [[c.feature, "==", str(c.val)] for c in r.conds]
                rules.append({"id": f"R{len(rules) + 1}", "priority": cls, "conds": conds})
            remaining &= ys != cls
        self.rules = rules
        self.annotate(Zs, ys)
        log.info("RIPPER learned %d rules (default %s)", len(rules), self.default)
        return self


class TreeSurrogate(RuleList):
    learner = "tree"

    def __init__(self, tree_depth=4, tree_min_leaf=20, seed=0, max_train=None, **_):
        super().__init__()
        self.depth, self.min_leaf, self.seed, self.max_train = tree_depth, tree_min_leaf, seed, max_train

    def fit(self, Z: pd.DataFrame, y: np.ndarray) -> "TreeSurrogate":
        from sklearn.tree import DecisionTreeClassifier

        y = np.asarray(y, dtype=object)
        sub = _stratified_cap(y, self.max_train, np.random.default_rng(self.seed))
        Zs, ys = Z.iloc[sub].reset_index(drop=True), y[sub]
        dummies = pd.get_dummies(Zs, prefix_sep="\x1f").astype(np.uint8)
        cols = list(dummies.columns)
        tree = DecisionTreeClassifier(max_depth=self.depth, min_samples_leaf=self.min_leaf,
                                      random_state=self.seed).fit(dummies.to_numpy(), ys)
        t = tree.tree_
        rules = []

        def walk(node, conds):
            if t.children_left[node] == -1:
                prio = tree.classes_[int(np.argmax(t.value[node][0]))]
                rules.append({"id": f"T{len(rules) + 1}", "priority": str(prio), "conds": list(conds)})
                return
            col, val = cols[t.feature[node]].split("\x1f", 1)
            # one-hot <= 0.5  ->  col != val
            walk(t.children_left[node], conds + [[col, "!=", val]])
            walk(t.children_right[node], conds + [[col, "==", val]])

        walk(0, [])
        # simplify: an equality makes inequalities on the same column redundant
        for r in rules:
            eq_cols = {c[0] for c in r["conds"] if c[1] == "=="}
            r["conds"] = [c for c in r["conds"] if c[1] == "==" or c[0] not in eq_cols]
        self.rules = rules
        self.default = None
        self.annotate(Zs, ys)
        return self


class LocalAnchors:
    """Anchors-style per-event rules over z (see module docstring)."""

    learner = "anchors"

    def __init__(self, anchor_precision=0.9, anchor_min_support=10, max_conds=4, max_train=None, seed=0, **_):
        self.tau, self.min_support, self.max_conds = anchor_precision, anchor_min_support, max_conds
        self.max_train, self.seed = max_train, seed

    def fit(self, Z: pd.DataFrame, y: np.ndarray) -> "LocalAnchors":
        y = np.asarray(y, dtype=object)
        sub = _stratified_cap(y, self.max_train, np.random.default_rng(self.seed))
        self.Z = Z.iloc[sub].reset_index(drop=True)
        self.y = y[sub]
        self.classes = np.array(["P1", "P2", "P3"], dtype=object)
        self.Y = np.stack([self.y == c for c in self.classes], axis=1)
        self.cols = list(self.Z.columns)
        self.codes = {}
        for c in self.cols:
            vals = self.Z[c].to_numpy()
            self.codes[c] = {v: vals == v for v in np.unique(vals)}
        self.default = self.classes[np.argmax(self.Y.sum(0))]
        return self

    def explain_one(self, z: pd.Series):
        mask = np.ones(len(self.y), dtype=bool)
        conds = []
        best = None
        for _ in range(self.max_conds):
            cand = None
            for c in self.cols:
                if any(c == k[0] for k in conds):
                    continue
                m_c = self.codes[c].get(z[c])
                if m_c is None:
                    continue
                m = mask & m_c
                n = int(m.sum())
                if n < self.min_support:
                    continue
                counts = self.Y[m].sum(0)
                prec = counts.max() / n
                key = (prec, n)
                if cand is None or key > cand[0]:
                    cand = (key, c, m, self.classes[int(np.argmax(counts))])
            if cand is None:
                break
            (prec, n), c, mask, prio = cand
            conds.append([c, "==", z[c]])
            best = (prio, list(conds), prec, n)
            if prec >= self.tau:
                break
        if best is None:
            return self.default, [], 0.0, 0, True
        return best[0], best[1], best[2], best[3], best[2] < self.tau

    def apply(self, Z: pd.DataFrame):
        n = len(Z)
        prio = np.empty(n, dtype=object)
        rid = np.empty(n, dtype=object)
        is_default = np.zeros(n, dtype=bool)
        self.anchors: dict[str, dict] = {}
        for i in range(n):
            p, conds, prec, sup, low = self.explain_one(Z.iloc[i])
            key = json.dumps(conds)
            aid = "A" + hashlib.sha256((key + p).encode()).hexdigest()[:8]
            self.anchors[aid] = {"id": aid, "priority": p, "conds": conds, "precision": prec, "support": sup}
            prio[i], rid[i], is_default[i] = p, aid, low
        return prio, rid, is_default

    @property
    def n_rules(self) -> int:
        return len(getattr(self, "anchors", {}))

    @property
    def mean_length(self) -> float:
        a = getattr(self, "anchors", {})
        return float(np.mean([len(v["conds"]) for v in a.values()])) if a else 0.0

    def features_of(self, rule_id: str, disc_only: bool = False) -> list[str]:
        r = self.anchors.get(rule_id)
        return cond_features(r["conds"], disc_only) if r else []

    @property
    def version(self) -> str:
        return f"anchors-tau{self.tau}-n{len(self.y)}"

    def to_dict(self) -> dict:
        return {"learner": "anchors", "tau": self.tau, "anchors": list(getattr(self, "anchors", {}).values())}

    def text_of(self, rule_id: str, rep=None) -> str:
        r = self.anchors.get(rule_id)
        if r is None:
            return rule_id
        conds = [rep.describe_condition(*c) if rep else f"{c[0]} == {c[2]}" for c in r["conds"]]
        return f"IF {' AND '.join(conds) or 'TRUE'} THEN {r['priority']}"


LEARNERS = {"ripper": OrderedRipper, "tree": TreeSurrogate, "anchors": LocalAnchors}


def build_rules(rcfg: dict, seed: int, learner: str | None = None):
    name = learner or rcfg["learner"]
    params = dict(rcfg)
    params.pop("learner", None)
    return LEARNERS[name](seed=seed, **params)


def rules_from_dict(d: dict) -> RuleList:
    rl = RuleList(d["rules"], d["default"])
    rl.learner = d["learner"]
    return rl
