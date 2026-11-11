param(
    [string]$RunName=(Get-Date -Format 'yyyyMMdd-HHmmss'),
    [switch]$Profile,
    [switch]$WorkspaceCache,
    [switch]$Environment,
    [switch]$Motion,
    [string]$CacheRoot,
    [string]$ExtraConsoleCommands,
    [int]$TimeoutSeconds=600,
    [string]$EngineRoot='G:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference='Stop'
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Simple RunName required'}
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$env:DOTNET_EnableDiagnostics='0'
$env:DOTNET_CLI_HOME=Join-Path $repo 'Intermediate/DotNetHome'
$out=Join-Path $repo "Saved\SilentValley\views-$RunName"
if(Test-Path -LiteralPath $out){throw 'Previous captures preserved; choose another RunName'}
New-Item -ItemType Directory -Path $out|Out-Null
$commands='r.SetRes 1600x900w,DisableAllScreenMessages,t.MaxFPS,r.VSync,sg.ViewDistanceQuality,sg.ShadowQuality,sg.GlobalIlluminationQuality,sg.ReflectionQuality,sg.FoliageQuality,MASK.SilentValleyViews'
if($Motion){$commands=$commands.Replace('MASK.SilentValleyViews','MASK.SilentValleyMotion')}
if($Profile){$commands+=',csvprofile STARTFILE=SilentValley-'+$RunName+'.csv,csvprofile FRAMES=1200'}
if($Environment -or $Motion){$commands+=',t.MaxFPS 30'}
if($ExtraConsoleCommands){$commands+=','+$ExtraConsoleCommands}
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle=Thunderhawk?Mission=0','-game','-unattended','-nosteam','-nosound','-nosplash','-RenderOffscreen','-windowed','-ResX=1600','-ResY=900',('-ExecCmds="'+$commands+'"'),('-MigrationReportDir="'+$out+'"'),('-AbsLog="'+(Join-Path $out 'game.log')+'"'))
# Compiled editor rendering needs no SDK validation child process. In restricted
# sessions that .NET child can stall on a crash dialog (TargetPlatformManager).
$arguments+=@('-ForceRes','-SVShowcaseViews','-Multiprocess')
if($Environment){$arguments+='-SVEnvironmentViews'}
if($WorkspaceCache){
    $cacheDirectory=if($CacheRoot){[IO.Path]::GetFullPath($CacheRoot)}else{Join-Path $repo 'DerivedDataCache'}
    $shaderDirectory=if($CacheRoot){Join-Path $cacheDirectory 'Shaders/WorkingDirectory'}else{Join-Path $repo 'Intermediate/Shaders/WorkingDirectory'}
    $arguments+=@('-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+$cacheDirectory+'"'),('-ShaderWorkingDir="'+$shaderDirectory+'"'))
}
# No benchmark/fixed timestep: these are actual rendered frames. Camera cuts,
# screenshots and shader warmup still affect this diagnostic sample.
$p=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try{
    [ordered]@{arguments=$arguments;pid=$p.Id;profile=$Profile.IsPresent;resolution='1600x900';fixed_timestep=$false}|ConvertTo-Json -Depth 4|Set-Content -Encoding UTF8 (Join-Path $out 'launch.json')
    $end=(Get-Date).AddSeconds($TimeoutSeconds)
    do{$p.Refresh();if($p.HasExited){break};if((Get-Date) -gt $end){throw 'Capture timeout'};Start-Sleep -Seconds 1}while($true)
    $images=@(Get-ChildItem -LiteralPath $out -Filter '*.png')
    $expectedImages=if($Motion){20}else{10}
    if($p.ExitCode -ne 0 -or $images.Count -ne $expectedImages){throw "Capture failed: exit=$($p.ExitCode), images=$($images.Count)"}
    Write-Output "CAPTURES=$out IMAGES=$($images.Count) EXIT=$($p.ExitCode)"
}finally{$p.Refresh();if(!$p.HasExited){Stop-Process -Id $p.Id};$p.Dispose()}
