# XTriage results -- cic2017
## Data
* windows: {'fit': 529918, 'tune': 1346044, 'test': 954781}
* tune rows: 145064, test rows: 149837
* test priorities: {'P3': 88453, 'P2': 60421, 'P1': 963}
* test classes: {'Benign': 88453, 'DDoS': 15000, 'PortScan': 11225, 'DoS GoldenEye': 10293, 'DoS Hulk': 9742, 'DoS Slowhttptest': 3997, 'DoS slowloris': 3206, 'SSH-Patator': 2948, 'FTP-Patator': 2693, 'Bot': 936, 'Web Attack - Brute Force': 796, 'Web Attack - XSS': 521, 'Infiltration': 23, 'Heartbleed': 4}

## RQ1 triage effectiveness and RQ3 rule quality (mean ± s.d. over seeds)

| method | det_auroc | alerts | recall@1000 | workload@90_frac | ndcg | macro_f1 | p1_f1 | coverage | fidelity | fidelity_traffic_conds | n_rules | mean_rule_len | contested_rate | severe_caught |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1-score-only | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.01703 ± 0.0092 | 0.4528 ± 0.14 | 0.9232 ± 0.013 |  |  |  |  |  |  |  |  |  |
| XTriage | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.03863 ± 0.0047 | 0.2046 ± 0.33 | 0.9546 ± 0.0086 | 0.8158 ± 0.018 | 0.7363 ± 0.12 | 0.3644 ± 0.1 | 0.05649 ± 0.087 | 0.01263 ± 0.0079 | 13 ± 1.6 | 2.386 ± 0.046 | 0.7093 ± 0.084 | 0.7277 ± 0.1 |
| B3-raw-rules | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.0324 ± 0.0076 | 0.5717 ± 0.33 | 0.9932 ± 0.0032 | 0.8814 ± 0.023 | 0.7454 ± 0.11 | 0.3588 ± 0.099 | 0.06397 ± 0.036 | 0.06397 ± 0.036 | 14.8 ± 2.7 | 2.675 ± 0.19 | 0 ± 0 | 0 ± 0 |
| B4-tree-surrogate | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.0297 ± 0.0028 | 0.7936 ± 0.057 | 0.9506 ± 0.011 | 0.7475 ± 0.031 | 0.4693 ± 0.069 | 1 ± 0 | 0.021 ± 0.013 | 0.003397 ± 0.004 | 12 ± 0.71 | 3.698 ± 0.058 | 0.07416 ± 0.018 | 0.6727 ± 0.13 |
| Abl-no-SHAP-predicates | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.03946 ± 0.0042 | 0.2055 ± 0.34 | 0.9545 ± 0.0097 | 0.8269 ± 0.02 | 0.7525 ± 0.095 | 0.3561 ± 0.097 | 0.06263 ± 0.035 | 0.06263 ± 0.035 | 15.2 ± 2.3 | 2.605 ± 0.18 | 0.7173 ± 0.08 | 0.7115 ± 0.15 |
| Abl-no-score-band | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.03884 ± 0.0049 | 0.2045 ± 0.33 | 0.9548 ± 0.0085 | 0.815 ± 0.017 | 0.734 ± 0.11 | 0.3644 ± 0.1 | 0.0566 ± 0.087 | 0.01263 ± 0.0079 | 13.2 ± 1.8 | 2.381 ± 0.051 | 0.7093 ± 0.084 | 0.7406 ± 0.12 |
| Abl-no-guard | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.03115 ± 0.0086 | 0.5707 ± 0.33 | 0.9931 ± 0.0026 | 0.8744 ± 0.023 | 0.7363 ± 0.12 | 0.3644 ± 0.1 | 0.05649 ± 0.087 | 0.01263 ± 0.0079 | 13 ± 1.6 | 2.386 ± 0.046 | 0 ± 0 | 0 ± 0 |
| Abl-guard-review-tier | 0.7149 ± 0.0082 | 1.642e+04 ± 4.3e+03 | 0.0243 ± 0.011 | 0.4635 ± 0.22 | 0.9491 ± 0.01 | 0.7374 ± 0.081 | 0.5018 ± 0.29 | 0.3644 ± 0.1 | 0.05649 ± 0.087 | 0.01263 ± 0.0079 | 13 ± 1.6 | 2.386 ± 0.046 | 0.7093 ± 0.084 | 0.7277 ± 0.1 |
| B2-xgboost-shap | 0.9999 ± 5.9e-06 | 6.579e+04 ± 85 | 0 ± 0 | 0.8769 ± 0.00074 | 0.9753 ± 6.9e-05 |  |  |  |  |  |  |  |  |  |
| XTriage@sample | 0.7149 ± 0.0082 | 1500 ± 0 | 0.9722 ± 0.038 | 0.1876 ± 0.26 | 0.9228 ± 0.029 | 0.7648 ± 0.17 | 0.81 ± 0.081 | 0.5099 ± 0.088 | 0.04864 ± 0.044 | 0.01205 ± 0.009 | 7 ± 1.9 | 1.88 ± 0.3 | 0.5928 ± 0.035 | 0.6021 ± 0.45 |
| B5-LIME@sample | 0.7149 ± 0.0082 | 1500 ± 0 | 0.9675 ± 0.021 | 0.09333 ± 0.042 | 0.9252 ± 0.03 | 0.7884 ± 0.18 | 0.8412 ± 0.07 | 0.4915 ± 0.071 | 0.03167 ± 0.048 | 0.03167 ± 0.048 | 7.2 ± 1.3 | 1.983 ± 0.23 | 0.6093 ± 0.017 | 0.7556 ± 0.2 |
| B1-score-only@sample | 0.7149 ± 0.0082 | 1500 ± 0 | 0.977 ± 0.016 | 0.4721 ± 0.12 | 0.8125 ± 0.02 |  |  |  |  |  |  |  |  |  |
| Anchors@sample | 0.7149 ± 0.0082 | 2000 ± 0 | 0.5981 ± 0.22 | 0.6932 ± 0.075 | 0.8343 ± 0.014 | 0.5338 ± 0.022 | 0 ± 0 | 1 ± 0 | 0.3726 ± 0.13 | 0.1306 ± 0.14 | 37.2 ± 4.3 | 1.029 ± 0.066 | 0.129 ± 0.015 | 0.5608 ± 0.23 |
| XTriage@anchor-sample | 0.7149 ± 0.0082 | 2000 ± 0 | 0.9307 ± 0.064 | 0.1903 ± 0.26 | 0.9191 ± 0.025 | 0.7708 ± 0.18 | 0.822 ± 0.1 | 0.5061 ± 0.087 | 0.04768 ± 0.062 | 0.01276 ± 0.015 | 8.8 ± 1.5 | 2.195 ± 0.21 | 0.5927 ± 0.04 | 0.5321 ± 0.42 |

