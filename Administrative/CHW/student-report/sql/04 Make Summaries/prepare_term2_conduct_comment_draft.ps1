# Prepare 成績表初稿_供評語操行輸入 (S1-S5, term 2).
#
# Prerequisite: run run_calculate_score_term2_forms_1_5.ps1 (step 5 Make Summaries).
# Excel: generate_class_score_summary_term2.py (sheet names, names, scores, ranks).

param(
    [string]$OutDir = 'T:\25-26\ITAdmin_13_StudentReport\_Program\Copies\2026_06_26_S12345_成績表初稿_供評語操行輸入',
    [string]$GuidelineSrc = 'T:\24-25\ITAdmin_13_StudentReport\_Program\Copies\2025_06_24_S12345_成績表初稿_供評語操行輸入'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$genPy = Join-Path $scriptDir 'generate_class_score_summary_term2.py'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Get-ChildItem $GuidelineSrc -Filter '*.pdf' |
    Where-Object { $_.Name -notmatch 'ReportDraft|ClassSummary' } |
    Copy-Item -Destination $OutDir -Force

python $genPy (Join-Path $GuidelineSrc '4_Class Score Summary.xls') (Join-Path $OutDir '4_Class Score Summary.xls')
Write-Host "Done. Output folder: $OutDir"
