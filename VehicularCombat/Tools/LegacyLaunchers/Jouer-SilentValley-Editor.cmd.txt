@echo off
setlocal
set "SV_VEHICLE=%~1"
if "%SV_VEHICLE%"=="" set "SV_VEHICLE=Thunderhawk"
if /I "%SV_VEHICLE%"=="Thunderhawk" goto valid
if /I "%SV_VEHICLE%"=="Rhino" goto valid
if /I "%SV_VEHICLE%"=="Hurricane" goto valid
echo Choisir Thunderhawk, Rhino ou Hurricane.
exit /b 1
:valid
set "SV_EDITOR=G:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%SV_EDITOR%" (
  echo Utiliser Unreal Engine 5.8 pour ouvrir VehicularCombat.uproject.
  exit /b 1
)
start "" "%SV_EDITOR%" "%~dp0VehicularCombat.uproject" "/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle=%SV_VEHICLE%" -game -windowed -ResX=1600 -ResY=900 -nosteam
