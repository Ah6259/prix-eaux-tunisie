# -*- coding: utf-8 -*-
"""Pages « guides » pour Google, régénérées chaque nuit avec les prix du jour
(appelé par build_pages.py) :
  - prix-stika/  : prix de la stika d'eau en Tunisie aujourd'hui (FR + AR), toutes marques
  - quelle-eau/  : quelle eau choisir (peu salée, faiblement minéralisée, calcium, magnésium…)
                   d'après la composition officielle (data/composition.js)
  - prix-eau-<magasin>/ : prix de l'eau chez Carrefour, Géant, Monoprix, Otrity (08/10/2026, plan Google :
                   « une page par recherche » — les gens tapent « prix eau carrefour »)
"""
import json
import urllib.parse
from datetime import datetime

GRAND_FORMAT = 2.5


def _esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Mention des sources en bas de chaque page (les CGU de Carrefour demandent de citer la source)
SOURCES_HTML = ('Prix indicatifs relevés sur les boutiques en ligne : '
                '<a href="https://www.carrefour.tn" rel="noopener">Carrefour Tunisie</a> · '
                '<a href="https://www.geantdrive.tn" rel="noopener">Géant Drive</a> · '
                '<a href="https://otrity.com" rel="noopener">Otrity</a> · Monoprix (application). '
                'Les noms, marques et logos des enseignes appartiennent à leurs propriétaires.')

# Version de la feuille de style (cache des téléphones) : la changer avec celle d'index.html
CSS_V = "20261009e"

# Logo (goutte en aplats dans un carré bleu, comme l'icône du téléphone) : même dessin que l'en-tête de l'accueil
LOGO_SVG = ('<svg class="logo-mark" viewBox="0 0 512 512" aria-hidden="true"><defs><linearGradient id="lg-eau{n}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1797C4"/><stop offset="1" stop-color="#0A5F80"/></linearGradient></defs><rect width="512" height="512" rx="112" fill="url(#lg-eau{n})"/><path d="M256 84C256 84 142 236 142 318a114 114 0 0 0 228 0C370 236 256 84 256 84Z" fill="#fff"/><path d="M256 84C256 84 370 236 370 318a114 114 0 0 1-114 114Z" fill="#D5EEF7"/><path d="M150 336Q203 306 256 336T362 336Q356 410 256 432Q156 410 150 336Z" fill="#7FCBE6"/><path d="M256 336Q309 366 362 336Q356 410 256 432Z" fill="#5DB7D9"/></svg>')

ICONE_WA = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 '
            '12 2zm4.6 12.1c-.3-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.6.1a6.7 6.7 0 0 1-2-1.2 7.4 7.4 0 0 '
            '1-1.4-1.7c-.1-.3 0-.4.1-.5l.4-.5c.1-.2.2-.3.3-.5s0-.4 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 '
            '0-.7.3 2.9 2.9 0 0 0-.9 2.1 5 5 0 0 0 1 2.7 11.4 11.4 0 0 0 4.4 3.9c1.6.7 2.3.7 3.1.6a2.6 2.6 0 0 0 '
            '1.7-1.2 2.1 2.1 0 0 0 .2-1.2c-.1-.1-.3-.2-.6-.3z"/></svg>')


def entete(racine):
    """En-tête blanc des pages générées : logo + nom du site (lien vers l'accueil)."""
    return (f'<header class="site"><div class="wrap site-inner">\n'
            f'  <a class="titre" href="{racine}">{LOGO_SVG.format(n="")}'
            f'<div class="titre-txt"><p class="h-site">Prix des Eaux de Tunisie</p>'
            f'<p class="stats-line">Comparateur indépendant</p></div></a>\n'
            f'</div></header>')


