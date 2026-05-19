$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$errors = New-Object System.Collections.Generic.List[string]

function Add-MR9CError {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Read-JsonIfExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-MR9CError "Missing JSON file: $Path"
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Add-MR9CError "JSON parse failed for ${Path}: $($_.Exception.Message)"
        return $null
    }
}

$requiredFiles = @(
    "DIVERSE_X_V5_MR9C_MASTER_PLAN.md",
    "DIVERSE_X_V5_MR9C_TODO.md",
    "DIVERSE_X_V5_MR9C_RUN_STATE.md",
    "DIVERSE_X_V5_MR9C_EXTERNAL_SYNC_QUEUE.md",
    "repo\scripts\v5_mr9c_config_appendix.py",
    "repo\reports\runs\v5_mr9c_config_appendix.md",
    "repo\reports\tables\v5_mr9c_method_config_appendix.csv",
    "repo\reports\tables\v5_mr9c_selected_baseline_configs.csv",
    "repo\reports\tables\v5_mr9c_tuning_grid_summary.csv",
    "repo\reports\tables\v5_mr9c_reproducibility_locks.csv",
    "repo\data\manifests\v5_mr9c_config_appendix_manifest.json",
    "scripts\start_diversex_v5_mr9c.ps1",
    "scripts\resume_diversex_v5_mr9c.ps1",
    "scripts\validate_diversex_v5_mr9c.ps1"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        Add-MR9CError "Missing MR9C file: $file"
    }
}

foreach ($script in @(
    "scripts\start_diversex_v5_mr9c.ps1",
    "scripts\resume_diversex_v5_mr9c.ps1",
    "scripts\validate_diversex_v5_mr9c.ps1"
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
                Add-MR9CError "PowerShell parse error in ${script}: $($parseError.Message)"
            }
        }
    }
}

$manifest = Read-JsonIfExists "repo\data\manifests\v5_mr9c_config_appendix_manifest.json"
if ($null -ne $manifest) {
    if ($manifest.status -ne "MR9C_CONFIG_APPENDIX_COMPLETE") {
        Add-MR9CError "Unexpected MR9C manifest status: $($manifest.status)"
    }
    if ($manifest.no_new_outcome_evaluations -ne $true) {
        Add-MR9CError "MR9C manifest indicates outcome evaluations"
    }
    if ($manifest.locks.new_outcome_evaluations_run -ne $false) {
        Add-MR9CError "MR9C lock indicates new outcome evaluations"
    }
    if ($manifest.locks.diversex_retuned -ne $false) {
        Add-MR9CError "MR9C lock indicates DIVERSE-X retuning"
    }
    if ([int]$manifest.counts.selected_config_rows -ne 26) {
        Add-MR9CError "MR9C selected config row count is not 26"
    }
    if ([int]$manifest.counts.failed_locks -ne 0) {
        Add-MR9CError "MR9C manifest reports failed locks"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9c_selected_baseline_configs.csv") {
    $selected = Import-Csv "repo\reports\tables\v5_mr9c_selected_baseline_configs.csv"
    if ($selected.Count -ne 26) {
        Add-MR9CError "Expected 26 selected baseline configs"
    }
    $bad = $selected | Where-Object { $_.final_labels_used_for_selection -ne "False" }
    if ($bad.Count -gt 0) {
        Add-MR9CError "Selected configs indicate final-label selection"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9c_tuning_grid_summary.csv") {
    $grid = Import-Csv "repo\reports\tables\v5_mr9c_tuning_grid_summary.csv"
    foreach ($family in @("tuned_rf_ecfp_descriptor", "tuned_hgb_ecfp_descriptor")) {
        $row = $grid | Where-Object { $_.family -eq $family }
        if ($null -eq $row) {
            Add-MR9CError "Missing grid family: $family"
        } elseif ([int]$row.unique_config_count -ne 20) {
            Add-MR9CError "Grid family $family does not have 20 unique configs"
        }
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9c_method_config_appendix.csv") {
    $methods = Get-Content "repo\reports\tables\v5_mr9c_method_config_appendix.csv" -Raw
    foreach ($term in @(
        "audit_card_risk",
        "conformal_risk",
        "nearest_train_tanimoto",
        "scaffold_quota",
        "rf_epistemic_uncertainty",
        "hgb_margin_uncertainty"
    )) {
        if ($methods -notlike "*$term*") {
            Add-MR9CError "Method appendix missing term: $term"
        }
    }
}

if (Test-Path -LiteralPath "repo\reports\runs\v5_mr9c_config_appendix.md") {
    $report = Get-Content -LiteralPath "repo\reports\runs\v5_mr9c_config_appendix.md" -Raw
    foreach ($term in @(
        "does not run new outcome evaluations",
        "does not retune",
        "MR8C gate",
        "MR9A gate"
    )) {
        if ($report -notlike "*$term*") {
            Add-MR9CError "MR9C report missing term: $term"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "DIVERSE-X V5-MR9C validation FAILED"
    foreach ($err in $errors) {
        Write-Host " - $err"
    }
    exit 1
}

Write-Host "DIVERSE-X V5-MR9C validation PASSED"
