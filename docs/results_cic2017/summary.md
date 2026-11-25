# XTriage results -- cic2017
## Data
* windows: {'fit': 529918, 'tune': 1346044, 'test': 954781}
* tune rows: 145064, test rows: 149837
* test priorities: {'P3': 88453, 'P2': 60421, 'P1': 963}
* test classes: {'Benign': 88453, 'DDoS': 15000, 'PortScan': 11225, 'DoS GoldenEye': 10293, 'DoS Hulk': 9742, 'DoS Slowhttptest': 3997, 'DoS slowloris': 3206, 'SSH-Patator': 2948, 'FTP-Patator': 2693, 'Bot': 936, 'Web Attack - Brute Force': 796, 'Web Attack - XSS': 521, 'Infiltration': 23, 'Heartbleed': 4}

## RQ1 triage effectiveness and RQ3 rule quality (mean ± s.d. over seeds)

| method | det_auroc | alerts | recall@1000 | workload@90_frac | ndcg | macro_f1 | p1_f1 | coverage | fidelity | fidelity_traffic_conds | n_rules | mean_rule_len | contested_rate | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1-score-only | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.01734 ± 0.0065 | 0.4956 ± 0.15 | 0.9201 ± 0.011 |  |  |  |  |  |  |  |  |  |
| XTriage | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03925 ± 0.0038 | 0.2053 ± 0.31 | 0.9507 ± 0.0084 | 0.8104 ± 0.021 | 0.7491 ± 0.094 | 0.4023 ± 0.095 | 0.03834 ± 0.063 | 0.009022 ± 0.0075 | 13.2 ± 1.2 | 2.381 ± 0.072 | 0.677 ± 0.081 | 0.7497 ± 0.087 |
| B3-raw-rules | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03323 ± 0.006 | 0.5402 ± 0.3 | 0.9933 ± 0.0025 | 0.889 ± 0.019 | 0.7888 ± 0.092 | 0.3947 ± 0.089 | 0.05115 ± 0.035 | 0.05115 ± 0.035 | 14.8 ± 2.4 | 2.593 ± 0.19 | 0 ± 0 | 0 ± 0 |
| B4-tree-surrogate | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03074 ± 0.0042 | 0.7789 ± 0.049 | 0.947 ± 0.0099 | 0.7497 ± 0.027 | 0.4692 ± 0.063 | 1 ± 0 | 0.02258 ± 0.022 | 0.005186 ± 0.0065 | 12.1 ± 0.57 | 3.701 ± 0.052 | 0.0796 ± 0.015 | 0.6903 ± 0.1 |
| Abl-no-SHAP-predicates | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03956 ± 0.0035 | 0.2009 ± 0.31 | 0.9517 ± 0.0083 | 0.8344 ± 0.019 | 0.7899 ± 0.085 | 0.3866 ± 0.083 | 0.05074 ± 0.034 | 0.05074 ± 0.034 | 15.1 ± 2 | 2.548 ± 0.14 | 0.6922 ± 0.069 | 0.6781 ± 0.29 |
| Abl-no-score-band | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03977 ± 0.0042 | 0.205 ± 0.31 | 0.951 ± 0.0082 | 0.8123 ± 0.022 | 0.7546 ± 0.095 | 0.4023 ± 0.095 | 0.03839 ± 0.063 | 0.009022 ± 0.0075 | 13.1 ± 1.4 | 2.357 ± 0.13 | 0.677 ± 0.081 | 0.7919 ± 0.12 |
| Abl-no-guard | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03229 ± 0.0073 | 0.5366 ± 0.3 | 0.9914 ± 0.004 | 0.8706 ± 0.022 | 0.7491 ± 0.094 | 0.4023 ± 0.095 | 0.03834 ± 0.063 | 0.009022 ± 0.0075 | 13.2 ± 1.2 | 2.381 ± 0.072 | 0 ± 0 | 0 ± 0 |
| Abl-guard-review-tier | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.02482 ± 0.0085 | 0.4979 ± 0.18 | 0.9448 ± 0.0092 | 0.7361 ± 0.067 | 0.5269 ± 0.23 | 0.4023 ± 0.095 | 0.03834 ± 0.063 | 0.009022 ± 0.0075 | 13.2 ± 1.2 | 2.381 ± 0.072 | 0.677 ± 0.081 | 0.7497 ± 0.087 |
| Fix-calibrated-guard | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03229 ± 0.0073 | 0.5366 ± 0.3 | 0.9914 ± 0.004 | 0.8706 ± 0.022 | 0.7491 ± 0.094 | 0.4023 ± 0.095 | 0.03834 ± 0.063 | 0.009022 ± 0.0075 | 13.2 ± 1.2 | 2.381 ± 0.072 | 0.001471 ± 0.00071 | 0 ± 0 |
| Fix-SHAP-gated-bins | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03209 ± 0.0053 | 0.5501 ± 0.31 | 0.9435 ± 0.011 | 0.6948 ± 0.038 | 0.4775 ± 0.13 | 0.4277 ± 0.087 | 1 ± 0 | 1 ± 0 | 22.2 ± 7.6 | 2.896 ± 0.18 | 0.6559 ± 0.074 | 0.6643 ± 0.17 |
| Fix-no-port-bins | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03925 ± 0.0038 | 0.2013 ± 0.3 | 0.9506 ± 0.0083 | 0.8046 ± 0.022 | 0.7491 ± 0.094 | 0.4103 ± 0.092 | 0.08821 ± 0.051 | 0.06155 ± 0.038 | 18 ± 2.2 | 2.718 ± 0.2 | 0.6699 ± 0.076 | 0.6943 ± 0.14 |
| Fix-label-filter | 0.7194 ± 0.0089 | 1.497e+04 ± 3.6e+03 | 0.03832 ± 0.0039 | 0.2889 ± 0.35 | 0.9524 ± 0.0085 | 0.7739 ± 0.078 | 0.6241 ± 0.2 | 0.3954 ± 0.093 | 0.03404 ± 0.051 | 0.009211 ± 0.0087 | 13.3 ± 1.6 | 2.354 ± 0.2 | 0.6854 ± 0.077 | 0.7687 ± 0.069 |
| B2-xgboost-shap | 0.9999 ± 5.3e-06 | 6.576e+04 ± 1e+02 | 0 ± 0 | 0.8773 ± 0.0012 | 0.9752 ± 9.7e-05 |  |  |  |  |  |  |  |  |  |
| XTriage@sample | 0.7194 ± 0.0089 | 1500 ± 0 | 0.9724 ± 0.028 | 0.1245 ± 0.19 | 0.9321 ± 0.022 | 0.8173 ± 0.13 | 0.8517 ± 0.077 | 0.5222 ± 0.062 | 0.05166 ± 0.04 | 0.02491 ± 0.021 | 7.1 ± 1.4 | 1.779 ± 0.27 | 0.5908 ± 0.027 | 0.6363 ± 0.39 |
| B5-LIME@sample | 0.7194 ± 0.0089 | 1500 ± 0 | 0.97 ± 0.019 | 0.07687 ± 0.045 | 0.9337 ± 0.022 | 0.8281 ± 0.13 | 0.8711 ± 0.066 | 0.516 ± 0.06 | 0.02141 ± 0.034 | 0.02141 ± 0.034 | 7.5 ± 1.3 | 1.86 ± 0.28 | 0.5968 ± 0.03 | 0.7329 ± 0.17 |
| B1-score-only@sample | 0.7194 ± 0.0089 | 1500 ± 0 | 0.9445 ± 0.088 | 0.5067 ± 0.13 | 0.8193 ± 0.017 |  |  |  |  |  |  |  |  |  |
| Anchors@sample | 0.7194 ± 0.0089 | 2000 ± 0 | 0.6073 ± 0.18 | 0.6842 ± 0.079 | 0.837 ± 0.013 | 0.5272 ± 0.019 | 0 ± 0 | 1 ± 0 | 0.3338 ± 0.12 | 0.07282 ± 0.11 | 37.1 ± 3.8 | 1.047 ± 0.078 | 0.1351 ± 0.018 | 0.5692 ± 0.2 |
| XTriage@anchor-sample | 0.7194 ± 0.0089 | 2000 ± 0 | 0.9262 ± 0.047 | 0.1902 ± 0.24 | 0.9232 ± 0.019 | 0.796 ± 0.12 | 0.8103 ± 0.08 | 0.5321 ± 0.067 | 0.03856 ± 0.044 | 0.01261 ± 0.011 | 9.8 ± 1.6 | 2.228 ± 0.23 | 0.58 ± 0.034 | 0.645 ± 0.28 |

