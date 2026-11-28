# -*- coding: utf-8 -*-
"""Rapports du mois des prix de l'eau (18/10/2026, demande d'Ahmed ; règle commune § 25 : articles automatiques mais VRAIS).

Chaque mois, une page « Prix de l'eau en bouteille en Tunisie, <mois> » (rapports/AAAA-MM/) écrite par le robot à partir de
data/historique.json (relevés quotidiens, tools/build_history.py) : pour chaque marque, le prix de la bouteille d'eau plate 1,5 L
la moins chère trouvée ce jour-là parmi les magasins suivis. Jamais un chiffre inventé ni estimé.

Règles :
- une marque n'entre dans le rapport d'un mois qu'avec au moins MIN_JOURS jours de prix dans ce mois ;
- prix du mois d'une marque = MÉDIANE de ses prix quotidiens (la moitié des jours moins cher, l'autre moitié plus cher) ;
- le mois en cours est recalculé chaque nuit (« chiffres au <date> ») ; un mois FINI déjà écrit n'est plus jamais modifié
  (data/rapports.json) ;
- évolution d'un mois sur l'autre seulement pour une marque présente les deux mois (chacun avec MIN_JOURS jours), écart ≤ 60 %.
"""
import json
import os
import sys
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FICHIER = ROOT / "data" / "rapports.json"
MIN_JOURS = 3
VARIATION_MAX = 60
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_AR = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def mois_txt(m):
    return f"{MOIS[int(m[5:7]) - 1]} {m[:4]}"


def mois_ar(m):
    return f"{MOIS_AR[int(m[5:7]) - 1]} {m[:4]}"


def mois_precedent(m):
    a, n = int(m[:4]), int(m[5:7])
    return f"{a - 1}-12" if n == 1 else f"{a}-{n - 1:02d}"


def jour_txt(d):
    j = int(d[8:10])
    return f"{'1er' if j == 1 else j} {MOIS[int(d[5:7]) - 1]} {d[:4]}"


def calculer(serie, m):
    """Chiffres d'un mois à partir de la série quotidienne (None si aucun jour dans ce mois)."""
    jours = [j for j in serie if j["date"][:7] == m]
    if not jours:
        return None
    par = {}
    for j in jours:
        for nom, p in (j.get("parMarque") or {}).items():
            if isinstance(p, (int, float)) and p > 0:
                par.setdefault(nom, []).append((j["date"], p))
    marques = {}
    for nom, v in par.items():
        if len(v) < MIN_JOURS:
            continue
        prix = [p for _, p in v]
        d_min, p_min = min(v, key=lambda x: (x[1], x[0]))
        marques[nom] = {"med": round(statistics.median(prix), 3), "min": p_min, "min_date": d_min, "max": max(prix), "jours": len(v)}
    st = min(jours, key=lambda j: (j["stika15"], j["date"]))
    return {"du": jours[0]["date"], "au": jours[-1]["date"], "jours": len(jours), "marques": marques,
            "stika_min": {"prix": st["stika15"], "date": st["date"], "marques": st["marques"]}}


def lire():
    try:
        h = json.loads(FICHIER.read_text(encoding="utf-8"))
        return h if isinstance(h.get("mois"), dict) else {"mois": {}}
    except (OSError, ValueError, AttributeError):
        return {"mois": {}}


def mettre_a_jour(hist, serie):
    """Mois en cours (celui du dernier relevé) recalculé ; mois finis écrits une seule fois puis figés."""
    if not serie:
        return hist
    courant = serie[-1]["date"][:7]
    for m in sorted({j["date"][:7] for j in serie}):
        if m > courant:
            continue
        if m < courant and m in hist["mois"]:
            continue                                    # mois fini : jamais réécrit
        c = calculer(serie, m)
        if c and c["marques"]:
            # 1er jour où la page a existé (date de publication) : pour un mois fini écrit pour la 1re fois, le jour du relevé actuel
            debut = (hist["mois"].get(m) or {}).get("debut") or serie[-1]["date"]
            hist["mois"][m] = {**c, "debut": debut}
    return hist


def variation(a, b):
    if not a or not b:
        return None
    v = round((a - b) / b * 100)
    return v if abs(v) <= VARIATION_MAX else None


