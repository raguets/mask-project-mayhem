param(
    [string]$EngineRoot = 'G:\Program Files\Epic Games\UE_5.8',
    [string]$RunName = (Get-Date -Format 'yyyyMMdd-HHmmss'),
    [string]$GameExecutable,
    [switch]$RenderHost,
    [switch]$MenuButtons,
    [switch]$Thunderhawk,
    [switch]$Fleet,
    [switch]$Hurricane,
    [switch]$DockFixture,
    [int]$TimeoutSeconds = 900
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $repo 'VehicularCombat.uproject'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if ($GameExecutable) { $editor = [IO.Path]::GetFullPath($GameExecutable) }
if (!(Test-Path -LiteralPath $editor)) { throw "Unreal Editor absent: $editor" }
if ($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunName must be a simple folder name.' }
$reportDir = Join-Path $repo "Saved\Migration\runs\$RunName"
if (Test-Path -LiteralPath $reportDir) { throw "Use a new RunName; existing results are preserved: $reportDir" }
New-Item -ItemType Directory -Path $reportDir | Out-Null
$processes = @()
$commands = @()
try {
    foreach ($role in @('Host', 'Client')) {
        $arguments = @(('"' + $project + '"'), '/Game/Maps/MainMenu', '-game', '-unattended', '-nosplash', '-nosound', '-nosteam', '-windowed', '-ResX=1280', '-ResY=720', '-NoVSync')
        if ($GameExecutable) { $arguments = @($arguments | Where-Object { $_ -ne '-game' -and $_ -notlike '*.uproject"' }) }
        $arguments += '-MigrationReportDir="' + $reportDir + '"'
        $arguments += '-AbsLog="' + (Join-Path $reportDir ($role.ToLower() + '.log')) + '"'
        $arguments += '-ExecCmds="t.MaxFPS 30,VC.MigrationSmoke ' + $role + '"'
        if ($MenuButtons) { $arguments += '-MigrationMenuButtons' }
        if ($Thunderhawk -or $Fleet -or $Hurricane) { $arguments += '-MaskThunderhawk' }
        if ($Fleet -or $Hurricane) { $arguments += '-MaskFleet' }
        if ($Hurricane) { $arguments += '-MaskHurricane' }
        if ($DockFixture) { $arguments += '-FleetDockFixture' }
        if ($role -eq 'Client' -or !$RenderHost) { $arguments += @('-NullRHI', '-NoShaderCompile') }
        else { $arguments += '-RenderOffscreen' }
        $process = Start-Process -FilePath $editor -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
        $processes += $process
        $commands += [ordered]@{ role = $role; pid = $process.Id; executable = $editor; arguments = $arguments }
        Write-Output "$role PID=$($process.Id)"
        if ($role -eq 'Host') {
            # A first graphics launch may compile global shaders for minutes.
            # The probe writes this file only once the game loop has started.
            $warmupDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
            while (!(Test-Path -LiteralPath (Join-Path $reportDir 'host.json'))) {
                $process.Refresh()
                if ($process.HasExited) { throw 'Host exited before its game loop started; inspect host.log.' }
                if ((Get-Date) -gt $warmupDeadline) { throw 'Host shader/startup warmup timed out.' }
                Start-Sleep -Seconds 1
            }
        }
        Start-Sleep -Seconds 1
    }
    $commands | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $reportDir 'launch.json')
    Write-Output "RUN_DIR=$reportDir"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        foreach ($process in $processes) { $process.Refresh() }
        if (@($processes | Where-Object { !$_.HasExited }).Count -eq 0) { break }
        Start-Sleep -Seconds 1
    }
    $result = [ordered]@{ passed = $true; report_directory = $reportDir; roles = @() }
    foreach ($index in 0..1) {
        $process = $processes[$index]; $process.Refresh()
        if (!$process.HasExited) { Stop-Process -Id $process.Id; $result.passed = $false }
        $process.WaitForExit()
        $role = @('host','client')[$index]
        $path = Join-Path $reportDir ($role + '.json')
        $report = if (Test-Path -LiteralPath $path) { Get-Content -Raw -LiteralPath $path | ConvertFrom-Json } else { $null }
        $impactLog = Join-Path $reportDir ($role + '.log')
        $localImpacts = @(Select-String -LiteralPath $impactLog -Pattern 'VC_IMPACT_LOCAL.*configured=1').Count
        $expiryEffects = @(Select-String -LiteralPath $impactLog -Pattern 'VC_EXPIRY_LOCAL.*configured=1').Count
        $entry = [ordered]@{ role = $role; exit_code = $process.ExitCode; configured_local_impact_events = $localImpacts; configured_expiry_effect_events = $expiryEffects; report = $report }
        $result.roles += $entry
        if (!$report -or !$report.passed -or $process.ExitCode -ne 0 -or $localImpacts -eq 0) { $result.passed = $false }
    }
    $result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $reportDir 'summary.json')
    Write-Output "PASSED=$($result.passed)"
    if (!$result.passed) { exit 1 }
}
finally {
    foreach ($process in $processes) {
        $process.Refresh()
        if (!$process.HasExited) { Stop-Process -Id $process.Id }
        $process.Dispose()
    }
}
