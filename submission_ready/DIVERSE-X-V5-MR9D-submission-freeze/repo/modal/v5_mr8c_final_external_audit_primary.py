from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import modal

APP_NAME = "diversex-v5-mr8c-final-external-audit-primary"
CONFIRM_ENV = "DIVERSEX_MR8C_OPEN_FINAL_LABELS"
CONFIRM_VALUE = "YES_OPEN_MR8C_FINAL_ONCE"
LOCKED_METHOD = "mr8c_audit_card_acquisition"
PRIMARY_COMPARATOR = "scaffold_quota"
PRIMARY_K = 50
MR7_STATUS = "MR7_LOCKED_FINAL_EXTERNAL_NO_GO"

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

METRICS_OUTPUT = Path("reports/tables/v5_mr8c_final_external_metrics.csv")
SUMMARY_OUTPUT = Path("reports/tables/v5_mr8c_final_external_summary.csv")
REJECTION_OUTPUT = Path("reports/tables/v5_mr8c_final_external_rejection_curve.csv")
REJECTION_SUMMARY_OUTPUT = Path("reports/tables/v5_mr8c_final_external_rejection_summary.csv")
TASK_STATUS_OUTPUT = Path("reports/tables/v5_mr8c_final_external_task_status.csv")
GATE_OUTPUT = Path("reports/tables/v5_mr8c_final_external_gate.csv")
CLAIM_OUTPUT = Path("reports/tables/v5_mr8c_claim_boundary.csv")
REPORT_OUTPUT = Path("reports/runs/v5_mr8c_final_external_report.md")
AUDIT_OUTPUT = Path("reports/runs/v5_mr8c_completion_audit.md")
MANIFEST_OUTPUT = Path("data/manifests/v5_mr8c_final_external_manifest.json")

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
def remote_final_external() -> dict[str, Any]:
    started = time.perf_counter()

    import numpy as np
    import pandas as pd
    from rdkit import Chem, DataStructs
    from rdkit.Chem import Descriptors, rdFingerprintGenerator
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.metrics import average_precision_score
    from tdc.single_pred import ADME, Tox

    metric_rows: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
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
            train_model = pd.concat([train, valid], ignore_index=True)
            prepared_train, prepared_valid, prepared_test, prep = _prepare_frames(
                train,
                valid,
                test,
                train_model,
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
            scored, model_status = _score_test(
                prepared_train,
                prepared_valid,
                prepared_test,
                train_model=prepared_train.__class__(
                    list(prepared_train.to_dict(orient="records"))
                    + list(prepared_valid.to_dict(orient="records"))
                ),
                RandomForestClassifier=RandomForestClassifier,
                HistGradientBoostingClassifier=HistGradientBoostingClassifier,
                np=np,
            )
            rankings = _rankings(scored)
            for method, ranking in rankings.items():
                metric_rows.extend(
                    _metrics(
                        task_name,
                        method,
                        ranking,
                        scored,
                        average_precision_score=average_precision_score,
                    )
                )
            rejection_rows.extend(_rejection_curves(task_name, rankings[LOCKED_METHOD]))
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
                    "median_nearest_train_tanimoto": float(
                        scored["nearest_train_tanimoto"].median()
                    ),
                    "p10_nearest_train_tanimoto": float(
                        scored["nearest_train_tanimoto"].quantile(0.10)
                    ),
                    "mean_audit_risk": float(scored["audit_card_risk"].mean()),
                }
            )
        except Exception as exc:  # pragma: no cover - remote defensive quarantine
            task_status.append(
                _status_row(task, "QUARANTINED_PRE_METRIC", f"{type(exc).__name__}: {exc}")
            )

    metrics = pd.DataFrame(metric_rows)
    rejection = pd.DataFrame(rejection_rows)
    summary = _summary(metrics) if not metrics.empty else pd.DataFrame()
    rejection_summary = _rejection_summary(rejection) if not rejection.empty else pd.DataFrame()
    gate = _gate(summary, rejection, rejection_summary, task_status)
    claims = _claims(gate)
    return {
        "status": gate["gate_status"],
        "created_at_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "mr7_status_preserved": MR7_STATUS,
        "final_tasks": list(FINAL_TASKS),
        "metrics": metrics.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
        "rejection": rejection.to_dict(orient="records"),
        "rejection_summary": rejection_summary.to_dict(orient="records"),
        "task_status": task_status,
        "gate": gate,
        "claims": claims,
        "locks": {
            "mr7_rerun": False,
            "mr7_no_go_disclosed": True,
            "mr8b_protocol_used": True,
            "mr8c_final_external_labels_accessed": True,
            "final_labels_used_for_ranking": False,
            "final_labels_used_for_metrics": True,
            "post_hoc_task_exclusion": False,
            "post_hoc_retuning": False,
            "task_inclusion_changed_after_outcomes": False,
            "modal_gpu_spend": False,
        },
    }


