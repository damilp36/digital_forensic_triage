# XTriage results -- nf_cse_cic_ids2018_v3
## Data
* windows: {'fit': 1088073, 'tune': 1526283, 'test': 1737942}
* tune rows: 161321, test rows: 134151
* test priorities: {'P3': 69951, 'P2': 33959, 'P1': 30241}
* test classes: {'Benign': 69951, 'DDoS_attacks-LOIC-HTTP': 15000, 'DDOS_attack-HOIC': 15000, 'Infilteration': 15000, 'Bot': 15000, 'DDOS_attack-LOIC-UDP': 2976, 'Brute_Force_-Web': 745, 'SQL_Injection': 241, 'Brute_Force_-XSS': 238}

## RQ1 triage effectiveness and RQ3 rule quality (mean ± s.d. over seeds)

| method | det_auroc | alerts | recall@1000 | workload@90_frac | ndcg | macro_f1 | p1_f1 | coverage | fidelity | fidelity_traffic_conds | n_rules | mean_rule_len | contested_rate | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1-score-only | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.004534 ± 0.0024 | 0.8597 ± 0.062 | 0.8059 ± 0.042 |  |  |  |  |  |  |  |  |  |
| XTriage | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006316 ± 0.002 | 0.8144 ± 0.13 | 0.8381 ± 0.036 | 0.5696 ± 0.085 | 0.2871 ± 0.011 | 0.6357 ± 0.15 | 0.2592 ± 0.068 | 0.1716 ± 0.087 | 22.9 ± 2.3 | 3.408 ± 0.13 | 0.652 ± 0.094 | 0.1251 ± 0.039 |
| B3-raw-rules | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006005 ± 0.0022 | 0.8287 ± 0.057 | 0.8422 ± 0.039 | 0.6092 ± 0.093 | 0.2767 ± 0.016 | 0.6362 ± 0.15 | 0.1448 ± 0.042 | 0.1448 ± 0.042 | 24.6 ± 3.1 | 3.297 ± 0.13 | 0 ± 0 | 0 ± 0 |
| B4-tree-surrogate | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.004686 ± 0.0024 | 0.8931 ± 0.025 | 0.8363 ± 0.044 | 0.5627 ± 0.048 | 0.02886 ± 0.029 | 1 ± 0 | 0.492 ± 0.19 | 0.3471 ± 0.24 | 12.7 ± 2 | 3.753 ± 0.2 | 0.1168 ± 0.025 | 0.1993 ± 0.051 |
| Abl-no-SHAP-predicates | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.0062 ± 0.0021 | 0.8234 ± 0.052 | 0.8395 ± 0.034 | 0.5576 ± 0.096 | 0.2845 ± 0.013 | 0.6364 ± 0.15 | 0.1458 ± 0.052 | 0.1458 ± 0.052 | 24.1 ± 2.4 | 3.321 ± 0.1 | 0.6679 ± 0.1 | 0.1252 ± 0.038 |
| Abl-no-score-band | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006124 ± 0.002 | 0.787 ± 0.14 | 0.8379 ± 0.035 | 0.5657 ± 0.096 | 0.2861 ± 0.021 | 0.6358 ± 0.15 | 0.2475 ± 0.077 | 0.1538 ± 0.096 | 24 ± 2.9 | 3.423 ± 0.16 | 0.6577 ± 0.1 | 0.1194 ± 0.049 |
| Abl-no-guard | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006316 ± 0.002 | 0.8144 ± 0.13 | 0.8444 ± 0.037 | 0.6256 ± 0.083 | 0.2871 ± 0.011 | 0.6357 ± 0.15 | 0.2592 ± 0.068 | 0.1716 ± 0.087 | 22.9 ± 2.3 | 3.408 ± 0.13 | 0 ± 0 | 0 ± 0 |
| Abl-guard-review-tier | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.004917 ± 0.0028 | 0.8394 ± 0.058 | 0.8351 ± 0.043 | 0.5192 ± 0.076 | 0.2191 ± 0.12 | 0.6357 ± 0.15 | 0.2592 ± 0.068 | 0.1716 ± 0.087 | 22.9 ± 2.3 | 3.408 ± 0.13 | 0.652 ± 0.094 | 0.1251 ± 0.039 |
| Fix-calibrated-guard | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006316 ± 0.002 | 0.5562 ± 0.19 | 0.8312 ± 0.032 | 0.3559 ± 0.088 | 0.2871 ± 0.011 | 0.6357 ± 0.15 | 0.2592 ± 0.068 | 0.1716 ± 0.087 | 22.9 ± 2.3 | 3.408 ± 0.13 | 0.5009 ± 0.14 | 0.9838 ± 0.032 |
| Fix-SHAP-gated-bins | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.007708 ± 0.0013 | 0.8709 ± 0.051 | 0.8483 ± 0.037 | 0.5878 ± 0.083 | 0.3112 ± 0.036 | 0.6199 ± 0.13 | 1 ± 0 | 1 ± 0 | 25.7 ± 4.8 | 3.263 ± 0.26 | 0.6292 ± 0.13 | 0.1763 ± 0.057 |
| Fix-no-port-bins | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.006514 ± 0.0022 | 0.8188 ± 0.14 | 0.8403 ± 0.035 | 0.569 ± 0.098 | 0.2894 ± 0.014 | 0.6376 ± 0.15 | 0.2513 ± 0.07 | 0.1684 ± 0.083 | 23.4 ± 2.2 | 3.402 ± 0.15 | 0.6508 ± 0.089 | 0.1239 ± 0.045 |
| Fix-label-filter | 0.6899 ± 0.013 | 6755 ± 1.2e+03 | 0.008535 ± 0.00029 | 0.889 ± 0.032 | 0.8736 ± 0.034 | 0.648 ± 0.089 | 0.3756 ± 0.012 | 0.633 ± 0.15 | 0.2435 ± 0.093 | 0.1685 ± 0.087 | 19.6 ± 3.1 | 3.102 ± 0.15 | 0.5605 ± 0.1 | 0.1821 ± 0.054 |
| B2-xgboost-shap | 0.9666 ± 8.2e-05 | 5.946e+04 ± 53 | 0.001012 ± 0.0021 | 0.8942 ± 0.0057 | 0.948 ± 0.013 |  |  |  |  |  |  |  |  |  |
| XTriage@sample | 0.6899 ± 0.013 | 1500 ± 0 | 0.8929 ± 0.061 | 0.657 ± 0.18 | 0.9033 ± 0.026 | 0.533 ± 0.15 | 0.6727 ± 0.062 | 0.7477 ± 0.095 | 0.1992 ± 0.096 | 0.1383 ± 0.08 | 16.7 ± 2.6 | 3.179 ± 0.16 | 0.5617 ± 0.067 | 0.6547 ± 0.45 |
| B5-LIME@sample | 0.6899 ± 0.013 | 1500 ± 0 | 0.8878 ± 0.052 | 0.7231 ± 0.16 | 0.9021 ± 0.026 | 0.5314 ± 0.15 | 0.6753 ± 0.058 | 0.7371 ± 0.098 | 0.0748 ± 0.059 | 0.05131 ± 0.045 | 18 ± 2.5 | 3.202 ± 0.24 | 0.5621 ± 0.073 | 0.6473 ± 0.46 |
| B1-score-only@sample | 0.6899 ± 0.013 | 1500 ± 0 | 0.8064 ± 0.067 | 0.8758 ± 0.047 | 0.8557 ± 0.021 |  |  |  |  |  |  |  |  |  |
| Anchors@sample | 0.6899 ± 0.013 | 3000 ± 0 | 0.6329 ± 0.1 | 0.8983 ± 0.02 | 0.8317 ± 0.035 | 0.4839 ± 0.04 | 0.006478 ± 0.017 | 0.9445 ± 0.054 | 0.714 ± 0.17 | 0.4431 ± 0.2 | 121.4 ± 18 | 1.718 ± 0.095 | 0.1116 ± 0.055 | 0.2732 ± 0.083 |
| XTriage@anchor-sample | 0.6899 ± 0.013 | 3000 ± 0 | 0.7432 ± 0.052 | 0.8377 ± 0.11 | 0.867 ± 0.027 | 0.5147 ± 0.16 | 0.514 ± 0.053 | 0.6445 ± 0.13 | 0.2959 ± 0.1 | 0.1962 ± 0.11 | 12.2 ± 3 | 3.205 ± 0.29 | 0.5464 ± 0.078 | 0.5703 ± 0.45 |

