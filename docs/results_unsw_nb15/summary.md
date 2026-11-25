# XTriage results -- nf_unsw_nb15_v3
## Data
* windows: {'fit': 946169, 'tune': 709627, 'test': 709628}
* tune rows: 146218, test rows: 152024
* test priorities: {'P3': 97069, 'P2': 37500, 'P1': 17455}
* test classes: {'Benign': 97069, 'Exploits': 15000, 'Fuzzers': 15000, 'Generic': 10408, 'Reconnaissance': 8770, 'DoS': 2742, 'Backdoor': 1406, 'Shellcode': 974, 'Analysis': 580, 'Worms': 75}

## RQ1 triage effectiveness and RQ3 rule quality (mean ± s.d. over seeds)

| method | det_auroc | alerts | recall@1000 | workload@90_frac | ndcg | macro_f1 | p1_f1 | coverage | fidelity | fidelity_traffic_conds | n_rules | mean_rule_len | contested_rate | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1-score-only | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.004314 ± 0.0011 | 0.9259 ± 0.0081 | 0.8227 ± 0.014 |  |  |  |  |  |  |  |  |  |
| XTriage | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04456 ± 0.0026 | 0.8511 ± 0.01 | 0.9416 ± 0.0039 | 0.4087 ± 0.0099 | 0.7419 ± 0.017 | 0.527 ± 0.038 | 0.05823 ± 0.015 | 0.03226 ± 0.013 | 42.6 ± 3.7 | 3.53 ± 0.068 | 0.654 ± 0.027 | 1 ± 0 |
| B3-raw-rules | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04387 ± 0.0026 | 0.4105 ± 0.026 | 0.9729 ± 0.0028 | 0.8592 ± 0.0066 | 0.7446 ± 0.015 | 0.5268 ± 0.038 | 0.04287 ± 0.018 | 0.04287 ± 0.018 | 43.7 ± 3.3 | 3.582 ± 0.065 | 0 ± 0 | 0 ± 0 |
| B4-tree-surrogate | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.03982 ± 0.0038 | 0.4916 ± 0.03 | 0.9575 ± 0.0034 | 0.7653 ± 0.016 | 0.7075 ± 0.011 | 1 ± 0 | 0.1208 ± 0.075 | 0.1121 ± 0.078 | 14.4 ± 2 | 3.87 ± 0.16 | 0.3025 ± 0.04 | 0 ± 0 |
| Abl-no-SHAP-predicates | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04444 ± 0.0031 | 0.8434 ± 0.019 | 0.943 ± 0.003 | 0.4093 ± 0.0091 | 0.7458 ± 0.013 | 0.5268 ± 0.038 | 0.04301 ± 0.018 | 0.04301 ± 0.018 | 44 ± 3.2 | 3.585 ± 0.065 | 0.6599 ± 0.028 | 1 ± 0 |
| Abl-no-score-band | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04455 ± 0.0025 | 0.8506 ± 0.011 | 0.9419 ± 0.0039 | 0.4088 ± 0.0099 | 0.7425 ± 0.015 | 0.527 ± 0.038 | 0.05888 ± 0.014 | 0.03268 ± 0.013 | 42.4 ± 4 | 3.536 ± 0.082 | 0.6548 ± 0.028 | 1 ± 0 |
| Abl-no-guard | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04456 ± 0.0026 | 0.4162 ± 0.027 | 0.9731 ± 0.0034 | 0.8594 ± 0.0083 | 0.7419 ± 0.017 | 0.527 ± 0.038 | 0.05823 ± 0.015 | 0.03226 ± 0.013 | 42.6 ± 3.7 | 3.53 ± 0.068 | 0 ± 0 | 0 ± 0 |
| Abl-guard-review-tier | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.006697 ± 0.0016 | 0.9259 ± 0.0081 | 0.8415 ± 0.012 | 0.1789 ± 0.012 | 0.06347 ± 0.012 | 0.527 ± 0.038 | 0.05823 ± 0.015 | 0.03226 ± 0.013 | 42.6 ± 3.7 | 3.53 ± 0.068 | 0.654 ± 0.027 | 1 ± 0 |
| Fix-calibrated-guard | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04456 ± 0.0026 | 0.4263 ± 0.026 | 0.9716 ± 0.0034 | 0.8515 ± 0.0082 | 0.7419 ± 0.017 | 0.527 ± 0.038 | 0.05823 ± 0.015 | 0.03226 ± 0.013 | 42.6 ± 3.7 | 3.53 ± 0.068 | 0.5264 ± 0.036 | 0 ± 0 |
| Fix-SHAP-gated-bins | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.03543 ± 0.0029 | 0.9106 ± 0.009 | 0.9028 ± 0.0093 | 0.3162 ± 0.016 | 0.4831 ± 0.063 | 0.5404 ± 0.039 | 1 ± 0 | 1 ± 0 | 49.4 ± 5.3 | 3.696 ± 0.092 | 0.5853 ± 0.06 | 1 ± 0 |
| Fix-no-port-bins | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.04585 ± 0.0038 | 0.8545 ± 0.023 | 0.9416 ± 0.0048 | 0.4084 ± 0.012 | 0.7378 ± 0.016 | 0.5271 ± 0.038 | 0.07526 ± 0.028 | 0.0382 ± 0.013 | 42.4 ± 3.8 | 3.483 ± 0.083 | 0.6487 ± 0.026 | 1 ± 0 |
| Fix-label-filter | 0.8424 ± 0.022 | 1.409e+04 ± 1.2e+03 | 0.0428 ± 0.0035 | 0.8449 ± 0.012 | 0.9416 ± 0.004 | 0.405 ± 0.014 | 0.7416 ± 0.017 | 0.527 ± 0.038 | 0.06216 ± 0.018 | 0.03727 ± 0.012 | 43.7 ± 2 | 3.555 ± 0.12 | 0.6678 ± 0.028 | 1 ± 0 |
| B2-xgboost-shap | 1 ± 1e-07 | 6.17e+04 ± 5.4e+02 | 0.01748 ± 0.0039 | 0.8287 ± 0.0071 | 0.9452 ± 0.0022 |  |  |  |  |  |  |  |  |  |
| XTriage@sample | 0.8424 ± 0.022 | 1500 ± 0 | 0.7816 ± 0.044 | 0.8432 ± 0.059 | 0.9466 ± 0.0068 | 0.4213 ± 0.0095 | 0.7248 ± 0.032 | 0.666 ± 0.0019 | 0.02013 ± 0.02 | 0.007384 ± 0.0072 | 10.8 ± 2.3 | 2.694 ± 0.3 | 0.5819 ± 0.06 | 1 ± 0 |
| B5-LIME@sample | 0.8424 ± 0.022 | 1500 ± 0 | 0.7832 ± 0.031 | 0.8551 ± 0.025 | 0.944 ± 0.0071 | 0.4189 ± 0.012 | 0.7238 ± 0.029 | 0.6659 ± 0.0017 | 0.3418 ± 0.093 | 0.3384 ± 0.093 | 12.4 ± 2 | 2.816 ± 0.24 | 0.5909 ± 0.038 | 1 ± 0 |
| B1-score-only@sample | 0.8424 ± 0.022 | 1500 ± 0 | 0.5994 ± 0.012 | 0.9157 ± 0.014 | 0.813 ± 0.0086 |  |  |  |  |  |  |  |  |  |
| Anchors@sample | 0.8424 ± 0.022 | 3000 ± 0 | 0.6513 ± 0.018 | 0.7557 ± 0.068 | 0.9672 ± 0.0029 | 0.7022 ± 0.012 | 0.7009 ± 0.02 | 0.8035 ± 0.019 | 0.2394 ± 0.027 | 0.07347 ± 0.013 | 423.3 ± 23 | 3.304 ± 0.088 | 0.4892 ± 0.022 | 0.2062 ± 0.043 |
| XTriage@anchor-sample | 0.8424 ± 0.022 | 3000 ± 0 | 0.697 ± 0.031 | 0.851 ± 0.018 | 0.951 ± 0.0025 | 0.4306 ± 0.01 | 0.7496 ± 0.02 | 0.6679 ± 0.0014 | 0.05631 ± 0.026 | 0.03174 ± 0.018 | 32.3 ± 3.5 | 3.356 ± 0.15 | 0.5945 ± 0.022 | 1 ± 0 |

