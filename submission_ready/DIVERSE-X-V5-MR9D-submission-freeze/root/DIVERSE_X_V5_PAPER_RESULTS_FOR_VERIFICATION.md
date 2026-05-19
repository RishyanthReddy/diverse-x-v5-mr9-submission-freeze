# DIVERSE-X V5 Paper Results for Verification

Status: `RESULTS_ONLY`
Date: 2026-05-19

This file contains result values and artifact pointers only. It does not include
discussion, interpretation beyond recorded claim status, or next-step
recommendations.

## 1. Final Result Summary

| Result item | Value |
| --- | --- |
| Final external gate | `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT` |
| Final external gate reason | `audit_primary_and_secondary_collapse_gates_passed` |
| Final valid tasks | `13 / 13` |
| Locked final method | `mr8c_audit_card_acquisition` |
| Primary risk method | `audit_card` |
| Primary audit rejection AUC delta | `0.015094140002645945` |
| Best rejection fraction | `0.4` |
| Best rejection reliability delta | `0.07168512835444937` |
| Task nonnegative rejection rate at best fraction | `0.9230769230769231` |
| Mean guarded acquisition delta vs scaffold quota | `0.003043366700090366` |
| Mean AUPRC delta vs scaffold quota | `-0.0042903086102640264` |
| Severe acquisition losses below `-0.05` | `0` |
| MR7 status preserved | `MR7_LOCKED_FINAL_EXTERNAL_NO_GO` |
| MR7 no-go disclosed | `True` |
| Final labels used for ranking | `False` |
| Post-hoc retuning | `False` |
| MR8C Modal run | `https://modal.com/apps/rishyanth602/main/ap-U8gfrMIkEA1PckflHYNflB` |

Source artifact:

`repo/reports/tables/v5_mr8c_final_external_gate.csv`

## 1A. Post-MR8C Supplemental Baseline Closure

| Item | Result |
| --- | --- |
| Supplemental tuned baseline gate | `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED` |
| Modal run | `https://modal.com/apps/rishyanth602/main/ap-ycaHDelZKCybTfF3z7T1FL` |
| Frozen MR8C tasks valid | `13 / 13` |
| RF tuning budget | `20` train/valid-selected configs per valid task |
| HGB/XGB-style tuning budget | `20` train/valid-selected configs per valid task |
| Final labels used for hyperparameter selection | `False` |
| DIVERSE-X retuned | `False` |
| MR8C gate changed | `False` |
| Boundary | post-MR8C supplemental fairness analysis only |

This closes the earlier MR5B verification-line gap
`PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS` for manuscript
submission readiness. It does not alter the historical MR5B development status
or the MR8C final external gate.

## 1B. Supplementary Configuration Appendix Closure

| Item | Result |
| --- | --- |
| Configuration appendix gate | `MR9C_CONFIG_APPENDIX_COMPLETE` |
| Method configuration rows | `22` |
| Selected baseline config rows | `26` |
| Tuning grid families | `2` |
| Reproducibility locks | `8` |
| Failed locks | `0` |
| New outcome evaluations run | `False` |
| DIVERSE-X retuned | `False` |
| MR8C/MR9A gates changed | `False` |

Source artifacts:

- `repo/reports/runs/v5_mr9c_config_appendix.md`
- `repo/reports/tables/v5_mr9c_method_config_appendix.csv`
- `repo/reports/tables/v5_mr9c_selected_baseline_configs.csv`
- `repo/reports/tables/v5_mr9c_tuning_grid_summary.csv`
- `repo/reports/tables/v5_mr9c_reproducibility_locks.csv`
- `repo/data/manifests/v5_mr9c_config_appendix_manifest.json`

## 1C. Illustrative Molecule Example Closure

| Item | Result |
| --- | --- |
| Figure example gate | `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED` |
| Modal run | `https://modal.com/apps/rishyanth602/main/ap-Jg6N4cQ8dGAE4LeH3d3sLi` |
| Valid replay tasks | `13 / 13` |
| Hero examples | `3` |
| Villain examples | `3` |
| Candidate audit pool rows | `2537` |
| SVG structures | `6` |
| New claim gate | `False` |
| DIVERSE-X retuned | `False` |
| MR8C gate changed | `False` |

Example rows:

