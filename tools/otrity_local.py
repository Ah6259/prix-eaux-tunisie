# -*- coding: utf-8 -*-
"""Relevé des prix Otrity DEPUIS LE PC d'Ahmed -> data/otrity.json, puis envoi sur GitHub.

Pourquoi en local : otrity.com est protégé par Cloudflare, qui bloque les serveurs
de GitHub (erreur 403 « Just a moment ») mais laisse passer une connexion de
particulier. Une lecture par jour, comme une visite normale.

Lancé chaque jour à 12h par la tâche planifiée Windows « PrixEaux-Otrity »
(si le PC est éteint à midi : dès qu'il est rallumé). Ensuite :
  1. écrit data/otrity.json (date + offres au format de collect_prices.py)
  2. commit + push de CE SEUL fichier
  3. relance le workflow « Mise à jour des prix » pour publier tout de suite

Le workflow nocturne lit data/otrity.json si Otrity lui est bloqué, et l'ignore
s'il a plus de 3 jours (jamais de prix périmés).

Usage : python tools/otrity_local.py
Journal : tools/otrity_local.log
"""
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import collect_prices  # noqa: E402

OUT = ROOT / "data" / "otrity.json"
LOGO = ROOT / "assets" / "logos" / "otrity.png"   # logo affiché sur le site devant « Otrity »
LOG = ROOT / "tools" / "otrity_local.log"
GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "Ah6259/prix-eaux-tunisie"


def log(msg):
    ligne = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(ligne)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(ligne + "\n")


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(args)} : {r.stderr.strip()}")
    return r.stdout


def chercher_logo():
    """Une seule fois : l'icône officielle du site Otrity (WordPress la donne dans /wp-json/).
    Ne bloque jamais le relevé des prix si ça échoue."""
    if LOGO.exists():
        return False
    try:
        info = json.loads(collect_prices.http_get("https://otrity.com/wp-json/"))
        url = info.get("site_icon_url")
        if not url:
            raise RuntimeError("pas d'icône déclarée")
        LOGO.parent.mkdir(parents=True, exist_ok=True)
        LOGO.write_bytes(collect_prices.http_get(url))
        log(f"logo Otrity téléchargé ({url})")
        return True
    except Exception as e:
        log(f"logo Otrity non trouvé : {e}")
        return False


def main():
    try:
        collect_prices.RAW_DIR.mkdir(parents=True, exist_ok=True)
        offres = collect_prices.otrity()
        if not offres:
            raise RuntimeError("aucune offre trouvée")
    except Exception as e:
        log(f"ÉCHEC lecture Otrity : {e}")
        sys.exit(1)

    OUT.write_text(json.dumps({"date": datetime.date.today().isoformat(), "offres": offres},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"{len(offres)} offres Otrity relevées")
    nouveau_logo = chercher_logo()

    try:
        git("pull", "--rebase", "--autostash", "origin", "main")
        git("add", "data/otrity.json")
        if nouveau_logo:
            git("add", str(LOGO))
        if subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--quiet"]).returncode == 0:
            log("aucun changement à envoyer")
            return
        git("commit", "-m", f"Relevé Otrity depuis le PC ({datetime.date.today()})", "--", "data/otrity.json",
            *([str(LOGO)] if nouveau_logo else []))
        git("push", "origin", "main")
        log("envoyé sur GitHub")
        subprocess.run([GH, "workflow", "run", "maj-prix.yml", "-R", REPO], check=True, capture_output=True)
        log("mise à jour du site relancée")
    except Exception as e:
        log(f"ÉCHEC envoi : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