def bandeau(racine, h1, retour, ar=None, maj=None):
    """Bandeau bleu : lien de retour, titre de la page, ligne en arabe, pastille « à jour »."""
    return (f'<div class="hero page-hero"><div class="wrap">\n'
            f'  <p class="fil"><a href="{racine}">← {retour}</a></p>\n'
            f'  <h1>{h1}</h1>\n'
            + (f'  <p class="ar" dir="rtl" lang="ar">{ar}</p>\n' if ar else "")
            + (f'  <span class="maj">Prix relevés le {maj}</span>\n' if maj else "")
            + '</div></div>')


def pied(racine):
    """Pied de page complet, le même sur toutes les pages générées."""
    return f"""<footer><div class="wrap pied">
  <p class="pied-logo">{LOGO_SVG.format(n="-pied")}Prix des Eaux de Tunisie</p>
  <p class="pied-desc">Comparateur indépendant des prix de l'eau en bouteille en Tunisie.
  Site non officiel, sans lien avec les enseignes ni avec les marques citées.</p>
  <nav class="pied-nav" aria-label="Liens utiles"><a href="{racine}">Comparateur des prix de l'eau</a>
  <a href="{racine}prix-stika/">Prix de la stika aujourd'hui</a>
  <a href="{racine}quelle-eau/">Quelle eau choisir ?</a>
  <a href="https://ah6259.github.io/points-eau-tunisie/" rel="noopener">Où trouver de l'eau (sources, majels)</a>
  {_liens_magasins(racine)}
  <a href="https://t.me/prixeautunisie" rel="noopener">Alertes promo (Telegram)</a></nav>
  <p class="pied-titre">Sources des prix</p>
  <p class="pied-sources">{SOURCES_HTML}</p>
  <p class="credit-pied">Photos de bouteilles des marques absentes des boutiques suivies : <a href="https://world.openfoodfacts.org/" rel="noopener">Open Food Facts</a>, <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.fr" rel="license noopener">CC BY-SA 3.0</a>.</p>
  <p class="copyright">© 2026 Prix des Eaux de Tunisie — tous droits réservés.</p>
</div></footer>
<!-- Statistiques de visite anonymes, sans cookies (GoatCounter) -->
<script data-goatcounter="https://prix-eaux-tunisie.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>"""


MAGASINS = {"Carrefour": ("prix-eau-carrefour", "كارفور"), "Géant": ("prix-eau-geant", "جيان"),
            "Monoprix": ("prix-eau-monoprix", "مونوبري"), "Otrity": ("prix-eau-otrity", "أوتريتي")}


def _liens_magasins(racine):
    return "\n  ".join(f'<a href="{racine}{c}/">Prix de l&#39;eau chez {m}</a>' for m, (c, _) in MAGASINS.items())


NOMS_COLONNES = {"na": "Sodium", "tds": "Résidu sec", "ca": "Calcium", "mg": "Magnésium"}


def _iso(s):
    """Isole un mot latin (nom, prix) dans une phrase arabe : évite l'ordre « DT 3,540 بـ Melina »."""
    return "⁨" + str(s) + "⁩"


def _dt(v):
    return f"{v:,.3f}".replace(",", " ").replace(".", ",") + " DT"


