$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "DIVERSE-X V5-MR9D resume"

if (Test-Path -LiteralPath ".\DIVERSE_X_V5_MR9D_RUN_STATE.md") {
    Select-String -Path ".\DIVERSE_X_V5_MR9D_RUN_STATE.md" -Pattern "^Status:|^- Workspace|^- GitHub|^## Target|^## Final" | ForEach-Object {
        Write-Host $_.Line
    }
}

if (Test-Path -LiteralPath ".\DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_MANIFEST.json") {
    Write-Host ""
    Write-Host "MR9D manifest:"
    Get-Content ".\DIVERSE_X_V5_MR9D_SUBMISSION_FREEZE_MANIFEST.json" -TotalCount 80
} else {
    Write-Host ""
    Write-Host "MR9D manifest not present yet."
}

Write-Host ""
Write-Host "Next commands:"
Write-Host ".\scripts\start_diversex_v5_mr9d.ps1 -Generate"
Write-Host ".\scripts\start_diversex_v5_mr9d.ps1 -ValidateOnly"