### Paired Wilcoxon signed-rank tests, XTriage vs. each method (over seeds)

n = 10 seeds; with 5 the smallest attainable p-value is 0.0625 two-sided.

| reference | method | metric | n | ref_mean | other_mean | p_two_sided | p_one_sided |
|---|---|---|---|---|---|---|---|
| XTriage | B1-score-only | workload@90_frac | 10 | 0.814 | 0.860 | 0.275 | 0.138 |
| XTriage | B1-score-only | ndcg | 10 | 0.838 | 0.806 | 0.002 | 0.001 |
| XTriage | B1-score-only | recall@1000 | 10 | 0.006 | 0.005 | 0.002 | 0.001 |
| XTriage | B1-score-only | macro_f1 | 0 |  |  |  |  |
| XTriage | B1-score-only | fidelity | 0 |  |  |  |  |
| XTriage | B1-score-only | n_rules | 0 |  |  |  |  |
| XTriage | B3-raw-rules | workload@90_frac | 10 | 0.814 | 0.829 | 0.275 | 0.884 |
| XTriage | B3-raw-rules | ndcg | 10 | 0.838 | 0.842 | 0.193 | 0.920 |
| XTriage | B3-raw-rules | recall@1000 | 10 | 0.006 | 0.006 | 0.594 | 0.297 |
| XTriage | B3-raw-rules | macro_f1 | 10 | 0.570 | 0.609 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | fidelity | 10 | 0.259 | 0.145 | 0.002 | 0.001 |
| XTriage | B3-raw-rules | n_rules | 10 | 22.900 | 24.600 | 0.129 | 0.064 |
| XTriage | B4-tree-surrogate | workload@90_frac | 10 | 0.814 | 0.893 | 0.002 | 0.001 |
| XTriage | B4-tree-surrogate | ndcg | 10 | 0.838 | 0.836 | 0.922 | 0.461 |
| XTriage | B4-tree-surrogate | recall@1000 | 10 | 0.006 | 0.005 | 0.002 | 0.001 |
| XTriage | B4-tree-surrogate | macro_f1 | 10 | 0.570 | 0.563 | 0.322 | 0.161 |
| XTriage | B4-tree-surrogate | fidelity | 10 | 0.259 | 0.492 | 0.006 | 0.998 |
| XTriage | B4-tree-surrogate | n_rules | 10 | 22.900 | 12.700 | 0.002 | 1.000 |
| XTriage | Abl-no-SHAP-predicates | workload@90_frac | 10 | 0.814 | 0.823 | 0.322 | 0.862 |
| XTriage | Abl-no-SHAP-predicates | ndcg | 10 | 0.838 | 0.839 | 0.695 | 0.688 |
| XTriage | Abl-no-SHAP-predicates | recall@1000 | 10 | 0.006 | 0.006 | 1.000 | 0.500 |
| XTriage | Abl-no-SHAP-predicates | macro_f1 | 10 | 0.570 | 0.558 | 0.193 | 0.097 |
| XTriage | Abl-no-SHAP-predicates | fidelity | 10 | 0.259 | 0.146 | 0.002 | 0.001 |
| XTriage | Abl-no-SHAP-predicates | n_rules | 10 | 22.900 | 24.100 | 0.195 | 0.098 |
| XTriage | Abl-no-score-band | workload@90_frac | 10 | 0.814 | 0.787 | 0.844 | 0.629 |
| XTriage | Abl-no-score-band | ndcg | 10 | 0.838 | 0.838 | 0.820 | 0.633 |
| XTriage | Abl-no-score-band | recall@1000 | 10 | 0.006 | 0.006 | 0.977 | 0.543 |
| XTriage | Abl-no-score-band | macro_f1 | 10 | 0.570 | 0.566 | 1.000 | 0.527 |
| XTriage | Abl-no-score-band | fidelity | 10 | 0.259 | 0.248 | 0.250 | 0.125 |
| XTriage | Abl-no-score-band | n_rules | 10 | 22.900 | 24.000 | 0.211 | 0.105 |
| XTriage | Abl-no-guard | workload@90_frac | 10 | 0.814 | 0.814 |  |  |
| XTriage | Abl-no-guard | ndcg | 10 | 0.838 | 0.844 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | recall@1000 | 10 | 0.006 | 0.006 |  |  |
| XTriage | Abl-no-guard | macro_f1 | 10 | 0.570 | 0.626 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | fidelity | 10 | 0.259 | 0.259 |  |  |
| XTriage | Abl-no-guard | n_rules | 10 | 22.900 | 22.900 |  |  |
| XTriage | Abl-guard-review-tier | workload@90_frac | 10 | 0.814 | 0.839 | 1.000 | 0.500 |
| XTriage | Abl-guard-review-tier | ndcg | 10 | 0.838 | 0.835 | 0.557 | 0.278 |
| XTriage | Abl-guard-review-tier | recall@1000 | 10 | 0.006 | 0.005 | 0.008 | 0.004 |
| XTriage | Abl-guard-review-tier | macro_f1 | 10 | 0.570 | 0.519 | 0.010 | 0.005 |
| XTriage | Abl-guard-review-tier | fidelity | 10 | 0.259 | 0.259 |  |  |
| XTriage | Abl-guard-review-tier | n_rules | 10 | 22.900 | 22.900 |  |  |
| XTriage | Fix-calibrated-guard | workload@90_frac | 10 | 0.814 | 0.556 | 0.004 | 1.000 |
| XTriage | Fix-calibrated-guard | ndcg | 10 | 0.838 | 0.831 | 0.010 | 0.005 |
| XTriage | Fix-calibrated-guard | recall@1000 | 10 | 0.006 | 0.006 |  |  |
| XTriage | Fix-calibrated-guard | macro_f1 | 10 | 0.570 | 0.356 | 0.002 | 0.001 |
| XTriage | Fix-calibrated-guard | fidelity | 10 | 0.259 | 0.259 |  |  |
| XTriage | Fix-calibrated-guard | n_rules | 10 | 22.900 | 22.900 |  |  |
| XTriage | Fix-SHAP-gated-bins | workload@90_frac | 10 | 0.814 | 0.871 | 0.010 | 0.005 |
| XTriage | Fix-SHAP-gated-bins | ndcg | 10 | 0.838 | 0.848 | 0.010 | 0.997 |
| XTriage | Fix-SHAP-gated-bins | recall@1000 | 10 | 0.006 | 0.008 | 0.010 | 0.997 |
| XTriage | Fix-SHAP-gated-bins | macro_f1 | 10 | 0.570 | 0.588 | 0.193 | 0.920 |
| XTriage | Fix-SHAP-gated-bins | fidelity | 10 | 0.259 | 1.000 | 0.002 | 1.000 |
| XTriage | Fix-SHAP-gated-bins | n_rules | 10 | 22.900 | 25.700 | 0.062 | 0.031 |
| XTriage | Fix-no-port-bins | workload@90_frac | 10 | 0.814 | 0.819 | 0.625 | 0.312 |
| XTriage | Fix-no-port-bins | ndcg | 10 | 0.838 | 0.840 | 0.312 | 0.906 |
| XTriage | Fix-no-port-bins | recall@1000 | 10 | 0.006 | 0.007 | 0.625 | 0.812 |
| XTriage | Fix-no-port-bins | macro_f1 | 10 | 0.570 | 0.569 | 1.000 | 0.500 |
| XTriage | Fix-no-port-bins | fidelity | 10 | 0.259 | 0.251 | 0.641 | 0.320 |
| XTriage | Fix-no-port-bins | n_rules | 10 | 22.900 | 23.400 | 0.375 | 0.188 |
| XTriage | Fix-label-filter | workload@90_frac | 10 | 0.814 | 0.889 | 0.002 | 0.001 |
| XTriage | Fix-label-filter | ndcg | 10 | 0.838 | 0.874 | 0.002 | 1.000 |
| XTriage | Fix-label-filter | recall@1000 | 10 | 0.006 | 0.009 | 0.002 | 1.000 |
| XTriage | Fix-label-filter | macro_f1 | 10 | 0.570 | 0.648 | 0.002 | 1.000 |
| XTriage | Fix-label-filter | fidelity | 10 | 0.259 | 0.243 | 0.492 | 0.246 |
| XTriage | Fix-label-filter | n_rules | 10 | 22.900 | 19.600 | 0.012 | 0.998 |
| XTriage | B2-xgboost-shap | workload@90_frac | 10 | 0.814 | 0.894 | 0.002 | 0.001 |
| XTriage | B2-xgboost-shap | ndcg | 10 | 0.838 | 0.948 | 0.002 | 1.000 |
| XTriage | B2-xgboost-shap | recall@1000 | 10 | 0.006 | 0.001 | 0.002 | 0.001 |
| XTriage | B2-xgboost-shap | macro_f1 | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | fidelity | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | n_rules | 0 |  |  |  |  |