### Paired Wilcoxon signed-rank tests, XTriage vs. each method (over seeds)

With n = 5 seeds the smallest attainable p-value is 0.0625 two-sided and 0.03125 one-sided.

| reference | method | metric | n | ref_mean | other_mean | p_two_sided | p_one_sided |
|---|---|---|---|---|---|---|---|
| XTriage | B1-score-only | workload@90_frac | 5 | 0.205 | 0.453 | 0.188 | 0.094 |
| XTriage | B1-score-only | ndcg | 5 | 0.955 | 0.923 | 0.062 | 0.031 |
| XTriage | B1-score-only | recall@1000 | 5 | 0.039 | 0.017 | 0.062 | 0.031 |
| XTriage | B1-score-only | macro_f1 | 0 |  |  |  |  |
| XTriage | B1-score-only | fidelity | 0 |  |  |  |  |
| XTriage | B1-score-only | n_rules | 0 |  |  |  |  |
| XTriage | B3-raw-rules | workload@90_frac | 5 | 0.205 | 0.572 | 0.125 | 0.062 |
| XTriage | B3-raw-rules | ndcg | 5 | 0.955 | 0.993 | 0.062 | 1.000 |
| XTriage | B3-raw-rules | recall@1000 | 5 | 0.039 | 0.032 | 0.125 | 0.062 |
| XTriage | B3-raw-rules | macro_f1 | 5 | 0.816 | 0.881 | 0.062 | 1.000 |
| XTriage | B3-raw-rules | fidelity | 5 | 0.056 | 0.064 | 0.812 | 0.688 |
| XTriage | B3-raw-rules | n_rules | 5 | 13.000 | 14.800 | 0.312 | 0.156 |
| XTriage | B4-tree-surrogate | workload@90_frac | 5 | 0.205 | 0.794 | 0.062 | 0.031 |
| XTriage | B4-tree-surrogate | ndcg | 5 | 0.955 | 0.951 | 0.125 | 0.062 |
| XTriage | B4-tree-surrogate | recall@1000 | 5 | 0.039 | 0.030 | 0.062 | 0.031 |
| XTriage | B4-tree-surrogate | macro_f1 | 5 | 0.816 | 0.747 | 0.125 | 0.062 |
| XTriage | B4-tree-surrogate | fidelity | 5 | 0.056 | 0.021 | 0.812 | 0.406 |
| XTriage | B4-tree-surrogate | n_rules | 5 | 13.000 | 12.000 | 0.500 | 0.875 |
| XTriage | Abl-no-SHAP-predicates | workload@90_frac | 5 | 0.205 | 0.206 | 0.875 | 0.688 |
| XTriage | Abl-no-SHAP-predicates | ndcg | 5 | 0.955 | 0.954 | 1.000 | 0.594 |
| XTriage | Abl-no-SHAP-predicates | recall@1000 | 5 | 0.039 | 0.039 | 0.250 | 1.000 |
| XTriage | Abl-no-SHAP-predicates | macro_f1 | 5 | 0.816 | 0.827 | 0.625 | 0.781 |
| XTriage | Abl-no-SHAP-predicates | fidelity | 5 | 0.056 | 0.063 | 0.812 | 0.688 |
| XTriage | Abl-no-SHAP-predicates | n_rules | 5 | 13.000 | 15.200 | 0.188 | 0.094 |
| XTriage | Abl-no-score-band | workload@90_frac | 5 | 0.205 | 0.205 | 1.000 | 0.750 |
| XTriage | Abl-no-score-band | ndcg | 5 | 0.955 | 0.955 | 0.500 | 1.000 |
| XTriage | Abl-no-score-band | recall@1000 | 5 | 0.039 | 0.039 | 1.000 | 1.000 |
| XTriage | Abl-no-score-band | macro_f1 | 5 | 0.816 | 0.815 | 1.000 | 0.500 |
| XTriage | Abl-no-score-band | fidelity | 5 | 0.056 | 0.057 | 0.500 | 1.000 |
| XTriage | Abl-no-score-band | n_rules | 5 | 13.000 | 13.200 | 1.000 | 0.500 |
| XTriage | Abl-no-guard | workload@90_frac | 5 | 0.205 | 0.571 | 0.250 | 0.125 |
| XTriage | Abl-no-guard | ndcg | 5 | 0.955 | 0.993 | 0.062 | 1.000 |
| XTriage | Abl-no-guard | recall@1000 | 5 | 0.039 | 0.031 | 0.125 | 0.062 |
| XTriage | Abl-no-guard | macro_f1 | 5 | 0.816 | 0.874 | 0.062 | 1.000 |
| XTriage | Abl-no-guard | fidelity | 5 | 0.056 | 0.056 |  |  |
| XTriage | Abl-no-guard | n_rules | 5 | 13.000 | 13.000 |  |  |
| XTriage | Abl-guard-review-tier | workload@90_frac | 5 | 0.205 | 0.464 | 0.125 | 0.062 |
| XTriage | Abl-guard-review-tier | ndcg | 5 | 0.955 | 0.949 | 0.062 | 0.031 |
| XTriage | Abl-guard-review-tier | recall@1000 | 5 | 0.039 | 0.024 | 0.062 | 0.031 |
| XTriage | Abl-guard-review-tier | macro_f1 | 5 | 0.816 | 0.737 | 0.062 | 0.031 |
| XTriage | Abl-guard-review-tier | fidelity | 5 | 0.056 | 0.056 |  |  |
| XTriage | Abl-guard-review-tier | n_rules | 5 | 13.000 | 13.000 |  |  |
| XTriage | B2-xgboost-shap | workload@90_frac | 5 | 0.205 | 0.877 | 0.062 | 0.031 |
| XTriage | B2-xgboost-shap | ndcg | 5 | 0.955 | 0.975 | 0.062 | 1.000 |
| XTriage | B2-xgboost-shap | recall@1000 | 5 | 0.039 | 0.000 | 0.062 | 0.031 |
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

