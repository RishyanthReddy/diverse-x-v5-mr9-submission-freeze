$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "DIVERSE-X V5-MR9A resume"

if (Test-Path -LiteralPath ".\DIVERSE_X_V5_MR9A_RUN_STATE.md") {
    Select-String -Path ".\DIVERSE_X_V5_MR9A_RUN_STATE.md" -Pattern "^Status:|^- MR8C|^- MR9A|^## Required Run Command|^## Expected Final Status" | ForEach-Object {
        Write-Host $_.Line
    }
}

if (Test-Path -LiteralPath ".\repo\reports\tables\v5_mr9a_tuned_baseline_fairness_gate.csv") {
    Write-Host ""
    Write-Host "MR9A gate:"
    Import-Csv ".\repo\reports\tables\v5_mr9a_tuned_baseline_fairness_gate.csv" | Format-List
} else {
    Write-Host ""
    Write-Host "MR9A gate not present yet."
}

Write-Host ""
Write-Host "Next commands:"
Write-Host ".\scripts\start_diversex_v5_mr9a.ps1 -RunModal"
Write-Host ".\scripts\start_diversex_v5_mr9a.ps1 -ValidateOnly"
