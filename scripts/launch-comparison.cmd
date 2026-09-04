@echo off
setlocal

where pwsh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    pwsh -NoProfile -File "%~dp0launch-comparison.ps1" %*
) else (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch-comparison.ps1" %*
)

exit /b %ERRORLEVEL%
