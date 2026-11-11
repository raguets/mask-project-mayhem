param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Build','BuildGame','Blueprints','Assets','Network','NetworkRender','Editor','Play','Solo','TestSolo')]
    [string]$Task,
    [string]$EngineRoot = 'G:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $repo 'VehicularCombat.uproject'
$engineVersion = Get-Content -Raw -LiteralPath (Join-Path $EngineRoot 'Engine\Build\Build.version') | ConvertFrom-Json
if ($engineVersion.MajorVersion -ne 5 -or $engineVersion.MinorVersion -ne 8) { throw 'An installed Unreal Engine 5.8 is required; this script installs nothing.' }
$logs = Join-Path $repo 'Saved\Migration'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
Push-Location -LiteralPath $repo
try {
    switch ($Task) {
        { $_ -in 'Build','BuildGame' } {
            $target = if ($Task -eq 'Build') { 'VehicularCombatEditor' } else { 'VehicularCombat' }
            $log = Join-Path $logs ($target + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
            & (Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat') $target Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE -Unattended "-Log=$log"
            if ($LASTEXITCODE -ne 0) { throw "UBT failed ($LASTEXITCODE). See $log" }
        }
        { $_ -in 'Blueprints','Assets' } {
            $ueArguments = @($project, '-NullRHI', '-Unattended', '-NoSound', '-NoSplash', '-NoShaderCompile', '-stdout', '-FullStdOutLogOutput')
            if ($Task -eq 'Blueprints') {
                # CompileAllBlueprints has no ProjectOnly flag in this engine.
                $assets = Get-ChildItem -LiteralPath (Join-Path $repo 'Content') -Recurse -File -Filter '*.uasset' | Sort-Object FullName | ForEach-Object {
                    $relative = $_.FullName.Substring((Join-Path $repo 'Content').Length + 1).Replace([char]92,[char]47)
                    '/Game/' + $relative.Substring(0, $relative.Length - 7) + '.' + $_.BaseName
                }
                $assets | Set-Content -Encoding ASCII -LiteralPath (Join-Path $PSScriptRoot 'project-assets.allowlist')
                $ueArguments += @('-run=CompileAllBlueprints', '-AllowListFile=Tools/Migration/project-assets.allowlist')
            }
            else { $ueArguments += @('-run=DataValidation', '-IncludeOnlyOnDiskAssets') }
            $ueArguments += '-AbsLog=' + (Join-Path $logs ($Task + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log'))
            & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') @ueArguments
            if ($LASTEXITCODE -ne 0) { throw "$Task commandlet failed ($LASTEXITCODE); inspect Saved/Migration." }
        }
        'Network' { & (Join-Path $PSScriptRoot 'Test-TwoPlayers.ps1') -EngineRoot $EngineRoot }
        'NetworkRender' { & (Join-Path $PSScriptRoot 'Test-TwoPlayers.ps1') -EngineRoot $EngineRoot -RenderHost }
        'Editor' { & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') $project }
        'Play' { & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') $project '-game' '-windowed' }
        'Solo' { & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') $project '/Game/Maps/TestMaps/Test?Bots=3' '-game' '-windowed' }
        'TestSolo' { & (Join-Path $PSScriptRoot 'Test-Solo.ps1') -EngineRoot $EngineRoot -Render }
    }
}
finally { Pop-Location }