## RQ2 explanation reliability

| group | n | jaccard_bg | kendall_bg | jaccard_seed | kendall_seed | rule_change_bg | tier_change_bg |
|---|---|---|---|---|---|---|---|
| all | 600 | 0.956 | 0.896 | 0.514 | 0.714 | 0.023 | 0.022 |
| band=high | 51 | 0.923 | 0.920 | 0.445 | 0.726 | 0.015 | 0.015 |
| band=low | 275 | 0.976 | 0.878 | 0.569 | 0.703 | 0.006 | 0.006 |
| band=medium | 274 | 0.943 | 0.909 | 0.471 | 0.721 | 0.042 | 0.039 |
| priority=P1 | 39 | 0.968 | 0.907 | 0.487 | 0.733 | 0.006 | 0.006 |
| priority=P2 | 158 | 0.994 | 0.850 | 0.630 | 0.676 | 0.000 | 0.000 |
| priority=P3 | 403 | 0.940 | 0.913 | 0.471 | 0.727 | 0.034 | 0.032 |

Deletion-curve faithfulness (lower AUC = more faithful):

| method | n | deletion_auc | after_1 | after_3 | after_5 | after_10 |
|---|---|---|---|---|---|---|
| SHAP | 300 | 0.617 | 0.899 | 0.745 | 0.606 | 0.317 |
| LIME | 300 | 1.009 | 1.000 | 1.002 | 1.006 | 1.026 |
| random | 300 | 0.961 | 0.992 | 0.979 | 0.965 | 0.913 |

