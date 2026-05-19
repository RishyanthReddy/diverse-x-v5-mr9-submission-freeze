# DIVERSE-X V5 Locked Title and Abstract

Status: `LOCKED_FOR_MANUSCRIPT_DRAFT`
Date: 2026-05-19

## Locked Title

Audit-Card-Guided Molecular Selection Under Chemical-Space Shift

## Alternate Title

Navigating Molecular Selection Under Chemical-Space Shift with Guarded
Acquisition and Audit Cards

## Locked Abstract

Machine learning models for virtual screening often perform well on
retrospective benchmarks but fail silently under realistic chemical-space shift,
particularly when candidate selection must balance activity, structural
diversity, and developability-related properties. We introduce DIVERSE-X, a
guarded molecular acquisition framework that couples scaffold-aware candidate
selection with quantitative audit cards for transfer-risk assessment. Rather
than treating every high-scoring molecule as equally actionable, DIVERSE-X
assigns each selected candidate an audit risk derived from applicability-domain
distance, model uncertainty, conformal-style risk, and descriptor outlier
signals.

We evaluated DIVERSE-X under a frozen, audit-primary external protocol across 13
locked toxicity and ADME benchmark tasks, with task inclusion fixed before
outcome inspection and with final labels prohibited from ranking, threshold
selection, or post-hoc retuning. In the final MR8C external evaluation, all 13
tasks were valid. Audit-card rejection produced a positive rejection-curve AUC
delta of 0.0151, with the strongest fixed rejection point at 40% yielding a
+0.0717 reliability delta. Reliability was nonnegative on 92.3% of tasks at
this rejection point. As a secondary endpoint, guarded acquisition showed a mean
K50 delta of +0.0030 versus scaffold quota and no severe task-level collapses
below -0.05.

These results support DIVERSE-X as an auditable molecular selection strategy for
identifying and filtering high-risk selections under chemical-space shift, while
preserving the earlier MR7 no-go result as evidence that unguarded acquisition
claims remain fragile.

## Claim Boundary

Supported:

- audit-card-guided molecular selection under chemical-space shift;
- positive MR8C audit-primary external support;
- no severe guarded-acquisition collapse versus scaffold quota in MR8C;
- MR7 no-go preserved and disclosed.

Not claimed:

- universal SOTA;
- prospective wet-lab validation;
- clinical, safety, synthesis, or ADMET deployment guarantees;
- MR7 pass;
- post-hoc-retuned external success.

## Source Artifacts

- `repo/reports/tables/v5_mr8c_final_external_gate.csv`
- `repo/reports/tables/v5_mr8c_claim_boundary.csv`
- `repo/reports/runs/v5_mr8c_final_external_report.md`
- `DIVERSE_X_V5_PAPER_RESULTS_FOR_VERIFICATION.md`