| Example | Role | Task | Final label | Probability | Audit risk | Nearest train Tanimoto |
| --- | --- | --- | --- | --- | --- | --- |
| `hero_01` | hero | `CYP1A2_Veith` | `1` | `0.998774327633569` | `0.0345722184761716` | `0.925` |
| `hero_02` | hero | `AMES` | `1` | `0.9736119189345062` | `0.04958547423475079` | `0.9285714285714286` |
| `hero_03` | hero | `hERG_Karim` | `1` | `0.9936378302779957` | `0.06556816124087826` | `0.8636363636363636` |
| `villain_01` | villain | `ClinTox` | `0` | `0.18499004638086405` | `0.7061983207384392` | `0.256` |
| `villain_02` | villain | `CYP2C9_Substrate_CarbonMangels` | `0` | `0.3953749228265174` | `0.800235426579283` | `0.23076923076923078` |
| `villain_03` | villain | `CYP2D6_Substrate_CarbonMangels` | `0` | `0.5100128960095807` | `0.8178898995303376` | `0.35555555555555557` |

Source artifacts:

- `repo/reports/tables/v5_mr9b_figure_molecule_examples.csv`
- `repo/reports/tables/v5_mr9b_candidate_audit_pool.csv`
- `repo/reports/runs/v5_mr9b_figure_molecule_examples.md`
- `repo/reports/figures/mr9b_molecule_examples`

## 2. Claim Boundary Results

| Claim | Status | Evidence | Notes |
| --- | --- | --- | --- |
| `mr7_locked_final_external_success` | `BLOCKED` | `MR7_LOCKED_FINAL_EXTERNAL_NO_GO` | MR7 remains consumed no-go evidence. |
| `mr8c_audit_primary_external_support` | `SUPPORTED` | `audit_auc_delta=0.015094` | Primary MR8C endpoint. |
| `mr8c_q1_supporting_external_evidence` | `SUPPORTED` | `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT` | Requires audit primary pass and no severe secondary acquisition collapse. |
| `acquisition_dominates_scaffold_quota` | `SUPPORTED` | `mean_delta=0.003043` | Secondary endpoint only. |
| `post_hoc_retuning` | `BLOCKED` | `post_hoc_retuning_false` | No post-hoc retuning allowed or recorded. |

Source artifact:

`repo/reports/tables/v5_mr8c_claim_boundary.csv`

## 3. MR8C Final External Task Status

| Task | Loader | Priority | Status | Train rows | Valid rows | Test rows | Test positive rate | Median nearest-train Tanimoto | P10 nearest-train Tanimoto | Mean audit risk |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `hERG` | `Tox` | `core` | `PASS` | 458 | 65 | 132 | 0.6287878787878788 | 0.35714285714285715 | 0.2502747252747253 | 0.5253663672613766 |
| `AMES` | `Tox` | `core` | `PASS` | 5094 | 727 | 1457 | 0.574468085106383 | 0.5151515151515151 | 0.32432432432432434 | 0.47327187537229554 |
| `DILI` | `Tox` | `core` | `PASS` | 332 | 47 | 96 | 0.65625 | 0.3333333333333333 | 0.24195121951219511 | 0.5900950795446084 |
| `hERG_Karim` | `Tox` | `core` | `PASS` | 9411 | 1344 | 2690 | 0.4862453531598513 | 0.7058823529411765 | 0.3923802432365351 | 0.40559207938312786 |
| `ClinTox` | `Tox` | `core` | `PASS` | 1034 | 147 | 297 | 0.10774410774410774 | 0.4339622641509434 | 0.2630952380952381 | 0.4026355812658746 |
| `Skin Reaction` | `Tox` | `reserve` | `PASS` | 282 | 40 | 82 | 0.6097560975609756 | 0.29246411483253587 | 0.21439560439560437 | 0.5785971997910984 |
| `Carcinogens_Lagunin` | `Tox` | `reserve` | `PASS` | 196 | 28 | 56 | 0.16071428571428573 | 0.32576530612244897 | 0.2269989963198394 | 0.49624360511714727 |
| `CYP2C19_Veith` | `ADME` | `core` | `PASS` | 8865 | 1266 | 2534 | 0.425414364640884 | 0.4888888888888889 | 0.3333333333333333 | 0.4633770632292628 |
| `CYP1A2_Veith` | `ADME` | `core` | `PASS` | 8805 | 1257 | 2517 | 0.45292014302741357 | 0.5 | 0.3333333333333333 | 0.439784224247484 |
| `Bioavailability_Ma` | `ADME` | `reserve` | `PASS` | 448 | 64 | 128 | 0.796875 | 0.4100462379150904 | 0.24358885017421603 | 0.49504078015364217 |
| `CYP2C9_Substrate_CarbonMangels` | `ADME` | `reserve` | `PASS` | 468 | 66 | 135 | 0.16296296296296298 | 0.38235294117647056 | 0.25604863221884494 | 0.488715292381168 |
| `CYP2D6_Substrate_CarbonMangels` | `ADME` | `reserve` | `PASS` | 466 | 66 | 135 | 0.28888888888888886 | 0.40384615384615385 | 0.2703974562798092 | 0.5019424917447844 |
| `CYP3A4_Substrate_CarbonMangels` | `ADME` | `reserve` | `PASS` | 468 | 67 | 135 | 0.5555555555555556 | 0.38571428571428573 | 0.2857142857142857 | 0.5474136954799272 |

