# Recreate platform symlinks (Windows PowerShell). Run from repo root.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "_platform\shared-tools")) {
    Write-Error "Run first: git submodule update --init --recursive"
}

function Link-Platform {
    param([string]$Target, [string]$LinkPath)
    if ((Test-Path $LinkPath) -and -not (Get-Item $LinkPath).Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) {
        Write-Warning "Skip $LinkPath (exists, not a symlink)"
        return
    }
    if (Test-Path $LinkPath) { Remove-Item $LinkPath -Force }
    New-Item -ItemType SymbolicLink -Path $LinkPath -Target $Target | Out-Null
    Write-Host "Linked $LinkPath -> $Target"
}

Link-Platform "_platform\shared-tools" "shared-tools"
Link-Platform "_platform\templates" "templates"

# Cursor skills
Link-Platform "_platform\.cursor\skills\meeting-minutes" ".cursor\skills\meeting-minutes"
Link-Platform "_platform\.cursor\skills\_template" ".cursor\skills\_template"
Link-Platform "_platform\.cursor\skills\tidy-up" ".cursor\skills\tidy-up"

# Cursor rules (platform-level, always-apply)
if (-not (Test-Path ".cursor\rules")) { New-Item -ItemType Directory -Path ".cursor\rules" | Out-Null }
Link-Platform "_platform\.cursor\rules\privacy.mdc" ".cursor\rules\privacy.mdc"

Write-Host "Platform symlinks OK."
Write-Host "Note: CLAUDE.md already imports _platform/CLAUDE.md via @_platform/CLAUDE.md — no symlink needed."
