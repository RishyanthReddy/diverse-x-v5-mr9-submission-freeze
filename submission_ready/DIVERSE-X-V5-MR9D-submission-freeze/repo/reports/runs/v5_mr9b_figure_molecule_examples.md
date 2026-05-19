# DIVERSE-X V5-MR9B Figure Molecule Examples

Status: `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`
Date: 2026-05-19

## Boundary

MR9B is a post-MR8C illustrative exemplar extraction. It replays the frozen MR8C
scorer only to emit candidate-level SMILES and audit-card fields for manuscript
figures. It is not a new claim gate, does not retune DIVERSE-X, and does not
change the MR8C final gate.

It does not change the MR8C final gate.

## Gate

- Valid replay tasks: `13` of `13`
- Hero examples: `3`
- Villain examples: `3`
- Candidate pool rows: `2537`
- Final labels used for ranking: `False`
- Final labels used for illustrative selection:
  `True`

## Examples

| example_id   | role    | task_name                      |   final_label |   probability |   audit_card_risk |   nearest_train_tanimoto |   uncertainty_risk |   conformal_risk |   activity_rank |   audit_rank | audit_reason                                                                       | canonical_smiles                                                                                                                                             | structure_svg_path                                    |
|:-------------|:--------|:-------------------------------|--------------:|--------------:|------------------:|-------------------------:|-------------------:|-----------------:|----------------:|-------------:|:-----------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|
| hero_01      | hero    | CYP1A2_Veith                   |             1 |      0.998774 |         0.0345722 |                 0.925    |         0.00245134 |       0.00209382 |               1 |            1 | low_audit_risk_profile                                                             | c1cncc(CNc2nc(-c3cccnc3)nc3ccccc23)c1                                                                                                                        | reports/figures/mr9b_molecule_examples/hero_01.svg    |
| hero_02      | hero    | AMES                           |             1 |      0.973612 |         0.0495855 |                 0.928571 |         0.0527762  |       0.0424858  |              10 |            1 | low_audit_risk_profile                                                             | O=NN1CCCC1                                                                                                                                                   | reports/figures/mr9b_molecule_examples/hero_02.svg    |
| hero_03      | hero    | hERG_Karim                     |             1 |      0.993638 |         0.0655682 |                 0.863636 |         0.0127243  |       0.0102344  |               4 |            1 | low_audit_risk_profile                                                             | Cc1ncoc1-c1nnc(SCCCN2CC[C@]3(c4ccc(C(F)(F)F)cc4)C[C@@H]3C2)n1C                                                                                               | reports/figures/mr9b_molecule_examples/hero_03.svg    |
| villain_01   | villain | ClinTox                        |             0 |      0.18499  |         0.706198  |                 0.256    |         0.36998    |       0.789033   |              48 |          274 | low_nearest_train_tanimoto;high_conformal_risk;descriptor_outlier                  | CO[C@H]1C(=O)[C@]2(C)[C@@H](OC)C[C@H]3OC[C@@]3(OC(C)=O)[C@H]2[C@H](OC(=O)c2ccccc2)[C@]2(O)C[C@H](OC(=O)[C@H](O)[C@@H](NC(=O)OC(C)(C)C)c3ccccc3)C(C)=C1C2(C)C | reports/figures/mr9b_molecule_examples/villain_01.svg |
| villain_02   | villain | CYP2C9_Substrate_CarbonMangels |             0 |      0.395375 |         0.800235  |                 0.230769 |         0.79075    |       0.563941   |              22 |          110 | low_nearest_train_tanimoto;high_uncertainty;high_conformal_risk;descriptor_outlier | Cn1cnc2c1c(=O)[nH]c(=O)n2C                                                                                                                                   | reports/figures/mr9b_molecule_examples/villain_02.svg |
| villain_03   | villain | CYP2D6_Substrate_CarbonMangels |             0 |      0.510013 |         0.81789   |                 0.355556 |         0.979974   |       0.828963   |              22 |          105 | low_nearest_train_tanimoto;high_uncertainty;high_conformal_risk;descriptor_outlier | CN(C)CCOc1ccc(/C(=C(\CCCl)c2ccccc2)c2ccccc2)cc1                                                                                                              | reports/figures/mr9b_molecule_examples/villain_03.svg |

## Figure Use

Use these molecules as visual examples for audit-card figures only. Do not cite
MR9B as performance evidence.
