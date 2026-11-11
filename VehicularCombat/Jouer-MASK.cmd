@echo off
setlocal
set "MASK_GAME_EXE=%~dp0Saved\Packages\MASK-OnFoot-Development-r2\Windows\VehicularCombat\Binaries\Win64\VehicularCombat.exe"
if not exist "%MASK_GAME_EXE%" (
  echo Distribution absente. Voir docs\ON_FOOT_IMPLEMENTATION.md.
  exit /b 1
)
start "" "%MASK_GAME_EXE%" -windowed -ResX=1600 -ResY=900 -nosteam
