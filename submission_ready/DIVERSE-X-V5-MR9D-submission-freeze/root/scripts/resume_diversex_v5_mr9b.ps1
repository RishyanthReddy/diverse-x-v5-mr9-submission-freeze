$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "DIVERSE-X V5-MR9B resume"

if (Test-Path -LiteralPath ".\DIVERSE_X_V5_MR9B_RUN_STATE.md") {
    Select-String -Path ".\DIVERSE_X_V5_MR9B_RUN_STATE.md" -Pattern "^Status:|^- Analysis|^- New claim|^- DIVERSE|^- MR8C|^## Required Run Command|^## Expected Final Status" | ForEach-Object {
        Write-Host $_.Line
    }
}

if (Test-Path -LiteralPath ".\repo\data\manifests\v5_mr9b_figure_molecule_examples_manifest.json") {
    Write-Host ""
    Write-Host "MR9B manifest:"
    Get-Content ".\repo\data\manifests\v5_mr9b_figure_molecule_examples_manifest.json" -TotalCount 80
} else {
    Write-Host ""
    Write-Host "MR9B manifest not present yet."
}

Write-Host ""
Write-Host "Next commands:"
Write-Host ".\scripts\start_diversex_v5_mr9b.ps1 -RunModal"
Write-Host ".\scripts\start_diversex_v5_mr9b.ps1 -ValidateOnly"
