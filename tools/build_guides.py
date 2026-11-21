# -*- coding: utf-8 -*-
"""Pages « guides » pour Google, régénérées chaque nuit avec les prix du jour
(appelé par build_pages.py) :
  - prix-stika/  : prix de la stika d'eau en Tunisie aujourd'hui (FR, et AR dans ar/), toutes marques
  - quelle-eau/  : quelle eau choisir (peu salée, faiblement minéralisée, calcium, magnésium…)
                   d'après la composition officielle (data/composition.js)
  - prix-eau-<magasin>/ : prix de l'eau chez Carrefour et Géant (08/10/2026, plan Google :
                   « une page par recherche » — les gens tapent « prix eau carrefour »)
  - prix-eau-monoprix/, prix-eau-otrity/ : enseignes RETIRÉES le 23/10/2026 (décision d'Ahmed : site autonome,
                   ces prix ne se lisaient pas depuis GitHub) -> courte page « n'est plus suivi » en noindex,
                   hors du plan du site et sans lien (pas de 404 pour Google) : page_retiree() / RETIRES
"""
import json
import os
import sys
import urllib.parse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import langues as LG  # noqa: E402  (une adresse par langue : pages françaises + ar/)

GRAND_FORMAT = 2.5


def _esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Mention des sources en bas de chaque page (les CGU de Carrefour demandent de citer la source)
SOURCES_HTML = ('Prix indicatifs relevés sur les boutiques en ligne : '
                '<a href="https://www.carrefour.tn" rel="noopener">Carrefour Tunisie</a> · '
                '<a href="https://www.geantdrive.tn" rel="noopener">Géant Drive</a>. '
                'Les noms, marques et logos des enseignes appartiennent à leurs propriétaires.')

# Version de la feuille de style (cache des téléphones) : la changer avec celle d'index.html
CSS_V = "20261121c"

# Logo (goutte en aplats dans un carré bleu, comme l'icône du téléphone) : même dessin que l'en-tête de l'accueil
LOGO_SVG = ('<svg class="logo-mark" viewBox="0 0 512 512" aria-hidden="true"><defs><linearGradient id="lg-eau{n}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1797C4"/><stop offset="1" stop-color="#0A5F80"/></linearGradient></defs><rect width="512" height="512" rx="112" fill="url(#lg-eau{n})"/><path d="M256 84C256 84 142 236 142 318a114 114 0 0 0 228 0C370 236 256 84 256 84Z" fill="#fff"/><path d="M256 84C256 84 370 236 370 318a114 114 0 0 1-114 114Z" fill="#D5EEF7"/><path d="M150 336Q203 306 256 336T362 336Q356 410 256 432Q156 410 150 336Z" fill="#7FCBE6"/><path d="M256 336Q309 366 362 336Q356 410 256 432Z" fill="#5DB7D9"/></svg>')

ICONE_WA = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 '
            '12 2zm4.6 12.1c-.3-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.6.1a6.7 6.7 0 0 1-2-1.2 7.4 7.4 0 0 '
            '1-1.4-1.7c-.1-.3 0-.4.1-.5l.4-.5c.1-.2.2-.3.3-.5s0-.4 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 '
            '0-.7.3 2.9 2.9 0 0 0-.9 2.1 5 5 0 0 0 1 2.7 11.4 11.4 0 0 0 4.4 3.9c1.6.7 2.3.7 3.1.6a2.6 2.6 0 0 0 '
            '1.7-1.2 2.1 2.1 0 0 0 .2-1.2c-.1-.1-.3-.2-.6-.3z"/></svg>')


def entete(racine, lang="fr"):
    """En-tête blanc des pages générées : logo + nom du site (lien vers l'accueil) + bouton de langue (vers l'autre adresse)."""
    T = lambda fr, ar: ar if lang == "ar" else fr
    return (f'<header class="site"><div class="wrap site-inner">\n'
            f'  <a class="titre" href="{racine}">{LOGO_SVG.format(n="")}'
            f'<div class="titre-txt"><p class="h-site">{T("Prix des Eaux de Tunisie", "أسعار الماء في تونس")}</p>'
            f'<p class="stats-line">{T("Comparateur indépendant", "مقارن مستقل")}</p></div></a>\n'
            f'  {LG.bouton_langue(lang)}\n'
            f'</div></header>')


def bandeau(racine, h1, retour, ar=None, maj=None, lang="fr"):
    """Bandeau bleu : lien de retour, titre de la page, pastille « à jour ». (ar : ancien paramètre, plus utilisé : chaque page
    est maintenant écrite dans UNE langue, la page arabe est dans ar/.)"""
    fleche = "→" if lang == "ar" else "←"
    return (f'<div class="hero page-hero"><div class="wrap">\n'
            f'  <p class="fil"><a href="{racine}">{fleche} {retour}</a></p>\n'
            f'  <h1>{h1}</h1>\n'
            + (f'  <span class="maj">{"الأسعار مقروءة يوم" if lang == "ar" else "Prix relevés le"} {maj}</span>\n' if maj else "")
            + '</div></div>')


def pied(racine, lang="fr"):
    """Pied de page complet, le même sur toutes les pages générées (dans la langue de la page)."""
    T = lambda fr, ar: ar if lang == "ar" else fr
    ar_ = "ar/" if lang == "ar" else ""
    return f"""<footer><div class="wrap pied">
  <p class="pied-logo">{LOGO_SVG.format(n="-pied")}{T("Prix des Eaux de Tunisie", "أسعار الماء في تونس")}</p>
  <p class="pied-desc">{T("Comparateur indépendant des prix de l'eau en bouteille en Tunisie.\n  Site non officiel, sans lien avec les enseignes ni avec les marques citées.",
                          "مقارن مستقل لأسعار الماء المعبّأ في تونس. موقع غير رسمي، لا علاقة له بالمغازات ولا بالعلامات المذكورة.")}</p>
  <nav class="pied-nav" aria-label="{T("Liens utiles", "روابط مفيدة")}"><a href="{racine}">{T("Comparateur des prix de l'eau", "مقارن أسعار الماء")}</a>
  <a href="{racine}prix-stika/">{T("Prix de la stika aujourd'hui", "سعر الستيكة اليوم")}</a>
  <a href="{racine}quelle-eau/">{T("Quelle eau choisir ?", "أي ماء تختار؟")}</a>
  <a href="{racine}rapports/">{T("Rapports du mois (prix par marque)", "تقارير الشهر (الأسعار حسب العلامة)")}</a>
  <a href="{racine}a-propos/">{T("Comment fonctionne le site ?", "كيف يعمل الموقع؟")}</a>
  <a href="https://eau.clicvia.com/" rel="noopener">{T("Où trouver de l'eau (sources, majels)", "أين تجد الماء (عيون، مواجل)")}</a>
  <a href="https://clicvia.com/" rel="noopener">{T("Tous nos services", "كل خدماتنا")}</a>
  <a href="https://clicvia.com/{ar_}confidentialite/" rel="noopener">{T("Confidentialité", "الخصوصية")}</a>
  <a href="https://clicvia.com/{ar_}conditions/" rel="noopener">{T("Conditions d'utilisation", "شروط الاستعمال")}</a>
  {_liens_magasins(racine, lang)}
  <a href="https://t.me/prixeautunisie" rel="noopener">{T("Alertes promo (Telegram)", "تنبيهات التخفيضات (تيليغرام)")}</a></nav>
  <p class="pied-titre">{T("Sources des prix", "مصادر الأسعار")}</p>
  <p class="pied-sources">{sources_html(lang)}</p>
  <p class="credit-pied">{T("Photos de bouteilles des marques absentes des boutiques suivies", "صور قوارير العلامات غير الموجودة في المغازات المتابَعة")} : <a href="https://world.openfoodfacts.org/" rel="noopener">Open Food Facts</a>, <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.{lang}" rel="license noopener">CC BY-SA 3.0</a>.</p>
  <p class="copyright">© 2026 {T("Prix des Eaux de Tunisie — tous droits réservés.", "أسعار الماء في تونس — جميع الحقوق محفوظة.")}</p>
</div></footer>
<!-- Statistiques de visite anonymes, sans cookies (GoatCounter) -->
<script data-goatcounter="https://prix-eaux-tunisie.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>"""