### Paired Wilcoxon signed-rank tests, XTriage vs. each method (over seeds)

n = 10 seeds; with 5 the smallest attainable p-value is 0.0625 two-sided.

| reference | method | metric | n | ref_mean | other_mean | p_two_sided | p_one_sided |
|---|---|---|---|---|---|---|---|
| XTriage | B1-score-only | workload@90_frac | 10 | 0.851 | 0.926 | 0.002 | 0.001 |
| XTriage | B1-score-only | ndcg | 10 | 0.942 | 0.823 | 0.002 | 0.001 |
| XTriage | B1-score-only | recall@1000 | 10 | 0.045 | 0.004 | 0.002 | 0.001 |
| XTriage | B1-score-only | macro_f1 | 0 |  |  |  |  |
| XTriage | B1-score-only | fidelity | 0 |  |  |  |  |
| XTriage | B1-score-only | n_rules | 0 |  |  |  |  |
| XTriage | B3-raw-rules | workload@90_frac | 10 | 0.851 | 0.410 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | ndcg | 10 | 0.942 | 0.973 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | recall@1000 | 10 | 0.045 | 0.044 | 0.348 | 0.174 |
| XTriage | B3-raw-rules | macro_f1 | 10 | 0.409 | 0.859 | 0.002 | 1.000 |
| XTriage | B3-raw-rules | fidelity | 10 | 0.058 | 0.043 | 0.006 | 0.003 |
| XTriage | B3-raw-rules | n_rules | 10 | 42.600 | 43.700 | 0.572 | 0.286 |
| XTriage | B4-tree-surrogate | workload@90_frac | 10 | 0.851 | 0.492 | 0.002 | 1.000 |
| XTriage | B4-tree-surrogate | ndcg | 10 | 0.942 | 0.957 | 0.002 | 1.000 |
| XTriage | B4-tree-surrogate | recall@1000 | 10 | 0.045 | 0.040 | 0.039 | 0.020 |
| XTriage | B4-tree-surrogate | macro_f1 | 10 | 0.409 | 0.765 | 0.002 | 1.000 |
| XTriage | B4-tree-surrogate | fidelity | 10 | 0.058 | 0.121 | 0.064 | 0.976 |
| XTriage | B4-tree-surrogate | n_rules | 10 | 42.600 | 14.400 | 0.002 | 1.000 |
| XTriage | Abl-no-SHAP-predicates | workload@90_frac | 10 | 0.851 | 0.843 | 0.131 | 0.947 |
| XTriage | Abl-no-SHAP-predicates | ndcg | 10 | 0.942 | 0.943 | 0.084 | 0.968 |
| XTriage | Abl-no-SHAP-predicates | recall@1000 | 10 | 0.045 | 0.044 | 0.510 | 0.255 |
| XTriage | Abl-no-SHAP-predicates | macro_f1 | 10 | 0.409 | 0.409 | 0.922 | 0.461 |
| XTriage | Abl-no-SHAP-predicates | fidelity | 10 | 0.058 | 0.043 | 0.006 | 0.003 |
| XTriage | Abl-no-SHAP-predicates | n_rules | 10 | 42.600 | 44.000 | 0.482 | 0.241 |
| XTriage | Abl-no-score-band | workload@90_frac | 10 | 0.851 | 0.851 | 1.000 | 0.750 |
| XTriage | Abl-no-score-band | ndcg | 10 | 0.942 | 0.942 | 0.500 | 1.000 |
| XTriage | Abl-no-score-band | recall@1000 | 10 | 0.045 | 0.045 | 1.000 | 0.500 |
| XTriage | Abl-no-score-band | macro_f1 | 10 | 0.409 | 0.409 | 1.000 | 0.750 |
| XTriage | Abl-no-score-band | fidelity | 10 | 0.058 | 0.059 | 1.000 | 0.750 |
| XTriage | Abl-no-score-band | n_rules | 10 | 42.600 | 42.400 | 1.000 | 1.000 |
| XTriage | Abl-no-guard | workload@90_frac | 10 | 0.851 | 0.416 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | ndcg | 10 | 0.942 | 0.973 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | recall@1000 | 10 | 0.045 | 0.045 |  |  |
| XTriage | Abl-no-guard | macro_f1 | 10 | 0.409 | 0.859 | 0.002 | 1.000 |
| XTriage | Abl-no-guard | fidelity | 10 | 0.058 | 0.058 |  |  |
| XTriage | Abl-no-guard | n_rules | 10 | 42.600 | 42.600 |  |  |
| XTriage | Abl-guard-review-tier | workload@90_frac | 10 | 0.851 | 0.926 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | ndcg | 10 | 0.942 | 0.842 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | recall@1000 | 10 | 0.045 | 0.007 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | macro_f1 | 10 | 0.409 | 0.179 | 0.002 | 0.001 |
| XTriage | Abl-guard-review-tier | fidelity | 10 | 0.058 | 0.058 |  |  |
| XTriage | Abl-guard-review-tier | n_rules | 10 | 42.600 | 42.600 |  |  |
| XTriage | Fix-calibrated-guard | workload@90_frac | 10 | 0.851 | 0.426 | 0.002 | 1.000 |
| XTriage | Fix-calibrated-guard | ndcg | 10 | 0.942 | 0.972 | 0.002 | 1.000 |
| XTriage | Fix-calibrated-guard | recall@1000 | 10 | 0.045 | 0.045 |  |  |
| XTriage | Fix-calibrated-guard | macro_f1 | 10 | 0.409 | 0.851 | 0.002 | 1.000 |
| XTriage | Fix-calibrated-guard | fidelity | 10 | 0.058 | 0.058 |  |  |
| XTriage | Fix-calibrated-guard | n_rules | 10 | 42.600 | 42.600 |  |  |
| XTriage | Fix-SHAP-gated-bins | workload@90_frac | 10 | 0.851 | 0.911 | 0.002 | 0.001 |
| XTriage | Fix-SHAP-gated-bins | ndcg | 10 | 0.942 | 0.903 | 0.002 | 0.001 |
| XTriage | Fix-SHAP-gated-bins | recall@1000 | 10 | 0.045 | 0.035 | 0.002 | 0.001 |
| XTriage | Fix-SHAP-gated-bins | macro_f1 | 10 | 0.409 | 0.316 | 0.002 | 0.001 |
| XTriage | Fix-SHAP-gated-bins | fidelity | 10 | 0.058 | 1.000 | 0.002 | 1.000 |
| XTriage | Fix-SHAP-gated-bins | n_rules | 10 | 42.600 | 49.400 | 0.031 | 0.016 |
| XTriage | Fix-no-port-bins | workload@90_frac | 10 | 0.851 | 0.855 | 0.432 | 0.216 |
| XTriage | Fix-no-port-bins | ndcg | 10 | 0.942 | 0.942 | 0.695 | 0.348 |
| XTriage | Fix-no-port-bins | recall@1000 | 10 | 0.045 | 0.046 | 0.232 | 0.903 |
| XTriage | Fix-no-port-bins | macro_f1 | 10 | 0.409 | 0.408 | 0.922 | 0.461 |
| XTriage | Fix-no-port-bins | fidelity | 10 | 0.058 | 0.075 | 0.131 | 0.947 |
| XTriage | Fix-no-port-bins | n_rules | 10 | 42.600 | 42.400 | 0.828 | 0.703 |
| XTriage | Fix-label-filter | workload@90_frac | 10 | 0.851 | 0.845 | 0.105 | 0.958 |
| XTriage | Fix-label-filter | ndcg | 10 | 0.942 | 0.942 | 0.922 | 0.577 |
| XTriage | Fix-label-filter | recall@1000 | 10 | 0.045 | 0.043 | 0.055 | 0.027 |
| XTriage | Fix-label-filter | macro_f1 | 10 | 0.409 | 0.405 | 0.160 | 0.080 |
| XTriage | Fix-label-filter | fidelity | 10 | 0.058 | 0.062 | 0.432 | 0.812 |
| XTriage | Fix-label-filter | n_rules | 10 | 42.600 | 43.700 | 0.547 | 0.273 |
| XTriage | B2-xgboost-shap | workload@90_frac | 10 | 0.851 | 0.829 | 0.002 | 1.000 |
| XTriage | B2-xgboost-shap | ndcg | 10 | 0.942 | 0.945 | 0.037 | 0.986 |
| XTriage | B2-xgboost-shap | recall@1000 | 10 | 0.045 | 0.017 | 0.002 | 0.001 |
| XTriage | B2-xgboost-shap | macro_f1 | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | fidelity | 0 |  |  |  |  |
| XTriage | B2-xgboost-shap | n_rules | 0 |  |  |  |  |