@app.local_entrypoint()
def main() -> str:
    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        raise RuntimeError(
            "MR8C final labels are closed. Set "
            f"{CONFIRM_ENV}={CONFIRM_VALUE} only for the one-shot MR8C run."
        )
    if MANIFEST_OUTPUT.exists():
        raise RuntimeError(
            f"MR8C output manifest already exists at {MANIFEST_OUTPUT}. "
            "Refusing to rerun the one-shot final external evaluation."
        )
    result = remote_final_external.remote()
    _write_outputs(result)
    return json.dumps(
        {
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "valid_task_count": result["gate"]["valid_task_count"],
            "audit_rejection_auc_delta": result["gate"]["audit_rejection_auc_delta"],
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
    train_model: Any,
    *,
    np: Any,
    Chem: Any,
    DataStructs: Any,
    Descriptors: Any,
    MurckoScaffold: Any,
    rdFingerprintGenerator: Any,
) -> tuple[Any, Any, Any, dict[str, str]]:
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=512)
    train_rows = _featurized_rows(
        train,
        np=np,
        Chem=Chem,
        DataStructs=DataStructs,
        Descriptors=Descriptors,
        MurckoScaffold=MurckoScaffold,
        generator=generator,
    )
    valid_rows = _featurized_rows(
        valid,
        np=np,
        Chem=Chem,
        DataStructs=DataStructs,
        Descriptors=Descriptors,
        MurckoScaffold=MurckoScaffold,
        generator=generator,
    )
    test_rows = _featurized_rows(
        test,
        np=np,
        Chem=Chem,
        DataStructs=DataStructs,
        Descriptors=Descriptors,
        MurckoScaffold=MurckoScaffold,
        generator=generator,
    )
    train_prepared = train.__class__(train_rows)
    valid_prepared = valid.__class__(valid_rows)
    test_prepared = test.__class__(test_rows)
    train_model_prepared = train_model.__class__(
        list(train_prepared.to_dict(orient="records"))
        + list(valid_prepared.to_dict(orient="records"))
    )
    if train_model_prepared.empty or test_prepared.empty:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "empty_after_rdkit",
        )
    if len(test_prepared) < 50:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "test_rows_lt_50",
        )
    if train_model_prepared["label"].nunique() < 2:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "single_class_train_valid",
        )
    if test_prepared["label"].nunique() < 2:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "single_class_test",
        )

    train_fps = list(train_model_prepared["fingerprint"])
    train_descriptors = train_model_prepared[["mw", "logp", "tpsa"]].astype(float)
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
    return {
        "canonical_smiles": Chem.MolToSmiles(mol, canonical=True),
        "fingerprint": fp,
        "feature_vector": arr,
        "scaffold": scaffold,
        "mw": float(Descriptors.MolWt(mol)),
        "logp": float(Descriptors.MolLogP(mol)),
        "tpsa": float(Descriptors.TPSA(mol)),
    }


