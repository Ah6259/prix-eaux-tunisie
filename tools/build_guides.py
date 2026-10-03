# -*- coding: utf-8 -*-
"""Pages « guides » pour Google, régénérées chaque nuit avec les prix du jour
(appelé par build_pages.py) :
  - prix-stika/  : prix de la stika d'eau en Tunisie aujourd'hui (FR + AR), toutes marques
  - quelle-eau/  : quelle eau choisir (peu salée, faiblement minéralisée, calcium, magnésium…)
                   d'après la composition officielle (data/composition.js)
"""
import json
import urllib.parse
from datetime import datetime

GRAND_FORMAT = 2.5


def _esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


NOMS_COLONNES = {"na": "Sodium", "tds": "Résidu sec", "ca": "Calcium", "mg": "Magnésium"}


def _iso(s):
    """Isole un mot latin (nom, prix) dans une phrase arabe : évite l'ordre « DT 3,540 بـ Melina »."""
    return "⁨" + str(s) + "⁩"


def _dt(v):
    return f"{v:,.3f}".replace(",", " ").replace(".", ",") + " DT"


def _gabarit(SITE, chemin, titre, description, h1, corps, jsonld=None, ar_titre=None):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{_esc(titre)}</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{SITE}/{chemin}/">
<meta property="og:title" content="{_esc(titre)}">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:image" content="{SITE}/assets/og-image-v2.png">
<link rel="icon" type="image/svg+xml" href="../assets/icons/icon.svg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../style.css">
{f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""}
<style>
  .guide-table{{width:100%; border-collapse:collapse; font-size:14px; background:var(--surface); border:1px solid var(--line); border-radius:12px}}
  .guide-table th,.guide-table td{{padding:7px 10px; border-top:1px solid var(--line); text-align:left}}
  .guide-table th{{font-size:12px; color:var(--muted); border-top:0}}
  .guide-table td.n{{text-align:right; font-variant-numeric:tabular-nums; font-weight:700}}
  .guide-table a{{color:var(--ink); font-weight:600}}
  .ar{{font-size:15px; color:var(--muted); margin:4px 0 0}}
  .avert{{background:var(--gaz-soft); color:var(--gaz); border-radius:10px; padding:9px 12px; font-size:13px}}
  .partager{{display:inline-block; margin-top:12px; background:#25D366; color:#fff; font-weight:700;
    text-decoration:none; padding:8px 16px; border-radius:999px; font-size:14px}}
</style>
</head>
<body>
<header class="site"><div class="wrap site-inner">
  <h1>{_esc(h1)}</h1>
</div></header>
<div class="wrap">
  {f'<p class="ar" dir="rtl" lang="ar">{_esc(ar_titre)}</p>' if ar_titre else ""}
  <p class="intro" style="margin-top:12px"><a href="../">← Comparateur des prix de l'eau en Tunisie</a></p>
  {corps}
</div>
<footer><div class="wrap">
  <a href="../">Comparateur des prix de l'eau en Tunisie</a> · <a href="../prix-stika/">Prix de la stika</a> ·
  <a href="../quelle-eau/">Quelle eau choisir ?</a>
  <p class="copyright">© 2026 Prix des Eaux de Tunisie — tous droits réservés.</p>
</div></footer>
</body>
</html>
"""


def _partage(SITE, chemin, texte):
    url = "https://wa.me/?text=" + urllib.parse.quote(f"{texte} {SITE}/{chemin}/")
    return f'<a class="partager" href="{url}" target="_blank" rel="noopener">🟢 Partager sur WhatsApp</a>'


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
                    f"à {_dt(pg * 6)}. Comparatif de toutes les marques, mis à jour chaque jour.",
                    "Prix de la stika d'eau aujourd'hui", corps, jsonld,
                    f"ثمن ستيكة الماء في تونس اليوم — أرخص ستيكة: {_iso(g['name'])} بـ {_iso(_dt(pg * 6))}")


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
                    "eaux légères, riches en calcium ou en magnésium, avec leur prix de la stika.",
                    "Quelle eau minérale choisir ?", corps, None,
                    "أي ماء معدني أختار في تونس؟ ماء للرضيع، قليل الملح، غني بالكالسيوم")


def generer(data, COMPO, SITE, ROOT, maj_fr):
    """Écrit les pages guides et renvoie leurs URL (pour le sitemap)."""
    urls = []
    for chemin, html in (("prix-stika", page_prix_stika(data, SITE, maj_fr)),
                         ("quelle-eau", page_quelle_eau(data, COMPO, SITE, maj_fr))):
        if not html:
            continue
        d = ROOT / chemin
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"{SITE}/{chemin}/")
    return urls
