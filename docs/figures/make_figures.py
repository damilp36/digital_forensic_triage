"""Figures for Phase3.tex, built from the result tables in docs/results_*/.

Run from the repository root:  .venv/Scripts/python docs/figures/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DOCS = Path(__file__).resolve().parents[1]
CORPORA = {"NF-UNSW-NB15": "results_unsw_nb15", "NF-CIC-IDS2018": "results_cic2018", "CIC-IDS2017": "results_cic2017"}
MARK = {"NF-UNSW-NB15": "o", "NF-CIC-IDS2018": "s", "CIC-IDS2017": "^"}
GUARDS = {"Abl-no-guard": "no guard", "XTriage": "fixed guard", "Fix-calibrated-guard": "calibrated guard"}
GCOL = {"no guard": "#9e9e9e", "fixed guard": "#1f4e79", "calibrated guard": "#c0504d"}

plt.rcParams.update({"font.size": 7, "font.family": "serif", "axes.linewidth": 0.6, "lines.linewidth": 1.0})
fig, (a, b) = plt.subplots(1, 2, figsize=(3.5, 1.75))

for name, d in CORPORA.items():
    fs = pd.read_csv(DOCS / d / "probe_forest_size.csv")
    a.plot(fs["n_estimators"], fs["jaccard_seed"], marker=MARK[name], ms=3.5, color="k", label=name)
a.set_xscale("log")
a.set_xticks([100, 300, 1000])
a.set_xticklabels(["100", "300", "1000"])
a.set_ylim(0, 1)
a.set_xlabel("isolation-forest trees")
a.set_ylabel("top-5 Jaccard across seeds")
a.set_title("(a) explanation stability", fontsize=7)
a.legend(fontsize=5.5, frameon=False, loc="lower right")

for name, d in CORPORA.items():
    df = pd.read_csv(DOCS / d / "main_per_seed.csv")
    df = df[df["method"].isin(GUARDS)].copy()
    df["silent"] = df["severe_errors"] * (1 - df["severe_caught"].fillna(0)) / df["p1_alerts"] * 100
    g = df.groupby("method")[["workload@90_frac", "silent"]].mean()
    for m, lab in GUARDS.items():
        hollow = lab == "no guard"
        b.scatter(g.loc[m, "workload@90_frac"], g.loc[m, "silent"], marker=MARK[name], s=34 if hollow else 13,
                  facecolor="none" if hollow else GCOL[lab], edgecolor="k" if hollow else GCOL[lab],
                  linewidth=0.7, zorder=2 if hollow else 3)
for lab, c in GCOL.items():
    hollow = lab == "no guard"
    b.scatter([], [], marker="o", s=34 if hollow else 13, facecolor="none" if hollow else c,
              edgecolor="k" if hollow else c, linewidth=0.7, label=lab)
b.set_xlim(0, 1)
b.set_ylim(-1.5, 32)
b.set_xlabel("Workload@90")
b.set_ylabel("silent dismissals (% of P1)")
b.set_title("(b) guard trade-off", fontsize=7)
b.legend(fontsize=5.5, frameon=False, loc="upper left", handletextpad=0.2)

fig.tight_layout(pad=0.3, w_pad=0.8)
fig.savefig(DOCS / "figures" / "fig_results.pdf")
fig.savefig(DOCS / "figures" / "fig_results.png", dpi=200)
print("written", DOCS / "figures" / "fig_results.pdf")