def _dt(v):
    return f"{v:,.3f}".replace(",", " ").replace(".", ",") + " DT"


ICO_PART = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>'
            '<path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>')


def bouton_partage(url, titre, lang="fr"):
    """UN bouton « Partager ce rapport » (menu de partage du téléphone ; protection.js, button[data-partage-rapport])."""
    from html import escape
    a, c = (("شارك هذا التقرير", "تم نسخ الرابط ✓ — الصقه حيث تريد") if lang == "ar"
            else ("Partager ce rapport", "Lien copié ✓ — collez-le où vous voulez"))
    return (f'<div class="rp-partage"><button class="rp-partager" type="button" data-partage-rapport="{escape(url)}" data-titre="{escape(titre)}">'
            f'{ICO_PART}<span class="rp-a-copier">{a}</span><span class="rp-copie">{c}</span></button>'
            '</div>')


def jour_ar(d):
    return f"{int(d[8:10])} {MOIS_AR[int(d[5:7]) - 1]} {d[:4]}"


def page(m, d, prev, courant, ids, SITE, G, lang="fr"):
    """HTML du rapport d'un mois (G = module build_guides : gabarit, échappement), en français ou en arabe."""
    if lang == "ar":
        return page_ar(m, d, prev, courant, ids, SITE, G)
    esc, iso = G._esc, G._iso
    mt, ma = mois_txt(m), mois_ar(m)
    rang = sorted(d["marques"].items(), key=lambda x: (x[1]["med"], x[0]))
    lien = lambda nom: (f"<a href='../../marque/{ids[nom]}/'>{esc(nom)}</a>" if nom in ids else esc(nom))
    pm = (prev or {}).get("marques", {})
    def var(nom, x):
        v = variation(x["med"], pm[nom]["med"]) if nom in pm else None
        if v is None:
            return "<td class='n'>—</td>" if prev else ""
        return f"<td class='n'>{'+' if v > 0 else ''}{v} %</td>"
    lignes = "".join(f"<tr><td>{i}</td><td>{lien(nom)}<small>{x['jours']} jours de prix</small></td><td class='n'>{_dt(x['med'])}</td>"
                     f"<td class='n'>{_dt(x['med'] * 6)}</td><td class='n'>{_dt(x['min'])}<small>dès le {int(x['min_date'][8:10])}/{x['min_date'][5:7]}</small></td>{var(nom, x)}</tr>"
                     for i, (nom, x) in enumerate(rang, 1))
    statut = (f"Chiffres au {jour_txt(d['au'])}, mis à jour chaque jour jusqu'à la fin du mois." if m == courant
              else f"Rapport définitif ({d['jours']} jours de relevés, du {jour_txt(d['du'])} au {jour_txt(d['au'])}).")
    (n1, x1), (nz, xz) = rang[0], rang[-1]
    st = d["stika_min"]
    bref = [f"Marque la moins chère du mois (bouteille 1,5 L, prix médian) : <strong>{esc(n1)}</strong>, {_dt(x1['med'])} — soit {_dt(x1['med'] * 6)} la stika de 6.",
            f"La plus chère : <strong>{esc(nz)}</strong>, {_dt(xz['med'])} la bouteille.",
            f"Stika 1,5 L la moins chère vue ce mois-ci : {_dt(st['prix'])} le {jour_txt(st['date'])} ({esc(', '.join(st['marques']))}).",
            f"{len(rang)} marques suivies au moins {MIN_JOURS} jours, sur {d['jours']} jours de relevés."]
    if prev:
        hausses, baisses, ev = evolutions(d, pm)
        if hausses:
            bref.append("Hausses depuis " + mois_txt(mois_precedent(m)) + " : " + ", ".join(f"{esc(n)} (+{v} %)" for n, v in hausses) + ".")
        if baisses:
            bref.append("Baisses : " + ", ".join(f"{esc(n)} ({v} %)" for n, v in baisses) + ".")
        if not hausses and not baisses and ev:
            bref.append(f"Aucun changement de prix médian depuis {mois_txt(mois_precedent(m))} pour les {len(ev)} marques suivies les deux mois.")
    else:
        bref.append("Premier rapport : l'évolution d'un mois sur l'autre sera affichée à partir du mois prochain.")
    url = f"{SITE}/rapports/{m}/"
    titre = f"Prix de l'eau en bouteille en Tunisie, {mt} : la marque la moins chère est {n1}"
    desc = (f"Prix des Eaux de Tunisie — rapport du mois. {mt.capitalize()} : prix médian de la bouteille d'eau 1,5 L et de la stika pour {len(rang)} marques en Tunisie, "
            f"la moins chère ({n1}, {_dt(x1['med'])}), la plus chère, évolution. Calculé chaque jour sur les prix relevés en magasin, gratuit.")
    autres = " · ".join(f"<a href='../{x}/'>{mois_txt(x)}</a>" for x in sorted(G._RAPPORTS_MOIS, reverse=True) if x != m)
    corps = f"""
  <p class="rp-signature">Un rapport de <b>Prix des Eaux de Tunisie</b> · prix-eau.clicvia.com</p>
  {bouton_partage(url, titre)}
  <section>
    <p class="intro">Prix de l'eau en bouteille relevés chaque jour sur les boutiques en ligne des grandes surfaces de Tunisie (Carrefour, Géant) et sur Glovo (Aziza). {statut}</p>
    <ul class="intro">{"".join(f"<li>{b}</li>" for b in bref)}</ul>
  </section>
  <section>
    <h2>Toutes les marques : bouteille d'eau plate 1,5 L</h2>
    <div class="tableau-defile"><table class="guide-table magasin"><tr><th>#</th><th>Marque</th><th>Prix médian</th><th>Stika (×6)</th><th>Le plus bas</th>{"<th>Évol.</th>" if prev else ""}</tr>{lignes}</table></div>
  </section>
  <section>
    <h2>Comment ces chiffres sont calculés</h2>
    <p class="intro">Chaque jour, le robot du site relève les prix des magasins suivis (sources citées en bas de page) et garde, pour chaque marque,
    la bouteille d'eau plate 1,5 L la moins chère. Le <strong>prix médian</strong> du mois est le prix du milieu : la moitié des jours moins cher,
    l'autre moitié plus cher. Une marque n'apparaît qu'avec au moins {MIN_JOURS} jours de prix dans le mois. La stika = 6 bouteilles.
    Prix indicatifs : ils peuvent varier selon le magasin. Aucune estimation : seulement des prix relevés.</p>
  </section>
  {bouton_partage(url, titre)}
  <section>
    <h2>Citer ces chiffres</h2>
    <p class="intro">Journalistes, blogs : vous pouvez reprendre ces chiffres en citant la source :<br>
    <em>Source : Prix des Eaux de Tunisie, « {esc(titre)} », {url}</em></p>
    {f'<p class="intro">Autres mois : {autres} · <a href="../">tous les rapports</a></p>' if autres else '<p class="intro"><a href="../">Tous les rapports</a></p>'}
  </section>"""
    img = _APERCUS.get(m) or apercu(m, f"Prix de l’eau en bouteille en Tunisie", mt, f"La moins chère : {n1} · {_dt(x1['med'])}",
                                     f"Bouteille 1,5 L, prix médian · {len(rang)} marques comparées")
    _APERCUS[m] = img
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": titre[:110], "inLanguage": "fr",
           "datePublished": d.get("debut") or d["au"], "dateModified": max(d["au"], d.get("debut") or ""), "url": url,
           "author": {"@type": "Organization", "name": "Prix des Eaux de Tunisie", "url": SITE + "/"},
           "publisher": {"@type": "Organization", "name": "Prix des Eaux de Tunisie", "url": SITE + "/"}, "image": SITE + "/" + img},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": f"Quelle est l'eau en bouteille la moins chère en Tunisie en {mt} ?",
               "acceptedAnswer": {"@type": "Answer", "text": f"{n1}, avec un prix médian de {_dt(x1['med'])} la bouteille de 1,5 L ({_dt(x1['med'] * 6)} la stika de 6)."}}]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Rapports du mois", "item": SITE + "/rapports/"},
              {"@type": "ListItem", "position": 3, "name": mt, "item": url}]}]
    return G._gabarit(SITE, f"rapports/{m}", titre + " | Prix des Eaux de Tunisie", desc, f"Prix de l'eau en Tunisie : {mt}", corps,
                      json.dumps(ld, ensure_ascii=False), None, racine="../../", og_type="article", og_image=img)


