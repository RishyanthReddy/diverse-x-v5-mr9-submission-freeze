from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import modal

APP_NAME = "diversex-v5-mr9b-figure-molecule-examples"
CONFIRM_ENV = "DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE"
CONFIRM_VALUE = "YES_EXTRACT_FIGURE_EXAMPLES"
OVERWRITE_ENV = "DIVERSEX_MR9B_ALLOW_OVERWRITE"
OVERWRITE_VALUE = "YES_OVERWRITE_MR9B"
STATUS = "MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED"
LOCKED_METHOD = "mr8c_audit_card_acquisition"
PRIMARY_COMPARATOR = "scaffold_quota"

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

EXAMPLES_OUTPUT = Path("reports/tables/v5_mr9b_figure_molecule_examples.csv")
CANDIDATE_OUTPUT = Path("reports/tables/v5_mr9b_candidate_audit_pool.csv")
TASK_STATUS_OUTPUT = Path("reports/tables/v5_mr9b_task_status.csv")
REPORT_OUTPUT = Path("reports/runs/v5_mr9b_figure_molecule_examples.md")
MANIFEST_OUTPUT = Path("data/manifests/v5_mr9b_figure_molecule_examples_manifest.json")
FIGURE_DIR = Path("reports/figures/mr9b_molecule_examples")
MR8C_GATE_INPUT = Path("reports/tables/v5_mr8c_final_external_gate.csv")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libxrender1", "libxext6")
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
def remote_extract_examples() -> dict[str, Any]:
    started = time.perf_counter()

    import numpy as np
    import pandas as pd
    from rdkit import Chem, DataStructs
    from rdkit.Chem import Descriptors, Draw, rdFingerprintGenerator
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from tdc.single_pred import ADME, Tox

    candidate_rows: list[dict[str, Any]] = []
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
                train_model=pd.concat([train, valid], ignore_index=True),
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
            train_model = prepared_train.__class__(
                list(prepared_train.to_dict(orient="records"))
                + list(prepared_valid.to_dict(orient="records"))
            )
            scored, model_status = _score_test(
                prepared_train,
                prepared_valid,
                prepared_test,
                train_model=train_model,
                RandomForestClassifier=RandomForestClassifier,
                HistGradientBoostingClassifier=HistGradientBoostingClassifier,
                np=np,
            )
            ranked = _candidate_pool(scored)
            candidate_rows.extend(ranked.to_dict(orient="records"))
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
                }
            )
        except Exception as exc:  # pragma: no cover - remote defensive quarantine
            task_status.append(
                _status_row(task, "QUARANTINED_PRE_METRIC", f"{type(exc).__name__}: {exc}")
            )

    candidates = pd.DataFrame(candidate_rows)
    examples = _select_examples(candidates)
    examples = _add_svg(examples, Chem=Chem, Draw=Draw)
    gate = _gate(examples, candidates, task_status)
    return {
        "status": gate["gate_status"],
        "created_at_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "candidate_pool": candidates.to_dict(orient="records"),
        "examples": examples.to_dict(orient="records"),
        "task_status": task_status,
        "gate": gate,
        "locks": {
            "analysis_type": "post_MR8C_illustrative_exemplar_extraction",
            "new_claim_gate": False,
            "mr8c_gate_changed": False,
            "mr8c_recomputed_as_gate": False,
            "diversex_retuned": False,
            "final_labels_used_for_ranking": False,
            "final_labels_used_for_illustrative_selection": True,
            "selection_role": "figure_examples_only",
            "post_hoc_retuning": False,
            "modal_gpu_spend": False,
        },
    }