### Paired Wilcoxon signed-rank tests, XTriage vs. each method (over seeds)

n = 10 seeds; with 5 the smallest attainable p-value is 0.0625 two-sided.

| reference | method | metric | n | ref_mean | other_mean | p_two_sided | p_one_sided |
|---|---|---|---|---|---|---|---|
| XTriage | B1-score-only | workload@90_frac | 10 | 0.205 | 0.496 | 0.020 | 0.010 |
| XTriage | B1-score-only | ndcg | 10 | 0.951 | 0.920 | 0.002 | 0.001 |
| XTriage | B1-score-only | recall@1000 | 10 | 0.039 | 0.017 | 0.002 | 0.001 |
| XTriage | B1-score-only | macro_f1 | 0 |  |  |  |  |
| XTriage | B1-score-only | fidelity | 0 |  |  |  |  |
| XTriage | B1-score-only | n_rules | 0 |  |  |  |  |
| XTriage | B3-raw-rules | workload@90_frac | 10 | 0.205 | 0.540 | 0.012 | 0.006 |
| XTriage | B3-raw-rules | ndcg | 10 | 0.951 | 0.993 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | recall@1000 | 10 | 0.039 | 0.033 | 0.004 | 0.002 |
| XTriage | B3-raw-rules | macro_f1 | 10 | 0.810 | 0.889 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | fidelity | 10 | 0.038 | 0.051 | 0.322 | 0.862 |
| XTriage | B3-raw-rules | n_rules | 10 | 13.200 | 14.800 | 0.102 | 0.051 |
| XTriage | B4-tree-surrogate | workload@90_frac | 10 | 0.205 | 0.779 | 0.002 | 0.001 |
| XTriage | B4-tree-surrogate | ndcg | 10 | 0.951 | 0.947 | 0.010 | 0.005 |
| XTriage | B4-tree-surrogate | recall@1000 | 10 | 0.039 | 0.031 | 0.002 | 0.001 |
| XTriage | B4-tree-surrogate | macro_f1 | 10 | 0.810 | 0.750 | 0.004 | 0.002 |
| XTriage | B4-tree-surrogate | fidelity | 10 | 0.038 | 0.023 | 0.846 | 0.615 |
| XTriage | B4-tree-surrogate | n_rules | 10 | 13.200 | 12.100 | 0.062 | 0.992 |
| XTriage | Abl-no-SHAP-predicates | workload@90_frac | 10 | 0.205 | 0.201 | 0.426 | 0.820 |
| XTriage | Abl-no-SHAP-predicates | ndcg | 10 | 0.951 | 0.952 | 0.375 | 0.839 |
| XTriage | Abl-no-SHAP-predicates | recall@1000 | 10 | 0.039 | 0.040 | 0.594 | 0.797 |
| XTriage | Abl-no-SHAP-predicates | macro_f1 | 10 | 0.810 | 0.834 | 0.037 | 0.986 |
| XTriage | Abl-no-SHAP-predicates | fidelity | 10 | 0.038 | 0.051 | 0.322 | 0.862 |
| XTriage | Abl-no-SHAP-predicates | n_rules | 10 | 13.200 | 15.100 | 0.039 | 0.020 |
| XTriage | Abl-no-score-band | workload@90_frac | 10 | 0.205 | 0.205 | 0.500 | 0.875 |
| XTriage | Abl-no-score-band | ndcg | 10 | 0.951 | 0.951 | 0.250 | 1.000 |
| XTriage | Abl-no-score-band | recall@1000 | 10 | 0.039 | 0.040 | 0.500 | 1.000 |
| XTriage | Abl-no-score-band | macro_f1 | 10 | 0.810 | 0.812 | 0.750 | 0.750 |
| XTriage | Abl-no-score-band | fidelity | 10 | 0.038 | 0.038 | 0.500 | 0.875 |
| XTriage | Abl-no-score-band | n_rules | 10 | 13.200 | 13.100 | 1.000 | 0.750 |
| XTriage | Abl-no-guard | workload@90_frac | 10 | 0.205 | 0.537 | 0.031 | 0.016 |
| XTriage | Abl-no-guard | ndcg | 10 | 0.951 | 0.991 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | recall@1000 | 10 | 0.039 | 0.032 | 0.008 | 0.004 |
| XTriage | Abl-no-guard | macro_f1 | 10 | 0.810 | 0.871 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | fidelity | 10 | 0.038 | 0.038 |  |  |
| XTriage | Abl-no-guard | n_rules | 10 | 13.200 | 13.200 |  |  |
| XTriage | Abl-guard-review-tier | workload@90_frac | 10 | 0.205 | 0.498 | 0.008 | 0.004 |
| XTriage | Abl-guard-review-tier | ndcg | 10 | 0.951 | 0.945 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | recall@1000 | 10 | 0.039 | 0.025 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | macro_f1 | 10 | 0.810 | 0.736 | 0.004 | 0.002 |
| XTriage | Abl-guard-review-tier | fidelity | 10 | 0.038 | 0.038 |  |  |
| XTriage | Abl-guard-review-tier | n_rules | 10 | 13.200 | 13.200 |  |  |
| XTriage | Fix-calibrated-guard | workload@90_frac | 10 | 0.205 | 0.537 | 0.031 | 0.016 |
| XTriage | Fix-calibrated-guard | ndcg | 10 | 0.951 | 0.991 | 0.002 | 1.000 |
| XTriage | Fix-calibrated-guard | recall@1000 | 10 | 0.039 | 0.032 | 0.008 | 0.004 |
| XTriage | Fix-calibrated-guard | macro_f1 | 10 | 0.810 | 0.871 | 0.002 | 1.000 |
| XTriage | Fix-calibrated-guard | fidelity | 10 | 0.038 | 0.038 |  |  |
| XTriage | Fix-calibrated-guard | n_rules | 10 | 13.200 | 13.200 |  |  |
| XTriage | Fix-SHAP-gated-bins | workload@90_frac | 10 | 0.205 | 0.550 | 0.027 | 0.014 |
| XTriage | Fix-SHAP-gated-bins | ndcg | 10 | 0.951 | 0.943 | 0.004 | 0.002 |
| XTriage | Fix-SHAP-gated-bins | recall@1000 | 10 | 0.039 | 0.032 | 0.004 | 0.002 |
| XTriage | Fix-SHAP-gated-bins | macro_f1 | 10 | 0.810 | 0.695 | 0.002 | 0.001 |
| XTriage | Fix-SHAP-gated-bins | fidelity | 10 | 0.038 | 1.000 | 0.002 | 1.000 |
| XTriage | Fix-SHAP-gated-bins | n_rules | 10 | 13.200 | 22.200 | 0.006 | 0.003 |
| XTriage | Fix-no-port-bins | workload@90_frac | 10 | 0.205 | 0.201 | 0.500 | 1.000 |
| XTriage | Fix-no-port-bins | ndcg | 10 | 0.951 | 0.951 | 0.432 | 0.216 |
| XTriage | Fix-no-port-bins | recall@1000 | 10 | 0.039 | 0.039 |  |  |
| XTriage | Fix-no-port-bins | macro_f1 | 10 | 0.810 | 0.805 | 0.322 | 0.161 |
| XTriage | Fix-no-port-bins | fidelity | 10 | 0.038 | 0.088 | 0.064 | 0.976 |
| XTriage | Fix-no-port-bins | n_rules | 10 | 13.200 | 18.000 | 0.002 | 0.001 |
| XTriage | Fix-label-filter | workload@90_frac | 10 | 0.205 | 0.289 | 0.203 | 0.102 |
| XTriage | Fix-label-filter | ndcg | 10 | 0.951 | 0.952 | 0.064 | 0.976 |
| XTriage | Fix-label-filter | recall@1000 | 10 | 0.039 | 0.038 | 0.359 | 0.180 |
| XTriage | Fix-label-filter | macro_f1 | 10 | 0.810 | 0.774 | 0.322 | 0.161 |
| XTriage | Fix-label-filter | fidelity | 10 | 0.038 | 0.034 | 0.375 | 0.188 |
| XTriage | Fix-label-filter | n_rules | 10 | 13.200 | 13.300 | 0.984 | 0.492 |
| XTriage | B2-xgboost-shap | workload@90_frac | 10 | 0.205 | 0.877 | 0.002 | 0.001 |
| XTriage | B2-xgboost-shap | ndcg | 10 | 0.951 | 0.975 | 0.002 | 1.000 |
| XTriage | B2-xgboost-shap | recall@1000 | 10 | 0.039 | 0.000 | 0.002 | 0.001 |
| XTriage | B2-xgboost-shap | macro_f1 | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | fidelity | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | n_rules | 0 |  |  |  |  |