def _gabarit(SITE, chemin, titre, description, h1, corps, jsonld=None, ar_titre=None, maj=None):
    return f"""<!doctype html>
<html lang="fr" translate="no">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://gc.zgo.at https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://cdnjs.cloudflare.com https://prix-eaux-tunisie.goatcounter.com; connect-src 'self' https://docs.google.com https://formspree.io https://prix-eaux-tunisie.goatcounter.com; form-action 'self' https://docs.google.com https://formspree.io; object-src 'none'; base-uri 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="noai, noimageai">
<script src="../protection.js?v={CSS_V}"></script>
<title>{_esc(titre)}</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{SITE}/{chemin}/">
<meta property="og:title" content="{_esc(titre)}">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:image" content="{SITE}/assets/og-image-v7.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="icon" type="image/svg+xml" href="../assets/icons/icon.svg">
<link rel="manifest" href="../manifest.webmanifest">
<link rel="apple-touch-icon" href="../assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Prix Eaux">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../style.css?v={CSS_V}">
{f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""}
<style>
  .guide-table{{width:100%; border-collapse:collapse; font-size:14px; background:var(--surface); border:1px solid var(--line); border-radius:12px}}
  .guide-table th,.guide-table td{{padding:7px 10px; border-top:1px solid var(--line); text-align:left}}
  .guide-table th{{font-size:12px; color:var(--muted); border-top:0}}
  .guide-table td.n{{text-align:right; font-variant-numeric:tabular-nums; font-weight:700}}
  .guide-table a{{color:var(--ink); font-weight:600}}
  .guide-table.magasin{{font-size:13px}} .guide-table.magasin th,.guide-table.magasin td{{padding:7px 6px}}
  .guide-table.magasin td.n{{white-space:nowrap}} .guide-table small{{display:block; color:var(--muted); font-weight:400}}
  .ar{{font-size:15px; color:var(--muted); margin:4px 0 0}}
  .avert{{background:var(--gaz-soft); color:var(--gaz); border-radius:10px; padding:9px 12px; font-size:13px}}
</style>
</head>
<body>
{entete("../")}
{bandeau("../", _esc(h1), "Comparateur des prix de l'eau en Tunisie", _esc(ar_titre) if ar_titre else None, maj)}
<div class="wrap">
  {corps}
</div>
{pied("../")}
</body>
</html>
"""


def _partage(SITE, chemin, texte):
    url = "https://wa.me/?text=" + urllib.parse.quote(f"{texte} {SITE}/{chemin}/")
    return f'<a class="bouton-wa" href="{url}" target="_blank" rel="noopener">{ICONE_WA}Partager sur WhatsApp</a>'


def _meilleur(b, litres):
    c = [p for p in b.get("products") or [] if p["category"] == "plate" and not p.get("flavor")
         and abs(p["liters"] - litres) < .01 and p["prices"]]
    if not c:
        return None
    p = min(c, key=lambda p: min(p["prices"].values()))
    m = min(p["prices"].values())
    return m, [s for s, v in p["prices"].items() if v == m]


def page_prix_stika(data, SITE, maj_fr):
    def tableau(litres, n):
        rows = sorted(((b, _meilleur(b, litres)) for b in data["brands"]), key=lambda x: x[1][0] if x[1] else 9e9)
        rows = [(b, m) for b, m in rows if m]
        if not rows:
            return "", None
        lignes = "".join(f"<tr><td>{i}</td><td><a href='../marque/{b['id']}/'>{_esc(b['name'])}</a></td>"
                         f"<td class='n'>{_dt(m[0] * n)}</td><td>{_esc(', '.join(m[1]))}</td></tr>"
                         for i, (b, m) in enumerate(rows, 1))
        return (f"<table class='guide-table'><tr><th>#</th><th>Marque</th><th>Prix de la stika</th>"
                f"<th>Le moins cher chez</th></tr>{lignes}</table>"), rows
    t15, r15 = tableau(1.5, 6)
    t05, _ = tableau(0.5, 12)
    if not r15:
        return None
    g, (pg, mg) = r15[0][0], r15[0][1]
    corps = f"""
  <section>
    <p class="intro"><strong>Aujourd'hui ({maj_fr}), la stika d'eau 1,5 L la moins chère en Tunisie est
    {_esc(g['name'])} à {_dt(pg * 6)}</strong> (6 bouteilles, chez {_esc(', '.join(mg))}).
    Les prix ci-dessous sont relevés chaque jour dans les grandes surfaces et épiceries en ligne ;
    ils sont indicatifs et peuvent varier selon le magasin.</p>
    {_partage(SITE, "prix-stika", f"💧 Stika d'eau la moins chère aujourd'hui : {g['name']} {_dt(pg * 6)}.")}
  </section>
  <section>
    <h2>Stika 1,5 L (6 bouteilles)</h2>
    {t15}
  </section>
  {f'<section><h2>Stika 0,5 L (12 bouteilles)</h2>{t05}</section>' if t05 else ""}
  <section>
    <h2>Qu'est-ce qu'une stika ?</h2>
    <p class="intro">En Tunisie, la « stika » (ستيكة) est le pack de bouteilles d'eau : 6 bouteilles de 1,5 L
    ou 12 bouteilles de 0,5 L. Son prix est ici calculé à partir du prix de la bouteille en magasin.</p>
  </section>"""
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "Quel est le prix d'une stika d'eau en Tunisie aujourd'hui ?",
         "acceptedAnswer": {"@type": "Answer", "text":
             f"Le {maj_fr}, la stika 1,5 L la moins chère est {g['name']} à {_dt(pg * 6)} (6 bouteilles)."}},
        {"@type": "Question", "name": "كم ثمن ستيكة الماء في تونس اليوم؟",
         "acceptedAnswer": {"@type": "Answer", "text":
             f"أرخص ستيكة ماء 1,5 لتر اليوم: {_iso(g['name'])} بـ {_iso(_dt(pg * 6))}."}}]}, ensure_ascii=False)
    return _gabarit(SITE, "prix-stika",
                    f"Prix de la stika d'eau en Tunisie aujourd'hui — {g['name']} à {_dt(pg * 6)}",
                    f"Prix de la stika d'eau minérale en Tunisie le {maj_fr} : la moins chère est {g['name']} "
                    f"à {_dt(pg * 6)}. Comparatif gratuit de toutes les marques, mis à jour chaque jour.",
                    "Prix de la stika d'eau aujourd'hui", corps, jsonld,
                    f"ثمن ستيكة الماء في تونس اليوم — أرخص ستيكة: {_iso(g['name'])} بـ {_iso(_dt(pg * 6))}", maj=maj_fr)


