# DIVERSE-X V5-MR9C Master Plan

Status: `MR9C_CONFIG_APPENDIX_COMPLETE`
Date: 2026-05-19

## Mission

Create the exact UQ, conformal, scaffold, audit-card, and baseline configuration
appendix required for the manuscript supplement.

MR9C is documentation/reproducibility work only. It does not run outcome
evaluations, retune DIVERSE-X, or change MR8C/MR9A gates.

## Inputs

- `repo/modal/v5_mr8c_final_external_audit_primary.py`
- `repo/modal/v5_mr9a_tuned_baseline_fairness.py`
- `repo/reports/tables/v5_mr9a_tuned_baseline_config.csv`
- `repo/reports/tables/v5_mr8c_final_external_gate.csv`
- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv`
- MR8C and MR9A manifests.

## Outputs

- `repo/scripts/v5_mr9c_config_appendix.py`
- `repo/reports/runs/v5_mr9c_config_appendix.md`
- `repo/reports/tables/v5_mr9c_method_config_appendix.csv`
- `repo/reports/tables/v5_mr9c_selected_baseline_configs.csv`
- `repo/reports/tables/v5_mr9c_tuning_grid_summary.csv`
- `repo/reports/tables/v5_mr9c_reproducibility_locks.csv`
- `repo/data/manifests/v5_mr9c_config_appendix_manifest.json`

## Completion Gate

`MR9C_CONFIG_APPENDIX_COMPLETE` requires:

- MR8C gate preserved as `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`;
- MR9A gate preserved as `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`;
- exact audit-card, AD-distance, uncertainty, conformal, scaffold quota, RF,
  HGB, and ranking formulas documented;
- selected MR9A train/valid configs exported;
- no final-label hyperparameter selection recorded;
- no new outcome evaluations run.

## Final Outcome

Gate:

`MR9C_CONFIG_APPENDIX_COMPLETE`

Validation:

`PASSED`

Counts:

- Method configuration rows: `22`
- Selected MR9A config rows: `26`
- Tuning grid family rows: `2`
- Reproducibility locks: `8`
- Failed locks: `0`

Primary appendix:

`repo/reports/runs/v5_mr9c_config_appendix.md`
