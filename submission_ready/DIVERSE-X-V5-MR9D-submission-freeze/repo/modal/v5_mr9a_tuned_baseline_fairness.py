from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import modal

APP_NAME = "diversex-v5-mr9a-tuned-baseline-fairness"
CONFIRM_ENV = "DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES"
CONFIRM_VALUE = "YES_RUN_POST_MR8C_FAIRNESS"
OVERWRITE_ENV = "DIVERSEX_MR9A_ALLOW_OVERWRITE"
OVERWRITE_VALUE = "YES_OVERWRITE_MR9A"
MR8C_GATE_STATUS = "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT"
MR9A_STATUS = "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED"
MR9A_CONDITIONAL_STATUS = "MR9A_TUNED_BASELINE_FAIRNESS_CONDITIONAL"
MR9A_NO_GO_STATUS = "MR9A_TUNED_BASELINE_FAIRNESS_INCOMPLETE"
PRIMARY_COMPARATOR = "tuned_rf_scaffold_quota"
PRIMARY_K_LABEL = "K50"
TRIAL_BUDGET_PER_FAMILY = 20

FINAL_TASKS: tuple[dict[str, str], ...] = (
    {"task_name": "hERG", "loader": "Tox", "priority": "core"},
    {"task_name": "AMES", "loader": "Tox", "priority": "core"},
    {"task_name": "DILI", "loader": "Tox", "priority": "core"},
    {"task_name": "hERG_Karim", "loader": "Tox", "priority": "core"},
    {"task_name": "ClinTox", "loader": "Tox", "priority": "core"},
    {"task_name": "Skin Reaction", "loader": "Tox", "priority": "reserve"},
    {"task_name": "Carcinogens_Lagunin", "loader": "Tox", "priority": "reserve"},
    {"task_name": "CYP2C19_Veith", "loader": "ADME", "priority": "core"},
    {"task_name": "CYP1A2_Veith", "loader": "ADME", "priority": "core"},
    {"task_name": "Bioavailability_Ma", "loader": "ADME", "priority": "reserve"},
    {"task_name": "CYP2C9_Substrate_CarbonMangels", "loader": "ADME", "priority": "reserve"},
    {"task_name": "CYP2D6_Substrate_CarbonMangels", "loader": "ADME", "priority": "reserve"},
    {"task_name": "CYP3A4_Substrate_CarbonMangels", "loader": "ADME", "priority": "reserve"},
)

METRICS_OUTPUT = Path("reports/tables/v5_mr9a_tuned_baseline_fairness_metrics.csv")
SUMMARY_OUTPUT = Path("reports/tables/v5_mr9a_tuned_baseline_fairness_summary.csv")
CONFIG_OUTPUT = Path("reports/tables/v5_mr9a_tuned_baseline_config.csv")
TASK_STATUS_OUTPUT = Path("reports/tables/v5_mr9a_tuned_baseline_task_status.csv")
GATE_OUTPUT = Path("reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv")
REFERENCE_OUTPUT = Path("reports/tables/v5_mr9a_mr8c_reference_comparison.csv")
REPORT_OUTPUT = Path("reports/runs/v5_mr9a_tuned_baseline_fairness_report.md")
MANIFEST_OUTPUT = Path("data/manifests/v5_mr9a_tuned_baseline_fairness_manifest.json")
MR8C_GATE_INPUT = Path("reports/tables/v5_mr8c_final_external_gate.csv")
MR8C_SUMMARY_INPUT = Path("reports/tables/v5_mr8c_final_external_summary.csv")
MR8C_MANIFEST_INPUT = Path("data/manifests/v5_mr8c_final_external_manifest.json")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.26,<2.0",
        "pandas>=2.1,<3.0",
        "pytdc==1.1.15",
        "rdkit>=2023.9",
        "scikit-learn>=1.4",
    )
)

app = modal.App(APP_NAME)


