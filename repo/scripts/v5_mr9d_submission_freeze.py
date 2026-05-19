from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATUS = "MR9D_SUBMISSION_FREEZE_COMPLETE"
REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
FREEZE_NAME = "DIVERSE-X-V5-MR9D-submission-freeze"
FREEZE_DIR = ROOT / "submission_ready" / FREEZE_NAME
ARCHIVE = ROOT / "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE.zip"
ROOT_MANIFEST = ROOT / "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_MANIFEST.json"
ROOT_REPORT = ROOT / "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_REPORT.md"
REPO_REPORT = REPO / "reports/runs/v5_mr9d_submission_freeze_report.md"
REPO_MANIFEST = REPO / "data/manifests/v5_mr9d_submission_freeze_manifest.json"


@dataclass(frozen=True)
class FreezeInput:
    source: Path
    role: str
    destination: Path | None = None


def main() -> int:
    if FREEZE_DIR.exists():
        shutil.rmtree(FREEZE_DIR)
    FREEZE_DIR.mkdir(parents=True, exist_ok=True)

    inputs = _freeze_inputs()
    rows = [_copy_input(item) for item in inputs if item.source.exists()]
    missing = [
        str(item.source.relative_to(ROOT) if item.source.is_relative_to(ROOT) else item.source)
        for item in inputs
        if not item.source.exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing required freeze inputs: {missing}")

    _write_environment_files(rows)
    _write_submission_readme(rows)
    rows = _scan_freeze_dir()
    _write_file_manifest(rows)
    _write_checksums(rows)
    manifest = _manifest(rows)
    _write_json(FREEZE_DIR / "SUBMISSION_FREEZE_MANIFEST.json", manifest)
    _write_json(ROOT_MANIFEST, manifest)
    _write_json(REPO_MANIFEST, manifest)
    report = _report(manifest)
    (FREEZE_DIR / "SUBMISSION_FREEZE_REPORT.md").write_text(report, encoding="utf-8")
    ROOT_REPORT.write_text(report, encoding="utf-8")
    REPO_REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPO_REPORT.write_text(report, encoding="utf-8")
    _write_archive()
    print(
        json.dumps(
            {
                "status": STATUS,
                "freeze_dir": str(FREEZE_DIR),
                "archive": str(ARCHIVE),
                "file_count": len(rows),
                "archive_sha256": _sha256_file(ARCHIVE),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _freeze_inputs() -> list[FreezeInput]:
    root_docs = [
        "DIVERSE_X_V5_LOCKED_TITLE_ABSTRACT.md",
        "DIVERSE_X_V5_PAPER_RESULTS_FOR_VERIFICATION.md",
        "DIVERSE_X_V5_MR9_SUBMISSION_READINESS_GOALS.md",
        "DIVERSE_X_V5_MR9A_MASTER_PLAN.md",
        "DIVERSE_X_V5_MR9A_TODO.md",
        "DIVERSE_X_V5_MR9A_RUN_STATE.md",
        "DIVERSE_X_V5_MR9B_MASTER_PLAN.md",
        "DIVERSE_X_V5_MR9B_TODO.md",
        "DIVERSE_X_V5_MR9B_RUN_STATE.md",
        "DIVERSE_X_V5_MR9C_MASTER_PLAN.md",
        "DIVERSE_X_V5_MR9C_TODO.md",
        "DIVERSE_X_V5_MR9C_RUN_STATE.md",
    ]
    repo_files = [
        "pyproject.toml",
        "README.md",
        "modal/v5_mr8c_final_external_audit_primary.py",
        "modal/v5_mr9a_tuned_baseline_fairness.py",
        "modal/v5_mr9b_figure_molecule_examples.py",
        "scripts/v5_mr8b_preregistration.py",
        "scripts/v5_mr9c_config_appendix.py",
        "reports/tables/v5_mr8c_final_external_gate.csv",
        "reports/tables/v5_mr8c_final_external_metrics.csv",
        "reports/tables/v5_mr8c_final_external_summary.csv",
        "reports/tables/v5_mr8c_final_external_rejection_curve.csv",
        "reports/tables/v5_mr8c_final_external_rejection_summary.csv",
        "reports/tables/v5_mr8c_final_external_task_status.csv",
        "reports/tables/v5_mr8c_claim_boundary.csv",
        "reports/runs/v5_mr8c_final_external_report.md",
        "reports/runs/v5_mr8c_completion_audit.md",
        "data/manifests/v5_mr8c_final_external_manifest.json",
        "reports/tables/v5_mr9a_tuned_baseline_fairness_gate.csv",
        "reports/tables/v5_mr9a_tuned_baseline_fairness_summary.csv",
        "reports/tables/v5_mr9a_tuned_baseline_fairness_metrics.csv",
        "reports/tables/v5_mr9a_tuned_baseline_config.csv",
        "reports/tables/v5_mr9a_tuned_baseline_task_status.csv",
        "reports/tables/v5_mr9a_mr8c_reference_comparison.csv",
        "reports/runs/v5_mr9a_tuned_baseline_fairness_report.md",
        "data/manifests/v5_mr9a_tuned_baseline_fairness_manifest.json",
        "reports/tables/v5_mr9b_figure_molecule_examples.csv",
        "reports/tables/v5_mr9b_candidate_audit_pool.csv",
        "reports/tables/v5_mr9b_task_status.csv",
        "reports/runs/v5_mr9b_figure_molecule_examples.md",
        "data/manifests/v5_mr9b_figure_molecule_examples_manifest.json",
        "reports/tables/v5_mr9c_method_config_appendix.csv",
        "reports/tables/v5_mr9c_selected_baseline_configs.csv",
        "reports/tables/v5_mr9c_tuning_grid_summary.csv",
        "reports/tables/v5_mr9c_reproducibility_locks.csv",
        "reports/runs/v5_mr9c_config_appendix.md",
        "data/manifests/v5_mr9c_config_appendix_manifest.json",
    ]
    script_files = [
        "scripts/start_diversex_v5_mr9a.ps1",
        "scripts/resume_diversex_v5_mr9a.ps1",
        "scripts/validate_diversex_v5_mr9a.ps1",
        "scripts/start_diversex_v5_mr9b.ps1",
        "scripts/resume_diversex_v5_mr9b.ps1",
        "scripts/validate_diversex_v5_mr9b.ps1",
        "scripts/start_diversex_v5_mr9c.ps1",
        "scripts/resume_diversex_v5_mr9c.ps1",
        "scripts/validate_diversex_v5_mr9c.ps1",
    ]
    figure_files = [
        path.relative_to(REPO)
        for path in sorted((REPO / "reports/figures/mr9b_molecule_examples").glob("*.svg"))
    ]
    items = [
        FreezeInput(ROOT / path, "root_document", Path("root") / path)
        for path in root_docs
    ]
    items.extend(
        FreezeInput(REPO / path, "repo_artifact", Path("repo") / path)
        for path in repo_files
    )
    items.extend(
        FreezeInput(ROOT / path, "run_script", Path("root") / path)
        for path in script_files
    )
    items.extend(
        FreezeInput(REPO / path, "figure_asset", Path("repo") / path)
        for path in figure_files
    )
    return items


def _copy_input(item: FreezeInput) -> dict[str, Any]:
    destination = FREEZE_DIR / (item.destination or item.source.relative_to(ROOT))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item.source, destination)
    return _row_for_file(destination, role=item.role, source=item.source)


def _write_environment_files(rows: list[dict[str, Any]]) -> None:
    environment = FREEZE_DIR / "environment"
    environment.mkdir(parents=True, exist_ok=True)
    python_version = subprocess.run(
        [sys.executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (environment / "python_version.txt").write_text(python_version + "\n", encoding="utf-8")
    pip_freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    (environment / "pip_freeze_local.txt").write_text(pip_freeze, encoding="utf-8")
    modal_deps = """# Modal Dependencies

MR8C/MR9A/MR9B Modal runners declare:

- numpy>=1.26,<2.0
- pandas>=2.1,<3.0
- pytdc==1.1.15
- rdkit>=2023.9
- scikit-learn>=1.4

MR9B additionally installs Debian packages:

- libxrender1
- libxext6
"""
    (environment / "modal_dependencies.md").write_text(modal_deps, encoding="utf-8")
    rows.extend(
        [
            _row_for_file(environment / "python_version.txt", role="environment"),
            _row_for_file(environment / "pip_freeze_local.txt", role="environment"),
            _row_for_file(environment / "modal_dependencies.md", role="environment"),
        ]
    )


def _write_submission_readme(rows: list[dict[str, Any]]) -> None:
    readme = """# DIVERSE-X V5 MR9D Submission Freeze

This package freezes the DIVERSE-X V5 MR8C/MR9 submission-ready artifacts.

## Claim Boundary

- MR8C final gate: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`
- Primary supported claim: audit-card rejection reliability under chemical-space shift
- MR7 locked-final no-go remains disclosed
- MR9A is post-MR8C supplemental tuned-baseline fairness closure
- MR9B is illustrative molecule-example extraction only
- MR9C is a configuration appendix only
- MR9D is code/artifact freeze only

## Entry Points

- `root/DIVERSE_X_V5_PAPER_RESULTS_FOR_VERIFICATION.md`
- `repo/reports/runs/v5_mr8c_final_external_report.md`
- `repo/reports/runs/v5_mr9a_tuned_baseline_fairness_report.md`
- `repo/reports/runs/v5_mr9b_figure_molecule_examples.md`
- `repo/reports/runs/v5_mr9c_config_appendix.md`
- `SUBMISSION_FREEZE_MANIFEST.json`
- `CHECKSUMS_SHA256.txt`

## Reproducibility Notes

The Modal runners are included under `repo/modal`. MR9B molecule SVGs are
included under `repo/reports/figures/mr9b_molecule_examples`.

This repository/package is intended for reviewer verification and manuscript
support, not as a new evaluation gate.
"""
    path = FREEZE_DIR / "README.md"
    path.write_text(readme, encoding="utf-8")
    rows.append(_row_for_file(path, role="freeze_readme"))


def _scan_freeze_dir() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(FREEZE_DIR.rglob("*")):
        if path.is_file():
            rows.append(_row_for_file(path, role=_role_from_path(path)))
    return rows


def _row_for_file(path: Path, *, role: str, source: Path | None = None) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(FREEZE_DIR)).replace("\\", "/"),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "source": (
            str(source.relative_to(ROOT)).replace("\\", "/")
            if source and source.is_relative_to(ROOT)
            else ""
        ),
    }


def _role_from_path(path: Path) -> str:
    rel = str(path.relative_to(FREEZE_DIR)).replace("\\", "/")
    if rel.startswith("environment/"):
        return "environment"
    if rel.endswith(".svg"):
        return "figure_asset"
    if rel.startswith("repo/modal/") or rel.startswith("repo/scripts/"):
        return "code"
    if rel.endswith(".json") and "manifest" in rel.lower():
        return "manifest"
    if rel.endswith(".csv"):
        return "result_table"
    if rel.endswith(".md"):
        return "report_or_document"
    return "artifact"


def _write_file_manifest(rows: list[dict[str, Any]]) -> None:
    path = FREEZE_DIR / "FILE_MANIFEST.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "role", "bytes", "sha256", "source"])
        writer.writeheader()
        writer.writerows(rows)


def _write_checksums(rows: list[dict[str, Any]]) -> None:
    lines = [f"{row['sha256']}  {row['path']}" for row in rows]
    (FREEZE_DIR / "CHECKSUMS_SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _manifest(rows: list[dict[str, Any]]) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
    return {
        "status": STATUS,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "freeze_name": FREEZE_NAME,
        "archive": str(ARCHIVE.name),
        "archive_sha256": _sha256_file(ARCHIVE) if ARCHIVE.exists() else "",
        "file_count": len(rows),
        "role_counts": role_counts,
        "gates": {
            "mr8c": "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT",
            "mr9a": "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED",
            "mr9b": "MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED",
            "mr9c": "MR9C_CONFIG_APPENDIX_COMPLETE",
            "mr9d": STATUS,
        },
        "locks": {
            "new_outcome_evaluations_run": False,
            "diversex_retuned": False,
            "mr8c_gate_changed": False,
            "github_public_repo_target": "RishyanthReddy/diverse-x-v5-mr9-submission-freeze",
        },
        "outputs": {
            "freeze_dir": str(FREEZE_DIR.relative_to(ROOT)),
            "file_manifest": str((FREEZE_DIR / "FILE_MANIFEST.csv").relative_to(ROOT)),
            "checksums": str((FREEZE_DIR / "CHECKSUMS_SHA256.txt").relative_to(ROOT)),
            "report": str(ROOT_REPORT.relative_to(ROOT)),
            "repo_report": str(REPO_REPORT.relative_to(ROOT)),
        },
    }


def _report(manifest: dict[str, Any]) -> str:
    role_lines = "\n".join(
        f"- `{role}`: `{count}`" for role, count in sorted(manifest["role_counts"].items())
    )
    return f"""# DIVERSE-X V5-MR9D Submission Freeze Report

Status: `{STATUS}`
Date: 2026-05-19

## Boundary

MR9D freezes code and artifacts for submission readiness. It does not run new
outcome evaluations, does not retune DIVERSE-X, and does not change MR8C, MR9A,
MR9B, or MR9C gates.

## Gate Summary

- MR8C: `MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT`
- MR9A: `MR9A_TUNED_BASELINE_FAIRNESS_CLOSED`
- MR9B: `MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED`
- MR9C: `MR9C_CONFIG_APPENDIX_COMPLETE`
- MR9D: `{STATUS}`

## Package

- Freeze directory: `{manifest["outputs"]["freeze_dir"]}`
- Archive: `{manifest["archive"]}`
- Files: `{manifest["file_count"]}`
- Archive SHA256: `{manifest["archive_sha256"] or "written after archive creation"}`

## Role Counts

{role_lines}

## GitHub Target

`RishyanthReddy/diverse-x-v5-mr9-submission-freeze`

## Use

Use the `submission_ready/{FREEZE_NAME}` folder or
`DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE.zip` for reviewer verification and
manuscript support.
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_archive() -> None:
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(FREEZE_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(FREEZE_DIR.parent))
    manifest = _read_json(ROOT_MANIFEST)
    manifest["archive_sha256"] = _sha256_file(ARCHIVE)
    _write_json(ROOT_MANIFEST, manifest)
    _write_json(REPO_MANIFEST, manifest)
    freeze_manifest = FREEZE_DIR / "SUBMISSION_FREEZE_MANIFEST.json"
    _write_json(freeze_manifest, manifest)
    ROOT_REPORT.write_text(_report(manifest), encoding="utf-8")
    REPO_REPORT.write_text(_report(manifest), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