_APERCUS = {}


def evolutions(d, pm):
    ev = sorted(((nom, variation(x["med"], pm[nom]["med"])) for nom, x in d["marques"].items() if nom in pm), key=lambda x: (x[1] is None, x[1] or 0))
    ev = [e for e in ev if e[1] is not None]
    return [e for e in reversed(ev) if e[1] > 0][:3], [e for e in ev if e[1] < 0][:3], ev


def page_ar(m, d, prev, courant, ids, SITE, G):
    """Rapport du mois en arabe (ar/rapports/AAAA-MM/) : mêmes chiffres que la page française, calculés une seule fois."""
    esc, iso = G._esc, G._iso
    D = lambda v: G._dt(v, "ar")
    ma = mois_ar(m)
    rang = sorted(d["marques"].items(), key=lambda x: (x[1]["med"], x[0]))
    lien = lambda nom: (f"<a href='../../marque/{ids[nom]}/'>{esc(nom)}</a>" if nom in ids else esc(nom))
    pm = (prev or {}).get("marques", {})
    def var(nom, x):
        v = variation(x["med"], pm[nom]["med"]) if nom in pm else None
        if v is None:
            return "<td class='n'>—</td>" if prev else ""
        return f"<td class='n'>{'+' if v > 0 else ''}{v} %</td>"
    lignes = "".join(f"<tr><td>{i}</td><td>{lien(nom)}<small>{x['jours']} يومًا من الأسعار</small></td><td class='n'>{D(x['med'])}</td>"
                     f"<td class='n'>{D(x['med'] * 6)}</td><td class='n'>{D(x['min'])}<small>منذ {int(x['min_date'][8:10])}/{x['min_date'][5:7]}</small></td>{var(nom, x)}</tr>"
                     for i, (nom, x) in enumerate(rang, 1))
    statut = (f"أرقام إلى غاية {jour_ar(d['au'])}، تُحدَّث كل يوم حتى نهاية الشهر." if m == courant
              else f"تقرير نهائي ({d['jours']} يومًا من القراءات، من {jour_ar(d['du'])} إلى {jour_ar(d['au'])}).")
    (n1, x1), (nz, xz) = rang[0], rang[-1]
    st = d["stika_min"]
    bref = [f"أرخص علامة هذا الشهر (قارورة 1,5 لتر، السعر الوسيط): <strong>{iso(esc(n1))}</strong>، {D(x1['med'])} — أي {D(x1['med'] * 6)} للستيكة من 6.",
            f"الأغلى: <strong>{iso(esc(nz))}</strong>، {D(xz['med'])} للقارورة.",
            f"أرخص ستيكة 1,5 لتر شوهدت هذا الشهر: {D(st['prix'])} يوم {jour_ar(st['date'])} ({iso(esc('، '.join(st['marques'])))}).",
            f"{len(rang)} علامة متابَعة {MIN_JOURS} أيام على الأقل، من أصل {d['jours']} يومًا من القراءات."]
    if prev:
        hausses, baisses, ev = evolutions(d, pm)
        if hausses:
            bref.append(f"ارتفاع منذ {mois_ar(mois_precedent(m))}: " + "، ".join(f"{iso(esc(n))} (+{v} %)" for n, v in hausses) + ".")
        if baisses:
            bref.append("انخفاض: " + "، ".join(f"{iso(esc(n))} ({v} %)" for n, v in baisses) + ".")
        if not hausses and not baisses and ev:
            bref.append(f"لا تغيير في السعر الوسيط منذ {mois_ar(mois_precedent(m))} للعلامات الـ{len(ev)} المتابَعة في الشهرين.")
    else:
        bref.append("أول تقرير: تطوّر الأسعار من شهر إلى آخر سيظهر ابتداءً من الشهر القادم.")
    url = f"{SITE}/ar/rapports/{m}/"
    titre = f"سعر الماء المعبّأ في تونس، {ma}: أرخص علامة هي {iso(n1)}"
    desc = (f"أسعار الماء في تونس — تقرير الشهر. {ma}: السعر الوسيط لقارورة الماء 1,5 لتر وللستيكة لـ{len(rang)} علامة في تونس، "
            f"الأرخص ({iso(n1)}، {iso(D(x1['med']))})، الأغلى، والتطوّر. محسوب كل يوم من أسعار المغازات، مجانًا.")
    autres = " · ".join(f"<a href='../{x}/'>{mois_ar(x)}</a>" for x in sorted(G._RAPPORTS_MOIS, reverse=True) if x != m)
    corps = f"""
  <p class="rp-signature">تقرير من <b>أسعار الماء في تونس</b> · <bdi>prix-eau.clicvia.com</bdi></p>
  {bouton_partage(url, titre, "ar")}
  <section>
    <p class="intro">أسعار الماء المعبّأ تُقرأ كل يوم من المتاجر الإلكترونية للمغازات الكبرى في تونس (Carrefour وGéant) وعلى Glovo (Aziza). {statut}</p>
    <ul class="intro">{"".join(f"<li>{b}</li>" for b in bref)}</ul>
  </section>
  <section>
    <h2>كل العلامات: قارورة ماء عادي 1,5 لتر</h2>
    <div class="tableau-defile"><table class="guide-table magasin"><tr><th>#</th><th>العلامة</th><th>السعر الوسيط</th><th>الستيكة (×6)</th><th>الأدنى</th>{"<th>التطوّر</th>" if prev else ""}</tr>{lignes}</table></div>
  </section>
  <section>
    <h2>كيف تُحسب هذه الأرقام</h2>
    <p class="intro">كل يوم، يقرأ روبوت الموقع أسعار المغازات المتابَعة (المصادر مذكورة أسفل الصفحة) ويحتفظ لكل علامة بأرخص قارورة ماء عادي 1,5 لتر.
    <strong>السعر الوسيط</strong> للشهر هو السعر الذي في الوسط: نصف الأيام أرخص منه والنصف الآخر أغلى. لا تظهر علامة إلا إذا كان لها {MIN_JOURS} أيام
    من الأسعار على الأقل في الشهر. الستيكة = 6 قوارير. أسعار تقريبية قد تتغيّر حسب المغازة. لا تقدير: فقط أسعار مقروءة.</p>
  </section>
  {bouton_partage(url, titre, "ar")}
  <section>
    <h2>للاستشهاد بهذه الأرقام</h2>
    <p class="intro">صحفيون، مدوّنون: يمكنكم استعمال هذه الأرقام مع ذكر المصدر:<br>
    <em>المصدر: أسعار الماء في تونس، « {esc(titre)} »، <bdi>{url}</bdi></em></p>
    {f'<p class="intro">أشهر أخرى: {autres} · <a href="../">كل التقارير</a></p>' if autres else '<p class="intro"><a href="../">كل التقارير</a></p>'}
  </section>"""
    img = _APERCUS.get(m, "assets/og-image-v7.jpg")
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": titre[:110], "inLanguage": "ar",
           "datePublished": d.get("debut") or d["au"], "dateModified": max(d["au"], d.get("debut") or ""), "url": url,
           "author": {"@type": "Organization", "name": "Prix des Eaux de Tunisie", "url": SITE + "/"},
           "publisher": {"@type": "Organization", "name": "Prix des Eaux de Tunisie", "url": SITE + "/"}, "image": SITE + "/" + img},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": f"كم ثمن قارورة الماء في تونس في {ma}؟",
               "acceptedAnswer": {"@type": "Answer", "text": f"أرخص علامة: {iso(n1)} بـ {iso(D(x1['med']))} للقارورة 1,5 لتر."}}]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/ar/"},
              {"@type": "ListItem", "position": 2, "name": "تقارير الشهر", "item": SITE + "/ar/rapports/"},
              {"@type": "ListItem", "position": 3, "name": ma, "item": url}]}]
    return G._gabarit(SITE, f"rapports/{m}", titre + " | أسعار الماء في تونس", desc, f"سعر الماء في تونس: {ma}", corps,
                      json.dumps(ld, ensure_ascii=False), None, racine="../../", og_type="article", og_image=img, lang="ar")