Source artifact:

`repo/reports/tables/v5_mr8c_final_external_task_status.csv`

## 4. Primary Audit-Card Rejection Results

| Rejection fraction | Mean reliability delta | Task nonnegative rate | Min reliability delta | Max reliability delta | Mean kept positive fraction | Mean baseline positive fraction | Mean kept risk | Mean baseline risk |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 0.000000000000000016 | 1.0000000000000000 | -0.000000000000000111 | 0.000000000000000111 | 0.6876923076923076 | 0.6876923076923076 | 0.39898938568321995 | 0.39898938568321995 |
| 0.1 | 0.028931234129009623 | 0.9230769230769231 | -0.002773980596978032 | 0.09536293456293116 | 0.6991452991452991 | 0.6876923076923076 | 0.38151114300720185 | 0.39898938568321995 |
| 0.2 | 0.040602645718259694 | 0.9230769230769231 | -0.029872859650397154 | 0.10026650036891394 | 0.6980769230769230 | 0.6876923076923076 | 0.36877135534957567 | 0.39898938568321995 |
| 0.3 | 0.04556495600196545 | 0.8461538461538461 | -0.058175222005710264 | 0.1061834234512189 | 0.6901098901098901 | 0.6876923076923076 | 0.3558420120988369 | 0.39898938568321995 |
| 0.4 | 0.07168512835444937 | 0.9230769230769231 | -0.03528583847326128 | 0.13897473370689972 | 0.7025641025641025 | 0.6876923076923076 | 0.3421760522005655 | 0.39898938568321995 |
| AUC 0.0 to 0.4 | 0.015094140002645945 | 0.9230769230769231 | -0.03528583847326128 | 0.13897473370689972 | 0.7025641025641025 | 0.6876923076923076 | 0.3421760522005655 | 0.39898938568321995 |

Source artifacts:

- `repo/reports/tables/v5_mr8c_final_external_rejection_summary.csv`
- `repo/reports/tables/v5_mr8c_final_external_rejection_curve.csv`

## 5. Rejection-Risk Comparator Results