## RQ4 limitation probes

### Background set

| probe | variant | n_background | phi0 | jaccard_vs_ref | kendall_vs_ref | rule_change | tier_change | p1_tier_lost |
|---|---|---|---|---|---|---|---|---|
| background | size=10 | 10 | -12.307 | 0.925 | 0.787 | 0.052 | 0.048 | 0.012 |
| background | size=50 | 50 | -13.113 | 0.966 | 0.909 | 0.013 | 0.010 | 0.007 |
| background | size=100 | 100 | -13.311 | 0.974 | 0.918 | 0.013 | 0.012 | 0.000 |
| background | size=500 | 500 | -13.154 | 0.956 | 0.913 | 0.035 | 0.035 | 0.005 |
| background | window=early-fit | 100 | -13.095 | 0.963 | 0.909 | 0.042 | 0.040 | 0.007 |
| background | window=late-fit | 100 | -13.033 | 0.959 | 0.903 | 0.038 | 0.033 | 0.002 |
| background | mix=tune-benign | 100 | -13.154 | 0.958 | 0.888 | 0.033 | 0.030 | 0.005 |
| background | mix=tune-all-traffic | 100 | -12.507 | 0.933 | 0.755 | 0.048 | 0.047 | 0.012 |
| background | mix=50%-attack | 100 | -12.558 | 0.939 | 0.786 | 0.045 | 0.045 | 0.010 |