def apercu(m, titre_img, mt, chiffre, sous):
    """Image d'aperçu propre à l'article (18/10/2026 : au partage, Facebook montrait l'image du site). Le nom dépend du contenu :
    quand les chiffres changent, nouvelle adresse, donc Facebook prend la nouvelle image. Sans Pillow : image générale du site."""
    import hashlib
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import apercus as AP
    cle = hashlib.sha1(f"{titre_img}|{m}|{chiffre}|{sous}".encode()).hexdigest()[:8]
    rel = f"rapports/{m}/apercu-{cle}.jpg"
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dossier = os.path.join(racine, "rapports", m)
    os.makedirs(dossier, exist_ok=True)
    for f in os.listdir(dossier):
        if f.startswith("apercu-") and f != os.path.basename(rel):
            os.remove(os.path.join(dossier, f))
    return rel if AP.fabriquer(os.path.join(racine, rel), titre_img, mt, chiffre, sous) else "assets/og-image-v7.jpg"


def page_liste(hist, courant, SITE, G, lang="fr"):
    if lang == "ar":
        items = "".join(f"<li><a href='{m}/'><strong>{mois_ar(m)}</strong></a> — {len(hist['mois'][m]['marques'])} علامة · "
                        f"{'جارٍ' if m == courant else 'نهائي'}</li>" for m in sorted(hist["mois"], reverse=True))
        corps = f"""
  <section>
    <p class="intro">كل شهر، سعر الماء المعبّأ لكل العلامات المتابَعة، محسوب آليًا من الأسعار المقروءة كل يوم في المغازات. مجانًا.</p>
    <ul class="intro">{items}</ul>
  </section>"""
        return G._gabarit(SITE, "rapports", "تقارير الشهر: سعر الماء المعبّأ في تونس | أسعار الماء في تونس",
                          "كل شهر، السعر الوسيط لقارورة الماء 1,5 لتر وللستيكة لكل العلامات التي تُباع في تونس، الأرخص والتطوّر. "
                          "محسوب من الأسعار المقروءة كل يوم، مجانًا.",
                          "تقارير الشهر", corps, None, lang="ar")
    items = "".join(f"<li><a href='{m}/'><strong>{mois_txt(m).capitalize()}</strong></a> — {len(hist['mois'][m]['marques'])} marques · "
                    f"{'en cours' if m == courant else 'définitif'}</li>" for m in sorted(hist["mois"], reverse=True))
    corps = f"""
  <section>
    <p class="intro">Chaque mois, le prix de l'eau en bouteille de toutes les marques suivies, calculé automatiquement sur les prix relevés
    chaque jour en magasin. Gratuit.</p>
    <ul class="intro">{items}</ul>
  </section>"""
    return G._gabarit(SITE, "rapports", "Rapports du mois : prix de l'eau en bouteille en Tunisie | Prix des Eaux de Tunisie",
                      "Chaque mois, le prix médian de la bouteille d'eau 1,5 L et de la stika pour toutes les marques vendues en Tunisie, "
                      "la moins chère et l'évolution. Calculé sur les prix relevés chaque jour, gratuit.",
                      "Rapports du mois", corps, None)