def sources_html(lang="fr"):
    if lang != "ar":
        return SOURCES_HTML
    return ('أسعار تقريبية مقروءة من المتاجر الإلكترونية: '
            '<a href="https://www.carrefour.tn" rel="noopener">Carrefour</a> · '
            '<a href="https://www.geantdrive.tn" rel="noopener">Géant Drive</a>. '
            'أسماء المغازات وعلاماتها وشعاراتها ملك لأصحابها.')


MAGASINS = {"Carrefour": ("prix-eau-carrefour", "كارفور"), "Géant": ("prix-eau-geant", "جيان")}
# Enseignes retirées du comparateur (23/10/2026, décision d'Ahmed : le site doit être autonome) : Otrity bloque GitHub
# (Cloudflare, API wp-json comprise), Monoprix bloque même le PC. Leur ancienne page reste en ligne, courte et en noindex.
RETIRES = {"Monoprix": ("prix-eau-monoprix", "مونوبري"), "Otrity": ("prix-eau-otrity", "أوتريتي")}


def _liens_magasins(racine, lang="fr"):
    if lang == "ar":
        return "\n  ".join(f'<a href="{racine}{c}/">سعر الماء في {a}</a>' for m, (c, a) in MAGASINS.items())
    return "\n  ".join(f'<a href="{racine}{c}/">Prix de l&#39;eau chez {m}</a>' for m, (c, _) in MAGASINS.items())


NOMS_COLONNES = {"na": "Sodium", "tds": "Résidu sec", "ca": "Calcium", "mg": "Magnésium"}
NOMS_COLONNES_AR = {"na": "الصوديوم", "tds": "البقايا الجافة", "ca": "الكالسيوم", "mg": "المغنيزيوم"}


def _iso(s):
    """Isole un mot latin (nom, prix) dans une phrase arabe : évite l'ordre « DT 3,540 بـ Melina »."""
    return "⁨" + str(s) + "⁩"


def _dt(v, lang="fr"):
    return LG.dt(v, lang)


