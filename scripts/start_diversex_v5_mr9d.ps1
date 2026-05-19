param(
    [switch]$ValidateOnly,
    [switch]$Generate
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$repo = Join-Path $root "repo"

Set-Location -LiteralPath $root

if ($ValidateOnly) {
    & (Join-Path $PSScriptRoot "validate_diversex_v5_mr9d.ps1")
    exit $LASTEXITCODE
}

if ($Generate) {
    Set-Location -LiteralPath $repo
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    python -X utf8 scripts\v5_mr9d_submission_freeze.py
    exit $LASTEXITCODE
}

Write-Host "DIVERSE-X V5-MR9D start"
Write-Host "Use -Generate to rebuild the submission freeze package."
Write-Host "Use -ValidateOnly to validate generated artifacts."