def generer(data, SITE, G, fichier=None):
    """Met à jour data/rapports.json et prépare les pages (français + arabe, écrites par tools/langues.py) ;
    renvoie [(url, lastmod)] pour le plan du site."""
    global FICHIER
    import langues as LG
    if fichier:
        FICHIER = Path(fichier)
    serie = json.loads((ROOT / "data" / "historique.json").read_text(encoding="utf-8")).get("serie", [])
    hist = mettre_a_jour(lire(), serie)
    if not hist["mois"]:
        return []
    FICHIER.write_text(json.dumps(hist, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    ids = {b["name"]: b["id"] for b in data["brands"]}
    courant = max(hist["mois"])
    G._RAPPORTS_MOIS = list(hist["mois"])
    urls = []
    for m, d in sorted(hist["mois"].items()):
        prev = hist["mois"].get(mois_precedent(m))
        LG.ajouter(f"rapports/{m}/", page(m, d, prev, courant, ids, SITE, G), page(m, d, prev, courant, ids, SITE, G, "ar"))
        urls.append((f"{SITE}/rapports/{m}/", d["au"]))
    LG.ajouter("rapports/", page_liste(hist, courant, SITE, G), page_liste(hist, courant, SITE, G, "ar"))
    urls.insert(0, (f"{SITE}/rapports/", hist["mois"][courant]["au"]))
    return urls