| probe | variant | n | mean_abs_dq | mean_ds | evaded_detection | rule_changed | tier_changed | tier_changed_still_alerted | p1_downgraded | became_contested |
|---|---|---|---|---|---|---|---|---|---|---|
| evasion | padding=16 | 2000 | 0.001 | -0.077 | 0.022 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | padding=64 | 2000 | 0.003 | -0.019 | 0.034 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | padding=256 | 2000 | 0.005 | 0.318 | 0.000 | 0.001 | 0.001 | 0.001 | 0.000 | 0.004 |
| evasion | timing=0.5 | 2000 | 0.019 | -1.120 | 0.279 | 0.014 | 0.009 | 0.011 | 0.094 | 0.002 |
| evasion | timing=2.0 | 2000 | 0.007 | 0.671 | 0.000 | 0.006 | 0.004 | 0.004 | 0.125 | 0.003 |
| evasion | timing=5.0 | 2000 | 0.010 | 1.000 | 0.000 | 0.021 | 0.015 | 0.015 | 0.188 | 0.013 |
| evasion | port=80 | 2000 | 0.000 | -0.001 | 0.000 | 0.005 | 0.000 | 0.000 | 0.000 | 0.001 |
| evasion | port=443 | 2000 | 0.000 | 0.010 | 0.007 | 0.780 | 0.359 | 0.355 | 0.000 | 0.001 |

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

