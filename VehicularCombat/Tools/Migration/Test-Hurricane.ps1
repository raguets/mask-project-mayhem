param(
    [string]$EngineRoot='G:\Program Files\Epic Games\UE_5.8',
    [string]$RunName=(Get-Date -Format 'yyyyMMdd-HHmmss'),
    [string]$GameExecutable,
    [switch]$Render,
    [switch]$WheelProbe,
    [int]$TimeoutSeconds=300
)
$ErrorActionPreference='Stop'
if($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'Use a simple RunName.' }
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$report=Join-Path $repo "Saved\Art\hurricane-$RunName"
if(Test-Path -LiteralPath $report) { throw 'Choose a new RunName to preserve reports.' }
New-Item -ItemType Directory -Path $report | Out-Null
$exe=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'/Game/Maps/TestMaps/Test?Vehicle=Hurricane','-game')
if($GameExecutable) { $exe=[IO.Path]::GetFullPath($GameExecutable);$arguments=@('/Game/Maps/TestMaps/Test?Vehicle=Hurricane') }
$command=if($WheelProbe) {'MASK.HurricaneWheelProbe'} else {'MASK.HurricaneSmoke'}
$arguments+=@('-unattended','-nosound','-nosteam','-nosplash','-windowed','-ResX=1280','-ResY=720','-NoVSync',
    ('-ExecCmds="t.MaxFPS 30,'+$command+'"'),('-MigrationReportDir="'+$report+'"'),('-AbsLog="'+(Join-Path $report 'game.log')+'"'))
if($Render) { $arguments+='-RenderOffscreen' } else { $arguments+=@('-NullRHI','-NoShaderCompile') }
$process=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try {
    [ordered]@{executable=$exe;arguments=$arguments;pid=$process.Id} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $report 'launch.json')
    if(!$process.WaitForExit($TimeoutSeconds*1000)) { Stop-Process -Id $process.Id;throw "Hurricane timed out: $report" }
    $process.Refresh();$data=Get-Content -Raw -LiteralPath (Join-Path $report 'hurricane.json') | ConvertFrom-Json
    $summary=[ordered]@{passed=($data.passed -and $process.ExitCode -eq 0);exit_code=$process.ExitCode;report=$data}
    $summary | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $report 'summary.json')
    Write-Output "REPORT=$report PASSED=$($summary.passed) EXIT=$($process.ExitCode)"
    if(!$summary.passed) { throw "Hurricane validation failed: $report" }
}
finally { $process.Refresh();if(!$process.HasExited) { Stop-Process -Id $process.Id };$process.Dispose() }