| Risk method | AUC 0.0 to 0.4 | Best rejection fraction | Task nonnegative rate at best fraction | Min reliability delta at best fraction | Max reliability delta at best fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ad_distance` | 0.016949107086538975 | 0.4 | 1.0 | 0.039692471060434886 | 0.1555332686583179 |
| `audit_card` | 0.015094140002645945 | 0.4 | 0.9230769230769231 | -0.03528583847326128 | 0.13897473370689972 |
| `conformal_only` | 0.01870280095471176 | 0.4 | 0.9230769230769231 | -0.049485266371089104 | 0.28422555766662416 |
| `uncertainty_only` | 0.020912722205858176 | 0.4 | 0.9230769230769231 | -0.026487768139697748 | 0.29150890773212257 |

Source artifact:

`repo/reports/tables/v5_mr8c_final_external_rejection_summary.csv`

## 6. MR8C Secondary Acquisition Results by Task

Values are for `mr8c_audit_card_acquisition` at K50 versus `scaffold_quota`.

| Task | Positive selected | Delta vs scaffold quota | AUPRC delta vs scaffold quota |
| --- | ---: | ---: | ---: |
| `AMES` | 48 | -0.001194743130227001 | -0.0008776988638077299 |
| `Bioavailability_Ma` | 43 | 0.0 | 0.02225752434007955 |
| `CYP1A2_Veith` | 50 | 0.0 | -0.0021930953787583363 |
| `CYP2C19_Veith` | 49 | 0.0 | -0.0043151707092978775 |
| `CYP2C9_Substrate_CarbonMangels` | 12 | 0.0 | -0.02470447199459952 |
| `CYP2D6_Substrate_CarbonMangels` | 21 | 0.0 | -0.01521290118355012 |
| `CYP3A4_Substrate_CarbonMangels` | 34 | -0.026666666666666672 | -0.005157267722206593 |
| `Carcinogens_Lagunin` | 9 | 0.0 | 0.006615969946140665 |
| `ClinTox` | 17 | 0.03125 | -0.02982765024745887 |
| `DILI` | 40 | -0.015873015873015928 | -0.009989947941007715 |
| `Skin Reaction` | 33 | 0.040000000000000036 | 0.008886345350434532 |
| `hERG` | 42 | 0.01204819277108432 | 0.0016129817428645055 |
| `hERG_Karim` | 49 | 0.0 | -0.0028686292722648332 |

Aggregate values from final gate:

| Aggregate metric | Value |
| --- | ---: |
| Mean guarded acquisition delta vs scaffold quota | 0.003043366700090366 |
| Mean AUPRC delta vs scaffold quota | -0.0042903086102640264 |
| Severe acquisition losses below `-0.05` | 0 |

Source artifact:

`repo/reports/tables/v5_mr8c_final_external_summary.csv`

## 7. MR8C Integrity and Validation Results

| Check | Result |
| --- | --- |
| MR8C final labels accessed | `True` |
| Final labels used for metrics | `True` |
| Final labels used for ranking | `False` |
| MR7 rerun | `False` |
| MR7 no-go disclosed | `True` |
| MR8B protocol used | `True` |
| Post-hoc retuning | `False` |
| Post-hoc task exclusion | `False` |
| Task inclusion changed after outcomes | `False` |
| Modal GPU spend | `False` |
| `py_compile` | `PASSED` |
| `ruff` | `PASSED` |
| MR8C validator | `PASSED` |
| MR8C rerun status | `BLOCKED` |

Source artifacts:

- `repo/data/manifests/v5_mr8c_final_external_manifest.json`
- `repo/reports/runs/v5_mr8c_completion_audit.md`
- `scripts/validate_diversex_v5_mr8c.ps1`

## 8. MR8B Loader Smoke Results

| Result item | Value |
| --- | --- |
| Gate | `MR8B_PROTOCOL_FROZEN_READY_FOR_MR8C` |
| Gate reason | `loader_smoke_passed_minimum_external_task_gate` |
| Attempted tasks | 13 |
| Eligible tasks | 13 |
| Core eligible tasks | 7 |
| Repair tasks all eligible | `True` |
| Outcome metrics run | `False` |
| Model fit | `False` |
| Ranking run | `False` |
| MR8C final external allowed next | `True` |
| MR8B Modal run | `https://modal.com/apps/rishyanth602/main/ap-QIcXtxwK2vrSaVtItWnOVd` |

Source artifacts:

- `repo/reports/tables/v5_mr8b_loader_smoke_gate.csv`
- `repo/reports/tables/v5_mr8b_loader_smoke.csv`
- `repo/reports/runs/v5_mr8b_loader_smoke_report.md`
- `repo/reports/runs/v5_mr8b_completion_audit.md`

## 9. MR8 Post-MR7 Failure Analysis Results

| Result item | Value |
| --- | --- |
| Recommendation | `MR8_RECOVERY_PROTOCOL_CONDITIONAL_GO_AUDIT_PRIMARY` |
| MR7 status | `MR7_LOCKED_FINAL_EXTERNAL_NO_GO` |
| MR7 valid task count | 3 |
| MR7 attempted task count | 6 |
| MR7 quarantined pre-metric count | 3 |
| Loader mismatch repairable | `True` |
| CYP losses tiny but systematic | `True` |
| MR7 mean K50 recall delta vs scaffold quota | -0.0013554685413021 |
| MR7 mean AUPRC delta vs scaffold quota | -0.0108665608106388 |
| MR7 task non-worse rate | 0.0 |
| MR7 best rejection fraction | 0.4 |
| MR7 best rejection reliability delta | 0.06690171651512233 |
| Primary MR8 endpoint | `audit_card_rejection_reliability_or_aurc` |
| Secondary MR8 endpoint | `guarded_acquisition_delta_vs_scaffold_quota` |
| MR7 rerun allowed | `False` |
| MR8 final label access allowed at MR8 stage | `False` |

