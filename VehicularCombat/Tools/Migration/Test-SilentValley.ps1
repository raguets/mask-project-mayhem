param(
    [ValidateSet('Thunderhawk','Rhino','Hurricane','Raven')][string]$Vehicle='Thunderhawk',
    [string]$RunName=(Get-Date -Format 'yyyyMMdd-HHmmss'),
    [switch]$Render,
    [switch]$Fast,
    [switch]$FullRoute,
    [switch]$WorkspaceCache,
    [string]$CacheRoot,
    [int]$TimeoutSeconds=960,
    [string]$EngineRoot='G:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference='Stop'
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Simple RunName required'}
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'));$out=Join-Path $repo "Saved\SilentValley\drive-$RunName-$Vehicle"
$env:DOTNET_EnableDiagnostics='0'
$env:DOTNET_CLI_HOME=Join-Path $repo 'Intermediate/DotNetHome'
if(Test-Path -LiteralPath $out){throw 'Previous run preserved; choose another RunName'}
New-Item -ItemType Directory -Path $out|Out-Null
if(!(Test-Path -LiteralPath (Join-Path $repo 'Content/MASK/Environment/SilentValley/Structures/BP_SilentValleyGameMode.uasset'))){throw 'New GameMode not created; finish the editor build before testing driving.'}
$exe=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle='+$Vehicle+'?Mission=0'),'-game','-unattended','-nosteam','-nosound','-nosplash','-windowed','-ResX=1280','-ResY=720',('-ExecCmds="MASK.SilentValleyDrive '+$Vehicle+'"'),('-MigrationReportDir="'+$out+'"'),('-AbsLog="'+(Join-Path $out 'game.log')+'"'))
if($Render){$arguments+='-RenderOffscreen'}else{$arguments+=@('-NullRHI','-NoShaderCompile')}
if($Fast){$arguments+=@('-benchmark','-fps=60','-usefixedtimestep')}
if($FullRoute){$arguments+='-SVFullRoute'}
$arguments+='-Multiprocess'
if($WorkspaceCache){
    # Opt-in for restricted sessions; keep the user's global caches/settings intact.
    $cacheDirectory=if($CacheRoot){[IO.Path]::GetFullPath($CacheRoot)}else{Join-Path $repo 'DerivedDataCache'}
    $shaderDirectory=if($CacheRoot){Join-Path $cacheDirectory 'Shaders/WorkingDirectory'}else{Join-Path $repo 'Intermediate/Shaders/WorkingDirectory'}
    $arguments+=@('-DDC=InstalledNoZenLocalFallback',
        ('-LocalDataCachePath="'+$cacheDirectory+'"'),
        ('-ShaderWorkingDir="'+$shaderDirectory+'"'))
}
$p=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try{
    [ordered]@{executable=$exe;arguments=$arguments;pid=$p.Id}|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 (Join-Path $out 'launch.json')
    $end=(Get-Date).AddSeconds($TimeoutSeconds)
    do{$p.Refresh();if($p.HasExited){break};if((Get-Date) -gt $end){Stop-Process -Id $p.Id;throw 'Drive timed out'};Start-Sleep -Seconds 1}while($true)
    $reportPath=Join-Path $out 'drive.json'
    if(!(Test-Path -LiteralPath $reportPath)){
        $failure='Unreal exited before producing drive.json; driving was not validated. Inspect game.log.'
        [ordered]@{passed=$false;exit_code=$p.ExitCode;failure=$failure}|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $out 'summary.json')
        throw "$failure Report directory: $out"
    }
    $r=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
    [ordered]@{passed=($r.passed -and $p.ExitCode -eq 0);exit_code=$p.ExitCode;report=$r}|ConvertTo-Json -Depth 12|Set-Content -Encoding UTF8 (Join-Path $out 'summary.json')
    Write-Output "REPORT=$out PASSED=$($r.passed) EXIT=$($p.ExitCode)";if(!$r.passed -or $p.ExitCode -ne 0){throw 'Physical driving probe failed; inspect report'}
}finally{$p.Refresh();if(!$p.HasExited){Stop-Process -Id $p.Id};$p.Dispose()}