def page_quelle_eau(data, COMPO, SITE, maj_fr):
    marques = {b["id"]: b for b in data["brands"]}
    eaux = []
    for bid, lst in COMPO["waters"].items():
        if bid not in marques or not lst:
            continue
        e = lst[0]
        m = _meilleur(marques[bid], 1.5)
        eaux.append({"b": marques[bid], "c": e, "stika": m[0] * 6 if m else None})

    def liste(titre, explication, filtre, cle, unite, croissant=True, n=8):
        sel = sorted((x for x in eaux if filtre(x["c"])), key=lambda x: x["c"][cle], reverse=not croissant)[:n]
        if not sel:
            return ""
        lignes = "".join(f"<tr><td><a href='../marque/{x['b']['id']}/'>{_esc(x['b']['name'])}</a></td>"
                         f"<td class='n'>{x['c'][cle]:g} {unite}</td>"
                         f"<td class='n'>{_dt(x['stika']) if x['stika'] else '—'}</td></tr>" for x in sel)
        return (f"<section><h2>{titre}</h2><p class='sub'>{explication}</p>"
                f"<table class='guide-table'><tr><th>Marque</th><th>{NOMS_COLONNES.get(cle, cle)}</th>"
                f"<th>Stika 1,5 L dès</th></tr>{lignes}</table></section>")

    corps = f"""
  <p class="avert">⚠️ Guide indicatif, établi d'après la composition officielle des eaux (Office du Thermalisme).
  Il ne remplace pas l'avis d'un médecin, d'un pédiatre ou d'un pharmacien.</p>
  {liste("Eaux les moins salées (pauvres en sodium)",
         "Moins de 20 mg/L de sodium : conseillées pour un régime pauvre en sel ; souvent recommandées pour les biberons (demandez l'avis du pédiatre).",
         lambda c: c["na"] < 20, "na", "mg/L")}
  {liste("Eaux les plus légères (faiblement minéralisées)",
         "Résidu sec bas : eau légère, adaptée à une consommation quotidienne pour toute la famille.",
         lambda c: c["tds"] < 500, "tds", "mg/L")}
  {liste("Eaux riches en calcium",
         "Au moins 100 mg/L de calcium : apport utile pour les os (enfants, femmes enceintes, seniors).",
         lambda c: c["ca"] >= 100, "ca", "mg/L", croissant=False)}
  {liste("Eaux riches en magnésium",
         "Au moins 50 mg/L de magnésium : contre la fatigue et les crampes, utile aux sportifs.",
         lambda c: c["mg"] >= 50, "mg", "mg/L", croissant=False)}
  {liste("Eaux les plus minéralisées",
         "Résidu sec élevé : eau « lourde », à alterner avec une eau plus légère.",
         lambda c: c["tds"] >= 1000, "tds", "mg/L", croissant=False)}
  <section><p class="sub">Source : {_esc(COMPO['credit']['name'])} —
  <a href="{COMPO['credit']['url']}" rel="noopener">voir la publication</a>. Prix : relevés du {maj_fr}.</p>
  {_partage(SITE, "quelle-eau", "💧 Quelle eau minérale choisir en Tunisie (bébé, peu salée, calcium…) :")}</section>"""
    return _gabarit(SITE, "quelle-eau",
                    "Quelle eau minérale choisir en Tunisie ? Bébé, peu salée, calcium, magnésium",
                    "Quelle eau minérale choisir en Tunisie : eaux pauvres en sodium (bébé, régime sans sel), "
                    "eaux légères, riches en calcium ou en magnésium, avec leur prix de la stika. Guide gratuit.",
                    "Quelle eau minérale choisir ?", corps, None,
                    "أي ماء معدني أختار في تونس؟ ماء للرضيع، قليل الملح، غني بالكالسيوم", maj=maj_fr)