## RQ2 explanation reliability

| group | n | jaccard_bg | kendall_bg | jaccard_seed | kendall_seed | rule_change_bg | tier_change_bg |
|---|---|---|---|---|---|---|---|
| all | 600 | 0.967 | 0.926 | 0.270 | 0.694 | 0.001 | 0.000 |
| band=high | 115 | 0.951 | 0.947 | 0.196 | 0.731 | 0.000 | 0.000 |
| band=low | 243 | 0.970 | 0.908 | 0.332 | 0.650 | 0.000 | 0.000 |
| band=medium | 242 | 0.971 | 0.934 | 0.242 | 0.721 | 0.002 | 0.000 |
| priority=P1 | 11 | 0.921 | 0.919 | 0.229 | 0.664 | 0.000 | 0.000 |
| priority=P2 | 282 | 0.980 | 0.920 | 0.302 | 0.684 | 0.000 | 0.000 |
| priority=P3 | 307 | 0.956 | 0.932 | 0.242 | 0.704 | 0.002 | 0.000 |

Deletion-curve faithfulness (lower AUC = more faithful):

| method | n | deletion_auc | after_1 | after_3 | after_5 | after_10 |
|---|---|---|---|---|---|---|
| SHAP | 300 | 0.751 | 0.936 | 0.838 | 0.746 | 0.536 |
| LIME | 300 | 1.001 | 1.000 | 1.000 | 1.000 | 1.005 |
| random | 300 | 0.972 | 0.995 | 0.984 | 0.971 | 0.942 |

