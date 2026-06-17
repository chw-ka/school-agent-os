# Pull teaching files from panel share into the repo workspace.
# Maps panel Term1/Term2 flat layout → repo Term 01/02 + category subfolders.
# Default: -WhatIf (no copies). Remove -WhatIf to copy.
#
# Example:
#   .\pull-from-panel.ps1 -Subject S2-CMP -Year 2024-2025 -WhatIf
#   .\pull-from-panel.ps1 -Subject S3-CMP -Year 2024-2025 -Term 02

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('S1-CMP', 'S2-CMP', 'S3-CMP', 'S4-ICT', 'S5-ICT', 'S6-ICT')]
    [string]$Subject,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d{4}-\d{4}$')]
    [string]$Year,

    [ValidateSet('01', '02')]
    [string]$Term,

    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

$PanelRoot = 'S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others'
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')

$PanelFolderMap = @{
    'S1-CMP' = 'S1CMP'
    'S2-CMP' = 'S2CMP'
    'S3-CMP' = 'S3CMP'
    'S4-ICT' = 'S4ICT'
    'S5-ICT' = 'S5ICT'
    'S6-ICT' = 'S6ICT'
}

function Get-RepoCategory {
    param([string]$FileName)
    $n = $FileName.ToLower()
    if ($n -match 'practical.?mock|practical_mock') { return 'PracticalMock' }
    if ($n -match 'practical.?assessment|practical_assessment|practicalexam') { return 'PracticalAssessment' }
    if ($n -match 'practical') { return 'PracticalAssessment' }
    if ($n -match 'exam|written|test') { return 'WrittenExam' }
    return '_assets'
}

function Resolve-PanelExamRoot {
    param([string]$Year, [string]$PanelSubject)
    $candidates = @(
        Join-Path $PanelRoot "$Year\05_Test_and_Exam_Paper\$PanelSubject"
        Join-Path $PanelRoot "$Year\5_Test_and_Exam_Paper\$PanelSubject"
    )
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) { return $c }
    }
    return $null
}

if (-not (Test-Path -LiteralPath $PanelRoot)) {
    Write-Error "Panel share not reachable: $PanelRoot (expected at school only)."
}

$panelExam = Resolve-PanelExamRoot -Year $Year -PanelSubject $PanelFolderMap[$Subject]
if (-not $panelExam) {
    Write-Error "Panel exam folder not found for $Subject / $Year under $PanelRoot"
}

$repoPastPapers = Join-Path $RepoRoot "Subjects\$Subject\past-papers\$Year"
$repoAssessments = Join-Path $RepoRoot "Subjects\$Subject\assessments\$Year"

$termFolders = @()
if ($Term) {
    $termFolders += @{ Panel = "Term$([int]$Term)"; Repo = "Term $Term" }
} else {
    $termFolders += @{ Panel = 'Term1'; Repo = 'Term 01' }
    $termFolders += @{ Panel = 'Term2'; Repo = 'Term 02' }
}

Write-Host "Source: $panelExam"
Write-Host "Repo (finals):   $repoPastPapers"
Write-Host "Repo (assets):   $repoAssessments"
Write-Host "Mode:   $(if ($WhatIf) { 'WhatIf (no copies)' } else { 'COPY' })"
Write-Host ''

$copied = 0
foreach ($tf in $termFolders) {
    $srcTerm = Join-Path $panelExam $tf.Panel
    if (-not (Test-Path -LiteralPath $srcTerm)) { continue }

    Get-ChildItem -LiteralPath $srcTerm -File -Force | ForEach-Object {
        $cat = Get-RepoCategory $_.Name
        $repoBase = if ($cat -eq '_assets') { $repoAssessments } else { $repoPastPapers }
        $dest = Join-Path $repoBase (Join-Path $tf.Repo $cat)
        $target = Join-Path $dest $_.Name

        if ($WhatIf) {
            Write-Host "[WhatIf] $($_.FullName) -> $target"
        } else {
            if (-not (Test-Path -LiteralPath $dest)) {
                New-Item -ItemType Directory -Path $dest -Force | Out-Null
            }
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
            Write-Host "Copied: $($tf.Repo)/$cat/$($_.Name)"
        }
        $copied++
    }
}

if ($copied -eq 0) {
    Write-Warning 'No files matched. Check year or term folder names on panel.'
} else {
    Write-Host ''
    Write-Host "Done. $copied file(s) $(if ($WhatIf) { 'would be copied' } else { 'copied' })."
    if (-not $WhatIf) {
        Write-Host 'Next: git add, commit, and push so files are available at home.'
    }
}
