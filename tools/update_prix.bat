@echo off
rem Mise a jour manuelle des prix (double-clic). La version automatique passe par la tache planifiee.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update_prix.ps1"
echo.
echo Mise a jour terminee — voir update_log.txt pour le detail.
pause