## RQ4 limitation probes

### Background set

| probe | variant | n_background | phi0 | jaccard_vs_ref | kendall_vs_ref | rule_change | tier_change | p1_tier_lost |
|---|---|---|---|---|---|---|---|---|
| background | size=10 | 10 | -14.089 | 0.925 | 0.843 | 0.002 | 0.000 | 0.000 |
| background | size=50 | 50 | -14.546 | 0.977 | 0.921 | 0.000 | 0.000 | 0.000 |
| background | size=100 | 100 | -14.062 | 0.974 | 0.932 | 0.002 | 0.000 | 0.000 |
| background | size=500 | 500 | -14.641 | 0.970 | 0.932 | 0.000 | 0.000 | 0.000 |
| background | window=early-fit | 100 | -14.043 | 0.970 | 0.918 | 0.000 | 0.000 | 0.000 |
| background | window=late-fit | 100 | -14.540 | 0.967 | 0.942 | 0.002 | 0.002 | 0.002 |
| background | mix=tune-benign | 100 | -14.104 | 0.962 | 0.882 | 0.002 | 0.000 | 0.000 |
| background | mix=tune-all-traffic | 100 | -13.122 | 0.925 | 0.844 | 0.002 | 0.002 | 0.000 |
| background | mix=50%-attack | 100 | -13.553 | 0.925 | 0.852 | 0.000 | 0.000 | 0.000 |

