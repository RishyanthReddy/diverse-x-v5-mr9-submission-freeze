# DIVERSE-X V5-MR9B Master Plan

Status: `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`
Date: 2026-05-19

## Mission

Extract hero and villain molecule examples for manuscript figures.

MR9B is illustrative only. It replays the frozen MR8C scorer to emit
candidate-level SMILES and audit-card fields. It is not a new gate, does not
retune DIVERSE-X, and does not change MR8C claims.

## Selection Roles

Hero examples:

- high rank under MR8C audit-card acquisition;
- final label positive;
- low audit-card risk;
- interpretable audit profile.

Villain examples:

- high naive activity/probability rank;
- final label negative;
- high audit risk;
- clear reason such as low nearest-train Tanimoto, high uncertainty, conformal
  risk, or descriptor outlier.

## Outputs

- `repo/modal/v5_mr9b_figure_molecule_examples.py`
- `repo/reports/tables/v5_mr9b_figure_molecule_examples.csv`
- `repo/reports/tables/v5_mr9b_candidate_audit_pool.csv`
- `repo/reports/tables/v5_mr9b_task_status.csv`
- `repo/reports/runs/v5_mr9b_figure_molecule_examples.md`
- `repo/reports/figures/mr9b_molecule_examples/*.svg`
- `repo/data/manifests/v5_mr9b_figure_molecule_examples_manifest.json`

## Gate

`MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED` requires:

- 13/13 MR8C tasks replayed successfully;
- at least 3 hero examples;
- at least 3 villain examples;
- molecule SVGs written;
- boundary labels show illustrative-only use;
- no MR8C gate change and no DIVERSE-X retuning.

## Final Outcome

Gate:

`MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`

Modal run:

`https://modal.com/apps/rishyanth602/main/ap-Jg6N4cQ8dGAE4LeH3d3sLi`

Validation:

`PASSED`

Counts:

- Valid replay tasks: `13/13`
- Hero examples: `3`
- Villain examples: `3`
- Candidate audit pool rows: `2537`
- SVG molecule structures: `6`

Primary report:

`repo/reports/runs/v5_mr9b_figure_molecule_examples.md`
