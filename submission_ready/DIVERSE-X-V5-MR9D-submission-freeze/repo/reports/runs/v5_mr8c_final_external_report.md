# DIVERSE-X V5-MR8C Final External Audit-Primary Evaluation

Status: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`
Date: 2026-05-19

## Boundary

MR8C is the one-shot final external evaluation after MR8B. MR7 remains
`MR7_LOCKED_FINAL_EXTERNAL_NO_GO`. MR8C did not rerun MR7, did not retune after outcomes, and did
not use final labels for ranking or method selection.

## Gate

- Valid tasks: `13` of `13`
- Audit rejection AUC delta: `0.015094`
- Best rejection reliability delta:
  `0.071685` at fraction
  `0.4`
- Task nonnegative rejection rate at best fraction:
  `0.923`
- Mean guarded acquisition delta vs scaffold quota:
  `0.003043`
- Severe acquisition losses below -0.05:
  `0`

## Task Status

| task_name                      | loader   | priority   | status   |   test_rows |   test_positive_rate |
|:-------------------------------|:---------|:-----------|:---------|------------:|---------------------:|
| hERG                           | Tox      | core       | PASS     |         132 |             0.628788 |
| AMES                           | Tox      | core       | PASS     |        1457 |             0.574468 |
| DILI                           | Tox      | core       | PASS     |          96 |             0.65625  |
| hERG_Karim                     | Tox      | core       | PASS     |        2690 |             0.486245 |
| ClinTox                        | Tox      | core       | PASS     |         297 |             0.107744 |
| Skin Reaction                  | Tox      | reserve    | PASS     |          82 |             0.609756 |
| Carcinogens_Lagunin            | Tox      | reserve    | PASS     |          56 |             0.160714 |
| CYP2C19_Veith                  | ADME     | core       | PASS     |        2534 |             0.425414 |
| CYP1A2_Veith                   | ADME     | core       | PASS     |        2517 |             0.45292  |
| Bioavailability_Ma             | ADME     | reserve    | PASS     |         128 |             0.796875 |
| CYP2C9_Substrate_CarbonMangels | ADME     | reserve    | PASS     |         135 |             0.162963 |
| CYP2D6_Substrate_CarbonMangels | ADME     | reserve    | PASS     |         135 |             0.288889 |
| CYP3A4_Substrate_CarbonMangels | ADME     | reserve    | PASS     |         135 |             0.555556 |

## Primary Audit Rejection Curve

|   rejection_fraction |   mean_reliability_delta |   task_nonnegative_rate |   mean_kept_positive_fraction |   mean_baseline_positive_fraction |
|---------------------:|-------------------------:|------------------------:|------------------------------:|----------------------------------:|
|                  0   |              1.60128e-17 |                1        |                      0.687692 |                          0.687692 |
|                  0.1 |              0.0289312   |                0.923077 |                      0.699145 |                          0.687692 |
|                  0.2 |              0.0406026   |                0.923077 |                      0.698077 |                          0.687692 |
|                  0.3 |              0.045565    |                0.846154 |                      0.69011  |                          0.687692 |
|                  0.4 |              0.0716851   |                0.923077 |                      0.702564 |                          0.687692 |

## Secondary Acquisition Summary

| task_name                      |   positive_selected |   delta_vs_scaffold_quota |   auprc_delta_vs_scaffold_quota |
|:-------------------------------|--------------------:|--------------------------:|--------------------------------:|
| AMES                           |                  48 |               -0.00119474 |                    -0.000877699 |
| Bioavailability_Ma             |                  43 |                0          |                     0.0222575   |
| CYP1A2_Veith                   |                  50 |                0          |                    -0.0021931   |
| CYP2C19_Veith                  |                  49 |                0          |                    -0.00431517  |
| CYP2C9_Substrate_CarbonMangels |                  12 |                0          |                    -0.0247045   |
| CYP2D6_Substrate_CarbonMangels |                  21 |                0          |                    -0.0152129   |
| CYP3A4_Substrate_CarbonMangels |                  34 |               -0.0266667  |                    -0.00515727  |
| Carcinogens_Lagunin            |                   9 |                0          |                     0.00661597  |
| ClinTox                        |                  17 |                0.03125    |                    -0.0298277   |
| DILI                           |                  40 |               -0.015873   |                    -0.00998995  |
| Skin Reaction                  |                  33 |                0.04       |                     0.00888635  |
| hERG                           |                  42 |                0.0120482  |                     0.00161298  |
| hERG_Karim                     |                  49 |                0          |                    -0.00286863  |

## Claim Boundary

Q1 support is determined by the gate above. Audit-card external support can be
claimed only according to the claim-boundary table. Acquisition dominance is not
the primary claim.