### Shortcut features

| probe | variant | dropped | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90 | workload@90_frac | ndcg | macro_f1 | coverage | n_rules | fidelity | top1_is_shortcut | shortcut_attr_share | shortcut_share[Benign] | shortcut_share[DoS slowloris] | shortcut_share[DoS Slowhttptest] | shortcut_share[DoS Hulk] | shortcut_share[DoS GoldenEye] | shortcut_share[Heartbleed] | shortcut_share[Web Attack - Brute Force] | shortcut_share[Web Attack - XSS] | shortcut_share[Infiltration] | shortcut_share[Bot] | shortcut_share[DDoS] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shortcut | full | Destination Port;Init_Win_bytes_forward;Init_Win_bytes_backward | 149837 | 11339 | 0.076 | 0.581 | 0.107 | 0.045 | 4749 | 0.714 | 0.594 | 0.496 | 0.008 | 464 | 0.041 | 0.941 | 0.825 | 0.481 | 12 | 0.009 | 0.014 | 0.017 | 0.023 | 0.010 | 0.018 | 0.011 | 0.018 | 0.007 | 0.004 | 0.003 | 0.009 | 0.014 | 0.011 |
| shortcut | without-shortcuts | Destination Port;Init_Win_bytes_forward;Init_Win_bytes_backward | 149837 | 13819 | 0.092 | 0.660 | 0.149 | 0.045 | 4698 | 0.746 | 0.623 | 0.471 | 0.007 | 347 | 0.025 | 0.956 | 0.812 | 0.446 | 15 | 0.019 |  |  |  |  |  |  |  |  |  |  |  |  |  |

### Distribution shift (time)

| probe | variant | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90_frac | ndcg | macro_f1 | coverage | contested_rate | rule_error_rate | classes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shift-time | early-test | 74820 | 6176 | 0.083 | 0.642 | 0.121 | 1.000 | 2213 | 0.739 | 0.645 | 1.000 | 0.067 | 0.000 | 0.934 | 0.762 | 0.467 | 0.603 | 0.110 | Benign;DoS GoldenEye;DoS Hulk;DoS Slowhttptest;DoS slowloris;FTP-Patator;Heartbleed;SSH-Patator |
| shift-time | late-test | 75017 | 5163 | 0.069 | 0.509 | 0.092 | 0.042 | 2536 | 0.686 | 0.539 | 0.536 | 0.015 | 0.065 | 0.928 | 0.849 | 0.498 | 0.640 | 0.004 | Benign;Bot;DDoS;Heartbleed;Infiltration;PortScan;Web Attack - Brute Force;Web Attack - XSS |

### Feature-space evasion