def _titre_seo(t, maxi=70):
    """SEO (08/11/2026) : Google coupe les titres vers 60-70 caractères -> le suffixe « | Prix des Eaux de Tunisie » saute si le titre dépasse."""
    if len(t) <= maxi:
        return t
    court = t.split(" | ")[0].strip()
    if len(court) <= maxi:
        return court
    t = court
    for sep in (" : ", " — ", " (", " – ", "؛ ", "، "):
        i = t.rfind(sep, 0, maxi)
        if i >= 25:
            return t[:i].rstrip(" ,;:—-،")
    return t[:maxi - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-(،") + "…"


def _desc_seo(d, maxi=165):
    if len(d) <= maxi:
        return d
    coupe = d[:maxi]
    i = max(coupe.rfind(". "), coupe.rfind(".⁩ "))
    return coupe[:i + 1] if i >= 60 else coupe[:maxi - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-(،") + "…"


def _gabarit(SITE, chemin, titre, description, h1, corps, jsonld=None, ar_titre=None, maj=None, racine="../", og_type=None, og_image=None,
             noindex=False, lang="fr"):
    """Page complète dans UNE langue (lang = "fr" ou "ar"). La page arabe est écrite comme si elle était à la place de la page
    française (mêmes liens relatifs) : tools/langues.py la range dans ar/ et corrige ses liens."""
    titre, description = _titre_seo(titre), _desc_seo(description)
    retour = "مقارن أسعار الماء في تونس" if lang == "ar" else "Comparateur des prix de l'eau en Tunisie"
    html_tag = '<html lang="ar" dir="rtl" translate="no">' if lang == "ar" else '<html lang="fr" translate="no">'
    return f"""<!doctype html>
{html_tag}
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://gc.zgo.at https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://cdnjs.cloudflare.com https://prix-eaux-tunisie.goatcounter.com; connect-src 'self' https://docs.google.com https://formspree.io https://prix-eaux-tunisie.goatcounter.com; form-action 'self' https://docs.google.com https://formspree.io; object-src 'none'; base-uri 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="{'noindex, follow, ' if noindex else ''}noai, noimageai">
<script src="{racine}protection.js?v={CSS_V}"></script>
<title>{_esc(titre)}</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{SITE}/{chemin}/">
{f'<meta property="og:type" content="{og_type}">' if og_type else ""}
<meta property="og:url" content="{SITE}/{chemin}/">
<meta property="og:title" content="{_esc(titre)}">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:image" content="{SITE}/{og_image or 'assets/og-image-v7.jpg'}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="icon" type="image/svg+xml" href="{racine}assets/icons/icon.svg">
<link rel="manifest" href="{racine}manifest.webmanifest">
<link rel="apple-touch-icon" href="{racine}assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Prix Eaux">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{racine}style.css?v={CSS_V}">
{f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""}
<style>
  .guide-table{{width:100%; border-collapse:collapse; font-size:14px; background:var(--surface); border:1px solid var(--line); border-radius:12px}}
  .guide-table th,.guide-table td{{padding:7px 10px; border-top:1px solid var(--line); text-align:start}}
  .guide-table th{{font-size:12px; color:var(--muted); border-top:0}}
  .guide-table td.n{{text-align:end; font-variant-numeric:tabular-nums; font-weight:700}}
  .guide-table a{{color:var(--ink); font-weight:600}}
  /* 18/10/2026 (visiteur simulé : tableau du rapport plus large que l'écran du téléphone) : serré sur petit écran, jamais de débordement */
  @media (max-width:480px){{ .guide-table{{font-size:12.5px}} .guide-table th,.guide-table td{{padding:6px 5px}} .guide-table small{{display:block;font-size:10.5px}} }}
  .tableau-defile{{max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch}}
  .guide-table.magasin{{font-size:13px}} .guide-table.magasin th,.guide-table.magasin td{{padding:7px 6px}}
  .guide-table.magasin td.n{{white-space:nowrap}} .guide-table small{{display:block; color:var(--muted); font-weight:400}}
  /* 25/10/2026 (visiteur simulé : « dans 26 magasins sur 39 » élargissait le tableau de Carrefour à 399 px) : cette ligne peut passer à la ligne */
  .guide-table.magasin td.n small{{white-space:normal}}
  .ar{{font-size:15px; color:var(--muted); margin:4px 0 0}}
  .avert{{background:var(--gaz-soft); color:var(--gaz); border-radius:10px; padding:9px 12px; font-size:13px}}
  .rp-signature{{margin:4px 0 12px; font-size:14px; color:var(--muted)}}
  .rp-partage{{margin:12px 0 16px}}
  .rp-partager{{display:inline-flex; align-items:center; gap:8px; min-height:48px; padding:10px 20px; border:0; border-radius:999px;
    background:#0A6E95; color:#fff; font:inherit; font-weight:700; font-size:16px; cursor:pointer}}
  .rp-partager svg{{width:20px; height:20px; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round}}
  .rp-partager .rp-copie{{display:none}} .rp-partager.copie-ok{{background:#2E7D32}}
  .rp-partager.copie-ok .rp-copie{{display:inline}} .rp-partager.copie-ok .rp-a-copier{{display:none}}
  .rp-aide{{margin:6px 0 0; font-size:13px; color:var(--muted)}}
  .ap-liste{{margin:6px 0 0; padding-inline-start:20px; font-size:14.5px; line-height:1.55; max-width:68ch}}
  .ap-liste li{{margin:5px 0}}
</style>
</head>
<body>
{entete(racine, lang)}
{bandeau(racine, _esc(h1), retour, None, maj, lang)}
<div class="wrap">
  {corps}
</div>
{pied(racine, lang)}
</body>
</html>
"""


def _partage(SITE, chemin, texte, lang="fr"):
    adr = f"{SITE}/{'ar/' if lang == 'ar' else ''}{chemin}/"
    url = "https://wa.me/?text=" + urllib.parse.quote(f"{texte} {adr}")
    return f'<a class="bouton-wa" href="{url}" target="_blank" rel="noopener">{ICONE_WA}{"شارك على واتساب" if lang == "ar" else "Partager sur WhatsApp"}</a>'


def _meilleur(b, litres):
    c = [p for p in b.get("products") or [] if p["category"] == "plate" and not p.get("flavor")
         and abs(p["liters"] - litres) < .01 and p["prices"]]
    if not c:
        return None
    p = min(c, key=lambda p: min(p["prices"].values()))
    m = min(p["prices"].values())
    return m, [s for s, v in p["prices"].items() if v == m]


def page_prix_stika(data, SITE, maj_fr, lang="fr"):
    T = lambda fr, ar: ar if lang == "ar" else fr
    D = lambda v: _dt(v, lang)

    def tableau(litres, n):
        rows = sorted(((b, _meilleur(b, litres)) for b in data["brands"]), key=lambda x: x[1][0] if x[1] else 9e9)
        rows = [(b, m) for b, m in rows if m]
        if not rows:
            return "", None
        lignes = "".join(f"<tr><td>{i}</td><td><a href='../marque/{b['id']}/'>{_esc(b['name'])}</a></td>"
                         f"<td class='n'>{D(m[0] * n)}</td><td>{_esc(', '.join(m[1]))}</td></tr>"
                         for i, (b, m) in enumerate(rows, 1))
        return (f"<table class='guide-table'><tr><th>#</th><th>{T('Marque', 'العلامة')}</th><th>{T('Prix de la stika', 'سعر الستيكة')}</th>"
                f"<th>{T('Le moins cher chez', 'الأرخص في')}</th></tr>{lignes}</table>"), rows
    t15, r15 = tableau(1.5, 6)
    t05, _ = tableau(0.5, 12)
    if not r15:
        return None
    g, (pg, mg) = r15[0][0], r15[0][1]
    if lang == "ar":
        corps = f"""
  <section>
    <p class="intro"><strong>اليوم ({maj_fr})، أرخص ستيكة ماء 1,5 لتر في تونس هي {_iso(_esc(g['name']))} بـ {D(pg * 6)}</strong>
    (6 قوارير، في {_iso(_esc(', '.join(mg)))}). الأسعار أسفله تُقرأ كل يوم من المتاجر الإلكترونية للمغازات الكبرى (Carrefour وGéant)؛
    هي أسعار تقريبية وقد تتغيّر حسب المغازة.</p>
    {_partage(SITE, "prix-stika", f"💧 أرخص ستيكة ماء اليوم: {_iso(g['name'])} {_iso(D(pg * 6))}.", lang)}
  </section>
  <section>
    <h2>ستيكة 1,5 لتر (6 قوارير)</h2>
    {t15}
  </section>
  {f'<section><h2>ستيكة 0,5 لتر (12 قارورة)</h2>{t05}</section>' if t05 else ""}
  <section>
    <h2>ما هي الستيكة؟</h2>
    <p class="intro">في تونس، « الستيكة » هي علبة قوارير الماء: 6 قوارير من 1,5 لتر أو 12 قارورة من 0,5 لتر.
    سعرها هنا محسوب من سعر القارورة في المغازة.</p>
  </section>"""
        jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ar", "mainEntity": [
            {"@type": "Question", "name": "كم ثمن ستيكة الماء في تونس اليوم؟",
             "acceptedAnswer": {"@type": "Answer", "text":
                 f"يوم {maj_fr}، أرخص ستيكة ماء 1,5 لتر هي {_iso(g['name'])} بـ {_iso(D(pg * 6))} (6 قوارير)."}}]}, ensure_ascii=False)
        return _gabarit(SITE, "prix-stika", f"سعر ستيكة الماء في تونس اليوم — {_iso(g['name'])} بـ {_iso(D(pg * 6))}",
                        f"سعر ستيكة الماء المعدني في تونس يوم {maj_fr}: الأرخص هي {_iso(g['name'])} بـ {_iso(D(pg * 6))}. "
                        "مقارنة مجانية لكل العلامات، تُحدَّث كل يوم.",
                        "سعر ستيكة الماء اليوم", corps, jsonld, maj=maj_fr, lang="ar")
    corps = f"""
  <section>
    <p class="intro"><strong>Aujourd'hui ({maj_fr}), la stika d'eau 1,5 L la moins chère en Tunisie est
    {_esc(g['name'])} à {D(pg * 6)}</strong> (6 bouteilles, chez {_esc(', '.join(mg))}).
    Les prix ci-dessous sont relevés chaque jour sur les boutiques en ligne des grandes surfaces (Carrefour, Géant) ;
    ils sont indicatifs et peuvent varier selon le magasin.</p>
    {_partage(SITE, "prix-stika", f"💧 Stika d'eau la moins chère aujourd'hui : {g['name']} {D(pg * 6)}.")}
  </section>
  <section>
    <h2>Stika 1,5 L (6 bouteilles)</h2>
    {t15}
  </section>
  {f'<section><h2>Stika 0,5 L (12 bouteilles)</h2>{t05}</section>' if t05 else ""}
  <section>
    <h2>Qu'est-ce qu'une stika ?</h2>
    <p class="intro">En Tunisie, la « stika » est le pack de bouteilles d'eau : 6 bouteilles de 1,5 L
    ou 12 bouteilles de 0,5 L. Son prix est ici calculé à partir du prix de la bouteille en magasin.</p>
  </section>"""
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "Quel est le prix d'une stika d'eau en Tunisie aujourd'hui ?",
         "acceptedAnswer": {"@type": "Answer", "text":
             f"Le {maj_fr}, la stika 1,5 L la moins chère est {g['name']} à {D(pg * 6)} (6 bouteilles)."}}]}, ensure_ascii=False)
    return _gabarit(SITE, "prix-stika",
                    f"Prix de la stika d'eau en Tunisie aujourd'hui — {g['name']} à {D(pg * 6)}",
                    f"Prix de la stika d'eau minérale en Tunisie le {maj_fr} : la moins chère est {g['name']} "
                    f"à {D(pg * 6)}. Comparatif gratuit de toutes les marques, mis à jour chaque jour.",
                    "Prix de la stika d'eau aujourd'hui", corps, jsonld, maj=maj_fr)


