from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT / "repo"
TABLE_DIR = REPO_ROOT / "reports" / "tables"
RUN_DIR = REPO_ROOT / "reports" / "runs"
MANIFEST_DIR = REPO_ROOT / "data" / "manifests"

TASK_REGISTRY_OUT = TABLE_DIR / "v5_mr8b_task_registry.csv"
BASELINES_OUT = TABLE_DIR / "v5_mr8b_baseline_registry.csv"
ENDPOINTS_OUT = TABLE_DIR / "v5_mr8b_endpoint_registry.csv"
PASS_GATE_OUT = TABLE_DIR / "v5_mr8b_pass_gate.csv"
REPORT_OUT = RUN_DIR / "v5_mr8b_preregistration_contract.md"
MANIFEST_OUT = MANIFEST_DIR / "v5_mr8b_protocol_manifest.json"

SOURCE_OVERVIEW = "https://tdcommons.ai/single_pred_tasks/overview/"
SOURCE_ADME = "https://tdcommons.ai/single_pred_tasks/adme/"
SOURCE_TOX = "https://tdcommons.ai/single_pred_tasks/tox/"
SOURCE_ADMET_GROUP = "https://tdcommons.ai/benchmark/admet_group/overview/"


TASKS: list[dict[str, str]] = [
    {
        "task_name": "hERG",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "preselected_but_not_loaded",
        "mr8c_role": "loader_repair_secondary",
        "priority": "core",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "AMES",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "preselected_but_not_loaded",
        "mr8c_role": "loader_repair_secondary",
        "priority": "core",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "DILI",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "preselected_but_not_loaded",
        "mr8c_role": "loader_repair_secondary",
        "priority": "core",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "hERG_Karim",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_tox_primary",
        "priority": "core",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "ClinTox",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_tox_primary",
        "priority": "core",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "Skin Reaction",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_tox_primary",
        "priority": "reserve",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "Carcinogens_Lagunin",
        "loader": "Tox",
        "category": "toxicity",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_tox_primary",
        "priority": "reserve",
        "source_url": SOURCE_TOX,
    },
    {
        "task_name": "CYP2C19_Veith",
        "loader": "ADME",
        "category": "metabolism",
        "metric_family": "AUPRC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "core",
        "source_url": SOURCE_ADME,
    },
    {
        "task_name": "CYP1A2_Veith",
        "loader": "ADME",
        "category": "metabolism",
        "metric_family": "AUPRC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "core",
        "source_url": SOURCE_ADME,
    },
    {
        "task_name": "Bioavailability_Ma",
        "loader": "ADME",
        "category": "absorption",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "reserve",
        "source_url": SOURCE_ADME,
    },
    {
        "task_name": "CYP2C9_Substrate_CarbonMangels",
        "loader": "ADME",
        "category": "metabolism",
        "metric_family": "AUPRC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "reserve",
        "source_url": SOURCE_ADME,
    },
    {
        "task_name": "CYP2D6_Substrate_CarbonMangels",
        "loader": "ADME",
        "category": "metabolism",
        "metric_family": "AUPRC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "reserve",
        "source_url": SOURCE_ADME,
    },
    {
        "task_name": "CYP3A4_Substrate_CarbonMangels",
        "loader": "ADME",
        "category": "metabolism",
        "metric_family": "AUROC",
        "mr7_relationship": "new_unopened_task",
        "mr8c_role": "fresh_adme_primary",
        "priority": "reserve",
        "source_url": SOURCE_ADME,
    },
]

