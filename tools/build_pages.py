# -*- coding: utf-8 -*-
"""Génère les pages par marque (marque/<id>/index.html), le sitemap.xml
et la liste de liens statiques de l'accueil — pour le référencement Google.

À lancer après collect_prices.py (les pages reprennent les prix du jour) :
    python tools/build_pages.py
"""
import json
import re
import sys
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_guides import SOURCES_HTML, CSS_V, ICONE_WA, entete, bandeau, pied  # noqa: E402
import langues as LG  # noqa: E402  (une adresse par langue : pages françaises + ar/)

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://prix-eau.clicvia.com"

data = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
compo_js = (ROOT / "data" / "composition.js").read_text(encoding="utf-8")
COMPO = json.loads(re.search(r"window\.EAUX_COMPO\s*=\s*({.*})\s*;", compo_js, re.S).group(1))

STORES_ORDER = ["Carrefour", "Géant"]
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


COMPO_ROWS_AR = {"tds": "البقايا الجافة (TDS)", "ca": "الكالسيوم", "mg": "المغنيزيوم", "na": "الصوديوم", "k": "البوتاسيوم",
                 "hco3": "البيكربونات", "so4": "الكبريتات", "cl": "الكلوريد", "no3": "النترات", "f": "الفلوريد", "ph": "درجة الحموضة pH"}
# textes arabes des données des marques (notes, catégories officielles) : assets/textes-ar.js, aussi chargé par ar/index.html
TEXTES_AR = json.loads(re.search(r"window\.TEXTES_AR\s*=\s*({.*})\s*;", (ROOT / "assets" / "textes-ar.js").read_text(encoding="utf-8"), re.S).group(1))