## RQ2 explanation reliability

| group | n | jaccard_bg | kendall_bg | jaccard_seed | kendall_seed | rule_change_bg | tier_change_bg |
|---|---|---|---|---|---|---|---|
| all | 600 | 0.939 | 0.930 | 0.408 | 0.715 | 0.003 | 0.000 |
| band=high | 176 | 0.959 | 0.940 | 0.236 | 0.742 | 0.000 | 0.000 |
| band=low | 212 | 0.934 | 0.915 | 0.594 | 0.670 | 0.008 | 0.000 |
| band=medium | 212 | 0.928 | 0.935 | 0.365 | 0.739 | 0.000 | 0.000 |
| priority=P1 | 78 | 0.939 | 0.918 | 0.494 | 0.673 | 0.003 | 0.000 |
| priority=P2 | 116 | 0.966 | 0.915 | 0.582 | 0.667 | 0.013 | 0.000 |
| priority=P3 | 406 | 0.932 | 0.936 | 0.342 | 0.738 | 0.000 | 0.000 |

Deletion-curve faithfulness (lower AUC = more faithful):

| method | n | deletion_auc | after_1 | after_3 | after_5 | after_10 |
|---|---|---|---|---|---|---|
| SHAP | 300 | 0.709 | 0.936 | 0.820 | 0.704 | 0.439 |
| LIME | 300 | 0.990 | 0.991 | 0.990 | 0.989 | 0.989 |
| random | 300 | 0.948 | 0.988 | 0.969 | 0.949 | 0.893 |

