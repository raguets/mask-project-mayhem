param(
    [string]$EngineRoot = 'G:\Program Files\Epic Games\UE_5.8',
    [string]$RunName = (Get-Date -Format 'yyyyMMdd-HHmmss')
)
$ErrorActionPreference = 'Stop'
if ($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunName must be a simple folder name.' }
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$archive = Join-Path $repo "Saved\Packages\$RunName"
if (Test-Path -LiteralPath $archive) { throw 'Choose a new RunName to preserve prior packages.' }
$log = Join-Path $repo "Saved\Migration\package-$RunName.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
# Build/cook must finish before compiling the Editor DLL again: the cooker loads it.
$args = @('BuildCookRun',('-project='+ (Join-Path $repo 'VehicularCombat.uproject')),'-noP4',
    '-platform=Win64','-clientconfig=Development','-build','-cook','-stage','-pak','-iostore','-archive',
    ('-archivedirectory='+$archive),'-map=/Game/Maps/MainMenu+/Game/Maps/TestMaps/Test','-unattended','-utf8output')
$args | ConvertTo-Json | Set-Content -Encoding UTF8 ($log+'.arguments.json')
& (Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat') @args *> $log
if ($LASTEXITCODE -ne 0) { throw "BuildCookRun failed ($LASTEXITCODE): $log" }
$exe = Join-Path $archive 'Windows\VehicularCombat\Binaries\Win64\VehicularCombat.exe'
if (!(Test-Path -LiteralPath $exe)) { throw "Missing staged executable: $exe" }
Write-Output "PACKAGE=$archive EXECUTABLE=$exe"