def page_marque(b, lang="fr"):
    """Page d'une marque, en français (marque/<id>/) ou en arabe (ar/marque/<id>/, rangée par tools/langues.py)."""
    T = lambda fr, ar: ar if lang == "ar" else fr
    D = lambda v: LG.dt(v, lang)
    bid, nom = b["id"], b["name"]
    compo = COMPO["waters"].get(bid)
    prods = b.get("products") or []

    # tableau des prix
    lignes = []
    for p in sorted(prods, key=lambda p: (p["liters"], p["category"])):
        mag = p.get("magasins") or {}
        dans = (lambda s: f" <small>(في {mag[s][0]} مغازة من {mag[s][1]})</small>") if lang == "ar" else \
            (lambda s: f" <small>(dans {mag[s][0]} magasin{'s' if mag[s][0] > 1 else ''} sur {mag[s][1]})</small>")
        nom_s = (lambda s: f"<bdi>{esc(s)}</bdi>") if lang == "ar" else esc
        offres = " · ".join(f"{nom_s(s)} {D(v)}" + (dans(s) if s in mag else "")
                            for s, v in sorted(p["prices"].items(), key=lambda x: x[1]))
        mini = min(p["prices"].values())
        # enseignes vérifiées ce jour qui ne vendent pas ce format (23/10/2026)
        offres += "".join(f" · {esc(s)} <small>{T('non disponible', 'غير متوفر')}</small>" for s in p.get("non_dispo") or [])
        n = taille_stika(p["liters"])
        stika = D(mini * n) + f" <small>(×{n})</small>" if p["liters"] <= GRAND_FORMAT else "—"
        gaz = T(" gazeuse", " غازي") if p["category"] == "gazeuse" else ""
        fmt = esc(p['format']) if lang != "ar" else LG.litres(p["liters"], "ar") if p["liters"] >= 1 else f"{p['liters'] * 100:g} صل"
        lignes.append(f"<tr><td class='fmt'>{fmt}{gaz}</td>"
                      f"<td>{offres}</td><td style='text-align:end'>{stika}</td></tr>")
    tableau = (f"<table class='prices'><tr><th>{T('Format', 'الحجم')}</th><th>{T('Prix bouteille par enseigne', 'سعر القارورة حسب المغازة')}</th>"
               f"<th>{T('Stika', 'الستيكة')}</th></tr>{''.join(lignes)}</table>") if lignes else \
        T("<p><em>Prix non disponible pour le moment dans les enseignes que nous suivons (Carrefour, Géant).</em></p>",
          "<p><em>السعر غير متوفر حاليًا في المغازات التي نتابعها (Carrefour وGéant).</em></p>")

    # composition
    compo_html = ""
    if compo:
        cols = "".join(f"<th><bdi>{esc(e['src'])}</bdi></th>" for e in compo) if len(compo) > 1 else ""
        head = f"<tr><th></th>{cols}</tr>" if cols else ""
        unite = T(" <small>mg/L</small>", " <small>مغ/لتر</small>")
        rows = "".join(
            f"<tr><td>{COMPO_ROWS_AR[k] if lang == 'ar' else lab}{unite if k != 'ph' else ''}</td>" +
            "".join(f"<td style='text-align:end'>{e[k]}</td>" for e in compo) + "</tr>"
            for k, lab in COMPO_ROWS)
        cats = " · ".join(sorted({(TEXTES_AR["cats"] if lang == "ar" else COMPO['cats'])[str(e['cat'])] for e in compo}))
        compo_html = T(f"""
  <h2>Composition de l'eau {esc(nom)}</h2>
  <p class="sub">{esc(cats)} — d'après les fiches de l'Office National du Thermalisme
   (<a href="{COMPO['credit']['url']}" rel="noopener">source</a>), en mg/L sauf pH.</p>""", f"""
  <h2>تركيبة ماء {LG.iso(esc(nom))}</h2>
  <p class="sub">{esc(cats)} — حسب جداول الديوان الوطني للمياه المعدنية والاستشفاء بالمياه
   (<a href="{COMPO['credit']['url']}" rel="noopener">المصدر</a>)، بالمليغرام في اللتر ما عدا درجة الحموضة.</p>""") + \
            f"""
  <div class="compo" style="margin:0"><table class="compo-table">{head}{rows}</table></div>"""

    meta_bits = []
    if b.get("source"):
        meta_bits.append(T(f"Source : <b>{esc(b['source'])}</b>", f"العين: <b><bdi>{esc(b['source'])}</bdi></b>"))
    if b.get("company"):
        meta_bits.append(esc(b["company"]) if lang != "ar" else f"<bdi>{esc(b['company'])}</bdi>")
    if b.get("depuis"):
        meta_bits.append(T(f"Commercialisée depuis <b>{b['depuis']}</b>", f"في السوق منذ <b>{b['depuis']}</b>"))
    if b.get("note"):
        note = esc(b["note"]) if lang != "ar" else TEXTES_AR["notes"].get(bid)
        if note:
            meta_bits.append(note)

    prix15 = None
    c15 = [min(p["prices"].values()) for p in prods
           if p["category"] == "plate" and abs(p["liters"] - 1.5) < .01 and p["prices"]]
    if c15:
        prix15 = min(c15)
    # SEO (08/11/2026) : description <= 165 caractères (Google coupe au-delà), sans promesse de livraison (commande fermée)
    if lang == "ar":
        desc = (f"سعر ماء {LG.iso(nom)} في تونس: القارورة والستيكة في Géant وCarrefour، يُحدَّث كل يوم."
                + (f" قارورة 1,5 لتر من {LG.iso(D(prix15))}." if prix15 else "")
                + " التركيبة، مقارن مجاني.")
    else:
        desc = (f"Prix de l'eau {nom} en Tunisie : bouteille et stika chez Géant et Carrefour, mis à jour chaque jour."
                + (f" 1,5 L dès {D(prix15).replace(chr(160), ' ')}." if prix15 else "")
                + " Composition, comparateur gratuit.")

    img = f"../../{b['img']}" if b.get("img") else None
    photo_html = f'<img src="{esc(img)}" alt="{T("Bouteille", "قارورة")} {esc(nom)}" loading="lazy">' if img else ""
    cr = b.get("img_credit")
    if img and cr:  # photo libre (Open Food Facts…) : crédit obligatoire juste sous la photo
        photo_html = (f'<figure class="photo-libre">{photo_html}<figcaption class="credit-photo">'
                      f'<a href="{esc(cr["page"])}" rel="noopener">{T("Photo", "صورة")} : {esc(cr["source"])}</a>, '
                      f'<a href="{esc(cr["licence_url"])}" rel="license noopener">CC BY-SA</a></figcaption></figure>')
    # le prix de la stika dans le titre Google : donne envie de cliquer dans les résultats
    if lang == "ar":
        titre = (f"سعر ماء {LG.iso(esc(nom))} — ستيكة 1,5 لتر بـ {LG.iso(D(prix15 * 6))} | مقارن مجاني" if prix15
                 else f"سعر ماء {LG.iso(esc(nom))} — القارورة والستيكة | مقارن مجاني")
        wa_txt = f"💧 سعر ماء {nom}" + (f": ستيكة 1,5 لتر بـ {D(prix15 * 6)}" if prix15 else "") + f" — {SITE}/ar/marque/{bid}/"
    else:
        titre = (f"Prix {esc(nom)} — stika 1,5 L à {D(prix15 * 6)} | comparateur gratuit"      # <= 70 caractères (SEO)
                 if prix15 else f"Prix {esc(nom)} — bouteille et stika | comparateur gratuit")
        wa_txt = f"💧 Prix de l'eau {nom}" + (f" : stika 1,5 L à {D(prix15 * 6)}" if prix15 else "") + f" — {SITE}/marque/{bid}/"
    wa = "https://wa.me/?text=" + urllib.parse.quote(wa_txt)

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": T(f"Eau minérale {nom}", f"ماء معدني {nom}"),
        **({"inLanguage": "ar"} if lang == "ar" else {}),
        "brand": {"@type": "Brand", "name": nom},
        **({"image": f"{SITE}/{b['img']}"} if b.get("img") else {}),
        **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TND",
                       "lowPrice": min(min(p["prices"].values()) for p in prods),
                       "highPrice": max(max(p["prices"].values()) for p in prods),
                       "offerCount": sum(len(p["prices"]) for p in prods)}} if prods else {}),
    }, ensure_ascii=False)

    html_tag = '<html lang="ar" dir="rtl" translate="no">' if lang == "ar" else '<html lang="fr" translate="no">'
    bas = T(f"""<p class="sub" style="margin-top:10px">Prix relevés le {maj_fr} sur les boutiques en ligne des
    grandes surfaces — indicatifs, ils peuvent varier selon le magasin.
    Stika = pack de 6 bouteilles (12 pour les 50 cl).</p>""", f"""<p class="sub" style="margin-top:10px">أسعار مقروءة يوم {maj_fr} من المتاجر
    الإلكترونية للمغازات الكبرى — تقريبية، وقد تتغيّر حسب المغازة. الستيكة = علبة من 6 قوارير (12 للقوارير 50 صل).</p>""")
    credit = ""
    if img and cr:
        credit = T(f'<p class="credit-pied">Photo de la bouteille : <a href="{esc(cr["page"])}" rel="noopener">{esc(cr["source"])}</a>, licence <a href="{esc(cr["licence_url"])}" rel="license noopener">{esc(cr["licence"])}</a> ; recadrée sur fond blanc.</p>',
                   f'<p class="credit-pied">صورة القارورة: <a href="{esc(cr["page"])}" rel="noopener">{esc(cr["source"])}</a>، رخصة <a href="{esc(cr["licence_url"])}" rel="license noopener">{esc(cr["licence"])}</a>، مقصوصة على خلفية بيضاء.</p>')
    commande = T(f"""<h2>Commande et livraison de l'eau {esc(nom)} — bientôt</h2>
    <p class="intro" style="margin-top:6px">La commande avec livraison à domicile arrive bientôt sur
    <a href="../../">Prix des Eaux de Tunisie</a> : vous commanderez auprès de grossistes et dépôts partenaires
    de votre région, à leurs propres prix, livraison comprise (les prix ci-dessus sont ceux des grandes
    surfaces, à titre indicatif). <a href="https://t.me/prixeautunisie" rel="noopener">Être prévenu de l'ouverture</a>.</p>""",
                 f"""<h2>طلب ماء {LG.iso(esc(nom))} وتوصيله — قريبًا</h2>
    <p class="intro" style="margin-top:6px">الطلب مع التوصيل إلى المنزل قريبًا في <a href="../../">أسعار الماء في تونس</a>: ستطلب من تجّار جملة
    ومخازن شريكة في جهتك، بأسعارهم الخاصة، مع التوصيل (الأسعار أعلاه هي أسعار المغازات الكبرى، للإرشاد فقط).
    <a href="https://t.me/prixeautunisie" rel="noopener">أعلِمني عند الافتتاح</a>.</p>""")

    return f"""<!doctype html>
{html_tag}
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://gc.zgo.at https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://cdnjs.cloudflare.com https://prix-eaux-tunisie.goatcounter.com; connect-src 'self' https://docs.google.com https://formspree.io https://prix-eaux-tunisie.goatcounter.com; form-action 'self' https://docs.google.com https://formspree.io; object-src 'none'; base-uri 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="noai, noimageai">
<script src="../../protection.js?v={CSS_V}"></script>
<title>{titre}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/marque/{bid}/">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/marque/{bid}/">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og-image-v7.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="icon" type="image/svg+xml" href="../../assets/icons/icon.svg">
<link rel="manifest" href="../../manifest.webmanifest">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Prix Eaux">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../../style.css?v={CSS_V}">
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
{entete("../../", lang)}
{bandeau("../../", T("Prix de l'eau ", "سعر ماء ") + (esc(nom) if lang != "ar" else LG.iso(esc(nom))), T("Prix de toutes les eaux minérales en Tunisie", "أسعار كل المياه المعدنية في تونس"), None, maj_fr, lang)}
<div class="wrap">
  <section>
    <div class="card" style="max-width:680px">
      <div class="card-head">
        {photo_html}
        <div class="id"><h2 style="margin:0">{esc(nom)}</h2></div>
      </div>
      {f'<div class="meta">{" · ".join(meta_bits)}</div>' if meta_bits else ""}
      {tableau}
    </div>
    {bas}
    {credit}
    <a class="bouton-wa" href="{wa}" target="_blank" rel="noopener">{ICONE_WA}{T("Partager sur WhatsApp", "شارك على واتساب")}</a>
  </section>
  <section>{compo_html}</section>
  <section>
    {commande}
  </section>
</div>
{pied("../../", lang)}
</body>
</html>
"""