def page_quelle_eau(data, COMPO, SITE, maj_fr, lang="fr"):
    T = lambda fr, ar: ar if lang == "ar" else fr
    marques = {b["id"]: b for b in data["brands"]}
    eaux = []
    for bid, lst in COMPO["waters"].items():
        if bid not in marques or not lst:
            continue
        e = lst[0]
        m = _meilleur(marques[bid], 1.5)
        eaux.append({"b": marques[bid], "c": e, "stika": m[0] * 6 if m else None})
    unite = T("mg/L", "مغ/لتر")
    noms = NOMS_COLONNES_AR if lang == "ar" else NOMS_COLONNES

    def liste(titre, explication, filtre, cle, croissant=True, n=8):
        sel = sorted((x for x in eaux if filtre(x["c"])), key=lambda x: x["c"][cle], reverse=not croissant)[:n]
        if not sel:
            return ""
        lignes = "".join(f"<tr><td><a href='../marque/{x['b']['id']}/'>{_esc(x['b']['name'])}</a></td>"
                         f"<td class='n'>{x['c'][cle]:g} {unite}</td>"
                         f"<td class='n'>{_dt(x['stika'], lang) if x['stika'] else '—'}</td></tr>" for x in sel)
        return (f"<section><h2>{titre}</h2><p class='sub'>{explication}</p>"
                f"<table class='guide-table'><tr><th>{T('Marque', 'العلامة')}</th><th>{noms.get(cle, cle)}</th>"
                f"<th>{T('Stika 1,5 L dès', 'ستيكة 1,5 لتر من')}</th></tr>{lignes}</table></section>")

    corps = f"""
  <p class="avert">{T("⚠️ Guide indicatif, établi d'après la composition officielle des eaux (Office du Thermalisme).\n  Il ne remplace pas l'avis d'un médecin, d'un pédiatre ou d'un pharmacien.",
                      "⚠️ دليل للإرشاد، مبني على التركيبة الرسمية للمياه (ديوان المياه المعدنية). لا يعوّض رأي الطبيب أو طبيب الأطفال أو الصيدلي.")}</p>
  {liste(T("Eaux les moins salées (pauvres en sodium)", "المياه الأقل ملوحة (قليلة الصوديوم)"),
         T("Moins de 20 mg/L de sodium : conseillées pour un régime pauvre en sel ; souvent recommandées pour les biberons (demandez l'avis du pédiatre).",
           "أقل من 20 مغ/لتر من الصوديوم: يُنصح بها في الحمية قليلة الملح، وكثيرًا ما يُنصح بها لرضّاعات الأطفال (اسأل طبيب الأطفال)."),
         lambda c: c["na"] < 20, "na")}
  {liste(T("Eaux les plus légères (faiblement minéralisées)", "المياه الأخف (قليلة الأملاح)"),
         T("Résidu sec bas : eau légère, adaptée à une consommation quotidienne pour toute la famille.",
           "بقايا جافة قليلة: ماء خفيف، مناسب للشرب اليومي لكل العائلة."),
         lambda c: c["tds"] < 500, "tds")}
  {liste(T("Eaux riches en calcium", "مياه غنية بالكالسيوم"),
         T("Au moins 100 mg/L de calcium : apport utile pour les os (enfants, femmes enceintes, seniors).",
           "100 مغ/لتر من الكالسيوم على الأقل: مفيد للعظام (الأطفال، الحوامل، كبار السن)."),
         lambda c: c["ca"] >= 100, "ca", croissant=False)}
  {liste(T("Eaux riches en magnésium", "مياه غنية بالمغنيزيوم"),
         T("Au moins 50 mg/L de magnésium : contre la fatigue et les crampes, utile aux sportifs.",
           "50 مغ/لتر من المغنيزيوم على الأقل: ضد التعب والتشنّجات، مفيد للرياضيين."),
         lambda c: c["mg"] >= 50, "mg", croissant=False)}
  {liste(T("Eaux les plus minéralisées", "المياه الأكثر أملاحًا"),
         T("Résidu sec élevé : eau « lourde », à alterner avec une eau plus légère.",
           "بقايا جافة مرتفعة: ماء « ثقيل »، يُستحسن التداول بينه وبين ماء أخف."),
         lambda c: c["tds"] >= 1000, "tds", croissant=False)}
  <section><p class="sub">{T("Source : " + _esc(COMPO['credit']['name']) + " —", "المصدر: ديوان المياه المعدنية والاستشفاء بالمياه، نشر الدكتور عماد حسين —")}
  <a href="{COMPO['credit']['url']}" rel="noopener">{T("voir la publication", "انظر المنشور")}</a>. {T("Prix : relevés du", "الأسعار: قراءة يوم")} {maj_fr}.</p>
  {_partage(SITE, "quelle-eau", T("💧 Quelle eau minérale choisir en Tunisie (bébé, peu salée, calcium…) :", "💧 أي ماء معدني تختار في تونس (للرضيع، قليل الملح، كالسيوم…):"), lang)}</section>"""
    if lang == "ar":
        return _gabarit(SITE, "quelle-eau", "أي ماء معدني تختار في تونس؟ للرضيع، قليل الملح، كالسيوم",
                        "أي ماء معدني تختار في تونس: مياه قليلة الصوديوم (للرضيع وللحمية دون ملح)، مياه خفيفة، غنية بالكالسيوم أو المغنيزيوم، "
                        "مع سعر الستيكة. دليل مجاني.",
                        "أي ماء معدني تختار؟", corps, None, maj=maj_fr, lang="ar")
    return _gabarit(SITE, "quelle-eau",
                    "Quelle eau minérale choisir en Tunisie ? Bébé, peu salée, calcium, magnésium",
                    "Quelle eau minérale choisir en Tunisie : eaux pauvres en sodium (bébé, régime sans sel), "
                    "eaux légères, riches en calcium ou en magnésium, avec leur prix de la stika. Guide gratuit.",
                    "Quelle eau minérale choisir ?", corps, None, maj=maj_fr)


