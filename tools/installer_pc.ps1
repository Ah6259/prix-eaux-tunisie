# Réinstalle sur un NOUVEAU PC (après vol, panne ou changement d'ordinateur) la tâche
# planifiée qui relève chaque jour à midi les prix Otrity (bloqués par Cloudflare sur GitHub).
#
# Prérequis (à installer d'abord, avec accord) : Python, Git, GitHub CLI (gh), puis
#   gh auth login            (se connecter au compte GitHub Ah6259)
#   gh repo clone Ah6259/prix-eaux-tunisie
# Ensuite, dans le dossier du site :
#   powershell -ExecutionPolicy Bypass -File tools\installer_pc.ps1
#
# Sans ce PC, le site continue de fonctionner : seuls les prix Otrity disparaissent
# (au bout de 3 jours), tout le reste tourne sur les serveurs de GitHub.

$ErrorActionPreference = "Stop"
$racine = Split-Path -Parent $PSScriptRoot
$script = Join-Path $racine "tools\otrity_local.py"

$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { throw "Python introuvable : installez-le d'abord (python.org ou Microsoft Store)." }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git introuvable : installez-le d'abord (git-scm.com)." }
if (-not (Test-Path "C:\Program Files\GitHub CLI\gh.exe")) { throw "GitHub CLI introuvable : installez-le puis lancez « gh auth login »." }

$action   = New-ScheduledTaskAction -Execute $py -Argument "`"$script`"" -WorkingDirectory $racine
$trigger  = New-ScheduledTaskTrigger -Daily -At 12:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
              -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "PrixEaux-Otrity" -Force `
  -Description "Releve quotidien des prix Otrity pour le site prix-eaux-tunisie (tools\otrity_local.py)" `
  -Action $action -Trigger $trigger -Settings $settings | Out-Null

Write-Host "Tâche « PrixEaux-Otrity » installée (chaque jour à 12h). Premier relevé maintenant…"
& $py $script
