param([string]$RunName='switchblade-r1',[string]$Vehicle='Switchblade',[switch]$FleetOnly,[switch]$Render,[string]$EngineRoot='G:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple run name.'}
$out=Join-Path $repo ('Saved/Art/smoke-'+$RunName)
if(Test-Path -LiteralPath $out){throw 'Choose a fresh RunName.'}
New-Item -ItemType Directory -Path $out | Out-Null
$cache=Join-Path $env:TEMP 'MASK_SilentValley_Environment_Cache'
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle='+$Vehicle+'?Bots=5?Mission=0'),'-game','-unattended','-nosound','-nosteam','-nosplash','-windowed','-ResX=1600','-ResY=900','-Multiprocess','-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+$cache+'"'),('-ShaderWorkingDir="'+(Join-Path $cache 'Shaders/WorkingDirectory')+'"'),'-ExecCmds="t.MaxFPS 30,MASK.SwitchbladeSmoke"',('-MigrationReportDir="'+$out+'"'),('-AbsLog="'+(Join-Path $out 'game.log')+'"'))
if($FleetOnly){$arguments+='-SwitchbladeFleetOnly'}
if($Render){$arguments+='-RenderOffscreen'}else{$arguments+=@('-NullRHI','-NoShaderCompile')}
$p=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try{
    @{pid=$p.Id;arguments=$arguments}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $out 'launch.json') -Encoding UTF8
    if(!$p.WaitForExit(480000)){Stop-Process -Id $p.Id;throw 'Switchblade test timed out.'};$p.Refresh()
    $r=Get-Content -Raw -LiteralPath (Join-Path $out 'switchblade.json')|ConvertFrom-Json
    @{passed=($r.passed -and $p.ExitCode -eq 0);exit_code=$p.ExitCode;report=$r}|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding UTF8
    Write-Output ('SWITCHBLADE_PASSED='+$r.passed+' EXIT='+$p.ExitCode)
    if(!$r.passed -or $p.ExitCode -ne 0){throw 'Switchblade validation failed.'}
}finally{$p.Refresh();if(!$p.HasExited){Stop-Process -Id $p.Id};$p.Dispose()}