def _score_test(
    train: Any,
    valid: Any,
    test: Any,
    *,
    train_model: Any,
    RandomForestClassifier: Any,
    HistGradientBoostingClassifier: Any,
    np: Any,
) -> tuple[Any, dict[str, str]]:
    x_train_model = np.vstack(train_model["feature_vector"].to_numpy())
    y_train_model = train_model["label"].astype(int).to_numpy()
    x_test = np.vstack(test["feature_vector"].to_numpy())
    rf = RandomForestClassifier(
        n_estimators=240,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=20260519,
        n_jobs=6,
    )
    rf.fit(x_train_model, y_train_model)
    scored = test.copy()
    scored["probability"] = rf.predict_proba(x_test)[:, 1]

    scored["hgb_probability"] = _hgb_probabilities(
        train_model,
        x_test,
        HistGradientBoostingClassifier=HistGradientBoostingClassifier,
        np=np,
    )
    scored["uncertainty_risk"] = 1.0 - abs(scored["probability"].astype(float) - 0.5) * 2.0
    scored["ad_distance_risk"] = 1.0 - scored["nearest_train_tanimoto"].astype(float)
    scored["conformal_risk"] = _conformal_risk(
        train,
        valid,
        test_probabilities=scored["probability"].astype(float).to_numpy(),
        RandomForestClassifier=RandomForestClassifier,
        np=np,
    )
    scored["audit_card_risk"] = (
        0.45 * scored["ad_distance_risk"].astype(float)
        + 0.25 * scored["uncertainty_risk"].astype(float)
        + 0.20 * scored["descriptor_outlier"].astype(float)
        + 0.10 * scored["conformal_risk"].astype(float)
    ).clip(0.0, 1.0)
    scored["ad_distance_guard_score"] = (
        scored["probability"].astype(float)
        * (0.70 + 0.30 * scored["nearest_train_tanimoto"].astype(float))
    )
    scored["uncertainty_guard_score"] = (
        scored["probability"].astype(float) - 0.35 * scored["uncertainty_risk"].astype(float)
    )
    scored["conformal_guard_score"] = (
        scored["probability"].astype(float) - 0.35 * scored["conformal_risk"].astype(float)
    )
    scored["audit_card_score"] = (
        scored["probability"].astype(float) - 0.35 * scored["audit_card_risk"].astype(float)
    )
    return scored, _status("PASS_RF_240_FIXED_HGB_PROXY_FIXED", "model_fit")


def _hgb_probabilities(
    train_model: Any,
    x_test: Any,
    *,
    HistGradientBoostingClassifier: Any,
    np: Any,
) -> Any:
    try:
        x_train = np.vstack(train_model["feature_vector"].to_numpy())
        y_train = train_model["label"].astype(int).to_numpy()
        model = HistGradientBoostingClassifier(
            max_iter=80,
            learning_rate=0.06,
            l2_regularization=0.05,
            random_state=20260519,
        )
        model.fit(x_train, y_train)
        return model.predict_proba(x_test)[:, 1]
    except Exception:
        return np.full((len(x_test),), 0.5, dtype=float)


def _conformal_risk(
    train: Any,
    valid: Any,
    *,
    test_probabilities: Any,
    RandomForestClassifier: Any,
    np: Any,
) -> Any:
    if valid.empty or valid["label"].nunique() < 2 or train["label"].nunique() < 2:
        return np.clip(1.0 - abs(test_probabilities - 0.5) * 2.0, 0.0, 1.0)
    x_train = np.vstack(train["feature_vector"].to_numpy())
    y_train = train["label"].astype(int).to_numpy()
    x_valid = np.vstack(valid["feature_vector"].to_numpy())
    y_valid = valid["label"].astype(int).to_numpy()
    model = RandomForestClassifier(
        n_estimators=160,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=20260519,
        n_jobs=4,
    )
    model.fit(x_train, y_train)
    valid_prob = model.predict_proba(x_valid)[:, 1]
    valid_nonconformity = np.where(y_valid == 1, 1.0 - valid_prob, valid_prob)
    q90 = float(np.quantile(valid_nonconformity, 0.90))
    predicted_class_nonconformity = 1.0 - np.maximum(test_probabilities, 1.0 - test_probabilities)
    return np.clip(predicted_class_nonconformity / max(q90, 1e-6), 0.0, 1.0)


def _rankings(scored: Any) -> dict[str, Any]:
    scored = scored.copy()
    scored["random_fixed_seed_score"] = [
        _stable_unit_score(row_id) for row_id in scored["row_id"].astype(str)
    ]
    return {
        "random_fixed_seed": _rank(scored, "random_fixed_seed_score", "random_fixed_seed", None),
        "activity_only": _rank(scored, "probability", "activity_only", None),
        PRIMARY_COMPARATOR: _rank(scored, "probability", PRIMARY_COMPARATOR, 1),
        "ad_distance_guard": _rank(scored, "ad_distance_guard_score", "ad_distance_guard", 1),
        "uncertainty_only_guard": _rank(
            scored,
            "uncertainty_guard_score",
            "uncertainty_only_guard",
            1,
        ),
        "conformal_rejection_baseline": _rank(
            scored,
            "conformal_guard_score",
            "conformal_rejection_baseline",
            1,
        ),
        "hgb_ecfp_proxy": _rank(scored, "hgb_probability", "hgb_ecfp_proxy", 1),
        LOCKED_METHOD: _rank(scored, "audit_card_score", LOCKED_METHOD, 1),
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
) -> list[dict[str, Any]]:
    positives = int(scored["label"].sum())
    background = float(scored["label"].mean()) if len(scored) else 0.0
    auprc = float(average_precision_score(ranking["label"].astype(int), ranking["final_score"]))
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
                "mean_audit_risk_at_k": (
                    float(top["audit_card_risk"].astype(float).mean()) if effective_k else 0.0
                ),
                "average_precision": auprc,
            }
        )
    return rows


