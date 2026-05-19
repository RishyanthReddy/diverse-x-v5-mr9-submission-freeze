param(
    [switch]$ValidateOnly,
    [switch]$PrintRunCommand,
    [switch]$RunModal,
    [switch]$AllowOverwrite
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$repo = Join-Path $root "repo"

Set-Location -LiteralPath $root

if ($ValidateOnly) {
    & (Join-Path $PSScriptRoot "validate_diversex_v5_mr9a.ps1")
    exit $LASTEXITCODE
}

if ($PrintRunCommand) {
    Write-Host '$env:DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES="YES_RUN_POST_MR8C_FAIRNESS"'
    Write-Host "python -X utf8 -m modal run modal\v5_mr9a_tuned_baseline_fairness.py"
    Write-Host 'Remove-Item Env:\DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES -ErrorAction SilentlyContinue'
    exit 0
}

if ($RunModal) {
    Set-Location -LiteralPath $repo
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES = "YES_RUN_POST_MR8C_FAIRNESS"
    if ($AllowOverwrite) {
        $env:DIVERSEX_MR9A_ALLOW_OVERWRITE = "YES_OVERWRITE_MR9A"
    }
    python -X utf8 -m modal run modal\v5_mr9a_tuned_baseline_fairness.py
    $exitCode = $LASTEXITCODE
    Remove-Item Env:\DIVERSEX_MR9A_RUN_SUPPLEMENTAL_BASELINES -ErrorAction SilentlyContinue
    Remove-Item Env:\DIVERSEX_MR9A_ALLOW_OVERWRITE -ErrorAction SilentlyContinue
    exit $exitCode
}

Write-Host "DIVERSE-X V5-MR9A start"
Write-Host "Use -RunModal to execute the supplemental tuned baseline fairness matrix."
Write-Host "Use -ValidateOnly after the Modal run."