### Shortcut features

| probe | variant | dropped | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90 | workload@90_frac | ndcg | macro_f1 | coverage | n_rules | fidelity | top1_is_shortcut | shortcut_attr_share | shortcut_share[Benign] | shortcut_share[DDoS_attacks-LOIC-HTTP] | shortcut_share[DDOS_attack-LOIC-UDP] | shortcut_share[DDOS_attack-HOIC] | shortcut_share[Brute_Force_-Web] | shortcut_share[Brute_Force_-XSS] | shortcut_share[SQL_Injection] | shortcut_share[Infilteration] | shortcut_share[Bot] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shortcut | full | L4_DST_PORT;MIN_TTL;MAX_TTL | 134151 | 7123 | 0.053 | 0.535 | 0.059 | 0.014 | 3311 | 0.704 | 0.610 | 0.398 | 0.203 | 6093 | 0.855 | 0.840 | 0.616 | 0.574 | 26 | 0.314 | 0.003 | 0.027 | 0.042 | 0.012 | 0.012 | 0.027 | 0.021 | 0.021 | 0.021 | 0.032 | 0.040 |
| shortcut | without-shortcuts | L4_DST_PORT;MIN_TTL;MAX_TTL | 134151 | 7967 | 0.059 | 0.582 | 0.072 | 0.014 | 3329 | 0.698 | 0.611 | 0.382 | 0.190 | 7095 | 0.891 | 0.856 | 0.622 | 0.513 | 23 | 0.190 |  |  |  |  |  |  |  |  |  |  |  |

### Distribution shift (time)

| probe | variant | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90_frac | ndcg | macro_f1 | coverage | contested_rate | rule_error_rate | classes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shift-time | early-test | 67075 | 5107 | 0.076 | 0.706 | 0.105 | 0.867 | 1502 | 0.836 | 0.740 | 0.917 | 0.139 | 0.158 | 0.878 | 0.634 | 0.406 | 0.808 | 0.189 | Benign;Brute_Force_-Web;Brute_Force_-XSS;DDOS_attack-HOIC;DDOS_attack-LOIC-UDP;DDoS_attacks-LOIC-HTTP;SQL_Injection |
| shift-time | late-test | 67076 | 2016 | 0.030 | 0.103 | 0.007 | 0.007 | 1809 | 0.542 | 0.486 | 0.542 | 0.486 | 0.891 | 0.664 | 0.306 | 1.000 | 0.387 | 0.378 | Benign;Bot;Infilteration |

### Feature-space evasion

