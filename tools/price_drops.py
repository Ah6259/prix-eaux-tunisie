# -*- coding: utf-8 -*-
"""Détecte les baisses de prix du jour -> data/baisses.js + baisses.json,
et les publie sur le canal Telegram https://t.me/prixeautunisie.

Compare data/eaux.json (relevé du jour, pas encore commité) au dernier relevé
commité (git HEAD). Une baisse = même marque, même format, même enseigne,
prix en recul d'au moins 1 %.

Le fichier baisses n'est réécrit que si des baisses sont trouvées : relancer
le workflow le même jour (HEAD = relevé du jour) ne l'efface donc pas.
Le site n'affiche le bandeau que si baisses.date = date du relevé affiché.

Usage :
  python tools/price_drops.py              # détecte, écrit, publie si TELEGRAM_BOT_TOKEN
  python tools/price_drops.py --bienvenue  # publie seulement le message de présentation
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JS = ROOT / "data" / "baisses.js"
OUT_JSON = ROOT / "data" / "baisses.json"
CANAL = "@prixeautunisie"
SITE = "https://ah6259.github.io/prix-eaux-tunisie/"
SEUIL = 0.01          # baisse minimale : 1 %
MAX_MESSAGE = 12      # lignes max dans le message Telegram


def dt(v):
    return f"{v:.3f}".replace(".", ",") + " DT"


def taille_stika(litres):
    return 12 if litres <= 0.75 else 6


def cle(brand, p):
    return (brand["id"], round(p["liters"], 3), p.get("category"), p.get("flavor") or "")


def index(data):
    out = {}
    for b in data.get("brands", []):
        for p in b.get("products", []):
            out[cle(b, p)] = (b, p)
    return out


def detecter():
    actuel = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
    ref = os.environ.get("BAISSES_REF", "HEAD")   # autre commit de référence, pour tester
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:data/eaux.json"], capture_output=True)
    if r.returncode:
        print("Pas de relevé précédent dans git : rien à comparer.")
        return actuel, []
    avant = index(json.loads(r.stdout.decode("utf-8")))

    baisses = []
    for k, (b, p) in index(actuel).items():
        if k not in avant:
            continue
        anciens = avant[k][1].get("prices", {})
        for enseigne, prix in p.get("prices", {}).items():
            ancien = anciens.get(enseigne)
            if ancien and prix < ancien * (1 - SEUIL):
                baisses.append({
                    "id": b["id"], "marque": b["name"], "format": p.get("format"),
                    "litres": p["liters"], "gazeuse": p.get("category") == "gazeuse",
                    "saveur": p.get("flavor"), "enseigne": enseigne,
                    "avant": ancien, "prix": prix,
                    "pct": round((ancien - prix) / ancien * 100, 1),
                })
    baisses.sort(key=lambda x: -x["pct"])
    return actuel, baisses


def telegram(texte):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN absent : message non publié.")
        return
    corps = urllib.parse.urlencode({
        "chat_id": CANAL, "text": texte, "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", corps, timeout=30) as r:
        print("Telegram :", json.loads(r.read()).get("ok"))


def libelle(x):
    nom = f"{x['marque']} {x['format']}".replace(".", ",")
    if x["gazeuse"]:
        nom += " gazeuse"
    if x["saveur"]:
        nom += f" {x['saveur']}"
    return nom


def message(baisses):
    lignes = ["📉 <b>Baisses de prix de l'eau aujourd'hui</b>", ""]
    for x in baisses[:MAX_MESSAGE]:
        # prix de la stika (pack) ; les bidons et bonbonnes (> 2,5 L) sont vendus à l'unité
        n = taille_stika(x["litres"]) if x["litres"] <= 2.5 else 1
        quoi = f"Stika {libelle(x)} (×{n})" if n > 1 else libelle(x)
        lignes.append(f"• <b>{quoi}</b> chez {x['enseigne']} : {dt(x['avant'] * n)} → "
                      f"<b>{dt(x['prix'] * n)}</b> (−{str(x['pct']).replace('.', ',')} %)")
    if len(baisses) > MAX_MESSAGE:
        lignes.append(f"… et {len(baisses) - MAX_MESSAGE} autres baisses.")
    lignes += ["", f"💧 Tous les prix : {SITE}"]
    return "\n".join(lignes)


BIENVENUE = (
    "💧 <b>Bienvenue sur Prix Eau Tunisie — Promos !</b>\n\n"
    "Chaque nuit, notre robot relève les prix de l'eau minérale chez Carrefour, "
    "Géant et Otrity. Dès qu'un prix baisse, vous êtes prévenu ici 📉\n\n"
    "Partagez le canal : t.me/prixeautunisie\n"
    f"Comparer tous les prix : {SITE}"
)


def main():
    if "--bienvenue" in sys.argv:
        telegram(BIENVENUE)
        return
    actuel, baisses = detecter()
    print(f"{len(baisses)} baisse(s) de prix.")
    for x in baisses:
        print(f"  {libelle(x)} @ {x['enseigne']} : {x['avant']} -> {x['prix']} (-{x['pct']} %)")
    if not baisses:
        return
    data = {"date": actuel.get("updated"), "baisses": baisses}
    OUT_JS.write_text("window.EAUX_BAISSES = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        telegram(message(baisses))
    except Exception as e:   # une panne Telegram ne doit pas bloquer la mise à jour du site
        print("Échec Telegram :", e)


if __name__ == "__main__":
    main()
