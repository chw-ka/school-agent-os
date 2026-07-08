param(
    [string]$Period = "T1",  # T1 or T2
    [string]$DownloadsZip = "$env:USERPROFILE\Downloads\OTHERS_T1.zip",
    [string]$LocalDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..\cloudsams-templates\asr\_local")).Path,
    [string[]]$ExpectLevels = @("S1","S2","S3","S4","S5","S6")  # T2: use -ExpectLevels S1,S2,S3,S4,S5
)

$dest = Join-Path $LocalDir "whole-school-$Period-others-export.zip"
if (-not (Test-Path $DownloadsZip)) { throw "Missing $DownloadsZip" }
$srcTime = (Get-Item $DownloadsZip).LastWriteTime
Copy-Item -Force $DownloadsZip $dest
Write-Host "Copied -> $dest ($((Get-Item $dest).Length) bytes, src time $srcTime)"

$verify = Join-Path $LocalDir "_verify-whole-school-$Period"
if (Test-Path $verify) { Remove-Item -Recurse -Force $verify }
New-Item -ItemType Directory -Path $verify | Out-Null

$levelsJson = ($ExpectLevels | ConvertTo-Json -Compress)
python -c @"
import json, sys
from pathlib import Path
import pyzipper

pwd = b'EvanGelisTic1617!'
src = Path(r'$dest')
work = Path(r'$verify')
expect = set(json.loads(r'''$levelsJson'''))

with pyzipper.AESZipFile(src) as z:
    z.extractall(work, pwd=pwd)

inner = sorted(work.glob('*.zip'))
found = set()
for iz in inner:
    for lvl in expect:
        if f'_{lvl}_' in iz.name:
            found.add(lvl)
            break

print(f'Inner class zips: {len(inner)}')
for iz in inner[:8]:
    print(f'  {iz.name}')
if len(inner) > 8:
    print(f'  ... +{len(inner)-8} more')
missing = sorted(expect - found)
if missing:
    print('ERROR missing levels:', missing, file=sys.stderr)
    sys.exit(1)
print('OK whole-school', ','.join(sorted(found)))
"@