| probe | method | variant | n | mean_abs_dq | mean_ds | evaded_detection | rule_changed | tier_changed | tier_changed_still_alerted | p1_downgraded | became_contested |
|---|---|---|---|---|---|---|---|---|---|---|---|
| evasion | XTriage | padding=16 | 2000 | 0.002 | 0.073 | 0.000 | 0.013 | 0.014 | 0.014 | 0.035 | 0.003 |
| evasion | XTriage | padding=64 | 2000 | 0.010 | 0.379 | 0.000 | 0.016 | 0.020 | 0.020 | 0.045 | 0.006 |
| evasion | XTriage | padding=256 | 2000 | 0.015 | 0.774 | 0.000 | 0.051 | 0.041 | 0.041 | 0.066 | 0.018 |
| evasion | XTriage | timing=0.5 | 2000 | 0.022 | -0.437 | 0.647 | 0.083 | 0.021 | 0.054 | 0.027 | 0.018 |
| evasion | XTriage | timing=2.0 | 2000 | 0.007 | 0.132 | 0.026 | 0.064 | 0.033 | 0.033 | 0.018 | 0.022 |
| evasion | XTriage | timing=5.0 | 2000 | 0.014 | 0.104 | 0.026 | 0.074 | 0.038 | 0.039 | 0.004 | 0.013 |
| evasion | XTriage | port=80 | 2000 | 0.000 | 0.004 | 0.001 | 0.002 | 0.001 | 0.001 | 0.002 | 0.001 |
| evasion | XTriage | port=443 | 2000 | 0.000 | -0.002 | 0.001 | 0.003 | 0.003 | 0.003 | 0.010 | 0.001 |
| evasion | Fix-SHAP-gated-bins | padding=16 | 2000 | 0.002 | 0.073 | 0.000 | 0.195 | 0.007 | 0.007 | 0.013 | 0.003 |
| evasion | Fix-SHAP-gated-bins | padding=64 | 2000 | 0.010 | 0.379 | 0.000 | 0.225 | 0.017 | 0.017 | 0.025 | 0.009 |
| evasion | Fix-SHAP-gated-bins | padding=256 | 2000 | 0.015 | 0.774 | 0.000 | 0.302 | 0.095 | 0.095 | 0.173 | 0.052 |
| evasion | Fix-SHAP-gated-bins | timing=0.5 | 2000 | 0.022 | -0.437 | 0.647 | 0.037 | 0.018 | 0.041 | 0.046 | 0.011 |
| evasion | Fix-SHAP-gated-bins | timing=2.0 | 2000 | 0.007 | 0.132 | 0.026 | 0.070 | 0.041 | 0.042 | 0.142 | 0.032 |
| evasion | Fix-SHAP-gated-bins | timing=5.0 | 2000 | 0.014 | 0.104 | 0.026 | 0.082 | 0.074 | 0.076 | 0.179 | 0.051 |
| evasion | Fix-SHAP-gated-bins | port=80 | 2000 | 0.000 | 0.004 | 0.001 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 |
| evasion | Fix-SHAP-gated-bins | port=443 | 2000 | 0.000 | -0.002 | 0.001 | 0.001 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | Fix-no-port-bins | padding=16 | 2000 | 0.002 | 0.073 | 0.000 | 0.013 | 0.014 | 0.014 | 0.035 | 0.003 |
| evasion | Fix-no-port-bins | padding=64 | 2000 | 0.010 | 0.379 | 0.000 | 0.016 | 0.020 | 0.020 | 0.045 | 0.006 |
| evasion | Fix-no-port-bins | padding=256 | 2000 | 0.015 | 0.774 | 0.000 | 0.051 | 0.041 | 0.041 | 0.066 | 0.018 |
| evasion | Fix-no-port-bins | timing=0.5 | 2000 | 0.022 | -0.437 | 0.647 | 0.083 | 0.021 | 0.054 | 0.027 | 0.018 |
| evasion | Fix-no-port-bins | timing=2.0 | 2000 | 0.007 | 0.132 | 0.026 | 0.064 | 0.033 | 0.033 | 0.018 | 0.022 |
| evasion | Fix-no-port-bins | timing=5.0 | 2000 | 0.014 | 0.104 | 0.026 | 0.074 | 0.038 | 0.039 | 0.004 | 0.013 |
| evasion | Fix-no-port-bins | port=80 | 2000 | 0.000 | 0.004 | 0.001 | 0.002 | 0.001 | 0.001 | 0.002 | 0.001 |
| evasion | Fix-no-port-bins | port=443 | 2000 | 0.000 | -0.002 | 0.001 | 0.003 | 0.003 | 0.003 | 0.010 | 0.001 |
| evasion | Fix-calibrated-guard | padding=16 | 2000 | 0.002 | 0.073 | 0.000 | 0.013 | 0.011 | 0.011 | 0.035 | 0.000 |
| evasion | Fix-calibrated-guard | padding=64 | 2000 | 0.010 | 0.379 | 0.000 | 0.016 | 0.014 | 0.014 | 0.045 | 0.000 |
| evasion | Fix-calibrated-guard | padding=256 | 2000 | 0.015 | 0.774 | 0.000 | 0.051 | 0.029 | 0.029 | 0.066 | 0.000 |
| evasion | Fix-calibrated-guard | timing=0.5 | 2000 | 0.022 | -0.437 | 0.647 | 0.083 | 0.020 | 0.050 | 0.027 | 0.009 |
| evasion | Fix-calibrated-guard | timing=2.0 | 2000 | 0.007 | 0.132 | 0.026 | 0.064 | 0.031 | 0.032 | 0.018 | 0.002 |
| evasion | Fix-calibrated-guard | timing=5.0 | 2000 | 0.014 | 0.104 | 0.026 | 0.074 | 0.035 | 0.036 | 0.004 | 0.002 |
| evasion | Fix-calibrated-guard | port=80 | 2000 | 0.000 | 0.004 | 0.001 | 0.002 | 0.001 | 0.001 | 0.002 | 0.001 |
| evasion | Fix-calibrated-guard | port=443 | 2000 | 0.000 | -0.002 | 0.001 | 0.003 | 0.003 | 0.003 | 0.010 | 0.001 |

### Rule infidelity and the guard