| probe | method | variant | n | mean_abs_dq | mean_ds | evaded_detection | rule_changed | tier_changed | tier_changed_still_alerted | p1_downgraded | became_contested |
|---|---|---|---|---|---|---|---|---|---|---|---|
| evasion | XTriage | padding=16 | 2000 | 0.001 | -0.077 | 0.022 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | XTriage | padding=64 | 2000 | 0.003 | -0.019 | 0.034 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | XTriage | padding=256 | 2000 | 0.005 | 0.318 | 0.000 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | XTriage | timing=0.5 | 2000 | 0.019 | -1.120 | 0.279 | 0.014 | 0.009 | 0.011 | 0.094 | 0.002 |
| evasion | XTriage | timing=2.0 | 2000 | 0.007 | 0.671 | 0.000 | 0.006 | 0.004 | 0.004 | 0.125 | 0.003 |
| evasion | XTriage | timing=5.0 | 2000 | 0.010 | 1.000 | 0.000 | 0.021 | 0.015 | 0.015 | 0.188 | 0.013 |
| evasion | XTriage | port=80 | 2000 | 0.000 | -0.001 | 0.000 | 0.005 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | XTriage | port=443 | 2000 | 0.000 | 0.010 | 0.007 | 0.780 | 0.359 | 0.355 | 0.000 | 0.001 |
| evasion | Fix-SHAP-gated-bins | padding=16 | 2000 | 0.001 | -0.077 | 0.022 | 0.007 | 0.003 | 0.003 | 0.042 | 0.004 |
| evasion | Fix-SHAP-gated-bins | padding=64 | 2000 | 0.003 | -0.019 | 0.034 | 0.011 | 0.005 | 0.006 | 0.042 | 0.004 |
| evasion | Fix-SHAP-gated-bins | padding=256 | 2000 | 0.005 | 0.318 | 0.000 | 0.079 | 0.017 | 0.017 | 0.250 | 0.009 |
| evasion | Fix-SHAP-gated-bins | timing=0.5 | 2000 | 0.019 | -1.120 | 0.279 | 0.245 | 0.231 | 0.172 | 0.125 | 0.002 |
| evasion | Fix-SHAP-gated-bins | timing=2.0 | 2000 | 0.007 | 0.671 | 0.000 | 0.216 | 0.102 | 0.102 | 0.208 | 0.007 |
| evasion | Fix-SHAP-gated-bins | timing=5.0 | 2000 | 0.010 | 1.000 | 0.000 | 0.238 | 0.096 | 0.096 | 0.167 | 0.020 |
| evasion | Fix-SHAP-gated-bins | port=80 | 2000 | 0.000 | -0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | Fix-SHAP-gated-bins | port=443 | 2000 | 0.000 | 0.010 | 0.007 | 0.001 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | Fix-no-port-bins | padding=16 | 2000 | 0.001 | -0.077 | 0.022 | 0.011 | 0.011 | 0.011 | 0.000 | 0.008 |
| evasion | Fix-no-port-bins | padding=64 | 2000 | 0.003 | -0.019 | 0.034 | 0.034 | 0.032 | 0.033 | 0.000 | 0.029 |
| evasion | Fix-no-port-bins | padding=256 | 2000 | 0.005 | 0.318 | 0.000 | 0.087 | 0.059 | 0.059 | 0.000 | 0.046 |
| evasion | Fix-no-port-bins | timing=0.5 | 2000 | 0.019 | -1.120 | 0.279 | 0.075 | 0.014 | 0.008 | 0.094 | 0.010 |
| evasion | Fix-no-port-bins | timing=2.0 | 2000 | 0.007 | 0.671 | 0.000 | 0.053 | 0.046 | 0.046 | 0.125 | 0.045 |
| evasion | Fix-no-port-bins | timing=5.0 | 2000 | 0.010 | 1.000 | 0.000 | 0.070 | 0.058 | 0.058 | 0.188 | 0.056 |
| evasion | Fix-no-port-bins | port=80 | 2000 | 0.000 | -0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | Fix-no-port-bins | port=443 | 2000 | 0.000 | 0.010 | 0.007 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | Fix-calibrated-guard | padding=16 | 2000 | 0.001 | -0.077 | 0.022 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | Fix-calibrated-guard | padding=64 | 2000 | 0.003 | -0.019 | 0.034 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | Fix-calibrated-guard | padding=256 | 2000 | 0.005 | 0.318 | 0.000 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | Fix-calibrated-guard | timing=0.5 | 2000 | 0.019 | -1.120 | 0.279 | 0.014 | 0.009 | 0.012 | 0.094 | 0.004 |
| evasion | Fix-calibrated-guard | timing=2.0 | 2000 | 0.007 | 0.671 | 0.000 | 0.006 | 0.004 | 0.004 | 0.125 | 0.001 |
| evasion | Fix-calibrated-guard | timing=5.0 | 2000 | 0.010 | 1.000 | 0.000 | 0.021 | 0.016 | 0.016 | 0.188 | 0.000 |
| evasion | Fix-calibrated-guard | port=80 | 2000 | 0.000 | -0.001 | 0.000 | 0.005 | 0.003 | 0.003 | 0.000 | 0.001 |
| evasion | Fix-calibrated-guard | port=443 | 2000 | 0.000 | 0.010 | 0.007 | 0.780 | 0.736 | 0.734 | 0.000 | 0.001 |

### Rule infidelity and the guard

