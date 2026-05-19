from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

STATUS = "MR9C_CONFIG_APPENDIX_COMPLETE"
ROOT = Path(__file__).resolve().parents[1]

MR8C_GATE = ROOT / "reports/tables/v5_mr8c_final_external_gate.csv"
MR8C_MANIFEST = ROOT / "data/manifests/v5_mr8c_final_external_manifest.json"
MR9A_GATE = ROOT / "reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv"
MR9A_CONFIG = ROOT / "reports/tables/v5_mr9a_tuned_baseline_config.csv"
MR9A_MANIFEST = ROOT / "data/manifests/v5_mr9a_tuned_baseline_fairness_manifest.json"

METHOD_CONFIG_OUT = ROOT / "reports/tables/v5_mr9c_method_config_appendix.csv"
SELECTED_CONFIG_OUT = ROOT / "reports/tables/v5_mr9c_selected_baseline_configs.csv"
GRID_SUMMARY_OUT = ROOT / "reports/tables/v5_mr9c_tuning_grid_summary.csv"
LOCKS_OUT = ROOT / "reports/tables/v5_mr9c_reproducibility_locks.csv"
REPORT_OUT = ROOT / "reports/runs/v5_mr9c_config_appendix.md"
MANIFEST_OUT = ROOT / "data/manifests/v5_mr9c_config_appendix_manifest.json"


def main() -> int:
    _require_inputs()
    mr8c_gate = pd.read_csv(MR8C_GATE).iloc[0].to_dict()
    mr9a_gate = pd.read_csv(MR9A_GATE).iloc[0].to_dict()
    mr8c_manifest = _read_json(MR8C_MANIFEST)
    mr9a_manifest = _read_json(MR9A_MANIFEST)
    configs = pd.read_csv(MR9A_CONFIG)

    method_config = pd.DataFrame(_method_config_rows())
    selected = _selected_configs(configs)
    grid_summary = _grid_summary(configs)
    locks = pd.DataFrame(
        _lock_rows(
            mr8c_gate=mr8c_gate,
            mr9a_gate=mr9a_gate,
            mr8c_manifest=mr8c_manifest,
            mr9a_manifest=mr9a_manifest,
        )
    )
    manifest = _manifest(
        method_config=method_config,
        selected=selected,
        grid_summary=grid_summary,
        locks=locks,
    )

    for path in [
        METHOD_CONFIG_OUT,
        SELECTED_CONFIG_OUT,
        GRID_SUMMARY_OUT,
        LOCKS_OUT,
        REPORT_OUT,
        MANIFEST_OUT,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)

    method_config.to_csv(METHOD_CONFIG_OUT, index=False)
    selected.to_csv(SELECTED_CONFIG_OUT, index=False)
    grid_summary.to_csv(GRID_SUMMARY_OUT, index=False)
    locks.to_csv(LOCKS_OUT, index=False)
    REPORT_OUT.write_text(
        _report(
            method_config=method_config,
            selected=selected,
            grid_summary=grid_summary,
            locks=locks,
            mr8c_gate=mr8c_gate,
            mr9a_gate=mr9a_gate,
        ),
        encoding="utf-8",
    )
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "selected_config_rows": len(selected)}, indent=2))
    return 0