| seed | method | rule_error_rate | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|
| 0 | XTriage | 0.242 | 0.689 | 0.735 | 0.259 | 79.000 | 0.139 |
| 0 | B4-tree-surrogate | 0.065 | 0.101 | 0.115 | 0.074 | 199.000 | 0.196 |
| 0 | Abl-no-guard | 0.242 | 0.000 | 0.000 |  | 79.000 | 0.000 |
| 1 | XTriage | 0.249 | 0.747 | 0.830 | 0.276 | 78.000 | 0.128 |
| 1 | B4-tree-surrogate | 0.069 | 0.104 | 0.060 | 0.040 | 222.000 | 0.135 |
| 1 | Abl-no-guard | 0.249 | 0.000 | 0.000 |  | 78.000 | 0.000 |
| 2 | XTriage | 0.271 | 0.735 | 0.772 | 0.285 | 71.000 | 0.141 |
| 2 | B4-tree-surrogate | 0.066 | 0.116 | 0.117 | 0.067 | 221.000 | 0.195 |
| 2 | Abl-no-guard | 0.271 | 0.000 | 0.000 |  | 71.000 | 0.000 |
| 3 | XTriage | 0.258 | 0.665 | 0.639 | 0.248 | 62.000 | 0.161 |
| 3 | B4-tree-surrogate | 0.078 | 0.097 | 0.057 | 0.046 | 224.000 | 0.143 |
| 3 | Abl-no-guard | 0.258 | 0.000 | 0.000 |  | 62.000 | 0.000 |
| 4 | XTriage | 0.393 | 0.519 | 0.608 | 0.460 | 25.000 | 0.200 |
| 4 | B4-tree-surrogate | 0.092 | 0.150 | 0.140 | 0.086 | 196.000 | 0.276 |
| 4 | Abl-no-guard | 0.393 | 0.000 | 0.000 |  | 25.000 | 0.000 |
| 5 | XTriage | 0.265 | 0.757 | 0.820 | 0.287 | 81.000 | 0.123 |
| 5 | B4-tree-surrogate | 0.071 | 0.121 | 0.105 | 0.062 | 231.000 | 0.173 |
| 5 | Abl-no-guard | 0.265 | 0.000 | 0.000 |  | 81.000 | 0.000 |
| 6 | XTriage | 0.214 | 0.658 | 0.537 | 0.174 | 80.000 | 0.075 |
| 6 | B4-tree-surrogate | 0.059 | 0.093 | 0.125 | 0.080 | 223.000 | 0.220 |
| 6 | Abl-no-guard | 0.214 | 0.000 | 0.000 |  | 80.000 | 0.000 |
| 7 | XTriage | 0.393 | 0.489 | 0.790 | 0.635 | 92.000 | 0.120 |
| 7 | B4-tree-surrogate | 0.112 | 0.170 | 0.092 | 0.060 | 234.000 | 0.179 |
| 7 | Abl-no-guard | 0.393 | 0.000 | 0.000 |  | 92.000 | 0.000 |
| 8 | XTriage | 0.232 | 0.578 | 0.483 | 0.194 | 64.000 | 0.078 |
| 8 | B4-tree-surrogate | 0.068 | 0.096 | 0.135 | 0.095 | 216.000 | 0.292 |
| 8 | Abl-no-guard | 0.232 | 0.000 | 0.000 |  | 64.000 | 0.000 |
| 9 | XTriage | 0.216 | 0.683 | 0.722 | 0.228 | 105.000 | 0.086 |
| 9 | B4-tree-surrogate | 0.070 | 0.120 | 0.084 | 0.049 | 222.000 | 0.185 |
| 9 | Abl-no-guard | 0.216 | 0.000 | 0.000 |  | 105.000 | 0.000 |

### Guard trade-off (calibrated guard, tau sweep; seed 0)

| probe | variant | tau | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|
| guard | Abl-no-guard |  | 0.855 | 0.846 | 0.657 | 0.281 | 0.000 | 0.000 |  | 79 | 0.000 |
| guard | XTriage |  | 0.855 | 0.840 | 0.616 | 0.281 | 0.689 | 0.735 | 0.259 | 79 | 0.139 |
| guard | calibrated | 0.002 | 0.430 | 0.825 | 0.330 | 0.281 | 0.512 | 0.775 | 0.367 | 79 | 1.000 |
| guard | calibrated | 0.005 | 0.430 | 0.825 | 0.330 | 0.281 | 0.512 | 0.775 | 0.367 | 79 | 1.000 |
| guard | calibrated | 0.010 | 0.399 | 0.830 | 0.410 | 0.281 | 0.459 | 0.774 | 0.409 | 79 | 0.975 |
| guard | calibrated | 0.020 | 0.398 | 0.830 | 0.414 | 0.281 | 0.456 | 0.773 | 0.411 | 79 | 0.962 |
| guard | calibrated | 0.050 | 0.861 | 0.845 | 0.650 | 0.281 | 0.224 | 0.729 | 0.788 | 79 | 0.013 |
| guard | calibrated | 0.100 | 0.855 | 0.846 | 0.657 | 0.281 | 0.216 | 0.728 | 0.817 | 79 | 0.000 |

### Alert threshold (mean over probe seeds)

| theta | alerts | det_p1_alerted | recall@1000 | workload@90 | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate |
|---|---|---|---|---|---|---|---|---|---|
| 0.900 | 11656.000 | 0.021 | 0.007 | 9837.000 | 0.844 | 0.853 | 0.650 | 0.288 | 0.604 |
| 0.950 | 7185.667 | 0.014 | 0.005 | 6242.333 | 0.869 | 0.840 | 0.592 | 0.277 | 0.724 |
| 0.990 | 845.667 | 0.002 | 0.002 | 621.000 | 0.738 | 0.638 | 0.096 | 0.266 | 0.719 |