### Oracle noise (mean over probe seeds)

| eta | macro_f1 | macro_f1_rules | p1_f1 | coverage | n_rules | mean_rule_len | fidelity | workload@90_frac | ndcg | contested_rate | guard_catch_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.824 | 0.887 | 0.789 | 0.383 | 13.333 | 2.373 | 0.084 | 0.034 | 0.954 | 0.697 | 0.044 |
| 0.100 | 0.630 | 0.693 | 0.165 | 0.381 | 9.667 | 2.756 | 0.081 | 0.579 | 0.945 | 0.711 | 0.230 |
| 0.200 | 0.482 | 0.644 | 0.000 | 0.531 | 12.333 | 3.008 | 0.110 | 0.571 | 0.930 | 0.531 | 0.332 |
| 0.300 | 0.367 | 0.634 | 0.000 | 0.465 | 9.667 | 2.994 | 0.036 | 0.633 | 0.931 | 0.555 | 0.700 |

## Detector robustness

| detector | method | det_auroc | det_auprc | alerts | alerts_explained | workload@90_frac | ndcg | recall@1000 | macro_f1 | fidelity | n_rules | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| autoencoder | XTriage | 0.9038 ± 0.0098 | 0.8068 ± 0.0095 | 3000 ± 0 | 3000 ± 0 | 0.09322 ± 0.0048 | 0.9454 ± 0.02 | 0.9919 ± 0.0052 | 0.6248 ± 0.2 | 0.1258 ± 0.043 | 19.33 ± 3.5 | 83.01 ± 3.6 |
| autoencoder | B1-score-only | 0.9038 ± 0.0098 | 0.8068 ± 0.0095 | 3000 ± 0 | 3000 ± 0 | 0.7253 ± 0.037 | 0.8064 ± 0.009 | 0.09738 ± 0.018 |  |  |  | 83.01 ± 3.6 |
| xgboost | XTriage | 0.9999 ± 6.5e-06 | 0.9999 ± 8e-06 | 6.585e+04 ± 35 | 6.585e+04 ± 35 | 0.03954 ± 0.0025 | 0.9953 ± 0.00066 | 0.4576 ± 0.094 | 0.7832 ± 0.0056 | 0.3041 ± 0.13 | 13.33 ± 1.5 | 101.3 ± 1.7 |
| xgboost | B1-score-only | 0.9999 ± 6.5e-06 | 0.9999 ± 8e-06 | 6.585e+04 ± 35 | 6.585e+04 ± 35 | 0.8766 ± 0.00058 | 0.9753 ± 4.1e-05 | 0 ± 0 |  |  |  | 101.3 ± 1.7 |

## RQ5 accountability

* records: 4462, chain verified: True, tamper detected: True (first bad seq 1011)
* replay success: 1.000 over 500 records {'score': 1.0, 'percentile': 1.0, 'attribution': 1.0, 'rule': 1.0, 'tier': 1.0, 'ok': 1.0}
* bytes per record: 1807; contested rate: 0.631
* testbed: 4 sensors, 60000 flows, 4462 alerts, 1469 flows/s; t1 1.655 ms/flow, t2 2.390 ms/alert, t3 0.365 ms/record, publish-to-ledger latency incl. queueing under max-rate replay p50 6995 ms / p95 22123 ms
