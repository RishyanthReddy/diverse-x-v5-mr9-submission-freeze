$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$errors = New-Object System.Collections.Generic.List[string]

function Add-MR9DError {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Read-JsonIfExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-MR9DError "Missing JSON file: $Path"
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Add-MR9DError "JSON parse failed for ${Path}: $($_.Exception.Message)"
        return $null
    }
}

function Get-FileSha256 {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$requiredFiles = @(
    "README.md",
    ".gitignore",
    "DIVERSE_X_V5_MR9D_MASTER_PLAN.md",
    "DIVERSE_X_V5_MR9D_TODO.md",
    "DIVERSE_X_V5_MR9D_RUN_STATE.md",
    "DIVERSE_X_V5_MR9D_EXTERNAL_SYNC_QUEUE.md",
    "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE.zip",
    "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_MANIFEST.json",
    "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_REPORT.md",
    "repo\scripts\v5_mr9d_submission_freeze.py",
    "repo\reports\runs\v5_mr9d_submission_freeze_report.md",
    "repo\data\manifests\v5_mr9d_submission_freeze_manifest.json",
    "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\README.md",
    "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\FILE_MANIFEST.csv",
    "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\CHECKSUMS_SHA256.txt",
    "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\SUBMISSION_FREEZE_MANIFEST.json",
    "scripts\start_diversex_v5_mr9d.ps1",
    "scripts\resume_diversex_v5_mr9d.ps1",
    "scripts\validate_diversex_v5_mr9d.ps1"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        Add-MR9DError "Missing MR9D file: $file"
    }
}

foreach ($script in @(
    "scripts\start_diversex_v5_mr9d.ps1",
    "scripts\resume_diversex_v5_mr9d.ps1",
    "scripts\validate_diversex_v5_mr9d.ps1"
)) {
    if (Test-Path -LiteralPath $script) {
        $tokens = $null
        $parseErrors = $null
        [System.Management.Automation.Language.Parser]::ParseFile(
            (Resolve-Path -LiteralPath $script),
            [ref]$tokens,
            [ref]$parseErrors
        ) | Out-Null
        if ($parseErrors.Count -gt 0) {
            foreach ($parseError in $parseErrors) {
                Add-MR9DError "PowerShell parse error in ${script}: $($parseError.Message)"
            }
        }
    }
}

$manifest = Read-JsonIfExists "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_MANIFEST.json"
if ($null -ne $manifest) {
    if ($manifest.status -ne "MR9D_SUBMISSION_FREEZE_COMPLETE") {
        Add-MR9DError "Unexpected MR9D manifest status: $($manifest.status)"
    }
    if ($manifest.gates.mr8c -ne "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT") {
        Add-MR9DError "MR8C gate not preserved in MR9D manifest"
    }
    if ($manifest.gates.mr9a -ne "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED") {
        Add-MR9DError "MR9A gate not preserved in MR9D manifest"
    }
    if ($manifest.gates.mr9b -ne "MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED") {
        Add-MR9DError "MR9B gate not preserved in MR9D manifest"
    }
    if ($manifest.gates.mr9c -ne "MR9C_CONFIG_APPENDIX_COMPLETE") {
        Add-MR9DError "MR9C gate not preserved in MR9D manifest"
    }
    if ($manifest.locks.new_outcome_evaluations_run -ne $false) {
        Add-MR9DError "MR9D manifest indicates new outcome evaluations"
    }
    if ($manifest.locks.diversex_retuned -ne $false) {
        Add-MR9DError "MR9D manifest indicates DIVERSE-X retuning"
    }
    if ([int]$manifest.file_count -lt 60) {
        Add-MR9DError "MR9D freeze file count unexpectedly low"
    }
    if (Test-Path -LiteralPath "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE.zip") {
        $actual = Get-FileSha256 "DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE.zip"
        if ($actual -ne $manifest.archive_sha256) {
            Add-MR9DError "Archive SHA256 mismatch"
        }
    }
}

if (Test-Path -LiteralPath "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\FILE_MANIFEST.csv") {
    $fileManifest = Import-Csv "submission_ready\DIVERSE-X-V5-MR9D-submission-freeze\FILE_MANIFEST.csv"
    foreach ($requiredPath in @(
        "root/DIVERSE_X_V5_PAPER_RESULTS_FOR_VERIFICATION.md",
        "repo/reports/runs/v5_mr8c_final_external_report.md",
        "repo/reports/runs/v5_mr9a_tuned_baseline_fairness_report.md",
        "repo/reports/runs/v5_mr9b_figure_molecule_examples.md",
        "repo/reports/runs/v5_mr9c_config_appendix.md",
        "repo/modal/v5_mr8c_final_external_audit_primary.py",
        "repo/modal/v5_mr9a_tuned_baseline_fairness.py",
        "repo/modal/v5_mr9b_figure_molecule_examples.py"
    )) {
        if (-not ($fileManifest | Where-Object { $_.path -eq $requiredPath })) {
            Add-MR9DError "Freeze manifest missing required path: $requiredPath"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "DIVERSE-X V5-MR9D validation FAILED"
    foreach ($err in $errors) {
        Write-Host " - $err"
    }
    exit 1
}

Write-Host "DIVERSE-X V5-MR9D validation PASSED"