## RQ4 limitation probes

### Background set

| probe | variant | n_background | phi0 | jaccard_vs_ref | kendall_vs_ref | rule_change | tier_change | p1_tier_lost |
|---|---|---|---|---|---|---|---|---|
| background | size=10 | 10 | -12.801 | 0.918 | 0.840 | 0.005 | 0.002 | 0.002 |
| background | size=50 | 50 | -12.531 | 0.933 | 0.945 | 0.002 | 0.002 | 0.002 |
| background | size=100 | 100 | -12.526 | 0.958 | 0.943 | 0.000 | 0.000 | 0.000 |
| background | size=500 | 500 | -12.544 | 0.944 | 0.939 | 0.000 | 0.000 | 0.000 |
| background | window=early-fit | 100 | -12.464 | 0.942 | 0.945 | 0.002 | 0.000 | 0.000 |
| background | window=late-fit | 100 | -12.855 | 0.949 | 0.931 | 0.003 | 0.000 | 0.000 |
| background | mix=tune-benign | 100 | -12.555 | 0.917 | 0.907 | 0.003 | 0.000 | 0.000 |
| background | mix=tune-all-traffic | 100 | -11.917 | 0.921 | 0.866 | 0.002 | 0.002 | 0.002 |
| background | mix=50%-attack | 100 | -11.600 | 0.900 | 0.854 | 0.002 | 0.002 | 0.002 |

