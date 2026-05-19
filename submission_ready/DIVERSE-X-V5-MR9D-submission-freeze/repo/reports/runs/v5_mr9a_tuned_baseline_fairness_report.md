# DIVERSE-X V5-MR9A Tuned Baseline Fairness Matrix

Status: `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`
Date: 2026-05-19

## Boundary

MR9A is a **post-MR8C supplemental baseline fairness analysis**. It closes the
`PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS` reviewer gap. It does
not retune DIVERSE-X, does not alter the MR8C final task panel, and does not
change the MR8C final gate.

It does not change the MR8C final gate.

MR8C gate preserved locally: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`; MR9A writes only supplemental baseline files.

## Gate

- Valid tasks: `13` of `13`
- RF trial count per valid task: `20`
- HGB trial count per valid task: `20`
- Minimum required trial budget per family: `20`
- Final labels used for hyperparameter selection:
  `False`
- DIVERSE-X retuned: `False`
- MR8C gate changed: `False`

## Task Status

| task_name                      | loader   | priority   | status   |   train_rows |   valid_rows |   test_rows |
|:-------------------------------|:---------|:-----------|:---------|-------------:|-------------:|------------:|
| hERG                           | Tox      | core       | PASS     |          458 |           65 |         132 |
| AMES                           | Tox      | core       | PASS     |         5094 |          727 |        1457 |
| DILI                           | Tox      | core       | PASS     |          332 |           47 |          96 |
| hERG_Karim                     | Tox      | core       | PASS     |         9411 |         1344 |        2690 |
| ClinTox                        | Tox      | core       | PASS     |         1034 |          147 |         297 |
| Skin Reaction                  | Tox      | reserve    | PASS     |          282 |           40 |          82 |
| Carcinogens_Lagunin            | Tox      | reserve    | PASS     |          196 |           28 |          56 |
| CYP2C19_Veith                  | ADME     | core       | PASS     |         8865 |         1266 |        2534 |
| CYP1A2_Veith                   | ADME     | core       | PASS     |         8805 |         1257 |        2517 |
| Bioavailability_Ma             | ADME     | reserve    | PASS     |          448 |           64 |         128 |
| CYP2C9_Substrate_CarbonMangels | ADME     | reserve    | PASS     |          468 |           66 |         135 |
| CYP2D6_Substrate_CarbonMangels | ADME     | reserve    | PASS     |          466 |           66 |         135 |
| CYP3A4_Substrate_CarbonMangels | ADME     | reserve    | PASS     |          468 |           67 |         135 |

## Method Summary

The primary comparator for this supplemental table is
`tuned_rf_scaffold_quota` at `K50`.

| method                                 |   task_count |   mean_positive_recall_at_k |   mean_positive_fraction_at_k |   mean_enrichment_at_k |   mean_average_precision |   mean_auroc |   mean_delta_vs_tuned_rf_scaffold_quota |   task_nonworse_rate_vs_tuned_rf_scaffold_quota |   severe_task_losses_below_minus_0_05 |   mean_auprc_delta_vs_tuned_rf_scaffold_quota |
|:---------------------------------------|-------------:|----------------------------:|------------------------------:|-----------------------:|-------------------------:|-------------:|----------------------------------------:|------------------------------------------------:|--------------------------------------:|----------------------------------------------:|
| tuned_hgb_activity_only                |           13 |                    0.462059 |                      0.723077 |                1.75978 |                 0.745185 |     0.794999 |                              0.0420966  |                                        0.923077 |                                     0 |                                  -0.0155221   |
| tuned_rf_activity_only                 |           13 |                    0.453266 |                      0.721538 |                1.73305 |                 0.760707 |     0.804991 |                              0.0333031  |                                        1        |                                     0 |                                   0           |
| tuned_hgb_ad_distance_guard            |           13 |                    0.430269 |                      0.689231 |                1.66826 |                 0.746218 |     0.795538 |                              0.010306   |                                        0.769231 |                                     0 |                                  -0.0144893   |
| tuned_hgb_scaffold_quota               |           13 |                    0.429799 |                      0.692308 |                1.6746  |                 0.745185 |     0.794999 |                              0.00983621 |                                        0.846154 |                                     0 |                                  -0.0155221   |
| tuned_hgb_uncertainty_only_guard       |           13 |                    0.429799 |                      0.692308 |                1.6746  |                 0.745185 |     0.794999 |                              0.00983621 |                                        0.846154 |                                     0 |                                  -0.0155221   |
| tuned_rf_ad_distance_guard             |           13 |                    0.427457 |                      0.686154 |                1.65515 |                 0.757039 |     0.802299 |                              0.0074944  |                                        0.769231 |                                     0 |                                  -0.00366793  |
| tuned_rf_ucb_uncertainty_proxy         |           13 |                    0.421935 |                      0.683077 |                1.63203 |                 0.760617 |     0.804221 |                              0.00197239 |                                        1        |                                     0 |                                  -9.01455e-05 |
| tuned_rf_scaffold_quota                |           13 |                    0.419963 |                      0.681538 |                1.62671 |                 0.760707 |     0.804991 |                              0          |                                        1        |                                     0 |                                   0           |
| tuned_rf_uncertainty_only_guard        |           13 |                    0.405054 |                      0.673846 |                1.52746 |                 0.751141 |     0.789772 |                             -0.0149088  |                                        0.923077 |                                     1 |                                  -0.00956603  |
| tuned_hgb_conformal_rejection_baseline |           13 |                    0.403357 |                      0.675385 |                1.51753 |                 0.729192 |     0.762697 |                             -0.0166061  |                                        0.769231 |                                     1 |                                  -0.0315149   |
| tuned_rf_conformal_rejection_baseline  |           13 |                    0.398328 |                      0.667692 |                1.4982  |                 0.744489 |     0.771999 |                             -0.0216346  |                                        0.923077 |                                     1 |                                  -0.0162184   |
| random_fixed_seed                      |           13 |                    0.336834 |                      0.456923 |                1.01989 |                 0.489749 |     0.52835  |                             -0.0831284  |                                        0.153846 |                                     5 |                                  -0.270958    |

## Selected Train/Valid Configurations

| task_name                      | family                    | config_id   |   valid_average_precision | final_labels_used_for_selection   |
|:-------------------------------|:--------------------------|:------------|--------------------------:|:----------------------------------|
| hERG                           | tuned_rf_ecfp_descriptor  | rf_grid_15  |                  0.818568 | False                             |
| hERG                           | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.85998  | False                             |
| AMES                           | tuned_rf_ecfp_descriptor  | rf_grid_18  |                  0.899124 | False                             |
| AMES                           | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.894814 | False                             |
| DILI                           | tuned_rf_ecfp_descriptor  | rf_grid_13  |                  0.943625 | False                             |
| DILI                           | tuned_hgb_ecfp_descriptor | hgb_grid_10 |                  0.939082 | False                             |
| hERG_Karim                     | tuned_rf_ecfp_descriptor  | rf_grid_18  |                  0.843416 | False                             |
| hERG_Karim                     | tuned_hgb_ecfp_descriptor | hgb_grid_15 |                  0.862556 | False                             |
| ClinTox                        | tuned_rf_ecfp_descriptor  | rf_grid_16  |                  0.315212 | False                             |
| ClinTox                        | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.525178 | False                             |
| Skin Reaction                  | tuned_rf_ecfp_descriptor  | rf_grid_15  |                  0.873247 | False                             |
| Skin Reaction                  | tuned_hgb_ecfp_descriptor | hgb_grid_16 |                  0.813486 | False                             |
| Carcinogens_Lagunin            | tuned_rf_ecfp_descriptor  | rf_grid_13  |                  0.714286 | False                             |
| Carcinogens_Lagunin            | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.719298 | False                             |
| CYP2C19_Veith                  | tuned_rf_ecfp_descriptor  | rf_grid_10  |                  0.835209 | False                             |
| CYP2C19_Veith                  | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.828347 | False                             |
| CYP1A2_Veith                   | tuned_rf_ecfp_descriptor  | rf_grid_18  |                  0.909531 | False                             |
| CYP1A2_Veith                   | tuned_hgb_ecfp_descriptor | hgb_grid_08 |                  0.916421 | False                             |
| Bioavailability_Ma             | tuned_rf_ecfp_descriptor  | rf_grid_10  |                  0.886752 | False                             |
| Bioavailability_Ma             | tuned_hgb_ecfp_descriptor | hgb_grid_20 |                  0.901711 | False                             |
| CYP2C9_Substrate_CarbonMangels | tuned_rf_ecfp_descriptor  | rf_grid_02  |                  0.668333 | False                             |
| CYP2C9_Substrate_CarbonMangels | tuned_hgb_ecfp_descriptor | hgb_grid_09 |                  0.651889 | False                             |
| CYP2D6_Substrate_CarbonMangels | tuned_rf_ecfp_descriptor  | rf_grid_11  |                  0.6522   | False                             |
| CYP2D6_Substrate_CarbonMangels | tuned_hgb_ecfp_descriptor | hgb_grid_15 |                  0.56467  | False                             |
| CYP3A4_Substrate_CarbonMangels | tuned_rf_ecfp_descriptor  | rf_grid_06  |                  0.680997 | False                             |
| CYP3A4_Substrate_CarbonMangels | tuned_hgb_ecfp_descriptor | hgb_grid_13 |                  0.687887 | False                             |

## Fixed MR8C Reference Comparison

This reference table compares the already-locked MR8C DIVERSE-X selections to
post-MR8C tuned scaffold baselines. It is interpretive only and cannot move the
MR8C gate.

| method                   |   task_count |   mean_mr8c_fixed_delta_vs_tuned_baseline |   mean_mr8c_fixed_auprc_delta_vs_tuned_baseline |   nonworse_rate |
|:-------------------------|-------------:|------------------------------------------:|------------------------------------------------:|----------------:|
| tuned_hgb_scaffold_quota |           13 |                               -0.00863449 |                                     -0.00244841 |        0.615385 |
| tuned_rf_scaffold_quota  |           13 |                                0.00120172 |                                     -0.0179705  |        0.615385 |

## Interpretation

MR9A supplies tuned RF and HGB baseline fairness evidence for reviewers. The
primary paper claim remains audit-card rejection reliability under chemical-space
shift, supported by MR8C. Acquisition-vs-baseline comparisons remain secondary
and must be reported with the post-MR8C supplemental label.
