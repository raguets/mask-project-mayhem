@echo off
setlocal
set "MASK_EDITOR=G:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
set "MASK_PROJECT=%~dp0VehicularCombat\VehicularCombat.uproject"
if not exist "%MASK_EDITOR%" exit /b 1
if not exist "%MASK_PROJECT%" exit /b 1
start "M.A.S.K. Project Mayhem" "%MASK_EDITOR%" "%MASK_PROJECT%" "/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle=Thunderhawk?Bots=3" -game -windowed -ResX=1600 -ResY=900 -nosteam -Multiprocess