def _fmt_l(litres, lang="fr"):
    if lang == "ar":
        return (f"{litres:g} لتر".replace(".", ",") if litres >= 1 else f"{litres * 1000:g} مل")
    return (f"{litres:g} L".replace(".", ",") if litres >= 1 else f"{litres * 1000:g} ml")


def _mag(p, magasin, lang="fr"):
    """Vendu dans une partie des magasins de l'enseigne seulement (Carrefour, 23/10/2026)."""
    m = (p.get("magasins") or {}).get(magasin)
    if not m:
        return ""
    if lang == "ar":
        return f"<br><small>في {m[0]} مغازة من {m[1]}</small>"
    return f"<br><small>dans {m[0]} magasin{'s' if m[0] > 1 else ''} sur {m[1]}</small>"


def page_magasin(data, magasin, SITE, maj_fr, lang="fr"):
    """Prix de l'eau chez un magasin : une ligne par produit (marque + format), le moins cher d'abord.
    Colonne « ailleurs dès » = meilleur prix des autres magasins suivis (pour comparer d'un coup d'œil)."""
    T = lambda fr, ar: ar if lang == "ar" else fr
    D = lambda v: _dt(v, lang)
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
            return D(v * n) if n > 1 else "—"
        tr = "".join(f"<tr><td><a href='../marque/{b['id']}/'>{_esc(b['name'])}</a>"
                     f"{' <small>' + T('gazeuse', 'غازي') + '</small>' if p['category'] == 'gazeuse' else ''}"
                     f"{' <small>' + _fmt_l(p['liters'], lang) + '</small>' if fmt else ''}</td>"
                     f"<td class='n'>{D(v)}{_mag(p, magasin, lang)}</td><td class='n'>{stika(p, v)}</td>"
                     f"<td class='n'>{D(a) if a is not None else '—'}</td></tr>" for b, p, v, a in sel)
        return (f"<section><h2>{titre}</h2><table class='guide-table magasin'><tr><th>{T('Marque', 'العلامة')}</th><th>{T('Bouteille', 'القارورة')}</th>"
                f"<th>{T('Stika', 'الستيكة')}</th><th>{T('Ailleurs dès', 'في مكان آخر من')}</th></tr>{tr}</table></section>")
    eau15 = sorted((x for x in lignes if abs(x[1]["liters"] - 1.5) < .01 and x[1]["category"] == "plate"), key=lambda x: x[2])
    if eau15:
        b0, _, v0, _ = eau15[0]
        accroche = T(f"<strong>Chez {magasin}, la stika d'eau 1,5 L la moins chère aujourd'hui ({maj_fr}) est "
                     f"{_esc(b0['name'])} à {D(v0 * 6)}</strong> (6 bouteilles).",
                     f"<strong>في {nom_ar}، أرخص ستيكة ماء 1,5 لتر اليوم ({maj_fr}) هي {_iso(_esc(b0['name']))} بـ {D(v0 * 6)}</strong> (6 قوارير).")
        court = T(f"stika dès {D(v0 * 6)}", f"الستيكة من {_iso(D(v0 * 6))}")
        rep = T(f"Le {maj_fr}, la stika d'eau 1,5 L la moins chère chez {magasin} est {b0['name']} à {D(v0 * 6)}.",
                f"أرخص ستيكة ماء 1,5 لتر في {nom_ar} يوم {maj_fr}: {_iso(b0['name'])} بـ {_iso(D(v0 * 6))}.")
    else:
        accroche = T(f"<strong>{len(lignes)} prix d'eau relevés chez {magasin} ({maj_fr}).</strong>",
                     f"<strong>{len(lignes)} سعر ماء مقروء في {nom_ar} ({maj_fr}).</strong>")
        court = T(f"{len(lignes)} prix", f"{len(lignes)} سعر")
        rep = T(f"{len(lignes)} prix d'eau sont relevés chez {magasin} le {maj_fr}.", f"أسعار الماء المعدني في {nom_ar} اليوم.")
    if lang == "ar":
        autres = " · ".join(f'<a href="../{c}/">{a}</a>' for m, (c, a) in MAGASINS.items() if m != magasin)
        corps = f"""
  <section>
    <p class="intro">{accroche} الأسعار هي سعر القارورة وسعر الستيكة (6 قوارير 1,5 لتر أو 12 قارورة 0,5 لتر).
    هي أسعار تقريبية وقد تتغيّر حسب المغازة. عمود « في مكان آخر من » يعرض أفضل سعر في المغازات الأخرى المتابَعة.</p>
    {_partage(SITE, chemin, f"💧 سعر الماء في {nom_ar} اليوم: {court}.", lang)}
  </section>
  {tableau(lambda p: abs(p["liters"] - 1.5) < .01 and p["category"] == "plate", "ماء 1,5 لتر", fmt=False)}
  {tableau(lambda p: p["liters"] <= .75, "قوارير صغيرة (0,5 لتر وأقل)")}
  {tableau(lambda p: not (abs(p["liters"] - 1.5) < .01 and p["category"] == "plate") and p["liters"] > .75, "أحجام أخرى وماء غازي")}
  <section><p class="sub">قارن مع: {autres} · <a href="../prix-stika/">كل العلامات</a> · <a href="../">المقارن</a>.</p></section>"""
        jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ar", "mainEntity": [
            {"@type": "Question", "name": f"كم ثمن الماء المعدني في {nom_ar}؟", "acceptedAnswer": {"@type": "Answer", "text": rep}}]}, ensure_ascii=False)
        return _gabarit(SITE, chemin, f"سعر الماء في {nom_ar} تونس اليوم — {court}، مقارن مجاني",
                        f"سعر الماء المعدني في {nom_ar} يوم {maj_fr}: القارورة والستيكة لكل العلامات، مقارنة بالمغازات الأخرى. "
                        "مقارن مجاني يُحدَّث كل يوم.",
                        f"سعر الماء في {nom_ar}", corps, jsonld, maj=maj_fr, lang="ar")
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
         "acceptedAnswer": {"@type": "Answer", "text": rep}}]}, ensure_ascii=False)
    return _gabarit(SITE, chemin,
                    f"Prix de l'eau chez {magasin} Tunisie aujourd'hui — {court}, comparateur gratuit",
                    f"Prix de l'eau minérale chez {magasin} le {maj_fr} : bouteille et stika, toutes les marques, "
                    f"comparées aux autres magasins. Comparateur gratuit mis à jour chaque jour.",
                    f"Prix de l'eau chez {magasin}", corps, jsonld, maj=maj_fr)


