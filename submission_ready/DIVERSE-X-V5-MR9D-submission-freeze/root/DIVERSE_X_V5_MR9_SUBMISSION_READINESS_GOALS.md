# DIVERSE-X V5-MR9 Submission-Readiness Goals

Status: `MR9A_MR9B_MR9C_COMPLETED_MR9D_NEXT`
Date: 2026-05-19

## Bottom Line

These tasks are worth doing before manuscript submission.

The core MR8C science is already locked:

- final gate: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`;
- primary claim: audit-card rejection reliability under chemical-space shift;
- MR7 no-go preserved;
- final labels not used for ranking;
- no post-hoc retuning.

However, the paper package still needs several submission-readiness closures so
Reviewer 2 cannot attack baseline fairness, method reproducibility, chemical
interpretability, or artifact availability.

## Requirement Classification

| Item | Required before manuscript submission? | Why |
| --- | --- | --- |
| Tuned baseline closure | Yes, as supplemental fairness analysis | The verification file still records `PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS` in MR5B. Reviewers may ask whether stronger tuned baselines were evaluated. |
| Hero/villain molecule extraction | Strongly recommended | Not required for the statistical claim, but needed for compelling chemical figures and audit-card examples. |
| UQ/conformal/baseline hyperparameter documentation | Yes | The final paper must disclose exact uncertainty, conformal, RF, HGB/XGB, and audit-risk configurations. |
| Code/environment/artifact freeze | Yes | Required for reproducibility and submission package. |
| Public GitHub packaging | Yes if the target journal expects code/data availability | Current local folder is not a git repository, so repo setup or repo selection must be part of the freeze. |

## Non-Negotiable Boundary

MR8C remains the final one-shot external evaluation. MR9 tasks must not:

- rerun MR8C as a new final gate;
- change MR8C task inclusion;
- retune DIVERSE-X after seeing MR8C outcomes;
- relabel MR7 as a pass;
- claim new primary external evidence from supplemental analyses.

Any additional baseline work after MR8C must be reported as:

`post-MR8C supplemental baseline fairness analysis`

and must not alter:

- `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`;
- the locked MR8C primary endpoint;
- the MR8C claim boundary.

## Goal MR9A: Supplemental Tuned Baseline Fairness Matrix

Status: `COMPLETED`

Purpose:

Resolve the pending tuned-baseline line and create a reviewer-facing fairness
table.

Scope:

- Use the frozen 13 MR8C tasks.
- Use train/valid folds only for tuning.
- Do not tune DIVERSE-X.
- Do not use final labels for hyperparameter selection.
- Evaluate final test labels only once for the supplemental baseline table.
- Label results as supplemental/post-MR8C fairness analysis.

Baselines:

- scaffold quota;
- activity-only;
- AD-distance guard;
- uncertainty-only guard;
- conformal/rejection baseline;
- tuned RF/ECFP;
- tuned HistGradientBoosting or XGB/ECFP;
- optional EI-like acquisition proxy only if framed as a simulated acquisition
  baseline and not as a required active-learning claim.

Minimum tuning budget:

- 20 Optuna-equivalent trials per tunable baseline family, or a fixed
  deterministic grid with 20 configurations if Optuna is unavailable.

Outputs:

- `repo/modal/v5_mr9a_tuned_baseline_fairness.py`
- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv`
- `repo/reports/tables/v5_mr9a_tuned_baseline_fairness_summary.csv`
- `repo/reports/tables/v5_mr9a_tuned_baseline_config.csv`
- `repo/reports/runs/v5_mr9a_tuned_baseline_fairness_report.md`
- `repo/data/manifests/v5_mr9a_tuned_baseline_fairness_manifest.json`

Suggested next prompt:

```text
Start DIVERSE-X V5-MR9A supplemental tuned baseline fairness matrix. Use the frozen MR8C 13-task panel and train/valid-only tuning. Do not retune DIVERSE-X, do not change MR8C claims, and do not use final labels for hyperparameter selection. Run Modal if needed. Produce a reviewer-facing tuned RF/HGB/XGB/guard/conformal/scaffold fairness table and close the pending tuned baseline status.
```

Completion:

- Gate: `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`
- Modal run:
  `https://modal.com/apps/rishyanth602/main/ap-ycaHDelZKCybTfF3z7T1FL`
- Valid tasks: `13/13`
- RF/HGB deterministic train/valid tuning budget: `20` configs per family per
  valid task
- Final labels used for hyperparameter selection: `False`
- DIVERSE-X retuned: `False`
- MR8C gate changed: `False`
- Output report:
  `repo/reports/runs/v5_mr9a_tuned_baseline_fairness_report.md`

## Goal MR9B: Hero/Villain Molecule Extraction for Figures

Status: `COMPLETED`

Purpose:

Extract representative molecules for visual audit-card figures.

Boundary:

Because MR8C candidate-level SMILES were not saved in the final result tables,
this must be labeled as post-MR8C illustrative exemplar extraction. It may replay
the frozen scoring code only to emit candidate rows and SMILES for figures. It
must not recompute or alter final gates.

Selection criteria:

Hero examples:

- high rank under MR8C;
- low audit-card risk;
- label-positive/safe in final test set;
- chemically interpretable structure.

Villain examples:

- high activity/probability score;
- high audit-card risk;
- final test label negative/failure;
- clear audit reason such as low nearest-train Tanimoto, uncertainty, conformal
  risk, or descriptor outlier.

Outputs:

- `repo/reports/tables/v5_mr9b_figure_molecule_examples.csv`
- `repo/reports/runs/v5_mr9b_figure_molecule_examples.md`
- optional RDKit PNG/SVG structures for the manuscript figure folder.

Suggested prompt:

```text
Start DIVERSE-X V5-MR9B figure molecule exemplar extraction. Replay only the frozen MR8C scorer to emit candidate-level SMILES and audit-card fields for illustrative figures. Do not rerun MR8C as a gate, do not retune, and do not alter claims. Extract 2-3 hero examples and 2-3 villain examples with SMILES, task, rank, probability, audit risk, AD distance, uncertainty, conformal risk, descriptor outlier, and final label.
```

Completion:

- Gate: `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`
- Modal run:
  `https://modal.com/apps/rishyanth602/main/ap-Jg6N4cQ8dGAE4LeH3d3sLi`
- Valid replay tasks: `13/13`
- Hero/villain examples: `3/3`
- Candidate audit pool rows: `2537`
- SVG molecule structures: `6`
- Output report:
  `repo/reports/runs/v5_mr9b_figure_molecule_examples.md`

## Goal MR9C: UQ, Conformal, and Baseline Configuration Appendix

Status: `COMPLETED`

Purpose:

Create exact method-configuration tables for supplementary information.

Already visible in MR8C code:

- RF activity model:
  - `n_estimators=240`
  - `max_depth=None`
  - `min_samples_leaf=2`
  - `class_weight=balanced_subsample`
  - `random_state=20260519`
- uncertainty risk:
  - `1 - abs(probability - 0.5) * 2`
- AD-distance risk:
  - `1 - nearest_train_tanimoto`
- descriptor outlier:
  - outside train+valid 5th/95th percentile range for MW, LogP, or TPSA
- conformal risk:
  - RF with `n_estimators=160`, `min_samples_leaf=2`,
    `class_weight=balanced_subsample`, `random_state=20260519`
  - trained on train split;
  - validation nonconformity;
  - normalized by validation nonconformity 90th percentile;
- audit-card risk:
  - `0.45 * AD distance risk`
  - `0.25 * uncertainty risk`
  - `0.20 * descriptor outlier`
  - `0.10 * conformal risk`
- audit-card score:
  - `probability - 0.35 * audit_card_risk`
- HGB proxy:
  - `max_iter=80`
  - `learning_rate=0.06`
  - `l2_regularization=0.05`
  - `random_state=20260519`

Outputs:

- `repo/reports/tables/v5_mr9c_method_config_appendix.csv`
- `repo/reports/tables/v5_mr9c_selected_baseline_configs.csv`
- `repo/reports/tables/v5_mr9c_tuning_grid_summary.csv`
- `repo/reports/tables/v5_mr9c_reproducibility_locks.csv`
- `repo/reports/runs/v5_mr9c_config_appendix.md`
- `repo/data/manifests/v5_mr9c_config_appendix_manifest.json`

Completion:

- Gate: `MR9C_CONFIG_APPENDIX_COMPLETE`
- Validation: `PASSED`
- Method configuration rows: `22`
- Selected baseline config rows: `26`
- Failed reproducibility locks: `0`
- New outcome evaluations: `False`

Suggested prompt:

```text
Start DIVERSE-X V5-MR9C supplementary method configuration appendix. Extract and document exact RF, HGB/XGB, uncertainty, conformal, AD-distance, descriptor-outlier, audit-card, scaffold quota, and rejection-curve configurations from the frozen MR8C/MR8B code. Do not run new metrics. Produce manuscript-ready tables for Supplementary Methods.
```

## Goal MR9D: Code, Environment, Artifact Freeze, and GitHub Package

Status: `REQUIRED_FOR_SUBMISSION_PACKAGE`

Purpose:

Freeze the exact code/results environment and prepare a shareable repository or
release archive.

Current local status:

- `C:\Users\rishi\Downloads\DIVERSE-X` is currently `NOT_A_GIT_REPO`.

Required steps:

- create or select the GitHub repository;
- decide whether to initialize git in this folder or copy a clean release tree;
- create a branch such as `codex/v5-mr9-submission-freeze` or
  `submission_ready`;
- capture environment:
  - `pip freeze`;
  - Modal dependency list from MR8B/MR8C runners;
  - PowerShell/Python validation commands;
- package final tables:
  - MR8C CSVs;
  - MR8B smoke CSVs;
  - MR8/MR7 boundary CSVs;
  - validation scripts;
  - manifest files;
- create release archive;
- push to public GitHub if approved;
- later create anonymous link if journal requires double blind.

Outputs:

- `requirements-lock.txt`
- `DIVERSE_X_V5_REPRODUCIBILITY_MANIFEST.md`
- `diversex_v5_submission_ready_release.zip`
- GitHub branch/repo link

Suggested prompt:

```text
Start DIVERSE-X V5-MR9D code and artifact freeze. Do not rerun MR8C. Capture environment, validation commands, final CSVs, manifests, scripts, and reports into a submission-ready release archive. Initialize or prepare a public GitHub repository/branch if needed, then push only after confirming the repository target.
```

## Recommended Execution Order

1. MR9A tuned baseline fairness matrix.
2. MR9C method configuration appendix.
3. MR9B hero/villain molecule extraction.
4. MR9D code/artifact/GitHub freeze.
5. MR10 manuscript and figure generation.

Reason for this order:

- MR9A closes the only obvious reviewer-facing technical gap.
- MR9C documents the exact configs before manuscript drafting.
- MR9B supplies molecules for figures after the scoring/exemplar boundary is
  explicit.
- MR9D freezes all artifacts after the final supplemental tables exist.

## Overall Recommendation

Do not start the manuscript as the next goal. Run MR9A first.

The MR8C result is strong enough for the Q1 audit-primary claim, but the
`PENDING` tuned-baseline status should be closed before manuscript drafting.
This is the one remaining item most likely to trigger reviewer criticism.
