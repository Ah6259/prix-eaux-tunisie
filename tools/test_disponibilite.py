# -*- coding: utf-8 -*-
"""Disponibilité des eaux dans les enseignes vérifiées par robot (23/10/2026).

Cas réel : Ahmed a vu Aqualine 1,5 L « Carrefour 3,780 DT » sur le site alors qu'elle était
indisponible dans son magasin Carrefour. Cause : le robot lisait le catalogue « par défaut »
de Carrefour (63 eaux), qui n'est pas un magasin ; les vrais magasins n'en vendent que 5 à 12.

Vérifie, sans rien télécharger :
  1. Carrefour : une eau vendue dans AUCUN magasin n'a pas de prix Carrefour ;
     une eau vendue dans une partie des magasins garde son prix + « dans N magasins sur M » ;
     un produit « OUT_OF_STOCK » ne compte pas ; le prix retenu est le plus courant.
  2. Géant : une quantité en stock à 0 = produit écarté.
  3. Le site reçoit « non_dispo » : enseignes lues ce jour qui ne vendent pas ce format
     (jamais une enseigne en panne ni Monoprix, relevé à la main).

Usage : python tools/test_disponibilite.py
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "tools"))
import collect_prices as c  # noqa: E402

ECHECS = []


def verifie(titre, condition, detail=""):
    print(("OK   " if condition else "ÉCHEC ") + titre + ("" if condition else f"\n     {detail}"))
    if not condition:
        ECHECS.append(titre)


TMP = Path(tempfile.mkdtemp())
c.RAW_DIR = TMP / "raw"
c.RAW_DIR.mkdir()
c.time.sleep = lambda s: None


# ------------------------------------------------------------------ 1. Carrefour, magasin par magasin
def produit(nom, sku, prix):
    return {"name": nom, "sku": sku, "url_key": sku, "short_description": {"html": ""},
            "small_image": {"url": None},
            "price_range": {"minimum_price": {"final_price": {"value": prix}, "regular_price": {"value": prix}}}}


CATALOGUE = [produit("Eau minérale AQUALINE 1.5L", "aq15", 0.63),      # vendue dans 2 magasins sur 3
             produit("Eau minérale PALMA 1.5L", "pa15", 0.80),         # au catalogue, vendue nulle part
             produit("Eau minérale JANNET 2L", "ja2", 0.83),           # en rupture partout
             produit("Eau minérale GARCI 1L", "ga1", 0.64)]            # prix différents selon le magasin
MAGASINS = {
    "marsa":  [("aq15", 0.63, "IN_STOCK"), ("ja2", 0.83, "OUT_OF_STOCK"), ("ga1", 0.66, "IN_STOCK")],
    "ariana": [("aq15", 0.63, "IN_STOCK"), ("ga1", 0.66, "IN_STOCK")],
    "aouina": [("ga1", 0.62, "IN_STOCK")],                             # pas d'Aqualine ici (cas d'Ahmed)
}


def faux_gql(q, magasin=None):
    if "availableStores" in q:
        return {"availableStores": [{"store_code": "default"}] + [{"store_code": m} for m in MAGASINS]}
    if magasin is None:
        return {"products": {"items": CATALOGUE}}
    return {"products": {"items": [{"sku": s, "stock_status": st,
                                    "price_range": {"minimum_price": {"final_price": {"value": p}}}}
                                   for s, p, st in MAGASINS[magasin]]}}


c.carrefour_gql = faux_gql
c.CARREFOUR_MIN_MAGASINS = 1  # 3 magasins simulés (le vrai robot en exige au moins 10)
res = {o["nom"]: o for o in c.carrefour()}
verifie("Carrefour : eau au catalogue mais vendue dans aucun magasin (Palma) -> pas de prix",
        not any("PALMA" in n for n in res), list(res))
verifie("Carrefour : eau en rupture dans tous les magasins (Jannet) -> pas de prix",
        not any("JANNET" in n for n in res), list(res))
aq = next((o for n, o in res.items() if "AQUALINE" in n), None)
verifie("Carrefour : Aqualine vendue dans 2 magasins sur 3 -> prix 0,630 + [2, 3]",
        aq is not None and aq["prix"] == 0.63 and aq["magasins"] == [2, 3], aq)
ga = next((o for n, o in res.items() if "GARCI" in n), None)
verifie("Carrefour : prix différents selon le magasin -> le plus courant (0,660)",
        ga is not None and ga["prix"] == 0.66 and ga["magasins"] == [3, 3], ga)


# ------------------------------------------------------------------ 2. Géant : stock à 0
def article(marque, desc, prix, stock):
    return (f'<article class="product-miniature js-product-miniature" data-id-product="1">'
            f'<h2 class="h3 product-title" itemprop="name"><a href="#">Eau minérale</a></h2>'
            f'<p class="manufacturer_product text-xs-left">\n {marque}</p>'
            f'<div itemprop="description" class="listds product_short">{desc}</div>'
            f'<span itemprop="price" class="price">{prix} DT</span>'
            f'<input type="hidden" value="{stock}" class="blocked quantity_product quantity_product_1" name="q">'
            f'</article>')


c.http_get = lambda *a, **k: ('<html>' + article("AQUALINE", "1.5L", "0,600", 1557)
                              + article("SAFIA", "1.5L", "0,690", 0) + '</html>').encode("utf-8")
g = c.geant()
verifie("Géant : produit en stock (quantité 1557) gardé", any(o["marque"] == "AQUALINE" for o in g), g)
verifie("Géant : produit à quantité 0 écarté", not any(o["marque"] == "SAFIA" for o in g), g)


# ------------------------------------------------------------------ 3. « non disponible » dans les données du site
def offre(ens, marque, vol, prix, **k):
    return dict({"enseigne": ens, "marque": marque, "nom": f"{marque} {vol}", "volume_l": vol, "nb_unites": 1,
                 "type": "plate", "prix": prix, "image_src": None}, **k)


(TMP / "data").mkdir()
c.ROOT, c.OUT_JSON, c.OUT_JS, c.IMG_AUTO = TMP, TMP / "data" / "eaux.json", TMP / "data" / "eaux.js", TMP / "img"
c.telecharger_image = lambda url: None
c.MINIMUM_OFFRES = {}
c.carrefour = lambda: [offre("carrefour", "AQUALINE", 1.5, 0.63, magasins=[26, 39]),
                       offre("carrefour", "TIJEN", 1.5, 0.68, magasins=[39, 39])]
c.geant = lambda: [offre("geant", "AQUALINE", 1.5, 0.60), offre("geant", "SAFIA", 1.5, 0.69)]
def _panne(): raise RuntimeError("403 Cloudflare")
c.otrity = _panne                           # Otrity en panne, pas de relevé local : jamais « non disponible »
sortie, sys.stdout = sys.stdout, open(TMP / "journal.txt", "w", encoding="utf-8")
try:
    c.main()
finally:
    sys.stdout.close()
    sys.stdout = sortie
data = json.loads(c.OUT_JSON.read_text(encoding="utf-8"))
P = {(b["name"], p["liters"]): p for b in data["brands"] for p in b["products"]}
aq, sa, ti = P.get(("Aqualine", 1.5)), P.get(("Safia", 1.5)), P.get(("Tijen", 1.5))
verifie("site : Aqualine 1,5 L Carrefour « dans 26 magasins sur 39 »",
        aq and aq.get("magasins") == {"Carrefour": [26, 39]}, aq)
verifie("site : Safia 1,5 L vendue chez Géant seulement -> Carrefour « non disponible »",
        sa and sa.get("non_dispo") == ["Carrefour"], sa)
verifie("site : vendu dans tous les magasins -> pas de mention « N magasins sur M »",
        ti and "magasins" not in ti, ti)
verifie("site : une enseigne en panne (Otrity) n'est jamais dite « non disponible »",
        all("Otrity" not in (p.get("non_dispo") or []) for p in P.values()), P)

# le site affiche bien ces informations (app.js, pages marque, pages magasin)
app = (ROOT / "app.js").read_text(encoding="utf-8")
verifie("app.js affiche « non disponible » et « dans N magasins sur M »",
        "p.non_dispo" in app and "non disponible" in app and "p.magasins" in app)
verifie("pages marque : « non disponible » (build_pages.py)",
        'non_dispo' in (ROOT / "tools" / "build_pages.py").read_text(encoding="utf-8"))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'TOUT PASSE' if not ECHECS else f'{len(ECHECS)} ÉCHEC(S)'}")
sys.exit(1 if ECHECS else 0)
