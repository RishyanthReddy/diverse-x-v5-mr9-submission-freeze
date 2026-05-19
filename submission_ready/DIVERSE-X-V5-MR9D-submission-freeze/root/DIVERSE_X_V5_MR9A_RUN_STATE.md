# DIVERSE-X V5-MR9A Run State

Status: `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`
Date: 2026-05-19

## Goal

Run the supplemental tuned-baseline fairness matrix required before manuscript
submission.

## Current State

- MR8C final gate is already locked: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`.
- MR9A runner is implemented at
  `repo/modal/v5_mr9a_tuned_baseline_fairness.py`.
- MR9A is explicitly supplemental/post-MR8C.
- Modal execution complete:
  `https://modal.com/apps/rishyanth602/main/ap-ycaHDelZKCybTfF3z7T1FL`
- Validation passed.

## Required Run Command

From `repo`:

```powershell
$env:DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES="YES_RUN_POST_MR8C_FAIRNESS"
python -X utf8 -m modal run modal\v5_mr9a_tuned_baseline_fairness.py
Remove-Item Env:\DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES -ErrorAction SilentlyContinue
```

## Expected Final Status

`MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`

## Final Metrics

- Valid tasks: `13/13`
- RF trial count per valid task: `20`
- HGB trial count per valid task: `20`
- Tuned methods evaluated: `12`
- Selected final-fit configs: `26`
- Fixed MR8C selections vs tuned RF scaffold quota:
  mean recall delta `+0.001202`, nonworse `8/13`
- Fixed MR8C selections vs tuned HGB scaffold quota:
  mean recall delta `-0.008634`, nonworse `8/13`

## Locks

- DIVERSE-X retuned: `False`
- Final labels used for hyperparameter selection: `False`
- MR8C gate changed: `False`
- Analysis type: `post_MR8C_supplemental_baseline_fairness`