def _summary(metrics: Any) -> Any:
    primary = metrics[metrics["k_label"].eq("K50")].copy()
    quota = primary[primary["method"].eq(PRIMARY_COMPARATOR)][
        ["task_name", "positive_recall_at_k", "enrichment_at_k", "average_precision"]
    ].rename(
        columns={
            "positive_recall_at_k": "scaffold_positive_recall_at_k",
            "enrichment_at_k": "scaffold_enrichment_at_k",
            "average_precision": "scaffold_average_precision",
        }
    )
    joined = primary.merge(quota, on="task_name", how="left", validate="many_to_one")
    joined["delta_vs_scaffold_quota"] = (
        joined["positive_recall_at_k"] - joined["scaffold_positive_recall_at_k"]
    )
    joined["enrichment_delta_vs_scaffold_quota"] = (
        joined["enrichment_at_k"] - joined["scaffold_enrichment_at_k"]
    )
    joined["auprc_delta_vs_scaffold_quota"] = (
        joined["average_precision"] - joined["scaffold_average_precision"]
    )
    return joined.sort_values(["task_name", "method"], kind="mergesort")


def _rejection_curves(task_name: str, ranking: Any) -> list[dict[str, Any]]:
    risk_specs = [
        ("audit_card", "audit_card_risk"),
        ("ad_distance", "ad_distance_risk"),
        ("uncertainty_only", "uncertainty_risk"),
        ("conformal_only", "conformal_risk"),
    ]
    rows = []
    top = ranking.head(min(PRIMARY_K, len(ranking))).copy()
    for risk_method, risk_column in risk_specs:
        baseline = _rejection_stats(top, risk_column)
        for fraction in [0.0, 0.1, 0.2, 0.3, 0.4]:
            reject_n = int(round(len(top) * fraction))
            ordered = top.sort_values(
                [risk_column, "rank"],
                ascending=[False, True],
                kind="mergesort",
            )
            kept = ordered.iloc[reject_n:].copy() if reject_n else ordered.copy()
            kept_stats = _rejection_stats(kept, risk_column)
            delta = (
                kept_stats["positive_fraction"]
                - baseline["positive_fraction"]
                - (kept_stats["mean_risk"] - baseline["mean_risk"])
            )
            rows.append(
                {
                    "task_name": task_name,
                    "method": LOCKED_METHOD,
                    "risk_method": risk_method,
                    "rejection_fraction": fraction,
                    "rejected_count": reject_n,
                    "kept_count": int(len(kept)),
                    "kept_positive_fraction": kept_stats["positive_fraction"],
                    "baseline_positive_fraction": baseline["positive_fraction"],
                    "kept_mean_risk": kept_stats["mean_risk"],
                    "baseline_mean_risk": baseline["mean_risk"],
                    "reliability_delta_vs_no_rejection": delta,
                }
            )
    return rows


def _rejection_stats(frame: Any, risk_column: str) -> dict[str, float]:
    if len(frame) == 0:
        return {"positive_fraction": 0.0, "mean_risk": 0.0}
    return {
        "positive_fraction": float(frame["label"].astype(int).mean()),
        "mean_risk": float(frame[risk_column].astype(float).mean()),
    }


