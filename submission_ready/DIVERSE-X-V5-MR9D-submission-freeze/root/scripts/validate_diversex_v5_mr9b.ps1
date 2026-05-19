$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$errors = New-Object System.Collections.Generic.List[string]

function Add-MR9BError {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Read-JsonIfExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-MR9BError "Missing JSON file: $Path"
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Add-MR9BError "JSON parse failed for ${Path}: $($_.Exception.Message)"
        return $null
    }
}

$requiredFiles = @(
    "DIVERSE_X_V5_MR9B_MASTER_PLAN.md",
    "DIVERSE_X_V5_MR9B_TODO.md",
    "DIVERSE_X_V5_MR9B_RUN_STATE.md",
    "DIVERSE_X_V5_MR9B_EXTERNAL_SYNC_QUEUE.md",
    "repo\modal\v5_mr9b_figure_molecule_examples.py",
    "repo\reports\tables\v5_mr9b_figure_molecule_examples.csv",
    "repo\reports\tables\v5_mr9b_candidate_audit_pool.csv",
    "repo\reports\tables\v5_mr9b_task_status.csv",
    "repo\reports\runs\v5_mr9b_figure_molecule_examples.md",
    "repo\data\manifests\v5_mr9b_figure_molecule_examples_manifest.json",
    "scripts\start_diversex_v5_mr9b.ps1",
    "scripts\resume_diversex_v5_mr9b.ps1",
    "scripts\validate_diversex_v5_mr9b.ps1"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        Add-MR9BError "Missing MR9B file: $file"
    }
}

foreach ($script in @(
    "scripts\start_diversex_v5_mr9b.ps1",
    "scripts\resume_diversex_v5_mr9b.ps1",
    "scripts\validate_diversex_v5_mr9b.ps1"
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
                Add-MR9BError "PowerShell parse error in ${script}: $($parseError.Message)"
            }
        }
    }
}

$manifest = Read-JsonIfExists "repo\data\manifests\v5_mr9b_figure_molecule_examples_manifest.json"
if ($null -ne $manifest) {
    if ($manifest.status -ne "MR9B_ILLUSTRATIVE_EXAMPLES_EXTRACTED") {
        Add-MR9BError "Unexpected MR9B manifest status: $($manifest.status)"
    }
    if ($manifest.locks.analysis_type -ne "post_MR8C_illustrative_exemplar_extraction") {
        Add-MR9BError "MR9B manifest missing illustrative analysis label"
    }
    if ($manifest.locks.new_claim_gate -ne $false) {
        Add-MR9BError "MR9B manifest indicates a new claim gate"
    }
    if ($manifest.locks.diversex_retuned -ne $false) {
        Add-MR9BError "MR9B manifest indicates DIVERSE-X retuning"
    }
    if ($manifest.locks.mr8c_gate_changed -ne $false) {
        Add-MR9BError "MR9B manifest indicates MR8C gate changed"
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9b_figure_molecule_examples.csv") {
    $examples = Import-Csv "repo\reports\tables\v5_mr9b_figure_molecule_examples.csv"
    $heroes = ($examples | Where-Object { $_.role -eq "hero" }).Count
    $villains = ($examples | Where-Object { $_.role -eq "villain" }).Count
    if ($heroes -lt 3) {
        Add-MR9BError "Expected at least 3 hero examples"
    }
    if ($villains -lt 3) {
        Add-MR9BError "Expected at least 3 villain examples"
    }
    foreach ($row in $examples) {
        if ($row.selection_boundary -ne "illustrative_only_not_a_claim_gate") {
            Add-MR9BError "Example missing illustrative boundary: $($row.example_id)"
        }
        $svgPath = $row.structure_svg_path
        if (-not (Test-Path -LiteralPath $svgPath)) {
            $svgPath = Join-Path "repo" $row.structure_svg_path
        }
        if (-not (Test-Path -LiteralPath $svgPath)) {
            Add-MR9BError "Missing SVG for example: $($row.example_id)"
        }
    }
}

if (Test-Path -LiteralPath "repo\reports\tables\v5_mr9b_task_status.csv") {
    $status = Import-Csv "repo\reports\tables\v5_mr9b_task_status.csv"
    $passed = ($status | Where-Object { $_.status -eq "PASS" }).Count
    if ($passed -ne 13) {
        Add-MR9BError "Expected 13 passed replay tasks"
    }
}

if (Test-Path -LiteralPath "repo\reports\runs\v5_mr9b_figure_molecule_examples.md") {
    $report = Get-Content -LiteralPath "repo\reports\runs\v5_mr9b_figure_molecule_examples.md" -Raw
    foreach ($term in @(
        "post-MR8C illustrative exemplar extraction",
        "not a new claim gate",
        "does not retune",
        "does not change the MR8C final gate"
    )) {
        if ($report -notlike "*$term*") {
            Add-MR9BError "MR9B report missing term: $term"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "DIVERSE-X V5-MR9B validation FAILED"
    foreach ($err in $errors) {
        Write-Host " - $err"
    }
    exit 1
}

Write-Host "DIVERSE-X V5-MR9B validation PASSED"