def page_retiree(magasin, SITE):
    """Ancienne page d'une enseigne retirée du comparateur (23/10/2026) : courte, en noindex (Google l'oublie sans
    tomber sur une erreur 404), avec un lien vers l'accueil et vers les magasins encore suivis. Aucun prix.
    Une seule adresse (pas de version arabe : page en noindex, hors du plan du site)."""
    chemin, nom_ar = RETIRES[magasin]
    suivis = " · ".join(f'<a href="../{c}/">Prix de l&#39;eau chez {m}</a>' for m, (c, _) in MAGASINS.items())
    corps = f"""
  <section>
    <p class="intro"><strong>{_esc(magasin)} n'est plus suivi par le comparateur.</strong> Ses prix ne pouvaient pas être
    relevés automatiquement chaque jour : pour ne jamais afficher un prix ancien ou incertain, nous l'avons retiré.</p>
    <p class="sub">Magasins suivis chaque jour : {suivis}.</p>
    <p class="sub"><a href="../">Voir le comparateur des prix de l&#39;eau</a> · <a href="../prix-stika/">prix de la stika aujourd&#39;hui</a>.</p>
  </section>"""
    h = _gabarit(SITE, chemin, f"{magasin} n'est plus suivi — Prix des Eaux de Tunisie",
                 f"{magasin} n'est plus suivi par le comparateur des prix de l'eau. Voir les prix chez Carrefour et Géant.",
                 f"{magasin} n'est plus suivi", corps, noindex=True)
    return LG.BOUTON.sub("", h)          # pas de version arabe : pas de bouton de langue


