param(
    [string]$EngineRoot='G:\Program Files\Epic Games\UE_5.8',
    [string]$RunName=(Get-Date -Format 'yyyyMMdd-HHmmss'),
    [string]$GameExecutable,
    [switch]$Network,
    [switch]$Render,
    [switch]$WorkspaceCache,
    [string]$CacheRoot,
    [switch]$Terrain,
    [ValidateSet('Thunderhawk','Rhino','Hurricane','Raven')][string]$Vehicle='Thunderhawk',
    [int]$TimeoutSeconds=360
)
$ErrorActionPreference='Stop'
if($Terrain -and ($Network -or $GameExecutable)) { throw 'Terrain probe currently requires a solo editor game.' }
if($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'Use a simple RunName.' }
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$report=Join-Path $repo "Saved\Migration\onfoot-$RunName"
if(Test-Path -LiteralPath $report) { throw 'Choose a new RunName; prior reports are preserved.' }
New-Item -ItemType Directory -Path $report | Out-Null
$exe=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if($GameExecutable) { $exe=[IO.Path]::GetFullPath($GameExecutable) }
$roles=@(if($Network) { 'host';'client' } else { 'solo' })
$processes=@();$launch=@()
try {
    foreach($role in $roles) {
        $url=if($role -eq 'client') { '127.0.0.1' } elseif($role -eq 'host') { '/Game/Maps/TestMaps/Test?Vehicle=Thunderhawk?listen' } else { '/Game/Maps/TestMaps/Test?Vehicle=Thunderhawk' }
        if($Terrain) { $url='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle='+$Vehicle+'?Mission=0' }
        $arguments=@($url,'-unattended','-nosound','-nosteam','-nosplash','-windowed','-ResX=1280','-ResY=720','-NoVSync',
            ('-ExecCmds="t.MaxFPS 30,MASK.OnFootSmoke '+$role+'"'),('-MigrationReportDir="'+$report+'"'),('-AbsLog="'+(Join-Path $report ($role+'.log'))+'"'))
        if(!$GameExecutable) { $arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'-game')+$arguments }
        if($Render) { $arguments+='-RenderOffscreen' } else { $arguments+=@('-NullRHI','-NoShaderCompile') }
        $arguments+='-Multiprocess'
        if($WorkspaceCache -or $CacheRoot) {
            $cacheDirectory=if($CacheRoot){[IO.Path]::GetFullPath($CacheRoot)}else{Join-Path $repo 'DerivedDataCache'}
            $arguments+=@('-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+$cacheDirectory+'"'),('-ShaderWorkingDir="'+(Join-Path $cacheDirectory 'Shaders/WorkingDirectory')+'"'))
        }
        if($Terrain) { $arguments+='-OnFootTerrain' }
        $p=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
        $processes+=$p;$launch+=[ordered]@{role=$role;pid=$p.Id;executable=$exe;arguments=$arguments}
        if($role -eq 'host') {
            $deadline=(Get-Date).AddSeconds($TimeoutSeconds)
            while(!(Test-Path -LiteralPath (Join-Path $report 'host.ready'))) {
                $p.Refresh();if($p.HasExited -or (Get-Date) -gt $deadline) { throw 'Host did not start; inspect its log.' };Start-Sleep -Seconds 1
            }
        }
    }
    $launch|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 (Join-Path $report 'launch.json')
    $deadline=(Get-Date).AddSeconds($TimeoutSeconds)
    while((Get-Date) -lt $deadline) {
        foreach($p in $processes) { $p.Refresh() }
        if(@($processes|Where-Object {!$_.HasExited}).Count -eq 0) { break };Start-Sleep -Seconds 1
    }
    $summary=[ordered]@{passed=$true;report_directory=$report;roles=@()}
    for($i=0;$i -lt $processes.Count;$i++) {
        $p=$processes[$i];$p.Refresh();if(!$p.HasExited) { Stop-Process -Id $p.Id;throw 'On-foot test timed out.' }
        $data=Get-Content -LiteralPath (Join-Path $report ($roles[$i]+'.json')) -Raw|ConvertFrom-Json
        $summary.passed=$summary.passed -and $data.passed -and ($p.ExitCode -eq 0)
        $summary.roles+=[ordered]@{role=$roles[$i];exit_code=$p.ExitCode;report=$data}
    }
    $summary|ConvertTo-Json -Depth 15|Set-Content -Encoding UTF8 (Join-Path $report 'summary.json')
    Write-Output "REPORT=$report PASSED=$($summary.passed)"
    if(!$summary.passed) { throw 'On-foot validation failed; inspect the report.' }
}
finally { foreach($p in $processes) { $p.Refresh();if(!$p.HasExited) { Stop-Process -Id $p.Id };$p.Dispose() } }
