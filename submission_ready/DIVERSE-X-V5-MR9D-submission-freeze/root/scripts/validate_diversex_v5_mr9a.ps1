$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$errors = New-Object System.Collections.Generic.List[string]

function Add-MR9AError {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Read-JsonIfExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-MR9AError "Missing JSON file: $Path"
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Add-MR9AError "JSON parse failed for ${Path}: $($_.Exception.Message)"
        return $null
    }
}

$requiredFiles = @(
    "DIVERSE_X_V5_MR9A_MASTER_PLAN.md",
    "DIVERSE_X_V5_MR9A_TODO.md",
    "DIVERSE_X_V5_MR9A_RUN_STATE.md",
    "DIVERSE_X_V5_MR9A_EXTERNAL_SYNC_QUEUE.md",
    "repo\modal\v5_mr9a_tuned_baseline_fairness.py",
    "repo\reports\tables\v5_mr9a_tuned_baseline_fairness_gate.csv",
    "repo\reports\tables\v5_mr9a_tuned_baseline_fairness_summary.csv",
    "repo\reports\tables\v5_mr9a_tuned_baseline_config.csv",
    "repo\reports\tables\v5_mr9a_tuned_baseline_task_status.csv",
    "repo\reports\runs\v5_mr9a_tuned_baseline_fairness_report.md",
    "repo\data\manifests\v5_mr9a_tuned_baseline_fairness_manifest.json",
    "repo\reports\tables\v5_mr8c_final_external_gate.csv",
    "repo\data\manifests\v5_mr8c_final_external_manifest.json",
    "scripts\start_diversex_v5_mr9a.ps1",
    "scripts\resume_diversex_v5_mr9a.ps1",
    "scripts\validate_diversex_v5_mr9a.ps1"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        Add-MR9AError "Missing MR9A file: $file"
    }
}

foreach ($script in @(
    "scripts\start_diversex_v5_mr9a.ps1",
    "scripts\resume_diversex_v5_mr9a.ps1",
    "scripts\validate_diversex_v5_mr9a.ps1"
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
                Add-MR9AError "PowerShell parse error in ${script}: $($parseError.Message)"
            }
        }
    }
}

$manifest = Read-JsonIfExists "repo\data\manifests\v5_mr9a_tuned_baseline_fairness_manifest.json"
if ($null -ne $manifest) {
    if ($manifest.status -ne "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED") {
        Add-MR9AError "Unexpected MR9A manifest status: $($manifest.status)"
    }
    if ($manifest.locks.analysis_type -ne "post_MR8C_supplemental_baseline_fairness") {
        Add-MR9AError "MR9A manifest missing supplemental analysis label"
    }
    if ($manifest.locks.diversex_retuned -ne $false) {
        Add-MR9AError "MR9A manifest indicates DIVERSE-X retuning"
    }
    if ($manifest.locks.final_labels_used_for_hyperparameter_selection -ne $false) {
        Add-MR9AError "MR9A manifest indicates final labels used for tuning"
    }
    if ($manifest.locks.mr8c_gate_changed -ne $false) {
        Add-MR9AError "MR9A manifest indicates MR8C gate changed"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9a_tuned_baseline_fairness_gate.csv") {
    $gate = Import-Csv "repo\reports\tables\v5_mr9a_tuned_baseline_fairness_gate.csv"
    if ($gate.gate_status -ne "MR9A_TUNED_BASELINE_FAIRNESS_CLOSED") {
        Add-MR9AError "Unexpected MR9A gate status: $($gate.gate_status)"
    }
    if ([int]$gate.valid_task_count -ne 13) {
        Add-MR9AError "MR9A valid task count is not 13"
    }
    if ([int]$gate.rf_trial_count_per_valid_task -lt 20) {
        Add-MR9AError "MR9A RF trial count below 20"
    }
    if ([int]$gate.hgb_trial_count_per_valid_task -lt 20) {
        Add-MR9AError "MR9A HGB trial count below 20"
    }
    if ($gate.final_labels_used_for_hyperparameter_selection -ne "False") {
        Add-MR9AError "MR9A gate indicates final labels used for tuning"
    }
    if ($gate.mr8c_gate_changed -ne "False") {
        Add-MR9AError "MR9A gate indicates MR8C gate changed"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9a_tuned_baseline_config.csv") {
    $configs = Import-Csv "repo\reports\tables\v5_mr9a_tuned_baseline_config.csv"
    $families = $configs | Group-Object task_name, family
    foreach ($group in $families) {
        if ($group.Count -lt 20) {
            Add-MR9AError "MR9A config group below 20 trials: $($group.Name)"
        }
    }
    $badSelection = $configs | Where-Object { $_.final_labels_used_for_selection -ne "False" }
    if ($badSelection.Count -gt 0) {
        Add-MR9AError "MR9A config table indicates final-label selection"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr8c_final_external_gate.csv") {
    $mr8cGate = Import-Csv "repo\reports\tables\v5_mr8c_final_external_gate.csv"
    if ($mr8cGate.gate_status -ne "MR8C_FINAL_EXTERNAL_PASS_Q1_SUPPORT") {
        Add-MR9AError "MR8C gate no longer shows final pass support"
    }
}

if (Test-Path -LiteralPath "repo\reports\runs\v5_mr9a_tuned_baseline_fairness_report.md") {
    $report = Get-Content -LiteralPath "repo\reports\runs\v5_mr9a_tuned_baseline_fairness_report.md" -Raw
    foreach ($term in @(
        "post-MR8C supplemental baseline fairness analysis",
        "does not change the MR8C final gate",
        "Final labels used for hyperparameter selection"
    )) {
        if ($report -notlike "*$term*") {
            Add-MR9AError "MR9A report missing term: $term"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "DIVERSE-X V5-MR9A validation FAILED"
    foreach ($err in $errors) {
        Write-Host " - $err"
    }
    exit 1
}

Write-Host "DIVERSE-X V5-MR9A validation PASSED"
