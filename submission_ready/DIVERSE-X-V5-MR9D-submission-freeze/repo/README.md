# DIVERSE-X

DIVERSE-X is a research implementation of a scaffold-aware, post-hoc reranker
for virtual-screening candidate lists. It takes an already scored molecule table
and greedily selects a top-K set while attenuating molecules from scaffolds that
have already appeared in the selected list.

The project is deliberately narrow. DIVERSE-X is not an affinity model, not a
generative model, not a docking workflow, and not evidence of prospective
activity, safety, toxicity, ADMET, synthesis, clinical value, or experimental hit
rates. The final benchmark supports a retrospective scaffold-aware reranking
result with explicit quota-equivalence boundaries.

## Method

For a molecule with base score `S_base` and scaffold `s`, the default decay at
selection step `t` is:

```text
decay(s, t) = beta + (1 - beta) * exp(-lambda * n_t(s))
S_final(molecule, t) = S_base(molecule) * decay(s, t)
```

`n_t(s)` is the number of already selected molecules with scaffold `s`. `beta`
is a floor that prevents repeated scaffolds from being excluded entirely.
`lambda` controls how strongly repeated scaffolds are attenuated. The default
benchmark setting is `beta=0.2` and `lambda=0.8`.

## Installation

From this repository directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[chem,dev]"
```

The `chem` extra installs RDKit for scaffold, fingerprint, and descriptor
features. The `dev` extra installs test and lint tools.

## CLI Quickstart

Check the installed command:

```powershell
.\.venv\Scripts\diversex.exe --help
```

Run the synthetic smoke pipeline:

```powershell
.\.venv\Scripts\diversex.exe run-synthetic `
  --config configs\synthetic.yaml `
  --output-dir reports\runs\quickstart_synthetic
```

Rerank a candidate table with DIVERSE-X:

```powershell
.\.venv\Scripts\diversex.exe rerank `
  --input reports\runs\quickstart_synthetic\synthetic_candidates.csv `
  --output reports\runs\quickstart_synthetic\diversex_rerank.csv `
  --method diversex `
  --k 50 `
  --beta 0.2 `
  --lambda 0.8
```

Evaluate a ranking against an affinity baseline:

```powershell
.\.venv\Scripts\diversex.exe evaluate `
  --ranking reports\runs\quickstart_synthetic\diversex_rerank.csv `
  --baseline reports\runs\quickstart_synthetic\affinity_ranking.csv `
  --output-dir reports\runs\quickstart_synthetic\eval `
  --k-values 50,100,200
```

## Release QA Commands

Run the full suite:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
```

Run the tiny real-data reproduction smoke:

```powershell
.\.venv\Scripts\python scripts\dx10_tiny_real_reproduction_smoke.py
```

The current release-QA evidence is:

- `reports/runs/dx10_fresh_environment_smoke.md`
- `reports/runs/dx10_tiny_real_reproduction/tiny_reproduction_report.md`
- `reports/runs/dx9_review.md`

## Main Artifacts

Final figures:

- `reports/figures/final/dx9_figure_01_pipeline.png`
- `reports/figures/final/dx9_figure_02_method_frontier_top100.png`
- `reports/figures/final/dx9_figure_03_parameter_regions.png`
- `reports/figures/final/dx9_figure_04_scaffold_definitions.png`
- `reports/figures/final/dx9_figure_05_runtime_comparison.png`
- `reports/figures/final/dx9_figure_06_claim_summary.png`

Final tables:

- `reports/tables/final/table_01_dataset_summary.csv`
- `reports/tables/final/table_02_top100_method_comparison.csv`
- `reports/tables/final/table_03_robustness_summary.csv`
- `reports/tables/final/table_04_runtime_summary.csv`
- `reports/tables/final/table_05_claim_audit.csv`
- `reports/tables/final/table_manifest.csv`

Writing package:

- `reports/runs/dx9_methods_notes.md`
- `reports/runs/dx9_result_summary.md`
- `reports/manuscript/dx9_manuscript_skeleton.md`
- `reports/runs/dx9_review.md`

## Benchmark Result Boundary

Across the eight-target retrospective benchmark, DIVERSE-X increases top-100
exact-scaffold coverage relative to affinity ranking while retaining high
retrospective oracle-score signal. At K=100, final tables report 100.0 mean
unique exact scaffolds and 0.9892 mean oracle-score retention for default
DIVERSE-X.

The central caveat is that scaffold quota matches DIVERSE-X on paired
scaffold-count and score-retention checks at K=50/100/200. Reports and
manuscript text must keep this boundary visible. Do not state that DIVERSE-X
beats scaffold quota, proves an advantage beyond one-per-scaffold selection, or
is empirically better than prior-art systems such as ScaffAug.

## Project Control

Execution is controlled by local files one directory above this repo:

- [Master plan](../DIVERSE_X_Research_Grade_Master_Plan.md)
- [TODO tracker](../DIVERSE_X_TODO.md)
- [Run state](../DIVERSE_X_RUN_STATE.md)
- [Evidence lock](../evidence/DIVERSE_X_PrePhase_Evidence_Intake.md)
- [Codex and Linear foundation](../DIVERSE_X_Codex_Linear_Foundation.md)

The TODO tracker is the execution source of truth. The evidence lock is a
planning artifact; implementation phases must not turn into recurring broad
literature-review work.

## External Code Boundary

ScaffAug and `xai-org/x-algorithm` are treated as context or inspiration only.
External source code must not be cloned, vendored, copied, or ported without a
specific review card approving URL, license, purpose, and contamination risk.
