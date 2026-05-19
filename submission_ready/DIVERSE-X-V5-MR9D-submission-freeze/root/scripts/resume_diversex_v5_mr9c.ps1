$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "DIVERSE-X V5-MR9C resume"

if (Test-Path -LiteralPath ".\DIVERSE_X_V5_MR9C_RUN_STATE.md") {
    Select-String -Path ".\DIVERSE_X_V5_MR9C_RUN_STATE.md" -Pattern "^Status:|^- New outcome|^- DIVERSE|^- MR8C|^- MR9A|^## Next Command|^## Final" | ForEach-Object {
        Write-Host $_.Line
    }
}

if (Test-Path -LiteralPath ".\repo\data\manifests\v5_mr9c_config_appendix_manifest.json") {
    Write-Host ""
    Write-Host "MR9C manifest:"
    Get-Content ".\repo\data\manifests\v5_mr9c_config_appendix_manifest.json" -TotalCount 80
} else {
    Write-Host ""
    Write-Host "MR9C manifest not present yet."
}

Write-Host ""
Write-Host "Next commands:"
Write-Host ".\scripts\start_diversex_v5_mr9c.ps1 -Generate"
Write-Host ".\scripts\start_diversex_v5_mr9c.ps1 -ValidateOnly"
