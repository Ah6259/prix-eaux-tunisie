# Mise à jour automatique des prix — lancé par la tâche planifiée Windows "PrixEauxTunisie-MAJ"
# (ou à la main : update_prix.bat). Journal : tools/update_log.txt
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$log = Join-Path $PSScriptRoot "update_log.txt"

"=== Mise a jour du $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" | Add-Content $log

$py = "C:\Users\ahmed\AppData\Local\Programs\Python\Python314\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

& $py -u collect_prices.py 2>&1 | Add-Content $log
& $py -u build_history.py  2>&1 | Add-Content $log

"=== Fin $(Get-Date -Format 'HH:mm') ===`r`n" | Add-Content $log