### Shortcut features

| probe | variant | dropped | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90 | workload@90_frac | ndcg | macro_f1 | coverage | n_rules | fidelity | top1_is_shortcut | shortcut_attr_share | shortcut_share[DoS] | shortcut_share[Exploits] | shortcut_share[Benign] | shortcut_share[Fuzzers] | shortcut_share[Shellcode] | shortcut_share[Reconnaissance] | shortcut_share[Backdoor] | shortcut_share[Generic] | shortcut_share[Worms] | shortcut_share[Analysis] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shortcut | full | L4_DST_PORT;MIN_TTL;MAX_TTL | 152024 | 14180 | 0.093 | 0.537 | 0.139 | 0.176 | 6562 | 0.862 | 0.636 | 0.745 | 0.202 | 11926 | 0.841 | 0.940 | 0.404 | 0.537 | 45 | 0.081 | 0.158 | 0.060 | 0.033 | 0.028 | 0.098 | 0.027 | 0.041 | 0.026 | 0.025 | 0.025 | 0.026 | 0.024 |
| shortcut | without-shortcuts | L4_DST_PORT;MIN_TTL;MAX_TTL | 152024 | 13639 | 0.090 | 0.511 | 0.127 | 0.155 | 6676 | 0.847 | 0.622 | 0.723 | 0.193 | 12225 | 0.896 | 0.938 | 0.403 | 0.512 | 42 | 0.110 |  |  |  |  |  |  |  |  |  |  |  |  |

### Distribution shift (time)

| probe | variant | flows | alerts | alert_rate | alert_precision | attack_recall | p1_alerted | benign_alerts | auroc | auprc | auroc_p1 | auprc_p1 | workload@90_frac | ndcg | macro_f1 | coverage | contested_rate | rule_error_rate | classes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shift-time | early-test | 76012 | 7303 | 0.096 | 0.530 | 0.140 | 0.185 | 3430 | 0.854 | 0.625 | 0.738 | 0.187 | 0.837 | 0.933 | 0.400 | 0.531 | 0.661 | 0.116 | Analysis;Backdoor;Benign;DoS;Exploits;Fuzzers;Generic;Reconnaissance;Shellcode;Worms |
| shift-time | late-test | 76012 | 6877 | 0.090 | 0.545 | 0.137 | 0.168 | 3132 | 0.870 | 0.648 | 0.752 | 0.217 | 0.847 | 0.936 | 0.409 | 0.544 | 0.639 | 0.113 | Analysis;Backdoor;Benign;DoS;Exploits;Fuzzers;Generic;Reconnaissance;Shellcode;Worms |

### Feature-space evasion

