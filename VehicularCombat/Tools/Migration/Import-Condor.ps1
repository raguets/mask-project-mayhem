param([string]$RunName='condor-import-r1',[string]$EngineRoot='G:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if($RunName -notmatch '^[A-Za-z0-9_-]+$'){throw 'Use a simple run name.'}
$out=Join-Path $repo ('Saved/Art/'+$RunName)
if(Test-Path -LiteralPath $out){throw 'Choose a fresh RunName.'}
New-Item -ItemType Directory -Path $out | Out-Null
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'-Unattended','-NoSound','-NoSplash','-run=pythonscript','-NullRHI','-NoShaderCompile','-Multiprocess','-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+(Join-Path $repo 'DerivedDataCache')+'"'),('-ShaderWorkingDir="'+(Join-Path $repo 'Intermediate/Shaders/WorkingDirectory')+'"'),('-AbsLog="'+(Join-Path $out 'editor.log')+'"'),('-script="'+(Join-Path $repo 'Tools/Art/import_condor_all.py')+'"'))
$p=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe') -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
@{pid=$p.Id;arguments=$arguments}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $out 'launch.json') -Encoding UTF8
try{
    if(!$p.WaitForExit(900000)){Stop-Process -Id $p.Id;throw 'Condor import timed out.'}
    $p.Refresh();Write-Output ('EDITOR_EXIT='+$p.ExitCode)
    foreach($file in @('condor-import.json','condor-locomotion-import.json','condor-finalize.json')){ $r=Get-Content -Raw -LiteralPath (Join-Path $repo ('Saved/Art/'+$file))|ConvertFrom-Json;if(!$r.passed){throw "Import failed: $file"};Write-Output ($file+' PASSED') }
    if($p.ExitCode -ne 0){throw 'Editor import failed.'}
}finally{$p.Dispose()}


