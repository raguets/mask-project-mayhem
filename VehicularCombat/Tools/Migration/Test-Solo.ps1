param(
    [string]$EngineRoot = 'G:\Program Files\Epic Games\UE_5.8',
    [string]$RunName = (Get-Date -Format 'yyyyMMdd-HHmmss'),
    [string]$GameExecutable,
    [switch]$Render,
    [switch]$Thunderhawk,
    [int]$TimeoutSeconds = 900
)
$ErrorActionPreference = 'Stop'
if ($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunName must be a simple folder name.' }
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$report = Join-Path $repo "Saved\Migration\training-$RunName"
if (Test-Path -LiteralPath $report) { throw 'Choose a new RunName; previous reports are preserved.' }
New-Item -ItemType Directory -Path $report | Out-Null
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$arguments = @(('"' + (Join-Path $repo 'VehicularCombat.uproject') + '"'), '/Game/Maps/MainMenu', '-game', '-unattended', '-nosound', '-nosteam', '-nosplash', '-windowed', '-ResX=1280', '-ResY=720', '-NoVSync', '-ExecCmds="t.MaxFPS 30,VC.TrainingSmoke"', ('-MigrationReportDir="' + $report + '"'), ('-AbsLog="' + (Join-Path $report 'game.log') + '"'))
if ($GameExecutable) {
    $editor = [IO.Path]::GetFullPath($GameExecutable)
    if (!(Test-Path -LiteralPath $editor)) { throw "Packaged executable absent: $editor" }
    # Cooked games must use their own staged content, without an external project.
    $arguments = @($arguments | Where-Object { $_ -ne '-game' -and $_ -notlike '*.uproject"' })
}
if ($Render) { $arguments += '-RenderOffscreen' } else { $arguments += @('-NullRHI','-NoShaderCompile') }
if ($Thunderhawk) { $arguments += '-MaskThunderhawk' }
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try {
    [ordered]@{ executable = $editor; arguments = $arguments; pid = $process.Id } | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $report 'launch.json')
    if (!$process.WaitForExit($TimeoutSeconds * 1000)) { Stop-Process -Id $process.Id; throw "Training test timed out: $report" }
    $process.Refresh()
    $result = Get-Content -Raw -LiteralPath (Join-Path $report 'training.json') | ConvertFrom-Json
    $summary = [ordered]@{ passed = ($result.passed -and $process.ExitCode -eq 0); exit_code = $process.ExitCode; report = $result }
    $summary | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $report 'summary.json')
    Write-Output "REPORT=$report PASSED=$($summary.passed) EXIT=$($process.ExitCode)"
    if (!$summary.passed) { throw "Training validation failed: $report" }
}
finally {
    $process.Refresh()
    if (!$process.HasExited) { Stop-Process -Id $process.Id }
    $process.Dispose()
}