# ---------------------------------------------------------------- génération
# Une adresse par langue (21/11/2026) : chaque page est préparée en français et en arabe, puis tools/langues.py les écrit
# ensemble (<chemin>/ et ar/<chemin>/), une fois connue la liste de toutes les pages arabes (liens qui restent dans ar/).
LG.MIROIR.add("")                                     # l'accueil existe en arabe (ar/index.html, fabriqué plus bas)
urls = [f"{SITE}/"]
for b in data["brands"]:
    LG.ajouter(f"marque/{b['id']}/", page_marque(b), page_marque(b, "ar"))
    urls.append(f"{SITE}/marque/{b['id']}/")

# pages de marques disparues de la liste : on les retire
ids = {b["id"] for b in data["brands"]}
for d in (ROOT / "marque").iterdir():
    if d.is_dir() and d.name not in ids:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()

# pages guides (prix de la stika du jour, quelle eau choisir)
sys.path.insert(0, str(ROOT / "tools"))
from build_guides import generer  # noqa: E402
urls += generer(data, COMPO, SITE, ROOT, maj_fr)

# rapports du mois (18/10/2026, règle commune § 25) : rapports/ et rapports/AAAA-MM/, chiffres tirés de data/historique.json
import build_guides as G  # noqa: E402
from build_rapports import generer as generer_rapports  # noqa: E402
urls_rapports = generer_rapports(data, SITE, G)          # (url, date des chiffres) : un mois fini garde sa date