| seed | method | rule_error_rate | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|
| 0 | XTriage | 0.061 | 0.620 | 0.030 | 0.003 | 11.000 | 0.727 |
| 0 | B4-tree-surrogate | 0.010 | 0.102 | 0.232 | 0.023 | 31.000 | 0.710 |
| 0 | Abl-no-guard | 0.061 | 0.000 | 0.000 |  | 11.000 | 0.000 |
| 1 | XTriage | 0.103 | 0.645 | 0.026 | 0.004 | 0.000 |  |
| 1 | B4-tree-surrogate | 0.030 | 0.083 | 0.163 | 0.058 | 26.000 | 0.808 |
| 1 | Abl-no-guard | 0.103 | 0.000 | 0.000 |  | 0.000 |  |
| 2 | XTriage | 0.014 | 0.825 | 0.075 | 0.001 | 20.000 | 0.850 |
| 2 | B4-tree-surrogate | 0.051 | 0.057 | 0.061 | 0.054 | 26.000 | 0.769 |
| 2 | Abl-no-guard | 0.014 | 0.000 | 0.000 |  | 20.000 | 0.000 |
| 3 | XTriage | 0.058 | 0.698 | 0.041 | 0.003 | 15.000 | 0.733 |
| 3 | B4-tree-surrogate | 0.006 | 0.068 | 0.392 | 0.034 | 30.000 | 0.500 |
| 3 | Abl-no-guard | 0.058 | 0.000 | 0.000 |  | 15.000 | 0.000 |
| 4 | XTriage | 0.023 | 0.759 | 0.088 | 0.003 | 20.000 | 0.600 |
| 4 | B4-tree-surrogate | 0.008 | 0.061 | 0.113 | 0.015 | 26.000 | 0.577 |
| 4 | Abl-no-guard | 0.023 | 0.000 | 0.000 |  | 20.000 | 0.000 |
| 5 | XTriage | 0.067 | 0.677 | 0.045 | 0.005 | 14.000 | 0.714 |
| 5 | B4-tree-surrogate | 0.011 | 0.081 | 0.227 | 0.030 | 26.000 | 0.692 |
| 5 | Abl-no-guard | 0.067 | 0.000 | 0.000 |  | 14.000 | 0.000 |
| 6 | XTriage | 0.073 | 0.604 | 0.036 | 0.004 | 15.000 | 0.867 |
| 6 | B4-tree-surrogate | 0.009 | 0.091 | 0.363 | 0.037 | 31.000 | 0.774 |
| 6 | Abl-no-guard | 0.073 | 0.000 | 0.000 |  | 15.000 | 0.000 |
| 7 | XTriage | 0.037 | 0.755 | 0.041 | 0.002 | 17.000 | 0.706 |
| 7 | B4-tree-surrogate | 0.007 | 0.068 | 0.290 | 0.030 | 27.000 | 0.778 |
| 7 | Abl-no-guard | 0.037 | 0.000 | 0.000 |  | 17.000 | 0.000 |
| 8 | XTriage | 0.113 | 0.589 | 0.014 | 0.003 | 10.000 | 0.800 |
| 8 | B4-tree-surrogate | 0.020 | 0.090 | 0.153 | 0.034 | 31.000 | 0.581 |
| 8 | Abl-no-guard | 0.113 | 0.000 | 0.000 |  | 10.000 | 0.000 |
| 9 | XTriage | 0.101 | 0.600 | 0.029 | 0.005 | 0.000 |  |
| 9 | B4-tree-surrogate | 0.018 | 0.096 | 0.152 | 0.029 | 28.000 | 0.714 |
| 9 | Abl-no-guard | 0.101 | 0.000 | 0.000 |  | 0.000 |  |

### Guard trade-off (calibrated guard, tau sweep; seed 0)

| probe | variant | tau | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|
| guard | Abl-no-guard |  | 0.560 | 0.991 | 0.896 | 0.810 | 0.000 | 0.000 |  | 11 | 0.000 |
| guard | XTriage |  | 0.041 | 0.941 | 0.825 | 0.810 | 0.620 | 0.030 | 0.003 | 11 | 0.727 |
| guard | calibrated | 0.002 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.250 | 11 | 0.000 |
| guard | calibrated | 0.005 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.273 | 11 | 0.000 |
| guard | calibrated | 0.010 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.273 | 11 | 0.000 |
| guard | calibrated | 0.020 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.273 | 11 | 0.000 |
| guard | calibrated | 0.050 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.273 | 11 | 0.000 |
| guard | calibrated | 0.100 | 0.560 | 0.991 | 0.896 | 0.810 | 0.001 | 0.004 | 0.273 | 11 | 0.000 |

### Alert threshold (mean over probe seeds)

| theta | alerts | det_p1_alerted | recall@1000 | workload@90 | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate |
|---|---|---|---|---|---|---|---|---|---|
| 0.900 | 33944.667 | 0.047 | 0.038 | 2447.000 | 0.072 | 0.963 | 0.551 | 0.518 | 0.529 |
| 0.950 | 16241.333 | 0.045 | 0.041 | 621.333 | 0.034 | 0.954 | 0.824 | 0.789 | 0.697 |
| 0.990 | 3963.000 | 0.033 | 0.029 | 1063.667 | 0.264 | 0.903 | 0.513 | 0.715 | 0.994 |

### Isolation-forest size vs. explanation stability across retraining seeds