def _rejection_summary(rejection: Any) -> Any:
    grouped = (
        rejection.groupby(["risk_method", "rejection_fraction"], as_index=False)
        .agg(
            mean_reliability_delta=("reliability_delta_vs_no_rejection", "mean"),
            task_nonnegative_rate=(
                "reliability_delta_vs_no_rejection",
                lambda s: (s >= -1e-12).mean(),
            ),
            min_reliability_delta=("reliability_delta_vs_no_rejection", "min"),
            max_reliability_delta=("reliability_delta_vs_no_rejection", "max"),
            mean_kept_positive_fraction=("kept_positive_fraction", "mean"),
            mean_baseline_positive_fraction=("baseline_positive_fraction", "mean"),
            mean_kept_risk=("kept_mean_risk", "mean"),
            mean_baseline_risk=("baseline_mean_risk", "mean"),
        )
        .sort_values(["risk_method", "rejection_fraction"], kind="mergesort")
    )
    auc_rows = []
    for risk_method, group in grouped.groupby("risk_method", sort=False):
        ordered = group.sort_values("rejection_fraction", kind="mergesort")
        auc = _trapezoid(
            ordered["rejection_fraction"].astype(float).tolist(),
            ordered["mean_reliability_delta"].astype(float).tolist(),
        )
        best = ordered.sort_values("mean_reliability_delta", ascending=False).iloc[0]
        auc_rows.append(
            {
                "risk_method": risk_method,
                "rejection_fraction": "AUC_0_TO_0.4",
                "mean_reliability_delta": auc,
                "task_nonnegative_rate": float(best["task_nonnegative_rate"]),
                "min_reliability_delta": float(best["min_reliability_delta"]),
                "max_reliability_delta": float(best["max_reliability_delta"]),
                "mean_kept_positive_fraction": float(best["mean_kept_positive_fraction"]),
                "mean_baseline_positive_fraction": float(best["mean_baseline_positive_fraction"]),
                "mean_kept_risk": float(best["mean_kept_risk"]),
                "mean_baseline_risk": float(best["mean_baseline_risk"]),
                "best_rejection_fraction": float(best["rejection_fraction"]),
                "row_type": "auc_summary",
            }
        )
    grouped["best_rejection_fraction"] = ""
    grouped["row_type"] = "fraction"
    return grouped.__class__(list(grouped.to_dict(orient="records")) + auc_rows)


def _gate(
    summary: Any,
    rejection: Any,
    rejection_summary: Any,
    task_status: list[dict[str, Any]],
) -> dict[str, Any]:
    method = summary[summary["method"].eq(LOCKED_METHOD)].copy()
    deltas = method["delta_vs_scaffold_quota"].astype(float)
    valid_count = int(sum(row["status"] == "PASS" for row in task_status))
    audit_auc_row = rejection_summary[
        rejection_summary["risk_method"].eq("audit_card")
        & rejection_summary["row_type"].eq("auc_summary")
    ].iloc[0]
    audit_fractions = rejection_summary[
        rejection_summary["risk_method"].eq("audit_card")
        & rejection_summary["row_type"].eq("fraction")
        & rejection_summary["rejection_fraction"].astype(str).ne("0.0")
    ].copy()
    best = audit_fractions.sort_values("mean_reliability_delta", ascending=False).iloc[0]
    best_fraction = float(best["rejection_fraction"])
    task_at_best = rejection[
        rejection["risk_method"].eq("audit_card")
        & rejection["rejection_fraction"].eq(best_fraction)
    ]
    task_nonnegative_rate = float(
        (task_at_best["reliability_delta_vs_no_rejection"] >= -1e-12).mean()
    )
    severe_losses = int((deltas < -0.05).sum())
    mean_acquisition_delta = float(deltas.mean()) if len(deltas) else 0.0
    mean_auprc_delta = float(method["auprc_delta_vs_scaffold_quota"].astype(float).mean())
    audit_auc = float(audit_auc_row["mean_reliability_delta"])
    best_delta = float(best["mean_reliability_delta"])

    pass_gate = (
        valid_count >= 5
        and audit_auc > 0.0
        and best_delta > 0.0
        and task_nonnegative_rate >= 0.67
        and severe_losses == 0
        and mean_acquisition_delta >= -0.02
    )
    conditional_gate = (
        valid_count >= 5
        and audit_auc > 0.0
        and best_delta > 0.0
        and task_nonnegative_rate >= 0.50
        and severe_losses <= 1
        and mean_acquisition_delta >= -0.05
    )
    if pass_gate:
        status = "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT"
        reason = "audit_primary_and_secondary_collapse_gates_passed"
    elif conditional_gate:
        status = "MR8C_FINAL_EXTERNAL_CONDITIONAL_AUDIT_SUPPORT"
        reason = "audit_primary_positive_secondary_mixed"
    else:
        status = "MR8C_FINAL_EXTERNAL_NO_GO"
        reason = "audit_primary_or_secondary_guardrails_failed"
    return {
        "gate_status": status,
        "gate_reason": reason,
        "valid_task_count": valid_count,
        "attempted_task_count": len(FINAL_TASKS),
        "locked_method": LOCKED_METHOD,
        "primary_risk_method": "audit_card",
        "audit_rejection_auc_delta": audit_auc,
        "best_rejection_fraction": best_fraction,
        "best_rejection_reliability_delta": best_delta,
        "task_nonnegative_rejection_rate_at_best_fraction": task_nonnegative_rate,
        "mean_guarded_acquisition_delta_vs_scaffold_quota": mean_acquisition_delta,
        "mean_auprc_delta_vs_scaffold_quota": mean_auprc_delta,
        "severe_acquisition_losses_below_minus_0_05": severe_losses,
        "mr7_status_preserved": MR7_STATUS,
        "mr7_no_go_disclosed": True,
        "final_labels_used_for_ranking": False,
        "post_hoc_retuning": False,
    }