def _fmt_l(litres):
    return (f"{litres:g} L".replace(".", ",") if litres >= 1 else f"{litres * 1000:g} ml")


def page_magasin(data, magasin, SITE, maj_fr):
    """Prix de l'eau chez un magasin : une ligne par produit (marque + format), le moins cher d'abord.
    Colonne « ailleurs dès » = meilleur prix des autres magasins suivis (pour comparer d'un coup d'œil)."""
    chemin, nom_ar = MAGASINS[magasin]
    lignes = []
    for b in data["brands"]:
        for p in b.get("products") or []:
            v = p["prices"].get(magasin)
            if v is None or p.get("flavor"):
                continue
            autres = [x for s, x in p["prices"].items() if s != magasin]
            lignes.append((b, p, v, min(autres) if autres else None))
    if len(lignes) < 3:
        return None
    def tableau(filtre, titre, fmt=True):
        sel = sorted((x for x in lignes if filtre(x[1])), key=lambda x: x[2])
        if not sel:
            return ""
        def stika(p, v):
            n = 12 if p["liters"] <= .75 else 6 if p["liters"] <= GRAND_FORMAT else 1
            return _dt(v * n) if n > 1 else "—"
        tr = "".join(f"<tr><td><a href='../marque/{b['id']}/'>{_esc(b['name'])}</a>"
                     f"{' <small>gazeuse</small>' if p['category'] == 'gazeuse' else ''}"
                     f"{' <small>' + _fmt_l(p['liters']) + '</small>' if fmt else ''}</td>"
                     f"<td class='n'>{_dt(v)}</td><td class='n'>{stika(p, v)}</td>"
                     f"<td class='n'>{_dt(a) if a is not None else '—'}</td></tr>" for b, p, v, a in sel)
        return (f"<section><h2>{titre}</h2><table class='guide-table magasin'><tr><th>Marque</th><th>Bouteille</th>"
                f"<th>Stika</th><th>Ailleurs dès</th></tr>{tr}</table></section>")
    eau15 = sorted((x for x in lignes if abs(x[1]["liters"] - 1.5) < .01 and x[1]["category"] == "plate"), key=lambda x: x[2])
    if eau15:
        b0, _, v0, _ = eau15[0]
        accroche = (f"<strong>Chez {magasin}, la stika d'eau 1,5 L la moins chère aujourd'hui ({maj_fr}) est "
                    f"{_esc(b0['name'])} à {_dt(v0 * 6)}</strong> (6 bouteilles).")
        court = f"stika dès {_dt(v0 * 6)}"
        ar = f"ثمن الماء المعدني في {nom_ar} اليوم — أرخص ستيكة 1,5 لتر: {_iso(b0['name'])} بـ {_iso(_dt(v0 * 6))}"
        rep_fr = f"Le {maj_fr}, la stika d'eau 1,5 L la moins chère chez {magasin} est {b0['name']} à {_dt(v0 * 6)}."
        rep_ar = f"أرخص ستيكة ماء 1,5 لتر في {nom_ar} اليوم: {_iso(b0['name'])} بـ {_iso(_dt(v0 * 6))}."
    else:
        b0, _, v0, _ = min(lignes, key=lambda x: x[2] / x[1]["liters"])
        accroche = f"<strong>{len(lignes)} prix d'eau relevés chez {magasin} ({maj_fr}).</strong>"
        court = f"{len(lignes)} prix"
        ar = f"ثمن الماء المعدني في {nom_ar} اليوم"
        rep_fr = f"{len(lignes)} prix d'eau sont relevés chez {magasin} le {maj_fr}."
        rep_ar = f"أسعار الماء المعدني في {nom_ar} اليوم."
    autres = " · ".join(f'<a href="../{c}/">{m}</a>' for m, (c, _) in MAGASINS.items() if m != magasin)
    corps = f"""
  <section>
    <p class="intro">{accroche} Les prix sont ceux de la bouteille, et de la stika (6 bouteilles de 1,5 L ou 12 de 0,5 L).
    Ils sont indicatifs et peuvent varier selon le magasin. La colonne « Ailleurs dès » montre le meilleur prix des autres magasins suivis.</p>
    {_partage(SITE, chemin, f"💧 Prix de l'eau chez {magasin} aujourd'hui : {court}.")}
  </section>
  {tableau(lambda p: abs(p["liters"] - 1.5) < .01 and p["category"] == "plate", "Eau 1,5 L", fmt=False)}
  {tableau(lambda p: p["liters"] <= .75, "Petites bouteilles (0,5 L et moins)")}
  {tableau(lambda p: not (abs(p["liters"] - 1.5) < .01 and p["category"] == "plate") and p["liters"] > .75, "Autres formats et eau gazeuse")}
  <section><p class="sub">Comparer avec : {autres} · <a href="../prix-stika/">toutes les marques</a> · <a href="../">le comparateur</a>.</p></section>"""
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f"Quel est le prix de l'eau chez {magasin} en Tunisie ?",
         "acceptedAnswer": {"@type": "Answer", "text": rep_fr}},
        {"@type": "Question", "name": f"كم ثمن الماء المعدني في {nom_ar}؟",
         "acceptedAnswer": {"@type": "Answer", "text": rep_ar}}]}, ensure_ascii=False)
    return _gabarit(SITE, chemin,
                    f"Prix de l'eau chez {magasin} Tunisie aujourd'hui — {court}, comparateur gratuit",
                    f"Prix de l'eau minérale chez {magasin} le {maj_fr} : bouteille et stika, toutes les marques, "
                    f"comparées aux autres magasins. Comparateur gratuit mis à jour chaque jour.",
                    f"Prix de l'eau chez {magasin}", corps, jsonld, ar, maj=maj_fr)


def generer(data, COMPO, SITE, ROOT, maj_fr):
    """Écrit les pages guides et renvoie leurs URL (pour le sitemap)."""
    urls = []
    for chemin, html in (("prix-stika", page_prix_stika(data, SITE, maj_fr)),
                         ("quelle-eau", page_quelle_eau(data, COMPO, SITE, maj_fr)),
                         *((c, page_magasin(data, m, SITE, maj_fr)) for m, (c, _) in MAGASINS.items())):
        if not html:
            continue
        d = ROOT / chemin
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"{SITE}/{chemin}/")
    return urls
