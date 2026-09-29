# -*- coding: utf-8 -*-
"""Génère les pages par marque (marque/<id>/index.html), le sitemap.xml
et la liste de liens statiques de l'accueil — pour le référencement Google.

À lancer après collect_prices.py (les pages reprennent les prix du jour) :
    python tools/build_pages.py
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ah6259.github.io/prix-eaux-tunisie"

data = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
compo_js = (ROOT / "data" / "composition.js").read_text(encoding="utf-8")
COMPO = json.loads(re.search(r"window\.EAUX_COMPO\s*=\s*({.*})\s*;", compo_js, re.S).group(1))

STORES_ORDER = ["Carrefour", "Géant", "Monoprix", "Aziza"]
GRAND_FORMAT = 2.5
taille_stika = lambda l: 12 if l <= 0.75 else 6
fmt_dt = lambda v: f"{v:,.3f}".replace(",", " ").replace(".", ",") + " DT"
maj_fr = "-".join(reversed(data["updated"].split("-")))  # jj-mm-aaaa approximatif
try:
    from datetime import datetime
    maj_fr = datetime.fromisoformat(data["updated"]).strftime("%d/%m/%Y")
except Exception:
    pass

COMPO_ROWS = [("tds", "Résidu sec (TDS)"), ("ca", "Calcium"), ("mg", "Magnésium"),
              ("na", "Sodium"), ("k", "Potassium"), ("hco3", "Bicarbonates"),
              ("so4", "Sulfates"), ("cl", "Chlorures"), ("no3", "Nitrates"),
              ("f", "Fluorures"), ("ph", "pH")]


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def page_marque(b):
    bid, nom = b["id"], b["name"]
    compo = COMPO["waters"].get(bid)
    prods = b.get("products") or []

    # tableau des prix
    lignes = []
    for p in sorted(prods, key=lambda p: (p["liters"], p["category"])):
        mini = min(p["prices"].values())
        gagnant = min(p["prices"], key=p["prices"].get)
        offres = " · ".join(f"{esc(s)} {fmt_dt(v)}" for s, v in sorted(p["prices"].items(), key=lambda x: x[1]))
        n = taille_stika(p["liters"])
        stika = fmt_dt(mini * n) + f" <small>(×{n})</small>" if p["liters"] <= GRAND_FORMAT else "—"
        gaz = " gazeuse" if p["category"] == "gazeuse" else ""
        lignes.append(f"<tr><td class='fmt'>{esc(p['format'])}{gaz}</td>"
                      f"<td>{offres}</td><td style='text-align:right'>{stika}</td></tr>")
    tableau = (f"<table class='prices'><tr><th>Format</th><th>Prix bouteille par enseigne</th>"
               f"<th>Stika</th></tr>{''.join(lignes)}</table>") if lignes else \
        "<p><em>Prix non disponible pour le moment dans les enseignes que nous suivons " \
        "(Carrefour, Géant, Monoprix, Aziza).</em></p>"

    # composition
    compo_html = ""
    if compo:
        cols = "".join(f"<th>{esc(e['src'])}</th>" for e in compo) if len(compo) > 1 else ""
        head = f"<tr><th></th>{cols}</tr>" if cols else ""
        rows = "".join(
            f"<tr><td>{lab}{' <small>mg/L</small>' if k != 'ph' else ''}</td>" +
            "".join(f"<td style='text-align:right'>{e[k]}</td>" for e in compo) + "</tr>"
            for k, lab in COMPO_ROWS)
        cats = " · ".join(sorted({COMPO['cats'][str(e['cat'])] for e in compo}))
        compo_html = f"""
  <h2>Composition de l'eau {esc(nom)}</h2>
  <p class="sub">{esc(cats)} — d'après les fiches de l'Office National du Thermalisme
   (<a href="{COMPO['credit']['url']}" rel="noopener">source</a>), en mg/L sauf pH.</p>
  <div class="compo" style="margin:0"><table class="compo-table">{head}{rows}</table></div>"""

    meta_bits = []
    if b.get("source"):
        meta_bits.append(f"Source : <b>{esc(b['source'])}</b>")
    if b.get("company"):
        meta_bits.append(esc(b["company"]))
    if b.get("depuis"):
        meta_bits.append(f"Commercialisée depuis <b>{b['depuis']}</b>")
    if b.get("note"):
        meta_bits.append(esc(b["note"]))

    prix15 = None
    c15 = [min(p["prices"].values()) for p in prods
           if p["category"] == "plate" and abs(p["liters"] - 1.5) < .01 and p["prices"]]
    if c15:
        prix15 = min(c15)
    desc = (f"Prix de l'eau {nom} en Tunisie : bouteille et stika chez Géant, Carrefour, Monoprix et Aziza, "
            f"mis à jour chaque jour."
            + (f" 1,5 L à partir de {fmt_dt(prix15).replace(chr(160), ' ')}." if prix15 else "")
            + (f" Source : {b['source']}." if b.get("source") else "")
            + " Composition et livraison à domicile.")

    img = f"../../{b['img']}" if b.get("img") else None

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"Eau minérale {nom}",
        "brand": {"@type": "Brand", "name": nom},
        **({"image": f"{SITE}/{b['img']}"} if b.get("img") else {}),
        **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TND",
                       "lowPrice": min(min(p["prices"].values()) for p in prods),
                       "highPrice": max(max(p["prices"].values()) for p in prods),
                       "offerCount": sum(len(p["prices"]) for p in prods)}} if prods else {}),
    }, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Prix {esc(nom)} en Tunisie — bouteille &amp; stika | Prix des Eaux de Tunisie</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/marque/{bid}/">
<link rel="icon" type="image/svg+xml" href="../../assets/icons/icon.svg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../../style.css">
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header class="site"><div class="wrap site-inner">
  <h1>Prix de l'eau {esc(nom)}</h1>
</div></header>
<div class="wrap">
  <p class="intro" style="margin-top:14px"><a href="../../">← Prix de toutes les eaux minérales en Tunisie</a></p>
  <section>
    <div class="card" style="max-width:680px">
      <div class="card-head">
        {f'<img src="{esc(img)}" alt="Bouteille {esc(nom)}" loading="lazy">' if img else ""}
        <div class="id"><h2 style="margin:0">{esc(nom)}</h2></div>
      </div>
      {f'<div class="meta">{" · ".join(meta_bits)}</div>' if meta_bits else ""}
      {tableau}
    </div>
    <p class="sub" style="margin-top:10px">Prix relevés le {maj_fr} sur les boutiques en ligne des
    grandes surfaces — indicatifs, ils peuvent varier selon le magasin.
    Stika = pack de 6 bouteilles (12 pour les 50 cl).</p>
  </section>
  <section>{compo_html}</section>
  <section>
    <h2>Commander l'eau {esc(nom)} avec livraison</h2>
    <p class="intro" style="margin-top:6px">Sur <a href="../../">Prix des Eaux de Tunisie</a>, ajoutez
    vos stikas {esc(nom)} au panier avec le bouton +, indiquez votre adresse et recevez votre eau
    à domicile — le prix total et les frais de livraison vous sont confirmés sur WhatsApp,
    paiement à la livraison.</p>
  </section>
</div>
<footer><div class="wrap">
  <a href="../../">Comparateur des prix de l'eau en Tunisie</a> — 35 marques, mis à jour chaque jour.
</div></footer>
</body>
</html>
"""