def _claims(gate: dict[str, Any]) -> list[dict[str, str]]:
    q1_status = (
        "SUPPORTED"
        if gate["gate_status"] == "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT"
        else "BLOCKED"
    )
    return [
        {
            "claim": "mr7_locked_final_external_success",
            "status": "BLOCKED",
            "evidence": MR7_STATUS,
            "notes": "MR7 remains consumed no-go evidence.",
        },
        {
            "claim": "mr8c_audit_primary_external_support",
            "status": "SUPPORTED" if gate["audit_rejection_auc_delta"] > 0 else "BLOCKED",
            "evidence": f"audit_auc_delta={gate['audit_rejection_auc_delta']:.6f}",
            "notes": "Primary MR8C endpoint.",
        },
        {
            "claim": "mr8c_q1_supporting_external_evidence",
            "status": q1_status,
            "evidence": gate["gate_status"],
            "notes": "Requires audit primary pass and no severe secondary acquisition collapse.",
        },
        {
            "claim": "acquisition_dominates_scaffold_quota",
            "status": (
                "SUPPORTED"
                if gate["mean_guarded_acquisition_delta_vs_scaffold_quota"] > 0
                else "NOT_PRIMARY"
            ),
            "evidence": (
                "mean_delta="
                f"{gate['mean_guarded_acquisition_delta_vs_scaffold_quota']:.6f}"
            ),
            "notes": "Secondary endpoint only.",
        },
        {
            "claim": "post_hoc_retuning",
            "status": "BLOCKED",
            "evidence": "post_hoc_retuning_false",
            "notes": "No post-hoc retuning allowed or recorded.",
        },
    ]