Loader diagnosis:

| Task | MR7 runner loader | MR7 status | Correct loader | MR8 action |
| --- | --- | --- | --- | --- |
| `CYP2C9_Veith` | `ADME` | `PASS` | `ADME` | `preserve_as_consumed_mr7_evidence` |
| `CYP2D6_Veith` | `ADME` | `PASS` | `ADME` | `preserve_as_consumed_mr7_evidence` |
| `CYP3A4_Veith` | `ADME` | `PASS` | `ADME` | `preserve_as_consumed_mr7_evidence` |
| `hERG` | `ADME` | `QUARANTINED_PRE_METRIC` | `Tox` | `repair_loader_in_new_mr8_protocol_not_mr7_rerun` |
| `AMES` | `ADME` | `QUARANTINED_PRE_METRIC` | `Tox` | `repair_loader_in_new_mr8_protocol_not_mr7_rerun` |
| `DILI` | `ADME` | `QUARANTINED_PRE_METRIC` | `Tox` | `repair_loader_in_new_mr8_protocol_not_mr7_rerun` |

Source artifacts:

- `repo/reports/tables/v5_mr8_recovery_gate.csv`
- `repo/reports/tables/v5_mr8_loader_diagnosis.csv`
- `repo/reports/runs/v5_mr8_post_mr7_failure_analysis.md`

## 10. MR7 Locked Final Results

| Result item | Value |
| --- | --- |
| MR7 gate | `MR7_LOCKED_FINAL_EXTERNAL_NO_GO` |
| Gate reason | `locked_final_required_gates_failed` |
| Valid task count | 3 |
| Attempted task count | 6 |
| Locked method | `mr5c_locked_final_switch_acquisition` |
| Mean K50 recall delta vs scaffold quota | -0.0013554685413021013 |
| Task non-worse rate | 0.0 |
| Severe primary losses below `-0.05` | 0 |
| Mean AUPRC delta vs scaffold quota | -0.010866560810638822 |
| Audit rejection positive | `True` |
| Best rejection reliability delta | 0.06690171651512236 |
| Locked final external labels accessed | `True` |
| Final labels used for ranking | `False` |
| Final labels used for metrics | `True` |
| MR7 Modal run | `https://modal.com/apps/rishyanth602/main/ap-OgR5WgdsoIOFxnSjjPYEwN` |

MR7 task status:

| Task | Status | Reason | Train rows | Test rows | Test positive rate | Switch rule |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `CYP2C9_Veith` | `PASS` | `PASS_RF_240_FIXED` | 9673 | 2419 | 0.34642414220752377 | `abstention_promoted` |
| `CYP2D6_Veith` | `PASS` | `PASS_RF_240_FIXED` | 10504 | 2626 | 0.19497334348819498 | `abstention_promoted` |
| `CYP3A4_Veith` | `PASS` | `PASS_RF_240_FIXED` | 9861 | 2467 | 0.44061613295500607 | `abstention_promoted` |
| `hERG` | `QUARANTINED_PRE_METRIC` | `ValueError: ('herg', 'does not match to available values. Please double check.')` | 0 | 0 | 0.0 | `not_run` |
| `AMES` | `QUARANTINED_PRE_METRIC` | `ValueError: ('ames', 'does not match to available values. Please double check.')` | 0 | 0 | 0.0 | `not_run` |
| `DILI` | `QUARANTINED_PRE_METRIC` | `ValueError: ('dili', 'does not match to available values. Please double check.')` | 0 | 0 | 0.0 | `not_run` |

Source artifacts:

- `repo/reports/tables/v5_mr7_locked_final_gate.csv`
- `repo/reports/tables/v5_mr7_locked_final_task_status.csv`
- `repo/reports/runs/v5_mr7_locked_final_external_report.md`
- `repo/reports/runs/v5_mr7_completion_audit.md`

## 11. MR6 Locked Final Protocol Results

