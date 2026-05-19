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
    & (Join-Path $PSScriptRoot "validate_diversex_v5_mr9b.ps1")
    exit $LASTEXITCODE
}

if ($PrintRunCommand) {
    Write-Host '$env:DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE="YES_EXTRACT_FIGURE_EXAMPLES"'
    Write-Host "python -X utf8 -m modal run modal\v5_mr9b_figure_molecule_examples.py"
    Write-Host 'Remove-Item Env:\DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE -ErrorAction SilentlyContinue'
    exit 0
}

if ($RunModal) {
    Set-Location -LiteralPath $repo
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE = "YES_EXTRACT_FIGURE_EXAMPLES"
    if ($AllowOverwrite) {
        $env:DIVERSEX_MR9B_ALLOW_OVERWRITE = "YES_OVERWRITE_MR9B"
    }
    python -X utf8 -m modal run modal\v5_mr9b_figure_molecule_examples.py
    $exitCode = $LASTEXITCODE
    Remove-Item Env:\DIVERSEX_MR9B_EXTRACT_ILLUSTRATIVE -ErrorAction SilentlyContinue
    Remove-Item Env:\DIVERSEX_MR9B_ALLOW_OVERWRITE -ErrorAction SilentlyContinue
    exit $exitCode
}

Write-Host "DIVERSE-X V5-MR9B start"
Write-Host "Use -RunModal to extract illustrative molecules."
Write-Host "Use -ValidateOnly after extraction."