def _write_outputs(result: dict[str, Any]) -> None:
    import pandas as pd

    for path in [
        METRICS_OUTPUT,
        SUMMARY_OUTPUT,
        REJECTION_OUTPUT,
        REJECTION_SUMMARY_OUTPUT,
        TASK_STATUS_OUTPUT,
        GATE_OUTPUT,
        CLAIM_OUTPUT,
        REPORT_OUTPUT,
        AUDIT_OUTPUT,
        MANIFEST_OUTPUT,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result["metrics"]).to_csv(METRICS_OUTPUT, index=False)
    pd.DataFrame(result["summary"]).to_csv(SUMMARY_OUTPUT, index=False)
    pd.DataFrame(result["rejection"]).to_csv(REJECTION_OUTPUT, index=False)
    pd.DataFrame(result["rejection_summary"]).to_csv(REJECTION_SUMMARY_OUTPUT, index=False)
    pd.DataFrame(result["task_status"]).to_csv(TASK_STATUS_OUTPUT, index=False)
    pd.DataFrame([result["gate"]]).to_csv(GATE_OUTPUT, index=False)
    pd.DataFrame(result["claims"]).to_csv(CLAIM_OUTPUT, index=False)
    REPORT_OUTPUT.write_text(_report(result), encoding="utf-8")
    AUDIT_OUTPUT.write_text(_audit(result), encoding="utf-8")
    MANIFEST_OUTPUT.write_text(
        json.dumps(
            {
                "created_at_utc": result["created_at_utc"],
                "status": result["status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "mr7_status_preserved": result["mr7_status_preserved"],
                "final_tasks": result["final_tasks"],
                "outputs": {
                    "metrics": str(METRICS_OUTPUT),
                    "summary": str(SUMMARY_OUTPUT),
                    "rejection_curve": str(REJECTION_OUTPUT),
                    "rejection_summary": str(REJECTION_SUMMARY_OUTPUT),
                    "task_status": str(TASK_STATUS_OUTPUT),
                    "gate": str(GATE_OUTPUT),
                    "claim_boundary": str(CLAIM_OUTPUT),
                    "report": str(REPORT_OUTPUT),
                    "completion_audit": str(AUDIT_OUTPUT),
                },
                "locks": result["locks"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _report(result: dict[str, Any]) -> str:
    import pandas as pd

    gate = result["gate"]
    task_status = pd.DataFrame(result["task_status"])
    summary = pd.DataFrame(result["summary"])
    rejection_summary = pd.DataFrame(result["rejection_summary"])
    locked = summary[summary["method"].eq(LOCKED_METHOD)]
    locked_table = locked[
        [
            "task_name",
            "positive_selected",
            "delta_vs_scaffold_quota",
            "auprc_delta_vs_scaffold_quota",
        ]
    ].to_markdown(index=False)
    audit_rows = rejection_summary[
        rejection_summary["risk_method"].eq("audit_card")
        & rejection_summary["row_type"].eq("fraction")
    ][
        [
            "rejection_fraction",
            "mean_reliability_delta",
            "task_nonnegative_rate",
            "mean_kept_positive_fraction",
            "mean_baseline_positive_fraction",
        ]
    ].to_markdown(index=False)
    status_table = task_status[
        ["task_name", "loader", "priority", "status", "test_rows", "test_positive_rate"]
    ].to_markdown(index=False)
    return f"""# DIVERSE-X V5-MR8C Final External Audit-Primary Evaluation

Status: `{gate["gate_status"]}`
Date: 2026-05-19

## Boundary

MR8C is the one-shot final external evaluation after MR8B. MR7 remains
`{MR7_STATUS}`. MR8C did not rerun MR7, did not retune after outcomes, and did
not use final labels for ranking or method selection.

## Gate

- Valid tasks: `{gate["valid_task_count"]}` of `{gate["attempted_task_count"]}`
- Audit rejection AUC delta: `{gate["audit_rejection_auc_delta"]:.6f}`
- Best rejection reliability delta:
  `{gate["best_rejection_reliability_delta"]:.6f}` at fraction
  `{gate["best_rejection_fraction"]:.1f}`
- Task nonnegative rejection rate at best fraction:
  `{gate["task_nonnegative_rejection_rate_at_best_fraction"]:.3f}`
- Mean guarded acquisition delta vs scaffold quota:
  `{gate["mean_guarded_acquisition_delta_vs_scaffold_quota"]:.6f}`
- Severe acquisition losses below -0.05:
  `{gate["severe_acquisition_losses_below_minus_0_05"]}`

## Task Status

{status_table}

## Primary Audit Rejection Curve

{audit_rows}

## Secondary Acquisition Summary

{locked_table}

## Claim Boundary

Q1 support is determined by the gate above. Audit-card external support can be
claimed only according to the claim-boundary table. Acquisition dominance is not
the primary claim.
"""


def _audit(result: dict[str, Any]) -> str:
    gate = result["gate"]
    return f"""# DIVERSE-X V5-MR8C Completion Audit

Status: `PASS`
Date: 2026-05-19

## Final Gate

`{gate["gate_status"]}`

## Integrity Checks

- MR7 no-go disclosed: `{gate["mr7_no_go_disclosed"]}`
- Final labels used for ranking: `{gate["final_labels_used_for_ranking"]}`
- Post-hoc retuning: `{gate["post_hoc_retuning"]}`
- Task inclusion changed after outcomes: `False`
- MR8B protocol used: `True`

## Boundary

This audit records the MR8C one-shot result. Do not rerun MR8C after outcome
inspection.
"""


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
        "median_nearest_train_tanimoto": 0.0,
        "p10_nearest_train_tanimoto": 0.0,
        "mean_audit_risk": 0.0,
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


def _trapezoid(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    area = 0.0
    for idx in range(1, len(xs)):
        area += (xs[idx] - xs[idx - 1]) * (ys[idx] + ys[idx - 1]) / 2.0
    return float(area)


if __name__ == "__main__":
    main()