BASELINES: list[dict[str, str]] = [
    {
        "baseline": "scaffold_quota",
        "role": "primary_secondary_comparator",
        "allowed_in_mr8c": "yes",
        "description": "Probability ranking with scaffold cap; acquisition comparator only.",
    },
    {
        "baseline": "activity_only",
        "role": "activity_ceiling_reference",
        "allowed_in_mr8c": "yes",
        "description": "Probability ranking with no scaffold cap.",
    },
    {
        "baseline": "ad_distance_guard",
        "role": "simple_audit_baseline",
        "allowed_in_mr8c": "yes",
        "description": "Nearest-train chemical distance as risk score.",
    },
    {
        "baseline": "uncertainty_only_guard",
        "role": "model_uncertainty_baseline",
        "allowed_in_mr8c": "yes",
        "description": "Predictive uncertainty as risk score.",
    },
    {
        "baseline": "conformal_rejection_baseline",
        "role": "selective_prediction_baseline",
        "allowed_in_mr8c": "yes",
        "description": "Calibration-set nonconformity threshold for reject/keep policy.",
    },
    {
        "baseline": "rf_ecfp",
        "role": "base_activity_model",
        "allowed_in_mr8c": "yes",
        "description": "Tuned or locked RF over ECFP features.",
    },
    {
        "baseline": "xgb_ecfp",
        "role": "strong_tabular_activity_model",
        "allowed_in_mr8c": "yes_if_available",
        "description": "Tuned XGBoost/gradient boosting baseline with fixed search budget.",
    },
]

ENDPOINTS: list[dict[str, str]] = [
    {
        "endpoint": "audit_card_rejection_reliability_or_aurc",
        "role": "primary",
        "pass_direction": "positive",
        "description": "Reliability gain or AURC improvement after rejecting high-risk selections.",
    },
    {
        "endpoint": "task_level_rejection_nonnegative_rate",
        "role": "primary_support",
        "pass_direction": "majority_nonnegative",
        "description": "Most valid tasks must show nonnegative rejection reliability.",
    },
    {
        "endpoint": "guarded_acquisition_delta_vs_scaffold_quota",
        "role": "secondary",
        "pass_direction": "no_severe_collapse",
        "description": "Acquisition may be mixed but cannot collapse against scaffold quota.",
    },
    {
        "endpoint": "valid_external_task_count",
        "role": "eligibility",
        "pass_direction": "at_least_5",
        "description": (
            "MR8C requires at least five valid external tasks after smoke-test eligibility."
        ),
    },
]

PASS_GATE: list[dict[str, Any]] = [
    {
        "gate": "MR8B_PROTOCOL_FROZEN_READY_FOR_MR8C",
        "condition": "loader_smoke_test_valid_task_count >= 5",
        "required": True,
    },
    {
        "gate": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
        "condition": "audit rejection reliability positive overall",
        "required": True,
    },
    {
        "gate": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
        "condition": "most valid tasks nonnegative on rejection reliability",
        "required": True,
    },
    {
        "gate": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
        "condition": "no severe guarded acquisition collapse versus scaffold quota",
        "required": True,
    },
    {
        "gate": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
        "condition": "MR7 no-go fully disclosed",
        "required": True,
    },
    {
        "gate": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
        "condition": "no post-hoc retuning and no final-label ranking access",
        "required": True,
    },
]