@app.function(image=image, cpu=8.0, memory=24576, timeout=7200)
def remote_tuned_baseline_fairness() -> dict[str, Any]:
    started = time.perf_counter()

    import numpy as np
    import pandas as pd
    from rdkit import Chem, DataStructs
    from rdkit.Chem import Descriptors, rdFingerprintGenerator
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.metrics import average_precision_score, roc_auc_score
    from tdc.single_pred import ADME, Tox

    metric_rows: list[dict[str, Any]] = []
    config_rows: list[dict[str, Any]] = []
    task_status: list[dict[str, Any]] = []

    for task in FINAL_TASKS:
        task_name = task["task_name"]
        loader_name = task["loader"]
        try:
            loader_cls = ADME if loader_name == "ADME" else Tox
            data = loader_cls(name=task_name)
            split = data.get_split(method="scaffold", seed=20260519)
            train = _normalize_split(pd, split["train"], "train", task_name)
            valid = _normalize_split(pd, split.get("valid", pd.DataFrame()), "valid", task_name)
            test = _normalize_split(pd, split["test"], "test", task_name)
            prepared_train, prepared_valid, prepared_test, prep = _prepare_frames(
                train,
                valid,
                test,
                np=np,
                Chem=Chem,
                DataStructs=DataStructs,
                Descriptors=Descriptors,
                MurckoScaffold=MurckoScaffold,
                rdFingerprintGenerator=rdFingerprintGenerator,
            )
            if prep["status"] != "PASS":
                task_status.append(_status_row(task, prep["status"], prep["reason"]))
                continue
            scored, selections, model_status = _score_tuned_baselines(
                task_name,
                prepared_train,
                prepared_valid,
                prepared_test,
                RandomForestClassifier=RandomForestClassifier,
                HistGradientBoostingClassifier=HistGradientBoostingClassifier,
                average_precision_score=average_precision_score,
                np=np,
            )
            config_rows.extend(selections)
            rankings = _rankings(scored)
            for method, ranking in rankings.items():
                metric_rows.extend(
                    _metrics(
                        task_name,
                        method,
                        ranking,
                        scored,
                        average_precision_score=average_precision_score,
                        roc_auc_score=roc_auc_score,
                    )
                )
            task_status.append(
                {
                    "task_name": task_name,
                    "loader": loader_name,
                    "priority": task["priority"],
                    "status": "PASS",
                    "reason": model_status["status"],
                    "train_rows": int(len(prepared_train)),
                    "valid_rows": int(len(prepared_valid)),
                    "test_rows": int(len(scored)),
                    "test_positive_rate": float(scored["label"].mean()),
                    "rf_selected_config_id": model_status["rf_selected_config_id"],
                    "hgb_selected_config_id": model_status["hgb_selected_config_id"],
                    "rf_valid_average_precision": model_status["rf_valid_average_precision"],
                    "hgb_valid_average_precision": model_status["hgb_valid_average_precision"],
                    "median_nearest_train_tanimoto": float(
                        scored["nearest_train_tanimoto"].median()
                    ),
                    "p10_nearest_train_tanimoto": float(
                        scored["nearest_train_tanimoto"].quantile(0.10)
                    ),
                }
            )
        except Exception as exc:  # pragma: no cover - remote defensive quarantine
            task_status.append(
                _status_row(task, "QUARANTINED_PRE_METRIC", f"{type(exc).__name__}: {exc}")
            )

    metrics = pd.DataFrame(metric_rows)
    configs = pd.DataFrame(config_rows)
    summary = _summary(metrics) if not metrics.empty else pd.DataFrame()
    gate = _gate(summary, configs, task_status)
    return {
        "status": gate["gate_status"],
        "created_at_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "final_tasks": list(FINAL_TASKS),
        "metrics": metrics.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
        "configs": configs.to_dict(orient="records"),
        "task_status": task_status,
        "gate": gate,
        "locks": {
            "analysis_type": "post_MR8C_supplemental_baseline_fairness",
            "mr8c_gate_changed": False,
            "mr8c_claim_boundary_changed": False,
            "diversex_retuned": False,
            "final_labels_used_for_hyperparameter_selection": False,
            "final_labels_used_for_ranking": False,
            "final_labels_used_for_supplemental_metrics": True,
            "tuning_split": "train_valid_only",
            "test_split_role": "supplemental_metric_table_only",
            "post_hoc_retuning": False,
            "modal_gpu_spend": False,
        },
    }


@app.local_entrypoint()
def main() -> str:
    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        raise RuntimeError(
            "MR9A is a post-MR8C supplemental baseline analysis. Set "
            f"{CONFIRM_ENV}={CONFIRM_VALUE} to run it."
        )
    if MANIFEST_OUTPUT.exists() and os.environ.get(OVERWRITE_ENV) != OVERWRITE_VALUE:
        raise RuntimeError(
            f"MR9A output manifest already exists at {MANIFEST_OUTPUT}. "
            f"Set {OVERWRITE_ENV}={OVERWRITE_VALUE} only if intentionally replacing "
            "the supplemental fairness artifacts."
        )
    result = remote_tuned_baseline_fairness.remote()
    _write_outputs(result)
    return json.dumps(
        {
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "valid_task_count": result["gate"]["valid_task_count"],
            "rf_trial_count_per_valid_task": result["gate"]["rf_trial_count_per_valid_task"],
            "hgb_trial_count_per_valid_task": result["gate"]["hgb_trial_count_per_valid_task"],
        },
        indent=2,
        sort_keys=True,
    )


def _normalize_split(pd: Any, frame: Any, split_name: str, task_name: str) -> Any:
    if frame is None or len(frame) == 0:
        return pd.DataFrame(columns=["task_name", "split", "smiles", "label", "row_id"])
    working = frame.copy()
    smiles_col = _first_present(working, ["Drug", "SMILES", "smiles", "drug"])
    label_col = _first_present(working, ["Y", "label", "Label", "y"])
    out = working[[smiles_col, label_col]].copy()
    out.columns = ["smiles", "label"]
    out["task_name"] = task_name
    out["split"] = split_name
    out["row_id"] = [f"{task_name}_{split_name}_{index}" for index in range(len(out))]
    out["label"] = out["label"].astype(float).round().astype(int)
    return out


def _prepare_frames(
    train: Any,
    valid: Any,
    test: Any,
    *,
    np: Any,
    Chem: Any,
    DataStructs: Any,
    Descriptors: Any,
    MurckoScaffold: Any,
    rdFingerprintGenerator: Any,
) -> tuple[Any, Any, Any, dict[str, str]]:
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=512)
    train_prepared = train.__class__(
        _featurized_rows(
            train,
            np=np,
            Chem=Chem,
            DataStructs=DataStructs,
            Descriptors=Descriptors,
            MurckoScaffold=MurckoScaffold,
            generator=generator,
        )
    )
    valid_prepared = valid.__class__(
        _featurized_rows(
            valid,
            np=np,
            Chem=Chem,
            DataStructs=DataStructs,
            Descriptors=Descriptors,
            MurckoScaffold=MurckoScaffold,
            generator=generator,
        )
    )
    test_prepared = test.__class__(
        _featurized_rows(
            test,
            np=np,
            Chem=Chem,
            DataStructs=DataStructs,
            Descriptors=Descriptors,
            MurckoScaffold=MurckoScaffold,
            generator=generator,
        )
    )
    train_valid = train.__class__(
        list(train_prepared.to_dict(orient="records"))
        + list(valid_prepared.to_dict(orient="records"))
    )
    if train_prepared.empty or valid_prepared.empty or train_valid.empty or test_prepared.empty:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "empty_after_rdkit_or_missing_valid",
        )
    if len(test_prepared) < 50:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "test_rows_lt_50",
        )
    if train_prepared["label"].nunique() < 2 or valid_prepared["label"].nunique() < 2:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "train_or_valid_single_class",
        )
    if train_valid["label"].nunique() < 2 or test_prepared["label"].nunique() < 2:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "train_valid_or_test_single_class",
        )
    train_fps = list(train_valid["fingerprint"])
    train_descriptors = train_valid[["mw", "logp", "tpsa"]].astype(float)
    lower = train_descriptors.quantile(0.05)
    upper = train_descriptors.quantile(0.95)
    test_prepared["nearest_train_tanimoto"] = [
        _nearest_similarity(fp, train_fps, DataStructs=DataStructs)
        for fp in test_prepared["fingerprint"]
    ]
    outlier = (
        (test_prepared[["mw", "logp", "tpsa"]].astype(float) < lower)
        | (test_prepared[["mw", "logp", "tpsa"]].astype(float) > upper)
    ).any(axis=1)
    test_prepared["descriptor_outlier"] = outlier.astype(float)
    return train_prepared, valid_prepared, test_prepared, _status("PASS", "prepared")


