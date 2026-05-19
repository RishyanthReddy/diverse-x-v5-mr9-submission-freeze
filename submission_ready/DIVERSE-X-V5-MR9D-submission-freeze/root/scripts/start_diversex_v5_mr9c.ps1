param(
    [switch]$ValidateOnly,
    [switch]$Generate
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$repo = Join-Path $root "repo"

Set-Location -LiteralPath $root

if ($ValidateOnly) {
    & (Join-Path $PSScriptRoot "validate_diversex_v5_mr9c.ps1")
    exit $LASTEXITCODE
}

if ($Generate) {
    Set-Location -LiteralPath $repo
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    python -X utf8 scripts\v5_mr9c_config_appendix.py
    exit $LASTEXITCODE
}

Write-Host "DIVERSE-X V5-MR9C start"
Write-Host "Use -Generate to rebuild the configuration appendix."
Write-Host "Use -ValidateOnly to validate generated artifacts."