| probe | method | variant | n | mean_abs_dq | mean_ds | evaded_detection | rule_changed | tier_changed | tier_changed_still_alerted | p1_downgraded | became_contested |
|---|---|---|---|---|---|---|---|---|---|---|---|
| evasion | XTriage | padding=16 | 2000 | 0.001 | -0.073 | 0.065 | 0.551 | 0.150 | 0.149 | 0.060 | 0.127 |
| evasion | XTriage | padding=64 | 2000 | 0.004 | 0.270 | 0.001 | 0.684 | 0.270 | 0.270 | 0.070 | 0.234 |
| evasion | XTriage | padding=256 | 2000 | 0.004 | 0.303 | 0.018 | 0.723 | 0.197 | 0.201 | 0.072 | 0.159 |
| evasion | XTriage | timing=0.5 | 2000 | 0.029 | -1.124 | 0.600 | 0.394 | 0.095 | 0.050 | 0.123 | 0.051 |
| evasion | XTriage | timing=2.0 | 2000 | 0.012 | 0.895 | 0.022 | 0.302 | 0.101 | 0.103 | 0.042 | 0.073 |
| evasion | XTriage | timing=5.0 | 2000 | 0.024 | 1.787 | 0.029 | 0.395 | 0.181 | 0.186 | 0.036 | 0.058 |
| evasion | XTriage | port=80 | 2000 | 0.000 | -0.022 | 0.020 | 0.086 | 0.027 | 0.028 | 0.058 | 0.003 |
| evasion | XTriage | port=443 | 2000 | 0.000 | -0.021 | 0.019 | 0.068 | 0.013 | 0.013 | 0.001 | 0.011 |
| evasion | Fix-SHAP-gated-bins | padding=16 | 2000 | 0.001 | -0.073 | 0.065 | 0.015 | 0.009 | 0.009 | 0.007 | 0.006 |
| evasion | Fix-SHAP-gated-bins | padding=64 | 2000 | 0.004 | 0.270 | 0.001 | 0.141 | 0.044 | 0.045 | 0.097 | 0.014 |
| evasion | Fix-SHAP-gated-bins | padding=256 | 2000 | 0.004 | 0.303 | 0.018 | 0.160 | 0.063 | 0.064 | 0.102 | 0.033 |
| evasion | Fix-SHAP-gated-bins | timing=0.5 | 2000 | 0.029 | -1.124 | 0.600 | 0.696 | 0.238 | 0.275 | 0.483 | 0.111 |
| evasion | Fix-SHAP-gated-bins | timing=2.0 | 2000 | 0.012 | 0.895 | 0.022 | 0.796 | 0.303 | 0.292 | 0.261 | 0.225 |
| evasion | Fix-SHAP-gated-bins | timing=5.0 | 2000 | 0.024 | 1.787 | 0.029 | 0.911 | 0.530 | 0.535 | 0.539 | 0.259 |
| evasion | Fix-SHAP-gated-bins | port=80 | 2000 | 0.000 | -0.022 | 0.020 | 0.007 | 0.003 | 0.002 | 0.000 | 0.003 |
| evasion | Fix-SHAP-gated-bins | port=443 | 2000 | 0.000 | -0.021 | 0.019 | 0.006 | 0.003 | 0.002 | 0.000 | 0.003 |
| evasion | Fix-no-port-bins | padding=16 | 2000 | 0.001 | -0.073 | 0.065 | 0.512 | 0.150 | 0.145 | 0.067 | 0.124 |
| evasion | Fix-no-port-bins | padding=64 | 2000 | 0.004 | 0.270 | 0.001 | 0.644 | 0.215 | 0.215 | 0.056 | 0.185 |
| evasion | Fix-no-port-bins | padding=256 | 2000 | 0.004 | 0.303 | 0.018 | 0.677 | 0.236 | 0.241 | 0.048 | 0.208 |
| evasion | Fix-no-port-bins | timing=0.5 | 2000 | 0.029 | -1.124 | 0.600 | 0.370 | 0.053 | 0.046 | 0.085 | 0.025 |
| evasion | Fix-no-port-bins | timing=2.0 | 2000 | 0.012 | 0.895 | 0.022 | 0.357 | 0.089 | 0.089 | 0.069 | 0.043 |
| evasion | Fix-no-port-bins | timing=5.0 | 2000 | 0.024 | 1.787 | 0.029 | 0.395 | 0.140 | 0.144 | 0.042 | 0.033 |
| evasion | Fix-no-port-bins | port=80 | 2000 | 0.000 | -0.022 | 0.020 | 0.004 | 0.001 | 0.001 | 0.003 | 0.001 |
| evasion | Fix-no-port-bins | port=443 | 2000 | 0.000 | -0.021 | 0.019 | 0.004 | 0.001 | 0.001 | 0.001 | 0.001 |
| evasion | Fix-calibrated-guard | padding=16 | 2000 | 0.001 | -0.073 | 0.065 | 0.551 | 0.156 | 0.151 | 0.060 | 0.003 |
| evasion | Fix-calibrated-guard | padding=64 | 2000 | 0.004 | 0.270 | 0.001 | 0.684 | 0.272 | 0.272 | 0.070 | 0.001 |
| evasion | Fix-calibrated-guard | padding=256 | 2000 | 0.004 | 0.303 | 0.018 | 0.723 | 0.199 | 0.202 | 0.072 | 0.001 |
| evasion | Fix-calibrated-guard | timing=0.5 | 2000 | 0.029 | -1.124 | 0.600 | 0.394 | 0.095 | 0.050 | 0.123 | 0.010 |
| evasion | Fix-calibrated-guard | timing=2.0 | 2000 | 0.012 | 0.895 | 0.022 | 0.302 | 0.101 | 0.103 | 0.042 | 0.000 |
| evasion | Fix-calibrated-guard | timing=5.0 | 2000 | 0.024 | 1.787 | 0.029 | 0.395 | 0.181 | 0.186 | 0.036 | 0.000 |
| evasion | Fix-calibrated-guard | port=80 | 2000 | 0.000 | -0.022 | 0.020 | 0.086 | 0.027 | 0.028 | 0.058 | 0.004 |
| evasion | Fix-calibrated-guard | port=443 | 2000 | 0.000 | -0.021 | 0.019 | 0.068 | 0.013 | 0.013 | 0.001 | 0.001 |

### Rule infidelity and the guard