### Isolation-forest size vs. explanation stability across retraining seeds

| probe | n_estimators | n | jaccard_seed | kendall_seed | mean_abs_dq_seed | jaccard_seed[low] | jaccard_seed[medium] | jaccard_seed[high] |
|---|---|---|---|---|---|---|---|---|
| forest-size | 100 | 600 | 0.514 | 0.714 | 0.006 | 0.569 | 0.471 | 0.445 |
| forest-size | 300 | 600 | 0.629 | 0.807 | 0.005 | 0.715 | 0.551 | 0.480 |
| forest-size | 1000 | 600 | 0.764 | 0.909 | 0.002 | 0.844 | 0.709 | 0.555 |

### Oracle noise (mean over probe seeds)

| method | eta | labels_filtered | macro_f1 | macro_f1_rules | p1_f1 | coverage | n_rules | mean_rule_len | fidelity | workload@90_frac | ndcg | contested_rate | guard_catch_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fix-label-filter | 0.000 | 216.667 | 0.681 | 0.751 | 0.383 | 0.574 | 20.000 | 2.971 | 0.265 | 0.909 | 0.883 | 0.632 | 0.711 |
| Fix-label-filter | 0.100 | 1820.333 | 0.674 | 0.743 | 0.372 | 0.577 | 22.000 | 3.151 | 0.272 | 0.908 | 0.878 | 0.634 | 0.700 |
| Fix-label-filter | 0.200 | 3186.000 | 0.661 | 0.729 | 0.350 | 0.574 | 15.667 | 3.318 | 0.291 | 0.903 | 0.863 | 0.649 | 0.736 |
| Fix-label-filter | 0.300 | 3392.000 | 0.654 | 0.718 | 0.341 | 0.569 | 18.333 | 3.650 | 0.259 | 0.910 | 0.861 | 0.651 | 0.724 |
| XTriage | 0.000 | 0.000 | 0.592 | 0.649 | 0.277 | 0.575 | 24.667 | 3.446 | 0.253 | 0.869 | 0.840 | 0.724 | 0.779 |
| XTriage | 0.100 | 0.000 | 0.670 | 0.734 | 0.353 | 0.567 | 13.667 | 3.386 | 0.328 | 0.910 | 0.866 | 0.633 | 0.690 |
| XTriage | 0.200 | 0.000 | 0.673 | 0.747 | 0.369 | 0.565 | 9.667 | 3.052 | 0.305 | 0.914 | 0.876 | 0.643 | 0.769 |
| XTriage | 0.300 | 0.000 | 0.685 | 0.757 | 0.372 | 0.558 | 8.000 | 3.148 | 0.376 | 0.910 | 0.891 | 0.622 | 0.718 |

## Detector robustness

| detector | method | det_auroc | det_auprc | alerts | alerts_explained | workload@90_frac | ndcg | recall@1000 | macro_f1 | fidelity | n_rules | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| autoencoder | XTriage | 0.856 ± 0.015 | 0.8638 ± 0.023 | 3000 ± 0 | 3000 ± 0 | 0.3109 ± 0.0012 | 0.9728 ± 0.0036 | 0.96 ± 0.0044 | 0.5391 ± 0.0044 | 0.3475 ± 0.17 | 16 ± 2.6 | 56.21 ± 1.3 |
| autoencoder | B1-score-only | 0.856 ± 0.015 | 0.8638 ± 0.023 | 3000 ± 0 | 3000 ± 0 | 0.7528 ± 0.16 | 0.8637 ± 0.011 | 0.1123 ± 0.039 |  |  |  | 56.21 ± 1.3 |
| xgboost | XTriage | 0.9666 ± 9.6e-05 | 0.9716 ± 7.2e-05 | 5.943e+04 ± 35 | 5.943e+04 ± 35 | 0.3416 ± 0.0037 | 0.9968 ± 0.00011 | 0.03307 ± 0 | 0.8846 ± 0.004 | 0.1324 ± 0.19 | 29.67 ± 9.5 | 104.9 ± 1.4 |
| xgboost | B1-score-only | 0.9666 ± 9.6e-05 | 0.9716 ± 7.2e-05 | 5.943e+04 ± 35 | 5.943e+04 ± 35 | 0.8941 ± 0.006 | 0.9405 ± 0.008 | 0 ± 0 |  |  |  | 104.9 ± 1.4 |

## RQ5 accountability

* records: 3249, chain verified: True, tamper detected: True (first bad seq 1000)
* replay success: 1.000 over 500 records {'score': 1.0, 'percentile': 1.0, 'attribution': 1.0, 'rule': 1.0, 'tier': 1.0, 'ok': 1.0}
* bytes per record: 1138; contested rate: 0.688
* testbed: 4 sensors, 60000 flows, 3249 alerts, 991 flows/s; t1 2.144 ms/flow, t2 2.240 ms/alert, t3 0.257 ms/record, publish-to-ledger latency incl. queueing under max-rate replay p50 13061 ms / p95 31517 ms
