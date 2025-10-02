@echo off
setlocal
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0Run.ps1" %*
exit /b %ERRORLEVEL%