| Result item | Value |
| --- | --- |
| MR6 gate | `MR6_LOCKED_FINAL_PROTOCOL_READY_STOP_BEFORE_LABELS` |
| Gate reason | `mr5c_go_method_and_final_benchmark_metadata_locked` |
| Upstream status | `MR5C_GO_LOCKED_FINAL_PROTOCOL_DESIGN_NEXT` |
| Locked method | `mr5c_locked_final_switch_acquisition` |
| Final task count | 6 |
| Excluded development task count | 3 |
| MR7 runner | `modal/v5_mr7_locked_final_external_run.py` |
| Locked final external labels accessed | `False` |
| Final benchmark data fetched | `False` |
| MR2 final retuning | `False` |
| MR3 final entry retuning | `False` |
| Post-hoc task exclusion | `False` |
| Ready for MR7 one-shot | `True` |

MR6 frozen final tasks:

| Task | Family | Category | Official metric | Split | MR7 role | Label access |
| --- | --- | --- | --- | --- | --- | --- |
| `CYP2C9_Veith` | `TDC_ADMET` | metabolism | AUPRC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |
| `CYP2D6_Veith` | `TDC_ADMET` | metabolism | AUPRC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |
| `CYP3A4_Veith` | `TDC_ADMET` | metabolism | AUPRC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |
| `hERG` | `TDC_ADMET` | toxicity | AUROC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |
| `AMES` | `TDC_ADMET` | toxicity | AUROC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |
| `DILI` | `TDC_ADMET` | toxicity | AUROC | scaffold | locked final | `NO_ACCESS_UNTIL_MR7` |

Source artifacts:

- `repo/reports/tables/v5_mr6_protocol_gate.csv`
- `repo/reports/tables/v5_mr6_locked_final_benchmark_registry.csv`
- `repo/reports/runs/v5_mr6_locked_final_protocol.md`

## 12. MR5C Development Results

| Result item | Value |
| --- | --- |
| Combined gate | `MR5C_GO_LOCKED_FINAL_PROTOCOL_DESIGN_NEXT` |
| Gate reason | `switch_internal_pass_litpcba_overlay_pass_tdc_admet_pass` |
| Recommended method | `mr5c_hard_shift_switch_acquisition` |
| Switch primary delta vs scaffold quota | 0.0223756778347697 |
| Switch hard delta vs scaffold quota | 0.0085389407674031 |
| Switch hard target wins | 47 |
| Switch hard target losses | 28 |
| Switch hard non-worse rate | 0.6266666666666667 |
| LIT-PCBA overlay mean delta | 0.034621795907108815 |
| LIT-PCBA overlay non-worse rate | 0.8 |
| LIT-PCBA audit rejection positive | `True` |
| TDC ADMET gate status | `MR5C_TDC_ADMET_EXTDEV_GO` |
| TDC ADMET mean delta vs scaffold quota | 0.0023130520865062 |
| TDC ADMET audit rejection positive | `True` |
| Locked final external labels accessed | `False` |
| MR2 final retuning | `False` |
| MR3 final entry retuning | `False` |
| Post-hoc target exclusion | `False` |

TDC ADMET external-development result:

| Result item | Value |
| --- | --- |
| Gate | `MR5C_TDC_ADMET_EXTDEV_GO` |
| Benchmark family | `TDC_ADMET` |
| Benchmark role | `external_development_only` |
| Method | `mr5c_tdc_abstention_promoted_acquisition` |
| Dataset count | 3 |
| Mean delta vs scaffold quota | 0.0023130520865062565 |
| Non-worse rate | 0.6666666666666666 |
| Wins | 2 |
| Ties | 0 |
| Losses | 1 |
| Audit rejection positive | `True` |
| Best rejection fraction | 0.4 |
| Best rejection reliability delta | 0.11764013165601339 |
| Locked final external labels accessed | `False` |
| TDC test labels used for ranking | `False` |
| TDC test labels used for metrics | `True` |

Source artifacts:

- `repo/reports/tables/v5_mr5c_combined_gate.csv`
- `repo/reports/tables/v5_mr5c_tdc_admet_gate.csv`
- `repo/reports/runs/v5_mr5c_combined_decision.md`
- `repo/reports/runs/v5_mr5c_tdc_admet_extdev.md`

## 13. MR5B Development Results

MR5B hard-shift/internal result:

