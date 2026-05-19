# DIVERSE-X V5-MR9A Master Plan

Status: `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`
Date: 2026-05-19

## Mission

Close the reviewer-facing tuned-baseline gap:

`PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS`

MR9A is a post-MR8C supplemental fairness analysis. It does not change the
MR8C final external gate, does not retune DIVERSE-X, and does not upgrade or
downgrade the locked MR8C claim boundary.

## Scientific Boundary

MR8C remains the final one-shot external evidence:

- final gate: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`;
- primary claim: audit-card rejection reliability under chemical-space shift;
- final labels were not used for ranking;
- no post-hoc retuning;
- MR7 no-go remains disclosed.

MR9A may use final test labels only for supplemental baseline metrics after the
baseline hyperparameters have been selected from train/valid folds.

## Frozen Task Panel

MR9A uses the exact 13-task MR8C panel:

| Task | Loader | Priority |
| --- | --- | --- |
| hERG | Tox | core |
| AMES | Tox | core |
| DILI | Tox | core |
| hERG_Karim | Tox | core |
| ClinTox | Tox | core |
| Skin Reaction | Tox | reserve |
| Carcinogens_Lagunin | Tox | reserve |
| CYP2C19_Veith | ADME | core |
| CYP1A2_Veith | ADME | core |
| Bioavailability_Ma | ADME | reserve |
| CYP2C9_Substrate_CarbonMangels | ADME | reserve |
| CYP2D6_Substrate_CarbonMangels | ADME | reserve |
| CYP3A4_Substrate_CarbonMangels | ADME | reserve |

## Baseline Families

Required supplemental baselines:

- random fixed seed;
- tuned RF activity-only;
- tuned RF scaffold quota;
- tuned RF AD-distance guard;
- tuned RF uncertainty-only guard;
- tuned RF conformal/rejection guard;
- tuned RF UCB-style uncertainty proxy;
- tuned HistGradientBoosting activity-only;
- tuned HistGradientBoosting scaffold quota;
- tuned HistGradientBoosting AD-distance guard;
- tuned HistGradientBoosting uncertainty-only guard;
- tuned HistGradientBoosting conformal/rejection guard.

HistGradientBoosting is the XGB-style boosted-tree comparator for this
dependency-light Modal run. It is tuned with the same 20-config deterministic
budget as RF.

## Tuning Contract

Each tunable family receives 20 deterministic Optuna-equivalent configurations
per valid task:

- RF/ECFP+descriptor: 20 configs;
- HGB/ECFP+descriptor: 20 configs.

Selection metric:

- validation average precision only.

Forbidden:

- no final-label hyperparameter selection;
- no DIVERSE-X threshold retuning;
- no post-MR8C task exclusion;
- no MR8C gate rewrite.

## Outputs

Required files:

- `repo/modal/v5_mr9a_tuned_baseline_fairness.py`;
- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv`;
- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_summary.csv`;
- `repo/reports/tables/v5_mr9a_tuned_baseline_config.csv`;
- `repo/reports/runs/v5_mr9a_tuned_baseline_fairness_report.md`;
- `repo/data/manifests/v5_mr9a_tuned_baseline_fairness_manifest.json`.

Additional reviewer-useful files:

- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_metrics.csv`;
- `repo/reports/tables/v5_mr9a_tuned_baseline_task_status.csv`;
- `repo/reports/tables/v5_mr9a_mr8c_reference_comparison.csv`.

## Pass Gate

`MR9A_TUNED_BASELINE_FAIRNESS_CLOSED` requires:

- all 13 MR8C tasks attempted;
- all 13 tasks valid;
- RF trial count per valid task >= 20;
- HGB trial count per valid task >= 20;
- final labels not used for hyperparameter selection;
- DIVERSE-X not retuned;
- MR8C gate unchanged;
- supplemental labeling present in report and manifest.

## Use In Manuscript

MR9A supports a Methods/Supplement statement such as:

> We additionally ran a post-MR8C supplemental fairness matrix with 20
> train/validation-selected configurations for each RF and boosted-tree
> baseline family. These analyses were conducted after the MR8C gate and did
> not affect the final external decision.

MR9A must not be described as a second final external gate.

## Final Outcome

Modal run:

`https://modal.com/apps/rishyanth602/main/ap-ycaHDelZKCybTfF3z7T1FL`

Gate:

`MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`

Closed evidence:

- 13/13 MR8C tasks valid;
- RF trial count per valid task: 20;
- HGB trial count per valid task: 20;
- 26 train/valid-selected final-fit configs recorded;
- final labels used for supplemental metrics only;
- final labels not used for hyperparameter selection;
- DIVERSE-X not retuned;
- MR8C gate unchanged.