# ---------------------------------------------------------------- génération
urls = [f"{SITE}/"]
for b in data["brands"]:
    d = ROOT / "marque" / b["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page_marque(b), encoding="utf-8")
    urls.append(f"{SITE}/marque/{b['id']}/")

# pages de marques disparues de la liste : on les retire
ids = {b["id"] for b in data["brands"]}
for d in (ROOT / "marque").iterdir():
    if d.is_dir() and d.name not in ids:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()

# sitemap
today = date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for i, u in enumerate(urls):
    sm.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod>"
              f"<changefreq>daily</changefreq><priority>{'1.0' if i == 0 else '0.7'}</priority></url>")
sm.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

# liens statiques sur l'accueil (entre <!--MARQUES--> et <!--/MARQUES-->)
index = ROOT / "index.html"
html = index.read_text(encoding="utf-8")
liens = "".join(f'<li><a href="marque/{b["id"]}/">Prix eau {esc(b["name"])}</a></li>'
                for b in data["brands"])
bloc = f"<!--MARQUES--><ul>{liens}</ul><!--/MARQUES-->"
if "<!--MARQUES-->" in html:
    html = re.sub(r"<!--MARQUES-->.*?<!--/MARQUES-->", bloc, html, flags=re.S)
    lien_accueil = "oui"
else:
    lien_accueil = "NON (marqueur absent de index.html)"

# nombre de marques tenu à jour dans les métas (description, og:description
# lue par WhatsApp/Facebook) et le JSON-LD ; la liste de marques du JSON-LD aussi
nb = len(data["brands"])
html = re.sub(r"\d+ marques", f"{nb} marques", html)
noms = ", ".join(b["name"] for b in data["brands"])
html = re.sub(r'("text": ")\d+ marques vendues en Tunisie : [^"]*(")',
              lambda m: m.group(1) + f"{nb} marques vendues en Tunisie : {noms}." + m.group(2),
              html)
index.write_text(html, encoding="utf-8")

print(f"{len(data['brands'])} pages marque générées · sitemap {len(urls)} URLs · liens accueil : {lien_accueil}")