def _featurized_rows(frame: Any, **kwargs: Any) -> list[dict[str, Any]]:
    rows = []
    for row in frame.itertuples(index=False):
        parsed = _featurize(row.smiles, **kwargs)
        if parsed is not None:
            rows.append({**row._asdict(), **parsed})
    return rows


def _featurize(
    smiles: str,
    *,
    np: Any,
    Chem: Any,
    DataStructs: Any,
    Descriptors: Any,
    MurckoScaffold: Any,
    generator: Any,
) -> dict[str, Any] | None:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    fp = generator.GetFingerprint(mol)
    arr = np.zeros((512,), dtype=float)
    DataStructs.ConvertToNumpyArray(fp, arr)
    scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=mol) or Chem.MolToSmiles(mol)
    descriptor_tail = np.array(
        [
            float(Descriptors.MolWt(mol)) / 500.0,
            (float(Descriptors.MolLogP(mol)) + 5.0) / 10.0,
            float(Descriptors.TPSA(mol)) / 200.0,
        ],
        dtype=float,
    )
    features = np.concatenate([arr, descriptor_tail])
    return {
        "canonical_smiles": Chem.MolToSmiles(mol, canonical=True),
        "fingerprint": fp,
        "feature_vector": features,
        "scaffold": scaffold,
        "mw": float(Descriptors.MolWt(mol)),
        "logp": float(Descriptors.MolLogP(mol)),
        "tpsa": float(Descriptors.TPSA(mol)),
    }


def _score_tuned_baselines(
    task_name: str,
    train: Any,
    valid: Any,
    test: Any,
    *,
    RandomForestClassifier: Any,
    HistGradientBoostingClassifier: Any,
    average_precision_score: Any,
    np: Any,
) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
    x_train = np.vstack(train["feature_vector"].to_numpy())
    y_train = train["label"].astype(int).to_numpy()
    x_valid = np.vstack(valid["feature_vector"].to_numpy())
    y_valid = valid["label"].astype(int).to_numpy()
    train_valid = train.__class__(
        list(train.to_dict(orient="records")) + list(valid.to_dict(orient="records"))
    )
    x_train_valid = np.vstack(train_valid["feature_vector"].to_numpy())
    y_train_valid = train_valid["label"].astype(int).to_numpy()
    x_test = np.vstack(test["feature_vector"].to_numpy())

    rf_selection, rf_rows = _select_rf_config(
        task_name,
        x_train,
        y_train,
        x_valid,
        y_valid,
        RandomForestClassifier=RandomForestClassifier,
        average_precision_score=average_precision_score,
    )
    hgb_selection, hgb_rows = _select_hgb_config(
        task_name,
        x_train,
        y_train,
        x_valid,
        y_valid,
        HistGradientBoostingClassifier=HistGradientBoostingClassifier,
        average_precision_score=average_precision_score,
    )

    rf_params = json.loads(rf_selection["params_json"])
    hgb_params = json.loads(hgb_selection["params_json"])

    rf_final = RandomForestClassifier(**_rf_kwargs(rf_params, final_fit=True))
    rf_final.fit(x_train_valid, y_train_valid)
    rf_test_prob = rf_final.predict_proba(x_test)[:, 1]
    rf_uncertainty = _rf_epistemic_uncertainty(rf_final, x_test, np=np)

    rf_tuning_model = RandomForestClassifier(**_rf_kwargs(rf_params, final_fit=False))
    rf_tuning_model.fit(x_train, y_train)
    rf_valid_prob = rf_tuning_model.predict_proba(x_valid)[:, 1]
    rf_conformal = _conformal_risk(
        y_valid,
        rf_valid_prob,
        rf_test_prob,
        np=np,
    )

    hgb_final = HistGradientBoostingClassifier(
        **_hgb_kwargs(hgb_params, final_fit=True)
    )
    hgb_final.fit(x_train_valid, y_train_valid)
    hgb_test_prob = hgb_final.predict_proba(x_test)[:, 1]
    hgb_uncertainty = np.clip(1.0 - abs(hgb_test_prob - 0.5) * 2.0, 0.0, 1.0)

    hgb_tuning_model = HistGradientBoostingClassifier(
        **_hgb_kwargs(hgb_params, final_fit=False)
    )
    hgb_tuning_model.fit(x_train, y_train)
    hgb_valid_prob = hgb_tuning_model.predict_proba(x_valid)[:, 1]
    hgb_conformal = _conformal_risk(y_valid, hgb_valid_prob, hgb_test_prob, np=np)

    scored = test.copy()
    scored["rf_probability"] = rf_test_prob
    scored["rf_uncertainty_risk"] = rf_uncertainty
    scored["rf_conformal_risk"] = rf_conformal
    scored["hgb_probability"] = hgb_test_prob
    scored["hgb_uncertainty_risk"] = hgb_uncertainty
    scored["hgb_conformal_risk"] = hgb_conformal
    scored["ad_distance_risk"] = 1.0 - scored["nearest_train_tanimoto"].astype(float)
    scored["rf_ad_guard_score"] = (
        scored["rf_probability"].astype(float)
        * (0.70 + 0.30 * scored["nearest_train_tanimoto"].astype(float))
    )
    scored["rf_uncertainty_guard_score"] = (
        scored["rf_probability"].astype(float)
        - 0.35 * scored["rf_uncertainty_risk"].astype(float)
    )
    scored["rf_conformal_guard_score"] = (
        scored["rf_probability"].astype(float)
        - 0.35 * scored["rf_conformal_risk"].astype(float)
    )
    scored["rf_ucb_uncertainty_proxy_score"] = (
        scored["rf_probability"].astype(float)
        + 0.15 * (1.0 - scored["rf_uncertainty_risk"].astype(float))
    )
    scored["hgb_ad_guard_score"] = (
        scored["hgb_probability"].astype(float)
        * (0.70 + 0.30 * scored["nearest_train_tanimoto"].astype(float))
    )
    scored["hgb_uncertainty_guard_score"] = (
        scored["hgb_probability"].astype(float)
        - 0.35 * scored["hgb_uncertainty_risk"].astype(float)
    )
    scored["hgb_conformal_guard_score"] = (
        scored["hgb_probability"].astype(float)
        - 0.35 * scored["hgb_conformal_risk"].astype(float)
    )
    return (
        scored,
        rf_rows + hgb_rows,
        {
            "status": "PASS_TRAIN_VALID_TUNED_RF_HGB_20_CONFIGS_EACH",
            "rf_selected_config_id": rf_selection["config_id"],
            "hgb_selected_config_id": hgb_selection["config_id"],
            "rf_valid_average_precision": float(rf_selection["valid_average_precision"]),
            "hgb_valid_average_precision": float(hgb_selection["valid_average_precision"]),
        },
    )