# toutes les pages préparées : écrites maintenant, en français et en arabe
LG.ecrire_tout(str(ROOT))

# page vidéo (video/) tirée de quelle-eau/ : mêmes en-tête, pied, CSP et ?v= (tools/page_video.py, réglages page_video.json) ;
# elle garde UNE adresse (?lang=ar) : ni langue fixe, ni bouton de langue, ni hreflang de sa page modèle
from page_video import pages_video  # noqa: E402
urls_video = [SITE + "/" + c for c in pages_video(str(ROOT))]
for c in urls_video:
    LG.page_unique(str(ROOT / c.replace(SITE + "/", "") / "index.html"))

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
# accueil arabe : ar/index.html tiré d'index.html (tools/langues.py, ACCUEIL) ; hreflang et bouton de langue sur les deux
fr_acc, ar_acc = LG.finir(html, LG.accueil_ar(html, nb), "")
index.write_text(fr_acc, encoding="utf-8", newline="\n")
LG.ecrire(str(ROOT), "ar/", ar_acc)
if LG.MANQUES:
    print("ATTENTION accueil arabe : morceau(x) d'index.html sans traduction (tools/langues.py, ACCUEIL) :", *LG.MANQUES, sep="\n  ")

# pages arabes dont la page française a disparu (marque retirée…) : retirées
for c in LG.nettoyer(str(ROOT)):
    print("page arabe retirée : ar/" + c)

# sitemap : chaque page française puis sa version arabe (ar/…), avec la date de ses chiffres
today = date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
toutes = [(u, today) for u in urls] + urls_rapports + [(u, today) for u in urls_video]
for i, (u, lm) in enumerate(toutes):
    chemin = u.replace(SITE + "/", "")
    versions = [u] + ([f"{SITE}/ar/{chemin}"] if chemin in LG.MIROIR else [])
    for v in versions:
        sm.append(f"  <url><loc>{v}</loc><lastmod>{lm}</lastmod>"
                  f"<changefreq>daily</changefreq><priority>{'1.0' if i == 0 else '0.7'}</priority></url>")
sm.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")

n_sm = len(sm) - 3
print(f"{len(data['brands'])} pages marque générées (+ arabe) · sitemap {n_sm} URLs · liens accueil : {lien_accueil}")