| Result item | Value |
| --- | --- |
| Gate | `MR5B_GO_MODAL_TUNED_BASELINE_REQUIRED` |
| Gate reason | `hard_shift_lead_fixed_full_tuned_baseline_matrix_pending` |
| Lead method | `mr5_applicability_domain_guarded_diversex` |
| Audit overlay method | `mr5_abstaining_frontier_policy` |
| Hard delta vs scaffold quota | 0.0085389407674031 |
| Hard delta vs DIVERSE-X default | 0.0008851738590547 |
| Primary delta vs scaffold quota | 0.0204940311556519 |
| Hard bootstrap mean delta | 0.008538940767402962 |
| Hard bootstrap CI95 low | 0.0035672696775688882 |
| Hard bootstrap CI95 high | 0.013949742220814307 |
| Hard target wins | 47 |
| Hard target losses | 28 |
| Audit overlay positive | `True` |
| Hard K sensitivity positive | `True` |
| Full tuned baseline matrix status | `PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS` |
| Locked final external labels accessed | `False` |
| MR2 final retuning | `False` |
| MR3 final entry retuning | `False` |
| Modal GPU spend | `False` |

MR5B LIT-PCBA external-development result:

| Result item | Value |
| --- | --- |
| Gate | `MR5B_EXTDEV_CONDITIONAL_GO_SECOND_DEV_BENCHMARK_REQUIRED` |
| Gate reason | `near_neutral_external_dev_signal_requires_second_dev_benchmark` |
| Benchmark ID | `lit_pcba` |
| Benchmark role | `external_development_only` |
| Lead method | `mr5b_external_ad_guarded_diversex` |
| Evaluated targets | 15 |
| Lead mean ASR@100 delta vs scaffold quota | -0.004813959437672159 |
| Lead median ASR@100 delta vs scaffold quota | 0.0 |
| Lead target wins | 1 |
| Lead target ties | 11 |
| Lead target losses | 3 |
| Lead target non-worse rate | 0.8 |
| Overlay mean ASR@100 delta vs scaffold quota | 0.03462179590710882 |
| Audit rejection positive | `True` |
| Best rejection fraction | 0.4 |
| Best rejection reliability delta | 0.08618303330712586 |
| Locked final external labels accessed | `False` |
| External development labels used for metrics | `True` |
| Validation labels used for ranking | `False` |
| MR2 final retuning | `False` |
| MR3 final entry retuning | `False` |
| Post-hoc target exclusion | `False` |
| Modal GPU spend | `False` |

Source artifacts:

- `repo/reports/tables/v5_mr5b_gate.csv`
- `repo/reports/tables/v5_mr5b_extdev_gate.csv`
- `repo/reports/runs/v5_mr5b_hard_shift_report.md`
- `repo/reports/runs/v5_mr5b_external_development_diagnostics.md`

## 14. Final Artifact Index

Primary final results:

- `DIVERSE_X_V5_MR8C_RUN_STATE.md`
- `repo/reports/runs/v5_mr8c_final_external_report.md`
- `repo/reports/runs/v5_mr8c_completion_audit.md`
- `repo/reports/tables/v5_mr8c_final_external_gate.csv`
- `repo/reports/tables/v5_mr8c_final_external_task_status.csv`
- `repo/reports/tables/v5_mr8c_final_external_rejection_summary.csv`
- `repo/reports/tables/v5_mr8c_final_external_rejection_curve.csv`
- `repo/reports/tables/v5_mr8c_final_external_summary.csv`
- `repo/reports/tables/v5_mr8c_final_external_metrics.csv`
- `repo/reports/tables/v5_mr8c_claim_boundary.csv`
- `repo/data/manifests/v5_mr8c_final_external_manifest.json`

Prerequisite and boundary results:

- `repo/reports/tables/v5_mr8b_loader_smoke_gate.csv`
- `repo/reports/tables/v5_mr8b_loader_smoke.csv`
- `repo/reports/tables/v5_mr8b_claim_boundary.csv`
- `repo/data/manifests/v5_mr8b_loader_smoke_manifest.json`
- `repo/reports/tables/v5_mr8_recovery_gate.csv`
- `repo/reports/tables/v5_mr8_loader_diagnosis.csv`
- `repo/reports/tables/v5_mr7_locked_final_gate.csv`
- `repo/reports/tables/v5_mr7_locked_final_task_status.csv`
- `repo/reports/tables/v5_mr6_protocol_gate.csv`
- `repo/reports/tables/v5_mr5c_combined_gate.csv`
- `repo/reports/tables/v5_mr5b_extdev_gate.csv`

Validation scripts:

- `scripts/validate_diversex_v5_mr8c.ps1`
- `scripts/validate_diversex_v5_mr8b.ps1`
- `scripts/validate_diversex_v5_mr8.ps1`
- `scripts/validate_diversex_v5_mr7.ps1`