def page_a_propos(data, SITE, maj_fr, lang="fr"):
    """« Comment fonctionne le site ? » (25/10/2026, règle commune § 44 d'Ahmed) : à quoi sert le site, d'où viennent les prix,
    chaque fonction visible (une ligne chacune), gratuit, vos données, mises à jour, site indépendant.
    RÈGLE : à mettre à jour à CHAQUE modification visible du site, dans le même envoi ; test FONCTIONS de tools/test_site.mjs.
    Deux versions (21/11/2026) : français (a-propos/) et arabe (ar/a-propos/), mêmes rubriques, une ligne par fonction."""
    import collect_prices as CP   # noqa: E402  (mêmes chiffres que le robot : jamais écrits deux fois)
    import signalements as SG     # noqa: E402
    N = " "
    nb = len(data["brands"])

    def bloc(titre, lignes):
        lis = "".join(f"<li>{x}</li>" for x in lignes)
        return f'<section><h2>{titre}</h2><ul class="ap-liste">{lis}</ul></section>'

    if lang == "ar":
        liens_mag = " · ".join(f'<a href="../{c}/">{a}</a>' for m, (c, a) in MAGASINS.items())
        corps = f"""
  <section>
    <p class="intro"><strong>« أسعار الماء في تونس » يقارن كل يوم ثمن الماء المعبّأ في المغازات التونسية</strong>: {nb}{N}علامة،
    القارورة والستيكة (6{N}قوارير، أو 12 للقوارير الصغيرة 0,5{N}لتر). مجاني ودون تسجيل، بالعربية وبالفرنسية. آخر قراءة للأسعار يوم {maj_fr}.</p>
  </section>
  {bloc("من أين تأتي الأسعار", [
        f"من المتاجر الإلكترونية لـ<b>{_iso('Carrefour')}</b> و<b>{_iso('Géant')}</b>: روبوت يقرأ أسعارها آليًا كل ليلة ({liens_mag}).",
        "لا نحتفظ بالسعر إلا إذا كان المنتوج <b>متوفرًا</b>. في Carrefour، يقرأ الموقع كل مغازة ويكتب « في N مغازة من M » تحت السعر.",
        "المنتوج الذي لا تبيعه مغازة اليوم يُكتب أمامه « غير متوفر ».",
        "<b>مغازة Carrefour متاعي</b>: اختر مغازتك فوق الترتيب؛ تصبح أسعار Carrefour أسعار هذه المغازة بالذات، والماء غير الموجود في مخزونها يُكتب « غير متوفر ». يبقى اختيارك في هاتفك (لا يُرسل شيء).",
        f"إذا لم يجب متجر، تبقى آخر أسعاره معروضة {CP.MAX_JOURS_REPRISE}{N}أيام على الأكثر، ثم تُحذف.",
        "إذا كانت الأسعار قديمة بعدة أيام، تنبّهك رسالة في أعلى الصفحة.",
        "تركيبة المياه (الصوديوم، الكالسيوم، البقايا الجافة…) مأخوذة من الجدول الرسمي لديوان المياه المعدنية.",
        f"<b>الأسعار المبلَّغ عنها</b> من الزوار تُراجَع آليًا، وتُعرض {SG.JOURS_MAX}{N}يومًا مع تاريخها، خارج الترتيب.",
        "الأسعار <b>تقريبية</b>: قد تتغيّر حسب المغازة والتخفيضات."])}
  {bloc("كيف تستعمله (الصفحة الرئيسية)", [
        f"<b>الأرخص اليوم</b>: البطاقة الخضراء تعرض فورًا أرخص ستيكة، ثم أول 5{N}علامات؛ زر « شارك » لإرسالها.",
        "« <b>شاهد الترتيب الكامل</b> »: كل العلامات، من الأرخص إلى الأغلى.",
        "<b>التصفية</b>: ثلاثة أزرار « ستيكة / قارورة » و« نوع الماء » (معدني، ماء عين، معالَج، غازي) و« الحجم ».",
        "<b>ابحث عن علامة</b>: اكتب اسمها، حتى إن كتبته بشكل خاطئ (Maroua تجد Marwa).",
        f"<b>رتّب</b> العلامات حسب الاسم، أو سعر قارورة 1,5{N}لتر، أو سعر اللتر، أو نسبة الأملاح.",
        "<b>الأسعار، علامة بعلامة</b>: كل بطاقة تعرض سعر كل حجم في كل مغازة؛ السهم ↓ يشير إلى الأرخص؛ « التركيبة » تفتح تفاصيل الماء.",
        f"<b>تخفيضات اليوم</b>: تظهر القائمة عندما ينخفض سعر بـ1{N}% على الأقل منذ القراءة السابقة.",
        "<b>تطوّر الأسعار</b>: منحنى أرخص ستيكة، يومًا بيوم.",
        "<b>الماء المفضّل لدى الحرفاء</b>: صوّت لمائك (صوت واحد لكل هاتف أو حاسوب) وشاهد الترتيب.",
        "<b>بلّغ عن سعر رأيته في المغازة</b>: العلامة، الحجم، السعر، المغازة والتاريخ؛ يُنشر بعد التثبّت في بطاقة العلامة وعلى تيليغرام.",
        "<b>الطلب والتوصيل (قريبًا)</b>: أزرار « + » تحضّر سلة، لكن الطلب غير مفتوح بعد.",
        "<b>تنبيهات التخفيضات</b>: قناة تيليغرام ترسل انخفاض الأسعار والأسعار المبلَّغ عنها.",
        "<b>أسئلة متكرّرة</b> و<b>رأيك</b> (استمارة لتكتب لنا) في أسفل الصفحة.",
        "<b>عنوان لكل لغة</b>: كل صفحة موجودة بالفرنسية وبالعربية (في ar/)، وزر اللغة في أعلى كل صفحة ينقلك إلى الصفحة نفسها باللغة الأخرى."])}
  {bloc("الصفحات الأخرى", [
        "صفحة لكل علامة (سعر القارورة والستيكة، التركيبة، العين).",
        f"صفحة لكل مغازة: {liens_mag}، مع أفضل سعر في مكان آخر للمقارنة.",
        '<a href="../prix-stika/">سعر الستيكة اليوم</a>: كل العلامات، من الأرخص إلى الأغلى.',
        '<a href="../quelle-eau/">أي ماء تختار؟</a>: مياه قليلة الملح، خفيفة، غنية بالكالسيوم أو المغنيزيوم.',
        '<a href="../rapports/">تقارير الشهر</a>: السعر الوسيط لكل علامة وتطوّره، محسوب من الأسعار المقروءة كل يوم.',
        '<a href="../video/?lang=ar">الفيديو التقديمي</a> للموقع، لتشاركه.'])}
  {bloc("مجاني، على هاتفك", [
        "الموقع <b>مجاني تمامًا</b>، دون تسجيل ودون دفع.",
        "يمكنك <b>تثبيته على هاتفك</b> كتطبيق (قائمة المتصفح: « إضافة إلى الشاشة الرئيسية »)؛ دون اتصال، يعرض آخر الأسعار التي شاهدتها.",
        "صفحات الأسعار فيها زر « شارك » (واتساب أو قائمة المشاركة في الهاتف)."])}
  {bloc("معطياتك", [
        "لا حساب ولا اسم مطلوب لمشاهدة الأسعار.",
        "إحصائيات زيارات <b>مجهولة الهوية، دون ملفات تعريف</b> (GoatCounter).",
        "سلّتك تبقى في هاتفك. صوتك يُحسب برمز مجهول يصنعه متصفحك، أبدًا باسمك.",
        "« بلّغ عن سعر » لا يطلب أي اسم؛ المدينة اختيارية.",
        "« رأيك » يطلب بريدًا إلكترونيًا فقط لنتمكّن من الرد عليك.",
        'القواعد المشتركة لكل مواقعنا في أسفل كل صفحة: <a href="https://clicvia.com/ar/confidentialite/" rel="noopener">الخصوصية</a> و<a href="https://clicvia.com/ar/conditions/" rel="noopener">شروط الاستعمال</a>.'])}
  {bloc("تحديث آلي", [
        "تُقرأ الأسعار <b>كل ليلة</b> بروبوت، وكل الصفحات تُعاد بالأسعار الجديدة.",
        f"الأسعار المبلَّغ عنها والأصوات تُحسب كل ساعتين، من 8{N}صباحًا إلى 22{N}ليلًا.",
        "تقرير الشهر الجاري يُعاد حسابه كل ليلة؛ الشهر المنتهي لا يتغيّر.",
        "هذه الصفحة تُحدَّث مع كل تغيير في الموقع."])}
  {bloc("موقع مستقل", [
        "موقع <b>غير رسمي</b>، لا علاقة له بالمغازات ولا بالعلامات المذكورة. الأسماء والشعارات ملك لأصحابها.",
        "لا نبيع الماء اليوم: نقارن الأسعار لنساعدك على الدفع أقل.",
        f"ينشره {_iso('Clicvia')} (<a href=\"https://clicvia.com/ar/\" rel=\"noopener\">clicvia.com</a>)، الذي يجمع خدمات عملية مجانية لتونس. لتكتب لنا: استمارة « رأيك » في أسفل الصفحة الرئيسية."])}
  <section><p class="sub"><a href="../">العودة إلى مقارن أسعار الماء</a> · <a href="../prix-stika/">سعر الستيكة اليوم</a>.</p></section>"""
        return _gabarit(SITE, "a-propos", "كيف يعمل الموقع؟ — أسعار الماء في تونس، مقارن مجاني",
                        "كيف يعمل موقع أسعار الماء في تونس: من أين تأتي الأسعار (Carrefour وGéant)، كيف تستعمل المقارن، معطياتك، "
                        "تحديث كل يوم. مجاني.",
                        "كيف يعمل الموقع؟", corps, None, maj=maj_fr, lang="ar")

    mags = " et ".join(data.get("stores") or MAGASINS)
    liens_mag = " · ".join(f'<a href="../{c}/">{m}</a>' for m, (c, _) in MAGASINS.items())
    corps = f"""
  <section>
    <p class="intro"><strong>Prix des Eaux de Tunisie compare chaque jour le prix de l'eau en bouteille dans les magasins
    tunisiens</strong> : {nb}{N}marques, la bouteille et la stika (6{N}bouteilles, ou 12 pour les petites de 0,5{N}L).
    Gratuit, sans inscription, en français et en arabe. Derniers prix relevés le {maj_fr}.</p>
  </section>
  {bloc("D'où viennent les prix", [
        f"Des boutiques en ligne de <b>{mags}</b> : un robot lit leurs prix automatiquement chaque nuit ({liens_mag}).",
        "Un prix n'est gardé que si le produit est <b>en stock</b>. Chez Carrefour, le site lit chaque magasin et écrit « dans N magasins sur M » sous le prix.",
        "Un produit qu'une enseigne ne vend pas aujourd'hui est marqué « non disponible ».",
        "<b>Mon Carrefour</b> : choisissez votre magasin Carrefour au-dessus du classement ; les prix Carrefour deviennent ceux de CE magasin, et une eau qu'il n'a pas en stock est marquée « non disponible ». Votre choix reste dans votre téléphone (rien n'est envoyé).",
        f"Si une boutique ne répond pas, ses derniers prix restent affichés {CP.MAX_JOURS_REPRISE}{N}jours au plus, puis ils sont retirés.",
        "Si les prix datent de plusieurs jours, un message vous prévient en haut de la page.",
        "La composition des eaux (sodium, calcium, résidu sec…) vient du tableau officiel de l'Office du Thermalisme.",
        f"Les <b>prix signalés</b> par les visiteurs sont vérifiés automatiquement, affichés {SG.JOURS_MAX}{N}jours avec leur date, hors classement.",
        "Les prix sont <b>indicatifs</b> : ils peuvent changer selon le magasin et les promotions."])}
  {bloc("Comment s'en servir (page d'accueil)", [
        f"<b>La moins chère aujourd'hui</b> : la carte verte montre tout de suite la stika la moins chère, puis le top{N}5 ; bouton « Partager » pour l'envoyer.",
        "« <b>Voir le classement complet</b> » : toutes les marques, de la moins chère à la plus chère.",
        "<b>Filtres</b> : trois boutons « Stika / Bouteille », « Type d'eau » (minérale, source, traitée, gazeuse) et « Format ».",
        "<b>Chercher une marque</b> : tapez son nom, même mal écrit (Maroua trouve Marwa).",
        f"<b>Trier</b> les marques par nom, par prix de la bouteille de 1,5{N}L, par prix au litre ou par minéralité.",
        "<b>Les prix, marque par marque</b> : chaque fiche montre le prix de chaque format dans chaque magasin ; la flèche ↓ marque le moins cher ; « Composition » ouvre le détail de l'eau.",
        f"<b>Baisses de prix du jour</b> : la liste apparaît quand un prix a baissé d'au moins 1{N}% depuis le relevé précédent.",
        "<b>Évolution des prix</b> : la courbe de la stika la moins chère, jour par jour.",
        "<b>L'eau préférée des clients</b> : votez pour votre eau (un vote par téléphone ou ordinateur) et voyez le classement.",
        "<b>Signaler un prix vu en magasin</b> : marque, format, prix, magasin et date ; il est publié après vérification, sur la fiche de la marque et sur Telegram.",
        "<b>Commande &amp; livraison (bientôt)</b> : les boutons « + » préparent un panier, mais la commande n'est pas encore ouverte.",
        "<b>Alertes / PROMO</b> : le canal Telegram envoie les baisses de prix et les prix signalés.",
        "<b>Questions fréquentes</b> et <b>Votre avis</b> (formulaire pour nous écrire) en bas de la page.",
        "<b>Une adresse par langue</b> : chaque page existe en français et en arabe (dans ar/) ; le bouton de langue, en haut de chaque page, ouvre la même page dans l’autre langue."])}
  {bloc("Les autres pages", [
        "Une page par marque (prix de la bouteille et de la stika, composition, source).",
        f"Une page par magasin : {liens_mag}, avec le meilleur prix ailleurs pour comparer.",
        '<a href="../prix-stika/">Prix de la stika aujourd&#39;hui</a> : toutes les marques, de la moins chère à la plus chère.',
        '<a href="../quelle-eau/">Quelle eau choisir ?</a> : eaux peu salées, légères, riches en calcium ou en magnésium.',
        '<a href="../rapports/">Rapports du mois</a> : prix médian par marque et évolution, calculés sur les prix relevés chaque jour.',
        '<a href="../video/">Vidéo de présentation</a> du site, à partager.'])}
  {bloc("Gratuit, sur votre téléphone", [
        "Le site est <b>entièrement gratuit</b>, sans inscription et sans paiement.",
        "Vous pouvez l'<b>installer sur votre téléphone</b> comme une application (menu du navigateur : « Ajouter à l'écran d'accueil ») ; sans connexion, il montre les derniers prix déjà vus.",
        "Les pages de prix ont un bouton « Partager » (WhatsApp ou menu de partage du téléphone)."])}
  {bloc("Vos données", [
        "Aucun compte, aucun nom demandé pour voir les prix.",
        "Statistiques de visite <b>anonymes, sans cookies</b> (GoatCounter).",
        "Votre panier reste dans votre téléphone. Votre vote est compté avec un code anonyme créé par votre navigateur, jamais avec votre nom.",
        "« Signaler un prix » ne demande aucun nom ; la ville est facultative.",
        "« Votre avis » demande un e-mail seulement pour pouvoir vous répondre.",
        'Les règles communes à tous nos sites sont en bas de chaque page : <a href="https://clicvia.com/confidentialite/" rel="noopener">Confidentialité</a> et <a href="https://clicvia.com/conditions/" rel="noopener">Conditions d&#39;utilisation</a>.'])}
  {bloc("Mises à jour automatiques", [
        "Les prix sont relus <b>chaque nuit</b> par un robot, et toutes les pages sont refaites avec les nouveaux prix.",
        f"Les prix signalés et les votes sont comptés toutes les 2{N}heures, de 8{N}h à 22{N}h.",
        "Le rapport du mois en cours est recalculé chaque nuit ; un mois fini ne change plus.",
        "Cette page est mise à jour à chaque changement du site."])}
  {bloc("Site indépendant", [
        "Site <b>non officiel</b>, sans lien avec les magasins ni avec les marques citées. Les noms et logos appartiennent à leurs propriétaires.",
        "Nous ne vendons pas d'eau aujourd'hui : nous comparons les prix pour vous aider à payer moins cher.",
        "Publié par <b>Clicvia</b> (<a href=\"https://clicvia.com/\" rel=\"noopener\">clicvia.com</a>), qui réunit des services pratiques et gratuits pour la Tunisie. Pour nous écrire : le formulaire « Votre avis » en bas de l'accueil."])}
  <section><p class="sub"><a href="../">Retour au comparateur des prix de l&#39;eau</a> · <a href="../prix-stika/">prix de la stika aujourd&#39;hui</a>.</p></section>"""
    return _gabarit(SITE, "a-propos", "Comment fonctionne le site ? — Prix des Eaux de Tunisie, comparateur gratuit",
                    "Comment fonctionne Prix des Eaux de Tunisie : d'où viennent les prix de l'eau (Carrefour, Géant), "
                    "comment utiliser le comparateur, vos données, mises à jour chaque jour. Gratuit.",
                    "Comment fonctionne le site ?", corps, None, maj=maj_fr)


def generer(data, COMPO, SITE, ROOT, maj_fr):
    """Prépare les pages guides en français ET en arabe (tools/langues.py les écrit ensemble : <chemin>/ et ar/<chemin>/)
    et renvoie leurs URL (pour le plan du site)."""
    # enseignes retirées : page courte en noindex, jamais dans le plan du site ni en arabe (23/10/2026)
    for m, (c, _) in RETIRES.items():
        d = ROOT / c
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page_retiree(m, SITE), encoding="utf-8", newline="\n")
    urls = []
    pages = (("prix-stika", lambda l: page_prix_stika(data, SITE, maj_fr, l)),
             ("quelle-eau", lambda l: page_quelle_eau(data, COMPO, SITE, maj_fr, l)),
             ("a-propos", lambda l: page_a_propos(data, SITE, maj_fr, l)),
             *((c, (lambda m: lambda l: page_magasin(data, m, SITE, maj_fr, l))(m)) for m, (c, _) in MAGASINS.items()))
    for chemin, faire in pages:
        fr = faire("fr")
        if not fr:
            continue
        LG.ajouter(chemin + "/", fr, faire("ar"))
        urls.append(f"{SITE}/{chemin}/")
    return urls