| probe | n_estimators | n | jaccard_seed | kendall_seed | mean_abs_dq_seed | jaccard_seed[low] | jaccard_seed[medium] | jaccard_seed[high] |
|---|---|---|---|---|---|---|---|---|
| forest-size | 100 | 600 | 0.270 | 0.694 | 0.005 | 0.332 | 0.242 | 0.196 |
| forest-size | 300 | 600 | 0.362 | 0.801 | 0.003 | 0.416 | 0.336 | 0.311 |
| forest-size | 1000 | 600 | 0.498 | 0.882 | 0.002 | 0.582 | 0.458 | 0.404 |

### Oracle noise (mean over probe seeds)

| method | eta | labels_filtered | macro_f1 | macro_f1_rules | p1_f1 | coverage | n_rules | mean_rule_len | fidelity | workload@90_frac | ndcg | contested_rate | guard_catch_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fix-label-filter | 0.000 | 5.000 | 0.797 | 0.860 | 0.690 | 0.374 | 14.000 | 2.435 | 0.073 | 0.070 | 0.954 | 0.706 | 0.058 |
| Fix-label-filter | 0.100 | 2038.333 | 0.729 | 0.791 | 0.514 | 0.389 | 13.333 | 2.744 | 0.097 | 0.325 | 0.954 | 0.692 | 0.071 |
| Fix-label-filter | 0.200 | 3048.000 | 0.563 | 0.626 | 0.053 | 0.457 | 23.333 | 3.508 | 0.066 | 0.759 | 0.963 | 0.697 | 0.573 |
| Fix-label-filter | 0.300 | 2625.667 | 0.525 | 0.587 | 0.006 | 0.558 | 21.333 | 3.530 | 0.080 | 0.795 | 0.973 | 0.677 | 0.689 |
| XTriage | 0.000 | 0.000 | 0.824 | 0.887 | 0.789 | 0.383 | 13.333 | 2.373 | 0.084 | 0.034 | 0.954 | 0.697 | 0.044 |
| XTriage | 0.100 | 0.000 | 0.630 | 0.693 | 0.165 | 0.381 | 9.667 | 2.756 | 0.081 | 0.579 | 0.945 | 0.711 | 0.230 |
| XTriage | 0.200 | 0.000 | 0.482 | 0.644 | 0.000 | 0.531 | 12.333 | 3.008 | 0.110 | 0.571 | 0.930 | 0.531 | 0.332 |
| XTriage | 0.300 | 0.000 | 0.367 | 0.634 | 0.000 | 0.465 | 9.667 | 2.994 | 0.036 | 0.633 | 0.931 | 0.555 | 0.700 |

## Detector robustness

| detector | method | det_auroc | det_auprc | alerts | alerts_explained | workload@90_frac | ndcg | recall@1000 | macro_f1 | fidelity | n_rules | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| autoencoder | XTriage | 0.9038 ± 0.0098 | 0.8068 ± 0.0095 | 3000 ± 0 | 3000 ± 0 | 0.09322 ± 0.0048 | 0.9454 ± 0.02 | 0.9919 ± 0.0052 | 0.6248 ± 0.2 | 0.1258 ± 0.043 | 19.33 ± 3.5 | 85.55 ± 2.9 |
| autoencoder | B1-score-only | 0.9038 ± 0.0098 | 0.8068 ± 0.0095 | 3000 ± 0 | 3000 ± 0 | 0.7253 ± 0.037 | 0.8064 ± 0.009 | 0.09738 ± 0.018 |  |  |  | 85.55 ± 2.9 |
| xgboost | XTriage | 0.9999 ± 6.5e-06 | 0.9999 ± 8e-06 | 6.585e+04 ± 35 | 6.585e+04 ± 35 | 0.03954 ± 0.0025 | 0.9953 ± 0.00066 | 0.4576 ± 0.094 | 0.7832 ± 0.0056 | 0.3041 ± 0.13 | 13.33 ± 1.5 | 102.8 ± 2.4 |
| xgboost | B1-score-only | 0.9999 ± 6.5e-06 | 0.9999 ± 8e-06 | 6.585e+04 ± 35 | 6.585e+04 ± 35 | 0.8766 ± 0.00058 | 0.9753 ± 4.1e-05 | 0 ± 0 |  |  |  | 102.8 ± 2.4 |

## RQ5 accountability

* records: 4462, chain verified: True, tamper detected: True (first bad seq 1011)
* replay success: 1.000 over 500 records {'score': 1.0, 'percentile': 1.0, 'attribution': 1.0, 'rule': 1.0, 'tier': 1.0, 'ok': 1.0}
* bytes per record: 1805; contested rate: 0.631
* testbed: 4 sensors, 60000 flows, 4462 alerts, 1451 flows/s; t1 1.671 ms/flow, t2 1.962 ms/alert, t3 0.370 ms/record, publish-to-ledger latency incl. queueing under max-rate replay p50 7089 ms / p95 22589 ms