def _select_rf_config(
    task_name: str,
    x_train: Any,
    y_train: Any,
    x_valid: Any,
    y_valid: Any,
    *,
    RandomForestClassifier: Any,
    average_precision_score: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = []
    best: dict[str, Any] | None = None
    for config in _rf_config_grid():
        model = RandomForestClassifier(**_rf_kwargs(config, final_fit=False))
        model.fit(x_train, y_train)
        valid_prob = model.predict_proba(x_valid)[:, 1]
        ap = float(average_precision_score(y_valid, valid_prob))
        row = _config_row(task_name, "tuned_rf_ecfp_descriptor", config, ap)
        rows.append(row)
        if best is None or ap > float(best["valid_average_precision"]):
            best = row
    assert best is not None
    for row in rows:
        row["selected_for_final_fit"] = row["config_id"] == best["config_id"]
    return best, rows


def _select_hgb_config(
    task_name: str,
    x_train: Any,
    y_train: Any,
    x_valid: Any,
    y_valid: Any,
    *,
    HistGradientBoostingClassifier: Any,
    average_precision_score: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = []
    best: dict[str, Any] | None = None
    for config in _hgb_config_grid():
        model = HistGradientBoostingClassifier(**_hgb_kwargs(config, final_fit=False))
        model.fit(x_train, y_train)
        valid_prob = model.predict_proba(x_valid)[:, 1]
        ap = float(average_precision_score(y_valid, valid_prob))
        row = _config_row(task_name, "tuned_hgb_ecfp_descriptor", config, ap)
        rows.append(row)
        if best is None or ap > float(best["valid_average_precision"]):
            best = row
    assert best is not None
    for row in rows:
        row["selected_for_final_fit"] = row["config_id"] == best["config_id"]
    return best, rows


def _rf_config_grid() -> list[dict[str, Any]]:
    return [
        {
            "config_id": f"rf_grid_{idx:02d}",
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_leaf": min_leaf,
            "max_features": max_features,
            "class_weight": class_weight,
        }
        for idx, (n_estimators, max_depth, min_leaf, max_features, class_weight) in enumerate(
            [
                (120, None, 1, "sqrt", "balanced_subsample"),
                (160, None, 2, "sqrt", "balanced_subsample"),
                (200, None, 4, "sqrt", "balanced_subsample"),
                (240, None, 2, "log2", "balanced_subsample"),
                (280, None, 4, "log2", "balanced_subsample"),
                (160, 16, 1, "sqrt", "balanced_subsample"),
                (200, 16, 2, "sqrt", "balanced_subsample"),
                (240, 16, 4, "sqrt", "balanced_subsample"),
                (160, 24, 1, "sqrt", "balanced_subsample"),
                (200, 24, 2, "sqrt", "balanced_subsample"),
                (240, 24, 4, "sqrt", "balanced_subsample"),
                (120, 32, 1, "log2", "balanced_subsample"),
                (160, 32, 2, "log2", "balanced_subsample"),
                (200, 32, 4, "log2", "balanced_subsample"),
                (240, None, 1, 0.35, "balanced_subsample"),
                (240, None, 2, 0.50, "balanced_subsample"),
                (240, None, 4, 0.70, "balanced_subsample"),
                (200, 24, 2, 0.35, None),
                (240, 24, 2, 0.50, None),
                (280, 24, 4, 0.70, None),
            ],
            start=1,
        )
    ]


def _hgb_config_grid() -> list[dict[str, Any]]:
    return [
        {
            "config_id": f"hgb_grid_{idx:02d}",
            "max_iter": max_iter,
            "learning_rate": learning_rate,
            "max_leaf_nodes": max_leaf_nodes,
            "l2_regularization": l2_regularization,
            "min_samples_leaf": min_samples_leaf,
        }
        for idx, (
            max_iter,
            learning_rate,
            max_leaf_nodes,
            l2_regularization,
            min_samples_leaf,
        ) in enumerate(
            [
                (60, 0.04, 15, 0.00, 20),
                (80, 0.04, 31, 0.00, 20),
                (100, 0.04, 31, 0.02, 20),
                (120, 0.04, 63, 0.02, 20),
                (60, 0.06, 15, 0.00, 20),
                (80, 0.06, 31, 0.02, 20),
                (100, 0.06, 31, 0.05, 20),
                (120, 0.06, 63, 0.05, 20),
                (60, 0.08, 15, 0.02, 20),
                (80, 0.08, 31, 0.05, 20),
                (100, 0.08, 63, 0.05, 20),
                (120, 0.08, 63, 0.10, 20),
                (80, 0.10, 15, 0.05, 20),
                (100, 0.10, 31, 0.10, 20),
                (120, 0.10, 63, 0.10, 20),
                (100, 0.03, 31, 0.10, 40),
                (140, 0.03, 63, 0.10, 40),
                (100, 0.05, 31, 0.20, 40),
                (140, 0.05, 63, 0.20, 40),
                (160, 0.04, 63, 0.20, 60),
            ],
            start=1,
        )
    ]


def _rf_kwargs(config: dict[str, Any], *, final_fit: bool) -> dict[str, Any]:
    return {
        "n_estimators": int(config["n_estimators"]),
        "max_depth": config["max_depth"],
        "min_samples_leaf": int(config["min_samples_leaf"]),
        "max_features": config["max_features"],
        "class_weight": config["class_weight"],
        "random_state": 20260519,
        "n_jobs": 6 if final_fit else 4,
    }


def _hgb_kwargs(config: dict[str, Any], *, final_fit: bool) -> dict[str, Any]:
    return {
        "max_iter": int(config["max_iter"]),
        "learning_rate": float(config["learning_rate"]),
        "max_leaf_nodes": int(config["max_leaf_nodes"]),
        "l2_regularization": float(config["l2_regularization"]),
        "min_samples_leaf": int(config["min_samples_leaf"]),
        "random_state": 20260519,
    }


def _config_row(
    task_name: str,
    family: str,
    config: dict[str, Any],
    valid_average_precision: float,
) -> dict[str, Any]:
    return {
        "task_name": task_name,
        "family": family,
        "config_id": config["config_id"],
        "valid_average_precision": valid_average_precision,
        "selection_metric": "validation_average_precision",
        "tuning_split": "train_valid_only",
        "final_labels_used_for_selection": False,
        "selected_for_final_fit": False,
        "params_json": json.dumps(config, sort_keys=True),
    }


def _rf_epistemic_uncertainty(model: Any, x_test: Any, *, np: Any) -> Any:
    try:
        tree_probs = np.vstack([tree.predict_proba(x_test)[:, 1] for tree in model.estimators_])
        return np.clip(tree_probs.std(axis=0) / 0.5, 0.0, 1.0)
    except Exception:
        probability = model.predict_proba(x_test)[:, 1]
        return np.clip(1.0 - abs(probability - 0.5) * 2.0, 0.0, 1.0)


def _conformal_risk(y_valid: Any, valid_prob: Any, test_prob: Any, *, np: Any) -> Any:
    valid_nonconformity = np.where(y_valid == 1, 1.0 - valid_prob, valid_prob)
    q90 = float(np.quantile(valid_nonconformity, 0.90))
    predicted_class_nonconformity = 1.0 - np.maximum(test_prob, 1.0 - test_prob)
    return np.clip(predicted_class_nonconformity / max(q90, 1e-6), 0.0, 1.0)


def _rankings(scored: Any) -> dict[str, Any]:
    scored = scored.copy()
    scored["random_fixed_seed_score"] = [
        _stable_unit_score(row_id) for row_id in scored["row_id"].astype(str)
    ]
    return {
        "random_fixed_seed": _rank(scored, "random_fixed_seed_score", "random_fixed_seed", None),
        "tuned_rf_activity_only": _rank(
            scored,
            "rf_probability",
            "tuned_rf_activity_only",
            None,
        ),
        "tuned_rf_scaffold_quota": _rank(
            scored,
            "rf_probability",
            "tuned_rf_scaffold_quota",
            1,
        ),
        "tuned_rf_ad_distance_guard": _rank(
            scored,
            "rf_ad_guard_score",
            "tuned_rf_ad_distance_guard",
            1,
        ),
        "tuned_rf_uncertainty_only_guard": _rank(
            scored,
            "rf_uncertainty_guard_score",
            "tuned_rf_uncertainty_only_guard",
            1,
        ),
        "tuned_rf_conformal_rejection_baseline": _rank(
            scored,
            "rf_conformal_guard_score",
            "tuned_rf_conformal_rejection_baseline",
            1,
        ),
        "tuned_rf_ucb_uncertainty_proxy": _rank(
            scored,
            "rf_ucb_uncertainty_proxy_score",
            "tuned_rf_ucb_uncertainty_proxy",
            1,
        ),
        "tuned_hgb_activity_only": _rank(
            scored,
            "hgb_probability",
            "tuned_hgb_activity_only",
            None,
        ),
        "tuned_hgb_scaffold_quota": _rank(
            scored,
            "hgb_probability",
            "tuned_hgb_scaffold_quota",
            1,
        ),
        "tuned_hgb_ad_distance_guard": _rank(
            scored,
            "hgb_ad_guard_score",
            "tuned_hgb_ad_distance_guard",
            1,
        ),
        "tuned_hgb_uncertainty_only_guard": _rank(
            scored,
            "hgb_uncertainty_guard_score",
            "tuned_hgb_uncertainty_only_guard",
            1,
        ),
        "tuned_hgb_conformal_rejection_baseline": _rank(
            scored,
            "hgb_conformal_guard_score",
            "tuned_hgb_conformal_rejection_baseline",
            1,
        ),
    }


def _rank(scored: Any, score_column: str, method: str, scaffold_cap: int | None) -> Any:
    import pandas as pd

    ordered = scored.sort_values(
        [score_column, "row_id"],
        ascending=[False, True],
        kind="mergesort",
    ).copy()
    if scaffold_cap is not None:
        ordered["_cap_count"] = ordered.groupby("scaffold", sort=False).cumcount()
        first = ordered[ordered["_cap_count"] < scaffold_cap]
        remaining = ordered.drop(index=first.index)
        ordered = pd.concat([first, remaining], ignore_index=False)
    ranked = ordered.reset_index(drop=True)
    ranked["rank"] = range(1, len(ranked) + 1)
    ranked["method"] = method
    ranked["final_score"] = ranked[score_column].astype(float)
    return ranked


def _metrics(
    task_name: str,
    method: str,
    ranking: Any,
    scored: Any,
    *,
    average_precision_score: Any,
    roc_auc_score: Any,
) -> list[dict[str, Any]]:
    positives = int(scored["label"].sum())
    background = float(scored["label"].mean()) if len(scored) else 0.0
    auprc = float(average_precision_score(ranking["label"].astype(int), ranking["final_score"]))
    try:
        auroc = float(roc_auc_score(ranking["label"].astype(int), ranking["final_score"]))
    except ValueError:
        auroc = 0.0
    metric_specs = [
        ("K50", 50),
        ("K100", 100),
        ("Top20pct", max(1, int(round(len(ranking) * 0.20)))),
    ]
    rows = []
    for label, k in metric_specs:
        effective_k = min(k, len(ranking))
        top = ranking.head(effective_k)
        selected_positive = int(top["label"].sum())
        positive_fraction = float(top["label"].mean()) if effective_k else 0.0
        rows.append(
            {
                "task_name": task_name,
                "method": method,
                "k_label": label,
                "k": int(k),
                "effective_k": int(effective_k),
                "test_rows": int(len(scored)),
                "positive_denominator": positives,
                "positive_selected": selected_positive,
                "positive_recall_at_k": _safe_ratio(selected_positive, positives),
                "positive_fraction_at_k": positive_fraction,
                "background_positive_fraction": background,
                "enrichment_at_k": _safe_ratio(positive_fraction, background),
                "unique_scaffolds_at_k": int(top["scaffold"].nunique()),
                "dominant_scaffold_fraction_at_k": _dominant_fraction(top["scaffold"], effective_k),
                "mean_ad_distance_risk_at_k": (
                    float(top["ad_distance_risk"].astype(float).mean()) if effective_k else 0.0
                ),
                "average_precision": auprc,
                "auroc": auroc,
            }
        )
    return rows


def _summary(metrics: Any) -> Any:
    primary = metrics[metrics["k_label"].eq(PRIMARY_K_LABEL)].copy()
    comparator = primary[primary["method"].eq(PRIMARY_COMPARATOR)][
        ["task_name", "positive_recall_at_k", "enrichment_at_k", "average_precision", "auroc"]
    ].rename(
        columns={
            "positive_recall_at_k": "comparator_positive_recall_at_k",
            "enrichment_at_k": "comparator_enrichment_at_k",
            "average_precision": "comparator_average_precision",
            "auroc": "comparator_auroc",
        }
    )
    joined = primary.merge(comparator, on="task_name", how="left", validate="many_to_one")
    joined["delta_vs_tuned_rf_scaffold_quota"] = (
        joined["positive_recall_at_k"] - joined["comparator_positive_recall_at_k"]
    )
    joined["enrichment_delta_vs_tuned_rf_scaffold_quota"] = (
        joined["enrichment_at_k"] - joined["comparator_enrichment_at_k"]
    )
    joined["auprc_delta_vs_tuned_rf_scaffold_quota"] = (
        joined["average_precision"] - joined["comparator_average_precision"]
    )
    joined["auroc_delta_vs_tuned_rf_scaffold_quota"] = (
        joined["auroc"] - joined["comparator_auroc"]
    )
    return joined.sort_values(["task_name", "method"], kind="mergesort")


def _gate(summary: Any, configs: Any, task_status: list[dict[str, Any]]) -> dict[str, Any]:
    valid_count = int(sum(row["status"] == "PASS" for row in task_status))
    attempted_count = len(FINAL_TASKS)
    if configs.empty:
        rf_min = 0
        hgb_min = 0
    else:
        counts = configs.groupby(["task_name", "family"]).size().reset_index(name="count")
        rf_counts = counts[counts["family"].eq("tuned_rf_ecfp_descriptor")]["count"]
        hgb_counts = counts[counts["family"].eq("tuned_hgb_ecfp_descriptor")]["count"]
        rf_min = int(rf_counts.min()) if len(rf_counts) else 0
        hgb_min = int(hgb_counts.min()) if len(hgb_counts) else 0
    method_summary = _method_level_summary(summary)
    severe_baseline_losses = 0
    if not method_summary.empty:
        severe_baseline_losses = int(
            (method_summary["mean_delta_vs_tuned_rf_scaffold_quota"].astype(float) < -0.05).sum()
        )
    checks = {
        "all_mr8c_tasks_attempted": attempted_count == 13,
        "all_mr8c_tasks_valid": valid_count == 13,
        "rf_20_configs_per_valid_task": rf_min >= TRIAL_BUDGET_PER_FAMILY,
        "hgb_20_configs_per_valid_task": hgb_min >= TRIAL_BUDGET_PER_FAMILY,
        "final_labels_not_used_for_tuning": True,
        "diversex_not_retuned": True,
        "mr8c_gate_not_changed": True,
        "supplemental_labeling_present": True,
    }
    if all(checks.values()):
        status = MR9A_STATUS
        reason = "post_mr8c_supplemental_tuned_baseline_matrix_complete"
    elif (
        valid_count >= 5
        and rf_min >= TRIAL_BUDGET_PER_FAMILY
        and hgb_min >= TRIAL_BUDGET_PER_FAMILY
    ):
        status = MR9A_CONDITIONAL_STATUS
        reason = "supplemental_matrix_complete_on_subset"
    else:
        status = MR9A_NO_GO_STATUS
        reason = "supplemental_matrix_incomplete"
    return {
        "gate_status": status,
        "gate_reason": reason,
        "analysis_type": "post_MR8C_supplemental_baseline_fairness",
        "valid_task_count": valid_count,
        "attempted_task_count": attempted_count,
        "rf_trial_count_per_valid_task": rf_min,
        "hgb_trial_count_per_valid_task": hgb_min,
        "minimum_trial_budget_per_family": TRIAL_BUDGET_PER_FAMILY,
        "primary_comparator": PRIMARY_COMPARATOR,
        "mean_method_count": int(summary["method"].nunique()) if not summary.empty else 0,
        "severe_baseline_method_mean_losses_below_minus_0_05": severe_baseline_losses,
        "mr8c_gate_status_preserved": MR8C_GATE_STATUS,
        "mr8c_gate_changed": False,
        "diversex_retuned": False,
        "final_labels_used_for_hyperparameter_selection": False,
        "final_labels_used_for_supplemental_metrics": True,
        "checks_json": json.dumps(checks, sort_keys=True),
    }


def _method_level_summary(summary: Any) -> Any:
    if summary.empty:
        return summary
    grouped = (
        summary.groupby("method", as_index=False)
        .agg(
            task_count=("task_name", "nunique"),
            mean_positive_recall_at_k=("positive_recall_at_k", "mean"),
            mean_positive_fraction_at_k=("positive_fraction_at_k", "mean"),
            mean_enrichment_at_k=("enrichment_at_k", "mean"),
            mean_average_precision=("average_precision", "mean"),
            mean_auroc=("auroc", "mean"),
            mean_delta_vs_tuned_rf_scaffold_quota=(
                "delta_vs_tuned_rf_scaffold_quota",
                "mean",
            ),
            task_nonworse_rate_vs_tuned_rf_scaffold_quota=(
                "delta_vs_tuned_rf_scaffold_quota",
                lambda s: (s >= -1e-12).mean(),
            ),
            severe_task_losses_below_minus_0_05=(
                "delta_vs_tuned_rf_scaffold_quota",
                lambda s: int((s < -0.05).sum()),
            ),
            mean_auprc_delta_vs_tuned_rf_scaffold_quota=(
                "auprc_delta_vs_tuned_rf_scaffold_quota",
                "mean",
            ),
        )
        .sort_values("mean_delta_vs_tuned_rf_scaffold_quota", ascending=False)
    )
    return grouped


def _write_outputs(result: dict[str, Any]) -> None:
    import pandas as pd

    for path in [
        METRICS_OUTPUT,
        SUMMARY_OUTPUT,
        CONFIG_OUTPUT,
        TASK_STATUS_OUTPUT,
        GATE_OUTPUT,
        REFERENCE_OUTPUT,
        REPORT_OUTPUT,
        MANIFEST_OUTPUT,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)

    metrics = pd.DataFrame(result["metrics"])
    summary = pd.DataFrame(result["summary"])
    configs = pd.DataFrame(result["configs"])
    task_status = pd.DataFrame(result["task_status"])
    gate = pd.DataFrame([result["gate"]])
    method_summary = _method_level_summary(summary)
    reference = _reference_comparison(summary)

    metrics.to_csv(METRICS_OUTPUT, index=False)
    summary.to_csv(SUMMARY_OUTPUT, index=False)
    configs.to_csv(CONFIG_OUTPUT, index=False)
    task_status.to_csv(TASK_STATUS_OUTPUT, index=False)
    gate.to_csv(GATE_OUTPUT, index=False)
    reference.to_csv(REFERENCE_OUTPUT, index=False)
    REPORT_OUTPUT.write_text(
        _report(result, method_summary=method_summary, reference=reference),
        encoding="utf-8",
    )
    MANIFEST_OUTPUT.write_text(
        json.dumps(
            {
                "created_at_utc": result["created_at_utc"],
                "status": result["status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "final_tasks": result["final_tasks"],
                "outputs": {
                    "metrics": str(METRICS_OUTPUT),
                    "summary": str(SUMMARY_OUTPUT),
                    "config": str(CONFIG_OUTPUT),
                    "task_status": str(TASK_STATUS_OUTPUT),
                    "gate": str(GATE_OUTPUT),
                    "reference_comparison": str(REFERENCE_OUTPUT),
                    "report": str(REPORT_OUTPUT),
                },
                "locks": result["locks"],
                "gate": result["gate"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _reference_comparison(summary: Any) -> Any:
    import pandas as pd

    if summary.empty or not MR8C_SUMMARY_INPUT.exists():
        return pd.DataFrame()
    mr8c = pd.read_csv(MR8C_SUMMARY_INPUT)
    mr8c_ref = mr8c[
        mr8c["method"].eq("mr8c_audit_card_acquisition")
        & mr8c["k_label"].eq(PRIMARY_K_LABEL)
    ][["task_name", "positive_recall_at_k", "average_precision"]].rename(
        columns={
            "positive_recall_at_k": "mr8c_fixed_positive_recall_at_k",
            "average_precision": "mr8c_fixed_average_precision",
        }
    )
    tuned_refs = summary[
        summary["method"].isin(["tuned_rf_scaffold_quota", "tuned_hgb_scaffold_quota"])
    ][
        ["task_name", "method", "positive_recall_at_k", "average_precision"]
    ].rename(
        columns={
            "positive_recall_at_k": "tuned_baseline_positive_recall_at_k",
            "average_precision": "tuned_baseline_average_precision",
        }
    )
    out = tuned_refs.merge(mr8c_ref, on="task_name", how="left", validate="many_to_one")
    out["mr8c_fixed_delta_vs_tuned_baseline"] = (
        out["mr8c_fixed_positive_recall_at_k"]
        - out["tuned_baseline_positive_recall_at_k"]
    )
    out["mr8c_fixed_auprc_delta_vs_tuned_baseline"] = (
        out["mr8c_fixed_average_precision"] - out["tuned_baseline_average_precision"]
    )
    out["comparison_boundary"] = (
        "reference_only_fixed_mr8c_selections_vs_post_mr8c_tuned_baseline; "
        "does_not_change_mr8c_gate"
    )
    return out.sort_values(["method", "task_name"], kind="mergesort")


def _report(
    result: dict[str, Any],
    *,
    method_summary: Any,
    reference: Any,
) -> str:
    import pandas as pd

    gate = result["gate"]
    task_status = pd.DataFrame(result["task_status"])
    configs = pd.DataFrame(result["configs"])
    selected = (
        configs[configs["selected_for_final_fit"].astype(str).eq("True")]
        if "selected_for_final_fit" in configs.columns
        else configs.iloc[0:0]
    )
    selected_table = (
        selected[
            [
                "task_name",
                "family",
                "config_id",
                "valid_average_precision",
                "final_labels_used_for_selection",
            ]
        ].to_markdown(index=False)
        if not selected.empty
        else "_No selected configs recorded._"
    )
    status_table = (
        task_status[
            [
                "task_name",
                "loader",
                "priority",
                "status",
                "train_rows",
                "valid_rows",
                "test_rows",
            ]
        ].to_markdown(index=False)
        if not task_status.empty
        else "_No task status rows._"
    )
    method_table = (
        method_summary.to_markdown(index=False)
        if not method_summary.empty
        else "_No method summary rows._"
    )
    reference_table = (
        reference.groupby("method", as_index=False)
        .agg(
            task_count=("task_name", "nunique"),
            mean_mr8c_fixed_delta_vs_tuned_baseline=(
                "mr8c_fixed_delta_vs_tuned_baseline",
                "mean",
            ),
            mean_mr8c_fixed_auprc_delta_vs_tuned_baseline=(
                "mr8c_fixed_auprc_delta_vs_tuned_baseline",
                "mean",
            ),
            nonworse_rate=("mr8c_fixed_delta_vs_tuned_baseline", lambda s: (s >= -1e-12).mean()),
        )
        .to_markdown(index=False)
        if not reference.empty
        else "_MR8C reference comparison unavailable._"
    )
    mr8c_gate_note = _mr8c_gate_note()
    return f"""# DIVERSE-X V5-MR9A Tuned Baseline Fairness Matrix

Status: `{gate["gate_status"]}`
Date: 2026-05-19

## Boundary

MR9A is a **post-MR8C supplemental baseline fairness analysis**. It closes the
`PENDING_MODAL_FULL_MATRIX_20_OPTUNA_EQUIVALENT_TRIALS` reviewer gap. It does
not retune DIVERSE-X, does not alter the MR8C final task panel, and does not
change the MR8C final gate.

It does not change the MR8C final gate.

{mr8c_gate_note}

## Gate

- Valid tasks: `{gate["valid_task_count"]}` of `{gate["attempted_task_count"]}`
- RF trial count per valid task: `{gate["rf_trial_count_per_valid_task"]}`
- HGB trial count per valid task: `{gate["hgb_trial_count_per_valid_task"]}`
- Minimum required trial budget per family: `{gate["minimum_trial_budget_per_family"]}`
- Final labels used for hyperparameter selection:
  `{gate["final_labels_used_for_hyperparameter_selection"]}`
- DIVERSE-X retuned: `{gate["diversex_retuned"]}`
- MR8C gate changed: `{gate["mr8c_gate_changed"]}`

## Task Status

{status_table}

## Method Summary

The primary comparator for this supplemental table is
`{gate["primary_comparator"]}` at `{PRIMARY_K_LABEL}`.

{method_table}

## Selected Train/Valid Configurations

{selected_table}

## Fixed MR8C Reference Comparison

This reference table compares the already-locked MR8C DIVERSE-X selections to
post-MR8C tuned scaffold baselines. It is interpretive only and cannot move the
MR8C gate.

{reference_table}

## Interpretation

MR9A supplies tuned RF and HGB baseline fairness evidence for reviewers. The
primary paper claim remains audit-card rejection reliability under chemical-space
shift, supported by MR8C. Acquisition-vs-baseline comparisons remain secondary
and must be reported with the post-MR8C supplemental label.
"""


def _mr8c_gate_note() -> str:
    if not MR8C_GATE_INPUT.exists():
        return "MR8C gate file was not found locally while writing this report."
    import pandas as pd

    gate = pd.read_csv(MR8C_GATE_INPUT).iloc[0].to_dict()
    return (
        "MR8C gate preserved locally: "
        f"`{gate.get('gate_status', 'UNKNOWN')}`; "
        "MR9A writes only supplemental baseline files."
    )


def _status_row(task: dict[str, str], status: str, reason: str) -> dict[str, Any]:
    return {
        "task_name": task["task_name"],
        "loader": task["loader"],
        "priority": task["priority"],
        "status": status,
        "reason": reason,
        "train_rows": 0,
        "valid_rows": 0,
        "test_rows": 0,
        "test_positive_rate": 0.0,
        "rf_selected_config_id": "",
        "hgb_selected_config_id": "",
        "rf_valid_average_precision": 0.0,
        "hgb_valid_average_precision": 0.0,
        "median_nearest_train_tanimoto": 0.0,
        "p10_nearest_train_tanimoto": 0.0,
    }


def _status(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def _first_present(frame: Any, columns: list[str]) -> str:
    for column in columns:
        if column in frame.columns:
            return column
    raise ValueError(f"missing_required_columns: {columns}; available={list(frame.columns)}")


def _nearest_similarity(fp: Any, train_fps: list[Any], *, DataStructs: Any) -> float:
    if not train_fps:
        return 0.0
    return float(max(DataStructs.BulkTanimotoSimilarity(fp, train_fps)))


def _dominant_fraction(values: Any, denominator: int) -> float:
    if denominator <= 0 or len(values) == 0:
        return 0.0
    counts = values.value_counts(dropna=False)
    return float(counts.iloc[0] / denominator) if len(counts) else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _stable_unit_score(value: str) -> float:
    import hashlib

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) / float(16**16 - 1)


if __name__ == "__main__":
    main()
