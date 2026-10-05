# -*- coding: utf-8 -*-
"""Applique les fiches META de collect_prices.py aux données existantes
(data/eaux.js + eaux.json) sans relancer le scraping des prix,
ainsi que les photos libres (data/photos_libres.json) des marques sans photo."""
import json
from pathlib import Path

from collect_prices import META, appliquer_photos_libres, slug

ROOT = Path(__file__).resolve().parent.parent
OUT_JS = ROOT / "data" / "eaux.js"
OUT_JSON = ROOT / "data" / "eaux.json"

data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
par_nom = {m["name"]: m for m in META.values()}
maj = 0
for b in data["brands"]:
    m = par_nom.get(b["name"])
    if not m:
        b.setdefault("depuis", None)
        continue
    for k in ("company", "source", "note"):
        b[k] = m[k]
    b["depuis"] = m.get("depuis")
    b["id"] = slug(m["name"])
    maj += 1

appliquer_photos_libres(data["brands"])
OUT_JS.write_text("window.EAUX_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{maj}/{len(data['brands'])} marques mises à jour -> {OUT_JSON}")
