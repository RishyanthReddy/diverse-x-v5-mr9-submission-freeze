# DIVERSE-X V5-MR9B Run State

Status: `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`
Date: 2026-05-19

## Goal

Extract 2-3 hero and 2-3 villain molecule examples with SMILES, audit-card
fields, ranks, labels, and SVG structures for manuscript figures.

## Boundary

- Analysis type: `post_MR8C_illustrative_exemplar_extraction`
- New claim gate: `False`
- DIVERSE-X retuned: `False`
- MR8C gate changed: `False`

## Required Run Command

From `repo`:

```powershell
$env:DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE="YES_EXTRACT_FIGURE_EXAMPLES"
python -X utf8 -m modal run modal\v5_mr9b_figure_molecule_examples.py
Remove-Item Env:\DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE -ErrorAction SilentlyContinue
```

## Expected Final Status

`MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`

## Final State

- Modal run:
  `https://modal.com/apps/rishyanth602/main/ap-Jg6N4cQ8dGAE4LeH3d3sLi`
- Validation: `PASSED`
- Valid replay tasks: `13/13`
- Hero examples: `3`
- Villain examples: `3`
- Candidate audit pool rows: `2537`
- Figure SVG directory:
  `repo/reports/figures/mr9b_molecule_examples`
