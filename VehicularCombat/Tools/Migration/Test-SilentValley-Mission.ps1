param([string]$RunName=(Get-Date -Format 'yyyyMMdd-HHmmss'),[switch]$Render,[string]$CacheRoot,[int]$TimeoutSeconds=240,[string]$EngineRoot='G:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Simple unique RunName required'}
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out=Join-Path $repo ('Saved/SilentValley/mission-'+$RunName)
$slot='SV_MissionTest_'+$RunName
if((Test-Path $out) -or (Test-Path (Join-Path $repo ('Saved/SaveGames/'+$slot+'.sav')))){throw 'Previous run preserved; choose another RunName'}
New-Item -ItemType Directory -Path $out|Out-Null
$cacheDirectory=if($CacheRoot){[IO.Path]::GetFullPath($CacheRoot)}else{Join-Path $repo 'DerivedDataCache'}
$shaderDirectory=if($CacheRoot){Join-Path $cacheDirectory 'Shaders/WorkingDirectory'}else{Join-Path $repo 'Intermediate/Shaders/WorkingDirectory'}
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle=Thunderhawk','-game','-unattended','-nosound','-nosteam','-nosplash','-windowed','-ResX=1600','-ResY=900','-ExecCmds="t.MaxFPS 30,MASK.SilentValleyMissionTest"',('-MigrationReportDir="'+$out+'"'),('-SVMissionSaveSlot='+$slot),('-AbsLog="'+(Join-Path $out 'game.log')+'"'),'-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+$cacheDirectory+'"'),('-ShaderWorkingDir="'+$shaderDirectory+'"'))
if($Render){$arguments+='-RenderOffscreen'}else{$arguments+=@('-NullRHI','-NoShaderCompile')}
$p=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try{
    @{pid=$p.Id;arguments=$arguments;save_slot=$slot}|ConvertTo-Json -Depth 5|Set-Content (Join-Path $out 'launch.json') -Encoding UTF8
    $end=(Get-Date).AddSeconds($TimeoutSeconds)
    do{$p.Refresh();if($p.HasExited){break};if((Get-Date) -gt $end){throw 'Mission fixture timed out'};Start-Sleep -Seconds 1}while($true)
    $r=Get-Content (Join-Path $out 'mission.json') -Raw|ConvertFrom-Json
    @{passed=($r.passed -and $p.ExitCode -eq 0);exit_code=$p.ExitCode;report=$r}|ConvertTo-Json -Depth 10|Set-Content (Join-Path $out 'summary.json') -Encoding UTF8
    Write-Output "REPORT=$out PASSED=$($r.passed) EXIT=$($p.ExitCode)"
    if(!$r.passed -or $p.ExitCode -ne 0){throw 'Mission fixture failed; inspect report and game.log'}
}finally{$p.Refresh();if(!$p.HasExited){Stop-Process -Id $p.Id};$p.Dispose()}