def main() -> None:
    for directory in [TABLE_DIR, RUN_DIR, MANIFEST_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    task_registry = pd.DataFrame(TASKS)
    task_registry["loader_contract"] = task_registry.apply(_loader_contract, axis=1)
    task_registry["smoke_test_scope"] = (
        "availability_schema_split_size_class_balance_only_no_performance_metrics"
    )
    task_registry["outcome_metric_allowed_in_mr8b"] = False

    baselines = pd.DataFrame(BASELINES)
    endpoints = pd.DataFrame(ENDPOINTS)
    pass_gate = pd.DataFrame(PASS_GATE)

    task_registry.to_csv(TASK_REGISTRY_OUT, index=False)
    baselines.to_csv(BASELINES_OUT, index=False)
    endpoints.to_csv(ENDPOINTS_OUT, index=False)
    pass_gate.to_csv(PASS_GATE_OUT, index=False)

    REPORT_OUT.write_text(_report(task_registry, baselines, endpoints, pass_gate), encoding="utf-8")
    MANIFEST_OUT.write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(UTC).isoformat(),
                "status": "MR8B_PREREGISTRATION_FROZEN_PENDING_SMOKE",
                "task_count": int(len(task_registry)),
                "core_task_count": int(task_registry["priority"].eq("core").sum()),
                "outputs": {
                    "task_registry": str(TASK_REGISTRY_OUT.relative_to(REPO_ROOT)),
                    "baseline_registry": str(BASELINES_OUT.relative_to(REPO_ROOT)),
                    "endpoint_registry": str(ENDPOINTS_OUT.relative_to(REPO_ROOT)),
                    "pass_gate": str(PASS_GATE_OUT.relative_to(REPO_ROOT)),
                    "contract": str(REPORT_OUT.relative_to(REPO_ROOT)),
                },
                "source_urls": {
                    "tdc_single_prediction_overview": SOURCE_OVERVIEW,
                    "tdc_adme": SOURCE_ADME,
                    "tdc_tox": SOURCE_TOX,
                    "tdc_admet_group": SOURCE_ADMET_GROUP,
                },
                "locks": {
                    "mr7_consumed_no_go_disclosed": True,
                    "mr7_rerun": False,
                    "mr8b_outcome_metrics_run": False,
                    "mr8b_model_fit": False,
                    "mr8b_acquisition_ranking_run": False,
                    "mr8c_final_run_allowed_before_smoke_go": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("MR8B_PREREGISTRATION_FROZEN_PENDING_SMOKE")


def _loader_contract(row: pd.Series) -> str:
    if row["loader"] == "Tox":
        return "tdc.single_pred.Tox"
    if row["loader"] == "ADME":
        return "tdc.single_pred.ADME"
    return "unsupported"


def _report(
    tasks: pd.DataFrame,
    baselines: pd.DataFrame,
    endpoints: pd.DataFrame,
    pass_gate: pd.DataFrame,
) -> str:
    task_table = tasks[
        [
            "task_name",
            "loader",
            "category",
            "metric_family",
            "mr7_relationship",
            "priority",
        ]
    ].to_markdown(index=False)
    baseline_table = baselines[["baseline", "role", "allowed_in_mr8c"]].to_markdown(index=False)
    endpoint_table = endpoints[["endpoint", "role", "pass_direction"]].to_markdown(index=False)
    gate_table = pass_gate[["gate", "condition", "required"]].to_markdown(index=False)

    return f"""# DIVERSE-X V5-MR8B Preregistration Contract

Status: `MR8B_PREREGISTRATION_FROZEN_PENDING_SMOKE`
Date: 2026-05-19

## Boundary

MR8B freezes the next external protocol before any outcome run. MR7 remains
`MR7_LOCKED_FINAL_EXTERNAL_NO_GO` and must be disclosed. MR8B does not rerun
MR7, train models, rank molecules, compute outcome metrics, or evaluate MR8C.

## Loader Contract

The broad TDC ADMET benchmark group contains both ADME and toxicity endpoints.
The single-prediction loader must match the endpoint family:

- `tdc.single_pred.ADME` for CYP and other ADME tasks.
- `tdc.single_pred.Tox` for toxicity tasks including `hERG`, `AMES`, and `DILI`.

References:

- TDC single-prediction overview: {SOURCE_OVERVIEW}
- TDC ADME tasks: {SOURCE_ADME}
- TDC Tox tasks: {SOURCE_TOX}
- TDC ADMET benchmark group: {SOURCE_ADMET_GROUP}

## Primary Claim

MR8C's primary endpoint is audit-card rejection reliability, not acquisition
dominance. The claim being tested is whether high-risk selections identified by
audit cards are genuinely harmful under external scaffold shift, and whether
rejecting them improves reliability.

## Secondary Claim

Guarded acquisition versus scaffold quota is secondary. It must avoid severe
collapse, but it does not need to dominate every task.

## Candidate Task Registry

{task_table}

## Baselines

{baseline_table}

## Endpoints

{endpoint_table}

## MR8C Pass Gate

{gate_table}

## MR8B Smoke Test Scope

Allowed:

- task availability;
- loader family correctness;
- schema detection for SMILES and labels;
- scaffold split availability;
- split sizes;
- class-balance counts.

Forbidden:

- model fitting;
- prediction scores;
- ranking;
- acquisition evaluation;
- audit rejection outcome metrics;
- retuning based on final labels.

## Stop Rule

Stop after smoke-test eligibility and validation. MR8C may run only after MR8B
returns a protocol-ready GO with at least five valid external tasks.
"""


if __name__ == "__main__":
    main()