| seed | method | rule_error_rate | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|
| 0 | XTriage | 0.115 | 0.651 | 0.393 | 0.069 | 2.000 | 1.000 |
| 0 | B4-tree-surrogate | 0.147 | 0.323 | 0.589 | 0.268 | 10.000 | 0.000 |
| 0 | Abl-no-guard | 0.115 | 0.000 | 0.000 |  | 2.000 | 0.000 |
| 1 | XTriage | 0.096 | 0.667 | 0.354 | 0.051 | 3.000 | 1.000 |
| 1 | B4-tree-surrogate | 0.137 | 0.313 | 0.569 | 0.249 | 8.000 | 0.000 |
| 1 | Abl-no-guard | 0.096 | 0.000 | 0.000 |  | 3.000 | 0.000 |
| 2 | XTriage | 0.100 | 0.624 | 0.270 | 0.043 | 2.000 | 1.000 |
| 2 | B4-tree-surrogate | 0.137 | 0.309 | 0.584 | 0.258 | 8.000 | 0.000 |
| 2 | Abl-no-guard | 0.100 | 0.000 | 0.000 |  | 2.000 | 0.000 |
| 3 | XTriage | 0.095 | 0.678 | 0.307 | 0.043 | 1.000 | 1.000 |
| 3 | B4-tree-surrogate | 0.136 | 0.324 | 0.638 | 0.267 | 9.000 | 0.000 |
| 3 | Abl-no-guard | 0.095 | 0.000 | 0.000 |  | 1.000 | 0.000 |
| 4 | XTriage | 0.115 | 0.656 | 0.399 | 0.070 | 2.000 | 1.000 |
| 4 | B4-tree-surrogate | 0.115 | 0.219 | 0.183 | 0.096 | 8.000 | 0.000 |
| 4 | Abl-no-guard | 0.115 | 0.000 | 0.000 |  | 2.000 | 0.000 |
| 5 | XTriage | 0.110 | 0.621 | 0.355 | 0.063 | 0.000 |  |
| 5 | B4-tree-surrogate | 0.156 | 0.345 | 0.632 | 0.285 | 8.000 | 0.000 |
| 5 | Abl-no-guard | 0.110 | 0.000 | 0.000 |  | 0.000 |  |
| 6 | XTriage | 0.089 | 0.700 | 0.354 | 0.045 | 1.000 | 1.000 |
| 6 | B4-tree-surrogate | 0.110 | 0.294 | 0.504 | 0.189 | 10.000 | 0.000 |
| 6 | Abl-no-guard | 0.089 | 0.000 | 0.000 |  | 1.000 | 0.000 |
| 7 | XTriage | 0.097 | 0.677 | 0.335 | 0.048 | 3.000 | 1.000 |
| 7 | B4-tree-surrogate | 0.143 | 0.332 | 0.612 | 0.263 | 18.000 | 0.000 |
| 7 | Abl-no-guard | 0.097 | 0.000 | 0.000 |  | 3.000 | 0.000 |
| 8 | XTriage | 0.117 | 0.648 | 0.383 | 0.069 | 1.000 | 1.000 |
| 8 | B4-tree-surrogate | 0.147 | 0.322 | 0.622 | 0.283 | 6.000 | 0.000 |
| 8 | Abl-no-guard | 0.117 | 0.000 | 0.000 |  | 1.000 | 0.000 |
| 9 | XTriage | 0.123 | 0.620 | 0.399 | 0.079 | 3.000 | 1.000 |
| 9 | B4-tree-surrogate | 0.123 | 0.243 | 0.256 | 0.130 | 5.000 | 0.000 |
| 9 | Abl-no-guard | 0.123 | 0.000 | 0.000 |  | 3.000 | 0.000 |

### Guard trade-off (calibrated guard, tau sweep; seed 0)

| probe | variant | tau | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate | guard_catch_rate | guard_precision | severe_errors | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|
| guard | Abl-no-guard |  | 0.420 | 0.970 | 0.851 | 0.727 | 0.000 | 0.000 |  | 2 | 0.000 |
| guard | XTriage |  | 0.841 | 0.940 | 0.404 | 0.727 | 0.651 | 0.393 | 0.069 | 2 | 1.000 |
| guard | calibrated | 0.002 | 0.497 | 0.961 | 0.791 | 0.727 | 0.601 | 0.953 | 0.182 | 2 | 0.000 |
| guard | calibrated | 0.005 | 0.497 | 0.961 | 0.791 | 0.727 | 0.601 | 0.953 | 0.182 | 2 | 0.000 |
| guard | calibrated | 0.010 | 0.431 | 0.969 | 0.842 | 0.727 | 0.535 | 0.953 | 0.204 | 2 | 0.000 |
| guard | calibrated | 0.020 | 0.431 | 0.969 | 0.842 | 0.727 | 0.535 | 0.953 | 0.204 | 2 | 0.000 |
| guard | calibrated | 0.050 | 0.431 | 0.969 | 0.842 | 0.727 | 0.535 | 0.953 | 0.204 | 2 | 0.000 |
| guard | calibrated | 0.100 | 0.420 | 0.970 | 0.851 | 0.727 | 0.512 | 0.950 | 0.213 | 2 | 0.000 |

### Alert threshold (mean over probe seeds)

| theta | alerts | det_p1_alerted | recall@1000 | workload@90 | workload@90_frac | ndcg | macro_f1 | p1_f1 | contested_rate |
|---|---|---|---|---|---|---|---|---|---|
| 0.900 | 37304.667 | 0.454 | 0.035 | 25351.667 | 0.682 | 0.955 | 0.406 | 0.639 | 0.609 |
| 0.950 | 14071.333 | 0.172 | 0.045 | 12004.667 | 0.853 | 0.943 | 0.411 | 0.742 | 0.647 |
| 0.990 | 1383.000 | 0.007 | 0.007 | 1064.000 | 0.769 | 0.875 | 0.274 | 0.658 | 0.793 |

### Isolation-forest size vs. explanation stability across retraining seeds