def _require_inputs() -> None:
    missing = [
        str(path.relative_to(ROOT))
        for path in [MR8C_GATE, MR8C_MANIFEST, MR9A_GATE, MR9A_CONFIG, MR9A_MANIFEST]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing required MR9C inputs: {missing}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _method_config_rows() -> list[dict[str, str]]:
    rows = [
        {
            "section": "data_split",
            "component": "task_panel",
            "scope": "MR8C/MR9A",
            "exact_configuration": (
                "Frozen 13-task MR8C panel; TDC Tox loader for hERG, AMES, DILI, "
                "hERG_Karim, ClinTox, Skin Reaction, Carcinogens_Lagunin; TDC ADME "
                "loader for CYP2C19_Veith, CYP1A2_Veith, Bioavailability_Ma, "
                "CYP2C9_Substrate_CarbonMangels, CYP2D6_Substrate_CarbonMangels, "
                "CYP3A4_Substrate_CarbonMangels."
            ),
            "source_artifact": "repo/data/manifests/v5_mr8c_final_external_manifest.json",
        },
        {
            "section": "data_split",
            "component": "split",
            "scope": "MR8C/MR9A",
            "exact_configuration": "TDC get_split(method='scaffold', seed=20260519).",
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "features",
            "component": "fingerprint",
            "scope": "MR8C/MR9A",
            "exact_configuration": "RDKit Morgan fingerprint radius=2, fpSize=512.",
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "features",
            "component": "MR8C_model_features",
            "scope": "MR8C",
            "exact_configuration": (
                "RF/HGB model input uses 512-bit ECFP vector only. MW, logP, and TPSA "
                "are computed separately for descriptor-outlier audit risk."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "features",
            "component": "MR9A_model_features",
            "scope": "MR9A",
            "exact_configuration": (
                "Tuned RF/HGB model input uses 512-bit ECFP plus scaled descriptors: "
                "MW/500, (logP + 5)/10, TPSA/200."
            ),
            "source_artifact": "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        },
        {
            "section": "scaffold",
            "component": "murcko_scaffold",
            "scope": "MR8C/MR9A",
            "exact_configuration": (
                "RDKit MurckoScaffoldSmiles(mol=mol); fallback to canonical molecule "
                "SMILES when no scaffold string is returned."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "applicability_domain",
            "component": "nearest_train_tanimoto",
            "scope": "MR8C/MR9A",
            "exact_configuration": (
                "For each test molecule, compute max BulkTanimotoSimilarity to all "
                "train+valid fingerprints."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "applicability_domain",
            "component": "ad_distance_risk",
            "scope": "MR8C/MR9A",
            "exact_configuration": "ad_distance_risk = 1.0 - nearest_train_tanimoto.",
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "descriptor_outlier",
            "component": "property_floor",
            "scope": "MR8C/MR9A",
            "exact_configuration": (
                "descriptor_outlier = any test MW/logP/TPSA value outside the "
                "train+valid 5th to 95th percentile range."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_fixed_model",
            "component": "rf_probability_model",
            "scope": "MR8C",
            "exact_configuration": (
                "RandomForestClassifier(n_estimators=240, max_depth=None, "
                "min_samples_leaf=2, class_weight='balanced_subsample', "
                "random_state=20260519, n_jobs=6), fit on train+valid."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_fixed_model",
            "component": "hgb_proxy",
            "scope": "MR8C",
            "exact_configuration": (
                "HistGradientBoostingClassifier(max_iter=80, learning_rate=0.06, "
                "l2_regularization=0.05, random_state=20260519), fit on train+valid; "
                "proxy baseline only."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_uncertainty",
            "component": "margin_uncertainty",
            "scope": "MR8C",
            "exact_configuration": "uncertainty_risk = 1.0 - abs(probability - 0.5) * 2.0.",
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_conformal",
            "component": "conformal_risk",
            "scope": "MR8C",
            "exact_configuration": (
                "Train RF on train only with n_estimators=160, max_depth=None, "
                "min_samples_leaf=2, class_weight='balanced_subsample', "
                "random_state=20260519, n_jobs=4. Compute valid nonconformity as "
                "1-valid_prob for positives and valid_prob for negatives; q90 = 90th "
                "percentile. Test risk = (1 - max(test_prob, 1-test_prob)) / q90, "
                "clipped to [0,1]."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_audit_card",
            "component": "audit_card_risk",
            "scope": "MR8C",
            "exact_configuration": (
                "clip(0.45*ad_distance_risk + 0.25*uncertainty_risk + "
                "0.20*descriptor_outlier + 0.10*conformal_risk, 0, 1)."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_scoring",
            "component": "guard_scores",
            "scope": "MR8C",
            "exact_configuration": (
                "ad_distance_guard_score = probability*(0.70 + 0.30*tanimoto); "
                "uncertainty_guard_score = probability - 0.35*uncertainty_risk; "
                "conformal_guard_score = probability - 0.35*conformal_risk; "
                "audit_card_score = probability - 0.35*audit_card_risk."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "ranking",
            "component": "scaffold_quota",
            "scope": "MR8C/MR9A",
            "exact_configuration": (
                "Sort candidates by score descending and row_id ascending. For scaffold "
                "quota, take first candidate per scaffold, then append remaining sorted "
                "candidates."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR8C_rejection",
            "component": "audit_rejection_curve",
            "scope": "MR8C",
            "exact_configuration": (
                "Use top K=50. Rejection fractions: 0.0, 0.1, 0.2, 0.3, 0.4. "
                "Within selected top K, reject highest-risk molecules by risk method. "
                "Reliability delta = kept_positive_fraction - baseline_positive_fraction "
                "- (kept_mean_risk - baseline_mean_risk)."
            ),
            "source_artifact": "repo/modal/v5_mr8c_final_external_audit_primary.py",
        },
        {
            "section": "MR9A_tuning",
            "component": "selection_metric",
            "scope": "MR9A",
            "exact_configuration": (
                "RF and HGB configs selected by validation average precision only. "
                "Selected config refit on train+valid before supplemental test metrics."
            ),
            "source_artifact": "repo/reports/tables/v5_mr9a_tuned_baseline_config.csv",
        },
        {
            "section": "MR9A_uncertainty",
            "component": "rf_epistemic_uncertainty",
            "scope": "MR9A",
            "exact_configuration": (
                "RF epistemic risk = std of per-tree positive-class probabilities / 0.5, "
                "clipped to [0,1]. Fallback is margin uncertainty."
            ),
            "source_artifact": "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        },
        {
            "section": "MR9A_uncertainty",
            "component": "hgb_margin_uncertainty",
            "scope": "MR9A",
            "exact_configuration": "HGB uncertainty risk = 1.0 - abs(hgb_prob - 0.5) * 2.0.",
            "source_artifact": "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        },
        {
            "section": "MR9A_conformal",
            "component": "selected_model_conformal_risk",
            "scope": "MR9A",
            "exact_configuration": (
                "For each selected RF/HGB config, fit the selected model on train only, "
                "score validation, compute class-conditional nonconformity as "
                "1-valid_prob for positives and valid_prob for negatives; q90 = 90th "
                "percentile. Test risk = (1 - max(test_prob, 1-test_prob)) / q90, "
                "clipped to [0,1]."
            ),
            "source_artifact": "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        },
        {
            "section": "MR9A_scoring",
            "component": "guard_scores",
            "scope": "MR9A",
            "exact_configuration": (
                "RF/HGB AD guard = probability*(0.70 + 0.30*tanimoto); uncertainty "
                "guard = probability - 0.35*uncertainty_risk; conformal guard = "
                "probability - 0.35*conformal_risk. RF UCB-style proxy = "
                "rf_probability + 0.15*(1.0 - rf_uncertainty_risk)."
            ),
            "source_artifact": "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        },
    ]
    return rows


def _selected_configs(configs: pd.DataFrame) -> pd.DataFrame:
    selected = configs[configs["selected_for_final_fit"].astype(str).eq("True")].copy()
    selected["selection_boundary"] = (
        "selected_on_validation_average_precision; final labels not used for selection"
    )
    selected["params_pretty"] = selected["params_json"].map(
        lambda value: json.dumps(json.loads(value), sort_keys=True)
    )
    return selected[
        [
            "task_name",
            "family",
            "config_id",
            "valid_average_precision",
            "selection_metric",
            "tuning_split",
            "final_labels_used_for_selection",
            "params_pretty",
            "selection_boundary",
        ]
    ].sort_values(["task_name", "family"], kind="mergesort")


def _grid_summary(configs: pd.DataFrame) -> pd.DataFrame:
    unique_configs = configs[["family", "config_id", "params_json"]].drop_duplicates()
    summary = (
        configs.groupby("family", as_index=False)
        .agg(
            task_count=("task_name", "nunique"),
            total_evaluated_configs=("config_id", "count"),
            unique_config_count=("config_id", "nunique"),
            selected_config_rows=(
                "selected_for_final_fit",
                lambda s: int(s.astype(str).eq("True").sum()),
            ),
            final_label_selection_flags=(
                "final_labels_used_for_selection",
                lambda s: int(s.astype(str).ne("False").sum()),
            ),
        )
        .sort_values("family", kind="mergesort")
    )
    ranges = []
    for family, group in unique_configs.groupby("family", sort=False):
        params = [json.loads(value) for value in group["params_json"]]
        ranges.append(
            {
                "family": family,
                "config_ids": ",".join(group["config_id"].astype(str).tolist()),
                "parameter_space_json": json.dumps(_parameter_space(params), sort_keys=True),
            }
        )
    return summary.merge(pd.DataFrame(ranges), on="family", how="left")


def _parameter_space(params: list[dict[str, Any]]) -> dict[str, list[Any]]:
    keys = sorted({key for row in params for key in row})
    return {
        key: sorted({json.dumps(row.get(key), sort_keys=True) for row in params})
        for key in keys
    }


def _lock_rows(
    *,
    mr8c_gate: dict[str, Any],
    mr9a_gate: dict[str, Any],
    mr8c_manifest: dict[str, Any],
    mr9a_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "lock_name": "mr8c_gate_status",
            "value": mr8c_gate["gate_status"],
            "expected": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
            "passed": mr8c_gate["gate_status"] == "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
            "source_artifact": str(MR8C_GATE.relative_to(ROOT)),
        },
        {
            "lock_name": "mr8c_final_labels_used_for_ranking",
            "value": str(mr8c_manifest["locks"]["final_labels_used_for_ranking"]),
            "expected": "False",
            "passed": mr8c_manifest["locks"]["final_labels_used_for_ranking"] is False,
            "source_artifact": str(MR8C_MANIFEST.relative_to(ROOT)),
        },
        {
            "lock_name": "mr8c_post_hoc_retuning",
            "value": str(mr8c_manifest["locks"]["post_hoc_retuning"]),
            "expected": "False",
            "passed": mr8c_manifest["locks"]["post_hoc_retuning"] is False,
            "source_artifact": str(MR8C_MANIFEST.relative_to(ROOT)),
        },
        {
            "lock_name": "mr9a_gate_status",
            "value": mr9a_gate["gate_status"],
            "expected": "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED",
            "passed": mr9a_gate["gate_status"] == "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED",
            "source_artifact": str(MR9A_GATE.relative_to(ROOT)),
        },
        {
            "lock_name": "mr9a_analysis_type",
            "value": mr9a_manifest["locks"]["analysis_type"],
            "expected": "post_MR8C_supplemental_baseline_fairness",
            "passed": mr9a_manifest["locks"]["analysis_type"]
            == "post_MR8C_supplemental_baseline_fairness",
            "source_artifact": str(MR9A_MANIFEST.relative_to(ROOT)),
        },
        {
            "lock_name": "mr9a_final_labels_used_for_hyperparameter_selection",
            "value": str(mr9a_manifest["locks"]["final_labels_used_for_hyperparameter_selection"]),
            "expected": "False",
            "passed": mr9a_manifest["locks"]["final_labels_used_for_hyperparameter_selection"]
            is False,
            "source_artifact": str(MR9A_MANIFEST.relative_to(ROOT)),
        },
        {
            "lock_name": "mr9a_diversex_retuned",
            "value": str(mr9a_manifest["locks"]["diversex_retuned"]),
            "expected": "False",
            "passed": mr9a_manifest["locks"]["diversex_retuned"] is False,
            "source_artifact": str(MR9A_MANIFEST.relative_to(ROOT)),
        },
        {
            "lock_name": "mr9c_new_outcome_evaluations",
            "value": "False",
            "expected": "False",
            "passed": True,
            "source_artifact": "repo/scripts/v5_mr9c_config_appendix.py",
        },
    ]


def _manifest(
    *,
    method_config: pd.DataFrame,
    selected: pd.DataFrame,
    grid_summary: pd.DataFrame,
    locks: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": STATUS,
        "analysis_type": "supplement_ready_configuration_appendix",
        "no_new_outcome_evaluations": True,
        "outputs": {
            "method_config_appendix": str(METHOD_CONFIG_OUT.relative_to(ROOT)),
            "selected_baseline_configs": str(SELECTED_CONFIG_OUT.relative_to(ROOT)),
            "tuning_grid_summary": str(GRID_SUMMARY_OUT.relative_to(ROOT)),
            "reproducibility_locks": str(LOCKS_OUT.relative_to(ROOT)),
            "report": str(REPORT_OUT.relative_to(ROOT)),
        },
        "counts": {
            "method_config_rows": int(len(method_config)),
            "selected_config_rows": int(len(selected)),
            "grid_family_rows": int(len(grid_summary)),
            "lock_rows": int(len(locks)),
            "failed_locks": int((locks["passed"].astype(str) != "True").sum()),
        },
        "locks": {
            "mr8c_gate_changed": False,
            "mr9a_gate_changed": False,
            "diversex_retuned": False,
            "final_labels_used_for_hyperparameter_selection": False,
            "new_outcome_evaluations_run": False,
        },
    }


def _report(
    *,
    method_config: pd.DataFrame,
    selected: pd.DataFrame,
    grid_summary: pd.DataFrame,
    locks: pd.DataFrame,
    mr8c_gate: dict[str, Any],
    mr9a_gate: dict[str, Any],
) -> str:
    method_table = method_config.to_markdown(index=False)
    selected_table = selected.to_markdown(index=False)
    grid_table = grid_summary.to_markdown(index=False)
    locks_table = locks.to_markdown(index=False)
    return f"""# DIVERSE-X V5-MR9C Exact Configuration Appendix

Status: `{STATUS}`
Date: 2026-05-19

## Boundary

MR9C is a supplement-ready configuration appendix. It documents MR8C and MR9A
configuration exactly. It does not run new outcome evaluations, does not retune
DIVERSE-X, and does not change MR8C or MR9A gates.

## Gate Context

- MR8C gate: `{mr8c_gate["gate_status"]}`
- MR9A gate: `{mr9a_gate["gate_status"]}`
- MR9C role: required reproducibility appendix for UQ, conformal, baseline,
  scaffold, audit-card, and ranking configurations.

## Reproducibility Locks

{locks_table}

## Method Configuration Appendix

{method_table}

## MR9A Tuning Grid Summary

{grid_table}

## MR9A Selected Baseline Configurations

{selected_table}

## Supplement Text Boundary

These configurations may be used in the Methods and Supplement. MR9C should be
cited as a configuration appendix only, not as an evaluation gate.
"""


if __name__ == "__main__":
    raise SystemExit(main())
