# -*- coding: utf-8 -*-
"""Reconstruit l'historique des prix depuis les commits git de data/eaux.json
-> data/historique.js + historique.json

Pour chaque jour : le prix de la stika d'eau plate 1,5 L la moins chère
(6 × la bouteille la moins chère), avec la ou les marques gagnantes,
plus le prix 1,5 L par marque (pour de futures courbes par marque).

Usage : python tools/build_history.py   (nécessite l'historique git complet)
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JS = ROOT / "data" / "historique.js"
OUT_JSON = ROOT / "data" / "historique.json"


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors="replace"))
    return r.stdout


def min15(brand):
    prix = [min(p["prices"].values())
            for p in brand.get("products", [])
            if p.get("category") == "plate" and not p.get("flavor")
            and abs(p.get("liters", 0) - 1.5) < .01 and p.get("prices")]
    return round(min(prix), 3) if prix else None


commits = git("log", "--reverse", "--format=%H %ad", "--date=short", "--", "data/eaux.json") \
    .decode().strip().splitlines()

releves = []
for ligne in commits:
    sha, date = ligne.split()
    try:
        releves.append(json.loads(git("show", f"{sha}:data/eaux.json").decode("utf-8")))
    except Exception:
        continue
# le fichier courant en dernier : le relevé du jour n'est pas encore commité
# quand ce script tourne dans GitHub Actions
releves.append(json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8")))

jours = {}  # date -> {"stika15", "marques", "parMarque"}  (le dernier relevé du jour gagne)
for data in releves:
    date = data.get("updated")
    if not date:
        continue
    par_marque = {}
    for b in data.get("brands", []):
        m = min15(b)
        if m is not None:
            par_marque[b["name"]] = m
    if not par_marque:
        continue
    mini = min(par_marque.values())
    jours[date] = {
        "stika15": round(mini * 6, 3),
        "bouteille15": mini,
        "marques": sorted(n for n, v in par_marque.items() if v == mini),
        "parMarque": par_marque,
    }

serie = [{"date": d, **jours[d]} for d in sorted(jours)]
data = {"note": "Prix relevés quotidiennement depuis le 2026-09-25", "serie": serie}

OUT_JS.write_text("window.EAUX_HISTO = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(serie)} jours -> {OUT_JSON}")
for j in serie:
    print(f"  {j['date']}  stika 1,5 L : {j['stika15']} DT ({', '.join(j['marques'])})")
