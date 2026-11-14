param([string]$RunName='manta-import-r1',[string]$Revision='',[switch]$NullRHI,[switch]$ReadOnly,[string]$EngineRoot='G:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple run name.'}
if($Revision){if($Revision -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple revision.'};$RunName+='-'+$Revision}
$actualRun=if($ReadOnly){$RunName+'-readback-'+(Get-Date -Format 'HHmmss')}else{$RunName}
$out=Join-Path $repo ('Saved/Art/'+$actualRun)
if(Test-Path -LiteralPath $out){throw 'Choose a new RunName.'}
New-Item -ItemType Directory -Path $out | Out-Null
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'-Unattended','-NoSound','-NoSplash','-run=pythonscript','-NullRHI','-NoShaderCompile','-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+(Join-Path $repo 'DerivedDataCache')+'"'),('-ShaderWorkingDir="'+(Join-Path $repo 'Intermediate/Shaders/WorkingDirectory')+'"'),('-AbsLog="'+(Join-Path $out 'editor.log')+'"'),('-script="'+(Join-Path $repo 'Tools/Art/import_manta_all.py')+'"'))
$arguments+='-Multiprocess'
if($ReadOnly){$arguments=$arguments | ForEach-Object { $_.Replace('import_manta_all.py','inspect_manta_saved.py') }}
if($NullRHI){$arguments+=@('-NullRHI','-NoShaderCompile')}
$p=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe') -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
@{pid=$p.Id;arguments=$arguments}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $out 'launch.json') -Encoding UTF8
try{
    if(!$p.WaitForExit(900000)){Stop-Process -Id $p.Id;throw 'Manta import timed out.'}
    $p.Refresh();Write-Output ('EDITOR_EXIT='+$p.ExitCode)
    foreach($file in @('manta-import.json','manta-locomotion-import.json','manta-finalize.json')){ $report=Get-Content -Raw -LiteralPath (Join-Path $repo ('Saved/Art/'+$file))|ConvertFrom-Json;if(!$report.passed){throw "Import failed: $file"};Write-Output ($file+' PASSED') }
    if($p.ExitCode -ne 0){throw 'Editor import failed.'}
}finally{$p.Dispose()}
