# Mise à jour automatique des prix — lancé par la tâche planifiée Windows "PrixEauxTunisie-MAJ"
# (ou à la main : update_prix.bat). Journal : tools/update_log.txt
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$log = Join-Path $PSScriptRoot "update_log.txt"

"=== Mise a jour du $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" | Add-Content $log

# vider le cache barka pour forcer un re-téléchargement des pages
Remove-Item -Recurse -Force (Join-Path $PSScriptRoot "pages") -ErrorAction SilentlyContinue

$py = "C:\Users\ahmed\AppData\Local\Programs\Python\Python314\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

& $py -u geant_scrape.py 2>&1 | Add-Content $log
& $py -u barka_scrape.py 2>&1 | Add-Content $log
& $py -u build_data.py   2>&1 | Add-Content $log

"=== Fin $(Get-Date -Format 'HH:mm') ===`r`n" | Add-Content $log