| probe | n_estimators | n | jaccard_seed | kendall_seed | mean_abs_dq_seed | jaccard_seed[low] | jaccard_seed[medium] | jaccard_seed[high] |
|---|---|---|---|---|---|---|---|---|
| forest-size | 100 | 600 | 0.408 | 0.715 | 0.003 | 0.594 | 0.365 | 0.236 |
| forest-size | 300 | 600 | 0.524 | 0.817 | 0.002 | 0.783 | 0.424 | 0.296 |
| forest-size | 1000 | 600 | 0.655 | 0.888 | 0.001 | 0.817 | 0.534 | 0.561 |

### Oracle noise (mean over probe seeds)

| method | eta | labels_filtered | macro_f1 | macro_f1_rules | p1_f1 | coverage | n_rules | mean_rule_len | fidelity | workload@90_frac | ndcg | contested_rate | guard_catch_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fix-label-filter | 0.000 | 179.000 | 0.413 | 0.864 | 0.748 | 0.529 | 41.667 | 3.480 | 0.077 | 0.851 | 0.943 | 0.652 | 0.361 |
| Fix-label-filter | 0.100 | 1099.667 | 0.400 | 0.849 | 0.728 | 0.529 | 45.667 | 3.529 | 0.063 | 0.848 | 0.943 | 0.668 | 0.448 |
| Fix-label-filter | 0.200 | 1965.000 | 0.397 | 0.844 | 0.706 | 0.529 | 44.667 | 3.411 | 0.090 | 0.858 | 0.940 | 0.640 | 0.317 |
| Fix-label-filter | 0.300 | 2462.333 | 0.394 | 0.839 | 0.697 | 0.530 | 52.333 | 3.617 | 0.111 | 0.869 | 0.937 | 0.640 | 0.335 |
| XTriage | 0.000 | 0.000 | 0.411 | 0.861 | 0.742 | 0.529 | 41.000 | 3.498 | 0.073 | 0.853 | 0.943 | 0.647 | 0.339 |
| XTriage | 0.100 | 0.000 | 0.403 | 0.852 | 0.727 | 0.529 | 40.000 | 3.537 | 0.061 | 0.854 | 0.942 | 0.654 | 0.381 |
| XTriage | 0.200 | 0.000 | 0.392 | 0.838 | 0.715 | 0.528 | 35.000 | 3.543 | 0.051 | 0.846 | 0.944 | 0.678 | 0.489 |
| XTriage | 0.300 | 0.000 | 0.366 | 0.809 | 0.686 | 0.529 | 30.667 | 3.662 | 0.102 | 0.831 | 0.939 | 0.718 | 0.615 |

## Detector robustness

| detector | method | det_auroc | det_auprc | alerts | alerts_explained | workload@90_frac | ndcg | recall@1000 | macro_f1 | fidelity | n_rules | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| autoencoder | XTriage | 0.9997 ± 1.4e-05 | 0.9992 ± 5.4e-05 | 3000 ± 0 | 3000 ± 0 | 0.5808 ± 0.012 | 0.9456 ± 0.0059 | 0.657 ± 0.026 | 0.3902 ± 0.0082 | 0.6189 ± 0.064 | 20.67 ± 5.5 | 58.39 ± 2.7 |
| autoencoder | B1-score-only | 0.9997 ± 1.4e-05 | 0.9992 ± 5.4e-05 | 3000 ± 0 | 3000 ± 0 | 0.6332 ± 0.0072 | 0.903 ± 0.0023 | 0.3593 ± 0.026 |  |  |  | 58.39 ± 2.7 |
| xgboost | XTriage | 1 ± 2.4e-08 | 1 ± 4.4e-08 | 6.143e+04 ± 2.5e+02 | 6.143e+04 ± 2.5e+02 | 0.5958 ± 0.01 | 0.9564 ± 0.0031 | 0.0203 ± 0.0058 | 0.3847 ± 0.0085 | 0.602 ± 0.073 | 35.67 ± 2.3 | 41.54 ± 3.7 |
| xgboost | B1-score-only | 1 ± 2.4e-08 | 1 ± 4.4e-08 | 6.143e+04 ± 2.5e+02 | 6.143e+04 ± 2.5e+02 | 0.8315 ± 0.0034 | 0.946 ± 0.0039 | 0.01822 ± 0.0051 |  |  |  | 41.54 ± 3.7 |

## RQ5 accountability

* records: 5583, chain verified: True, tamper detected: True (first bad seq 1004)
* replay success: 1.000 over 500 records {'score': 1.0, 'percentile': 1.0, 'attribution': 1.0, 'rule': 1.0, 'tier': 1.0, 'ok': 1.0}
* bytes per record: 1472; contested rate: 0.645
* testbed: 4 sensors, 60000 flows, 5583 alerts, 1524 flows/s; t1 0.567 ms/flow, t2 1.685 ms/alert, t3 0.285 ms/record, publish-to-ledger latency incl. queueing under max-rate replay p50 7836 ms / p95 15615 ms
