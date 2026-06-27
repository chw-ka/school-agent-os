# Run Calculate Score_special_edition.sql for forms 1-5, term 2.
# Uses connection.txt on T:\ (same as Summaries Excel ODBC).
# Usage: .\run_calculate_score_term2_forms_1_5.ps1 [-TuningFactor 7.45]

param(
    [double]$TuningFactor = 7.45
)

$ErrorActionPreference = 'Stop'
$connFile = 'T:\25-26\ITAdmin_13_StudentReport\_Program\Summaries\connection.txt'
$template = Join-Path $PSScriptRoot 'Calculate Score_special_edition.sql'

if (-not (Test-Path $connFile)) { throw "Missing connection file: $connFile" }
if (-not (Test-Path $template)) { throw "Missing SQL template: $template" }

$conn = (Get-Content $connFile -Raw).Trim()
$server = if ($conn -match 'Data Source=([^;]+)') { $Matches[1] } else { throw 'Cannot parse Data Source' }
$database = if ($conn -match 'Initial Catalog=([^;]+)') { $Matches[1] } else { throw 'Cannot parse Initial Catalog' }
$user = if ($conn -match 'User ID=([^;]+)') { $Matches[1] } else { 'sa' }
$password = if ($conn -match 'Password=([^;]+)') { $Matches[1] } else { throw 'Cannot parse Password' }

$sqlTemplate = Get-Content $template -Raw -Encoding Default
# Drop trailing example proc call (form 6) if present
$sqlTemplate = $sqlTemplate -replace '(?s)\r?\n\s*-- Run the original program.*$', ''

$tmpDir = Join-Path $env:TEMP 'chw-calculate-score'
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

foreach ($form in 1..5) {
    $sql = $sqlTemplate
    $sql = $sql -replace 'set @term = \d+', 'set @term = 2'
    $sql = $sql -replace 'set @form = \d+', "set @form = $form"
    $sql = $sql -replace 'set @tuningFactor = [\d.]+', "set @tuningFactor = $TuningFactor"
    $sql = $sql -replace '(?m)^\s*GO\s*$', ''

    $outFile = Join-Path $tmpDir "calculate_form_${form}_term2.sql"
    [System.IO.File]::WriteAllText($outFile, $sql, [System.Text.Encoding]::Default)

    Write-Host "Running form $form term 2 ..."
    & sqlcmd -S $server -d $database -U $user -P $password -i $outFile -b
    if ($LASTEXITCODE -ne 0) { throw "sqlcmd failed for form $form (exit $LASTEXITCODE)" }
}

Write-Host 'Done. Verify with:'
Write-Host "  SELECT form, COUNT(*) FROM tblZStudentRank2 WHERE term=2 AND form BETWEEN 1 AND 5 GROUP BY form"
