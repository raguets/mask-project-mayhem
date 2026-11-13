$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$cache=Join-Path $env:TEMP 'MASK_SilentValley_Environment_Cache'
$arguments=@(('"'+(Join-Path $repo 'VehicularCombat.uproject')+'"'),'-Unattended','-NoSound','-NoSplash','-run=pythonscript','-NullRHI','-NoShaderCompile','-Multiprocess','-DDC=InstalledNoZenLocalFallback',('-LocalDataCachePath="'+$cache+'"'),('-script="'+(Join-Path $repo 'Tools/Art/tune_air_landings.py')+'"'),('-AbsLog="'+(Join-Path $repo 'Saved/Art/air-landing-tuning.log')+'"'))
$p=Start-Process -FilePath 'G:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru
try { if(!$p.WaitForExit(240000)){Stop-Process -Id $p.Id;throw 'Tuning timed out'};$p.Refresh();if($p.ExitCode -ne 0){throw 'Tuning failed'};Get-Content (Join-Path $repo 'Saved/Art/air-landing-tuning.json') } finally {$p.Dispose()}
