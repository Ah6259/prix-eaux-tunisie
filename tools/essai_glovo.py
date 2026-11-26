# -*- coding: utf-8 -*-
"""ESSAI SILENCIEUX de Glovo comme source de prix (« fais » d'Ahmed du 22/11/2026).

Chaque jour : lit le rayon « eaux » de quelques magasins sur glovoapp.com (pages publiques, robots.txt « Allow: / »,
aucun barrage), garde nom + prix dans tools/essai/glovo.json (60 derniers jours).
RIEN n'est affiché sur le site : c'est seulement pour vérifier, pendant quelques jours,
  1. que la lecture marche chaque jour (prix stables, pas de page vide) ;
  2. que les prix Glovo ressemblent aux vrais prix : on compare Carrefour Market Sousse (Glovo)
     au prix de carrefour.tn déjà relevé chaque nuit (data/eaux.json).
Une page lue une seule fois par jour, 3 s entre deux pages (règle commune § 36). Jamais de contournement.
Robot : .github/workflows/essai-glovo.yml. Sortie rouge (code 1) si une page ne donne AUCUN produit (format changé).
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER = RACINE / "tools" / "essai" / "glovo.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
JOURS_GARDES = 60

MAGASINS = [
    {"id": "monoprix-tunis", "nom": "Monoprix Tunis", "enseigne": "Monoprix",
     "url": "https://glovoapp.com/fr/tn/tunis/stores/monoprix-tis?content=eaux-plates-c.37011387"},
    {"id": "carrefour-sousse", "nom": "Carrefour Market Sousse", "enseigne": "Carrefour",
     "url": "https://glovoapp.com/fr/tn/sousse/stores/carrefour-nso?content=eaux-plates-c.36071216"},
    {"id": "aziza-gabes", "nom": "Aziza Gabès", "enseigne": "Aziza",
     "url": "https://glovoapp.com/fr/tn/gabes/stores/magasins-aziza-gbs?content=eaux-c.50827073"},
]

TUILE = re.compile(r'ItemTile_title__\w+">([^<]+)</h3><div class="ItemTile_priceContainer__\w+">(.*?)</div>', re.S)
PRIX = re.compile(r"(\d+),(\d{3})\s*DT")


def lire_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "ignore")


def produits(page):
    """[{nom, prix, prix_barre}] — prix = premier prix affiché (prix payé), prix_barre = ancien prix s'il y en a un."""
    vus, res = set(), []
    for nom, bloc in TUILE.findall(page):
        nom = " ".join(html.unescape(nom).split())
        prix = [int(a) + int(b) / 1000 for a, b in PRIX.findall(bloc)]
        if not prix or nom in vus:
            continue
        vus.add(nom)
        res.append({"nom": nom, "prix": round(prix[0], 3),
                    "prix_barre": round(prix[1], 3) if len(prix) > 1 else None})
    return res


def litres(nom):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*L\b", nom, re.I)
    return float(m.group(1).replace(",", ".")) if m else None


def comparer_carrefour(prods):
    """Écart entre le prix Glovo (Carrefour Market Sousse) et le prix carrefour.tn du même jour (data/eaux.json)."""
    try:
        eaux = json.loads((RACINE / "data" / "eaux.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    res = []
    for p in prods:
        l = litres(p["nom"])
        for b in eaux.get("brands", []):
            if not re.search(r"\b" + re.escape(b["name"]) + r"\b", p["nom"], re.I):
                continue
            for f in b.get("products", []):
                ref = f.get("prices", {}).get("Carrefour")
                if ref and l and abs(f.get("liters", 0) - l) < 0.01 and f.get("category") == "plate":
                    res.append({"nom": p["nom"], "glovo": p["prix"], "carrefour_tn": ref,
                                "ecart_pct": round((p["prix"] - ref) / ref * 100, 1)})
    return res


def main():
    jour = dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).strftime("%Y-%m-%d")
    try:
        donnees = json.loads(FICHIER.read_text(encoding="utf-8"))
    except Exception:
        donnees = {"note": "Essai silencieux de Glovo (22/11/2026) : rien n'est affiché sur le site.", "releves": []}
    releve = {"date": jour, "magasins": {}}
    vides = []
    for i, m in enumerate(MAGASINS):
        if i:
            time.sleep(3)
        try:
            prods = produits(lire_page(m["url"]))
            erreur = None
        except Exception as e:  # page injoignable : notée, jamais devinée
            prods, erreur = [], f"{type(e).__name__}: {e}"[:200]
        if not prods:
            vides.append(m["nom"])
        entree = {"nom": m["nom"], "url": m["url"], "produits": prods}
        if erreur:
            entree["erreur"] = erreur
        if m["enseigne"] == "Carrefour":
            entree["comparaison_carrefour_tn"] = comparer_carrefour(prods)
        releve["magasins"][m["id"]] = entree
        print(f"{m['nom']} : {len(prods)} produits" + (f" — ÉCHEC {erreur}" if erreur else ""))
        for p in prods:
            print(f"   {p['nom']} : {p['prix']:.3f} DT" + (f" (barré {p['prix_barre']:.3f})" if p["prix_barre"] else ""))
        for c in entree.get("comparaison_carrefour_tn", []):
            print(f"   comparaison : {c['nom']} Glovo {c['glovo']:.3f} / carrefour.tn {c['carrefour_tn']:.3f} ({c['ecart_pct']:+} %)")
    donnees["releves"] = [r for r in donnees.get("releves", []) if r.get("date") != jour] + [releve]
    donnees["releves"] = sorted(donnees["releves"], key=lambda r: r["date"])[-JOURS_GARDES:]
    FICHIER.parent.mkdir(parents=True, exist_ok=True)
    FICHIER.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    if vides:
        print("ÉCHEC : aucune eau lue pour " + ", ".join(vides) + " (page changée ou injoignable)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