@app.local_entrypoint()
def main() -> str:
    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        raise RuntimeError(
            "MR9B is illustrative only. Set "
            f"{CONFIRM_ENV}={CONFIRM_VALUE} to extract figure examples."
        )
    if MANIFEST_OUTPUT.exists() and os.environ.get(OVERWRITE_ENV) != OVERWRITE_VALUE:
        raise RuntimeError(
            f"MR9B manifest already exists at {MANIFEST_OUTPUT}. "
            f"Set {OVERWRITE_ENV}={OVERWRITE_VALUE} only if intentionally replacing "
            "illustrative examples."
        )
    result = remote_extract_examples.remote()
    _write_outputs(result)
    return json.dumps(
        {
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "hero_count": result["gate"]["hero_count"],
            "villain_count": result["gate"]["villain_count"],
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
    feature_kwargs = {
        "Chem": Chem,
        "DataStructs": DataStructs,
        "Descriptors": Descriptors,
        "MurckoScaffold": MurckoScaffold,
        "generator": generator,
        "np": np,
    }
    train_prepared = train.__class__(_featurized_rows(train, **feature_kwargs))
    valid_prepared = valid.__class__(_featurized_rows(valid, **feature_kwargs))
    test_prepared = test.__class__(_featurized_rows(test, **feature_kwargs))
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
    if train_model_prepared["label"].nunique() < 2 or test_prepared["label"].nunique() < 2:
        return train_prepared, valid_prepared, test_prepared, _status(
            "QUARANTINED_PRE_METRIC",
            "single_class_train_valid_or_test",
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
    return scored, _status("PASS_FROZEN_MR8C_SCORER_REPLAYED_FOR_EXAMPLES", "model_fit")


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


def _candidate_pool(scored: Any) -> Any:
    rankings = {
        "activity_rank": _rank(scored, "probability", None)[["row_id", "rank"]],
        "audit_rank": _rank(scored, "audit_card_score", 1)[["row_id", "rank"]],
        "scaffold_quota_rank": _rank(scored, "probability", 1)[["row_id", "rank"]],
    }
    out = scored.copy()
    for rank_col, frame in rankings.items():
        out = out.merge(frame.rename(columns={"rank": rank_col}), on="row_id", how="left")
    out["audit_rank_drop_vs_activity"] = out["audit_rank"] - out["activity_rank"]
    out["activity_top_50"] = out["activity_rank"] <= 50
    out["audit_top_50"] = out["audit_rank"] <= 50
    out["candidate_pool_flag"] = (
        (out["activity_rank"] <= 100)
        | (out["audit_rank"] <= 100)
        | (out["audit_card_risk"] >= out["audit_card_risk"].quantile(0.90))
    )
    columns = [
        "task_name",
        "row_id",
        "smiles",
        "canonical_smiles",
        "label",
        "probability",
        "audit_card_score",
        "audit_card_risk",
        "ad_distance_risk",
        "nearest_train_tanimoto",
        "uncertainty_risk",
        "conformal_risk",
        "descriptor_outlier",
        "mw",
        "logp",
        "tpsa",
        "scaffold",
        "activity_rank",
        "audit_rank",
        "scaffold_quota_rank",
        "audit_rank_drop_vs_activity",
        "activity_top_50",
        "audit_top_50",
        "candidate_pool_flag",
    ]
    return out[out["candidate_pool_flag"]][columns].sort_values(
        ["task_name", "activity_rank", "audit_rank"],
        kind="mergesort",
    )


def _rank(scored: Any, score_column: str, scaffold_cap: int | None) -> Any:
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
    return ranked


def _select_examples(candidates: Any) -> Any:
    import pandas as pd

    if candidates.empty:
        return candidates
    work = candidates.copy()
    work["hero_score"] = (
        (1.0 / work["audit_rank"].clip(lower=1).astype(float))
        + work["probability"].astype(float)
        + (1.0 - work["audit_card_risk"].astype(float))
        + work["nearest_train_tanimoto"].astype(float)
    )
    work["villain_score"] = (
        (1.0 / work["activity_rank"].clip(lower=1).astype(float))
        + work["probability"].astype(float)
        + work["audit_card_risk"].astype(float)
        + work["audit_rank_drop_vs_activity"].clip(lower=0).astype(float) / 100.0
        + (1.0 - work["nearest_train_tanimoto"].astype(float))
    )
    hero_pool = work[
        work["label"].eq(1)
        & work["audit_top_50"].eq(True)
        & work["audit_card_risk"].le(work["audit_card_risk"].quantile(0.50))
    ].sort_values("hero_score", ascending=False, kind="mergesort")
    villain_pool = work[
        work["label"].eq(0)
        & work["activity_top_50"].eq(True)
        & work["audit_card_risk"].ge(work["audit_card_risk"].quantile(0.60))
    ].sort_values("villain_score", ascending=False, kind="mergesort")

    heroes = _take_task_diverse(hero_pool, 3)
    villains = _take_task_diverse(villain_pool, 3)
    if len(heroes) < 3:
        fallback = work[work["label"].eq(1)].sort_values("hero_score", ascending=False)
        heroes = _take_task_diverse(pd.concat([heroes, fallback]), 3)
    if len(villains) < 3:
        fallback = work[work["label"].eq(0)].sort_values("villain_score", ascending=False)
        villains = _take_task_diverse(pd.concat([villains, fallback]), 3)

    examples = []
    for idx, row in enumerate(heroes.to_dict(orient="records"), start=1):
        examples.append(_example_row(row, f"hero_{idx:02d}", "hero"))
    for idx, row in enumerate(villains.to_dict(orient="records"), start=1):
        examples.append(_example_row(row, f"villain_{idx:02d}", "villain"))
    return pd.DataFrame(examples)


def _take_task_diverse(frame: Any, n: int) -> Any:
    if frame.empty:
        return frame
    unique = frame.drop_duplicates(subset=["row_id"], keep="first")
    task_diverse = unique.drop_duplicates(subset=["task_name"], keep="first")
    if len(task_diverse) >= n:
        return task_diverse.head(n).copy()
    combined = unique.head(n).copy()
    return combined


def _example_row(row: dict[str, Any], example_id: str, role: str) -> dict[str, Any]:
    risk_reasons = []
    if float(row["ad_distance_risk"]) >= 0.45:
        risk_reasons.append("low_nearest_train_tanimoto")
    if float(row["uncertainty_risk"]) >= 0.40:
        risk_reasons.append("high_uncertainty")
    if float(row["conformal_risk"]) >= 0.40:
        risk_reasons.append("high_conformal_risk")
    if float(row["descriptor_outlier"]) >= 0.5:
        risk_reasons.append("descriptor_outlier")
    if not risk_reasons:
        fallback = "low_audit_risk_profile" if role == "hero" else "relative_audit_penalty"
        risk_reasons.append(fallback)
    return {
        "example_id": example_id,
        "role": role,
        "selection_boundary": "illustrative_only_not_a_claim_gate",
        "task_name": row["task_name"],
        "row_id": row["row_id"],
        "smiles": row["smiles"],
        "canonical_smiles": row["canonical_smiles"],
        "final_label": int(row["label"]),
        "probability": float(row["probability"]),
        "audit_card_score": float(row["audit_card_score"]),
        "audit_card_risk": float(row["audit_card_risk"]),
        "ad_distance_risk": float(row["ad_distance_risk"]),
        "nearest_train_tanimoto": float(row["nearest_train_tanimoto"]),
        "uncertainty_risk": float(row["uncertainty_risk"]),
        "conformal_risk": float(row["conformal_risk"]),
        "descriptor_outlier": float(row["descriptor_outlier"]),
        "mw": float(row["mw"]),
        "logp": float(row["logp"]),
        "tpsa": float(row["tpsa"]),
        "activity_rank": int(row["activity_rank"]),
        "audit_rank": int(row["audit_rank"]),
        "scaffold_quota_rank": int(row["scaffold_quota_rank"]),
        "audit_rank_drop_vs_activity": int(row["audit_rank_drop_vs_activity"]),
        "audit_reason": ";".join(risk_reasons),
    }


def _add_svg(examples: Any, *, Chem: Any, Draw: Any) -> Any:
    if examples.empty:
        examples["structure_svg"] = []
        return examples
    svg_values = []
    for smiles in examples["canonical_smiles"].astype(str):
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            svg_values.append("")
            continue
        drawer = Draw.rdMolDraw2D.MolDraw2DSVG(420, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg_values.append(drawer.GetDrawingText())
    out = examples.copy()
    out["structure_svg"] = svg_values
    out["structure_svg_path"] = [
        str(FIGURE_DIR / f"{example_id}.svg") for example_id in out["example_id"]
    ]
    return out


def _gate(examples: Any, candidates: Any, task_status: list[dict[str, Any]]) -> dict[str, Any]:
    hero_count = int(examples["role"].eq("hero").sum()) if not examples.empty else 0
    villain_count = int(examples["role"].eq("villain").sum()) if not examples.empty else 0
    valid_count = int(sum(row["status"] == "PASS" for row in task_status))
    pass_gate = (
        valid_count == 13
        and hero_count >= 3
        and villain_count >= 3
        and len(candidates) > 0
    )
    return {
        "gate_status": STATUS if pass_gate else "MR9B_ILLUSTRATIVE_EXTRACTION_INCOMPLETE",
        "gate_reason": (
            "illustrative_hero_villain_examples_extracted"
            if pass_gate
            else "insufficient_examples_or_task_replay"
        ),
        "analysis_type": "post_MR8C_illustrative_exemplar_extraction",
        "valid_task_count": valid_count,
        "attempted_task_count": len(FINAL_TASKS),
        "hero_count": hero_count,
        "villain_count": villain_count,
        "candidate_pool_rows": int(len(candidates)),
        "new_claim_gate": False,
        "mr8c_gate_changed": False,
        "diversex_retuned": False,
        "final_labels_used_for_ranking": False,
        "final_labels_used_for_illustrative_selection": True,
    }


def _write_outputs(result: dict[str, Any]) -> None:
    import pandas as pd

    for path in [
        EXAMPLES_OUTPUT,
        CANDIDATE_OUTPUT,
        TASK_STATUS_OUTPUT,
        REPORT_OUTPUT,
        MANIFEST_OUTPUT,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    examples = pd.DataFrame(result["examples"])
    candidate_pool = pd.DataFrame(result["candidate_pool"])
    task_status = pd.DataFrame(result["task_status"])
    if "structure_svg" in examples.columns:
        for row in examples.to_dict(orient="records"):
            svg_path = Path(row["structure_svg_path"])
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            svg_path.write_text(str(row.get("structure_svg", "")), encoding="utf-8")
        examples = examples.drop(columns=["structure_svg"])
    examples.to_csv(EXAMPLES_OUTPUT, index=False)
    candidate_pool.to_csv(CANDIDATE_OUTPUT, index=False)
    task_status.to_csv(TASK_STATUS_OUTPUT, index=False)
    REPORT_OUTPUT.write_text(_report(result, examples=examples), encoding="utf-8")
    MANIFEST_OUTPUT.write_text(
        json.dumps(
            {
                "created_at_utc": result["created_at_utc"],
                "status": result["status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "gate": result["gate"],
                "outputs": {
                    "examples": str(EXAMPLES_OUTPUT),
                    "candidate_pool": str(CANDIDATE_OUTPUT),
                    "task_status": str(TASK_STATUS_OUTPUT),
                    "report": str(REPORT_OUTPUT),
                    "figure_dir": str(FIGURE_DIR),
                },
                "locks": result["locks"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _report(result: dict[str, Any], *, examples: Any) -> str:
    gate = result["gate"]
    table = examples[
        [
            "example_id",
            "role",
            "task_name",
            "final_label",
            "probability",
            "audit_card_risk",
            "nearest_train_tanimoto",
            "uncertainty_risk",
            "conformal_risk",
            "activity_rank",
            "audit_rank",
            "audit_reason",
            "canonical_smiles",
            "structure_svg_path",
        ]
    ].to_markdown(index=False)
    return f"""# DIVERSE-X V5-MR9B Figure Molecule Examples

Status: `{gate["gate_status"]}`
Date: 2026-05-19

## Boundary

MR9B is a post-MR8C illustrative exemplar extraction. It replays the frozen MR8C
scorer only to emit candidate-level SMILES and audit-card fields for manuscript
figures. It is not a new claim gate, does not retune DIVERSE-X, and does not
change the MR8C final gate.

It does not change the MR8C final gate.

## Gate

- Valid replay tasks: `{gate["valid_task_count"]}` of `{gate["attempted_task_count"]}`
- Hero examples: `{gate["hero_count"]}`
- Villain examples: `{gate["villain_count"]}`
- Candidate pool rows: `{gate["candidate_pool_rows"]}`
- Final labels used for ranking: `{gate["final_labels_used_for_ranking"]}`
- Final labels used for illustrative selection:
  `{gate["final_labels_used_for_illustrative_selection"]}`

## Examples

{table}

## Figure Use

Use these molecules as visual examples for audit-card figures only. Do not cite
MR9B as performance evidence.
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


if __name__ == "__main__":
    main()
