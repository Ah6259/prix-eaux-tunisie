# -*- coding: utf-8 -*-
"""UNE ADRESSE PAR LANGUE (21/11/2026, demande d'Ahmed ; règle commune § 8 point 9 : « une adresse par langue, jamais seulement ?lang= »).

Méthode reprise de Code de la route (tools/construire.py) et d'Alerte Concours (robot/langues.py) :
  - chaque page publique existe en FRANÇAIS à son adresse (<chemin>) et en ARABE dans ar/<chemin>, déjà écrite dans sa langue
    (Google lit la page arabe telle quelle) ;
  - la page française n'a que du français (seule exception voulue : le verset sur la photo du bandeau de l'accueil, et le bouton
    « العربية » qui mène à la page arabe) ; la page arabe n'a que de l'arabe (noms de marques, de magasins et de lieux en lettres
    latines, isolés) ;
  - les deux pages se citent (hreflang fr / ar / x-default = fr), chacune a son canonical, son og:url et son og:locale ;
  - <html data-langue-fixe> : la langue est celle de l'ADRESSE ; le bouton de langue (a.langue-btn) mène à l'autre adresse
    (protection.js garde les paramètres et l'ancre ; un ancien lien « ?lang=ar » est renvoyé vers ar/) ;
  - les pages arabes sont écrites « comme si » elles étaient à la place de la page française (mêmes liens relatifs), puis
    _reecrire_liens() descend d'un dossier tout ce qui n'a pas de version arabe (style, scripts, données, images, page vidéo…).

Qui appelle : tools/build_pages.py (pages des marques, accueil, plan du site), tools/build_guides.py (guides, magasins, à propos),
tools/build_rapports.py (rapports du mois) — donc le robot de nuit maj-prix.yml. NE JAMAIS MODIFIER ar/ À LA MAIN : tout est refait
chaque nuit. L'accueil arabe ar/index.html est fabriqué à partir d'index.html (écrit à la main) par accueil_ar() : une phrase
française ajoutée à index.html doit recevoir sa traduction dans ACCUEIL (sinon tools/test_site.mjs la trouve dans ar/index.html).
"""
import html as H
import json
import os
import re
import shutil

URL_SITE = "https://prix-eau.clicvia.com/"
NOM_AR = "أسعار الماء في تونس"
MIROIR = set()        # chemins des pages qui existent en arabe ("" = accueil, "marque/safia/", "prix-stika/"…)
_A_ECRIRE = []        # (chemin, page française, page arabe) : écrites ensemble par ecrire_tout(), une fois MIROIR complet

BOUTON = re.compile(r'<a class="langue-btn"[^>]*>.*?</a>', re.S)
POLICE_AR = "&family=Noto+Sans+Arabic:wght@400;600;700;800"


def T(lang, fr, ar):
    return ar if lang == "ar" else fr


def iso(s):
    """Isole un mot latin (nom, prix) dans une phrase arabe (U+2068 … U+2069) : l'ordre des mots reste juste."""
    return "⁨" + str(s) + "⁩"


def dt(v, lang="fr"):
    """Prix en dinars : « 3,540 DT » en français, « 3,540 د.ت » en arabe (chiffres latins, comme en Tunisie)."""
    n = f"{v:,.3f}".replace(",", " ").replace(".", ",")
    return n + (" د.ت" if lang == "ar" else " DT")


def litres(x, lang="fr"):
    """« 1,5 L » / « 1,5 لتر »."""
    return f"{x:g}".replace(".", ",") + (" لتر" if lang == "ar" else " L")


def bouton_langue(lang, href="#"):
    """Bouton de langue de l'en-tête : un vrai lien vers l'autre adresse (lisible par Google, marche sans JavaScript).
    Jamais un span data-l (règle commune § 53 : le style le cacherait)."""
    if lang == "ar":
        return (f'<a class="langue-btn" href="{href}" hreflang="fr" lang="fr" title="Lire cette page en français">'
                '<span class="lb-long">Français</span><span class="lb-court" aria-hidden="true">Fr</span></a>')
    return (f'<a class="langue-btn" href="{href}" hreflang="ar" lang="ar" title="اقرأ هذه الصفحة بالعربية">'
            '<span class="lb-long">العربية</span><span class="lb-court" aria-hidden="true">ع</span></a>')


def _resoudre(chemin, rel):
    """Adresse d'un lien relatif écrit sur la page <chemin> (dossier), en chemin depuis la racine du site."""
    parts = [x for x in chemin.split("/") if x]
    for x in rel.split("/"):
        if x in ("", "."):
            continue
        if x == "..":
            if parts:
                parts.pop()
        else:
            parts.append(x)
    return "/".join(parts) + ("/" if parts else "")


def _plus_un_niveau(url, chemin):
    """Lien d'une page arabe (un dossier plus bas que la française) : une page qui existe en arabe reste dans ar/ ;
    tout le reste (style, scripts, données, images, page vidéo, anciennes pages) est pris à la racine du site."""
    if not url or re.match(r"^([a-z][a-z0-9+.-]*:|//|/|#|\?)", url, re.I):
        return url
    p = url.split("#")[0].split("?")[0]
    if (p == "" or p.endswith("/") or p in (".", "..")) and _resoudre(chemin, p) in MIROIR:
        return url
    return "../" + url


def _reecrire_liens(page, chemin):
    def attr(m):
        nom, val = m.group(1), m.group(2)
        if nom == "srcset":
            morceaux = [s.strip() for s in val.split(",") if s.strip()]
            val = ", ".join(" ".join([_plus_un_niveau(s.split()[0], chemin)] + s.split()[1:]) for s in morceaux)
        else:
            val = _plus_un_niveau(val, chemin)
        return f'{nom}="{val}"'
    return re.sub(r'\b(href|src|srcset|action|poster)="([^"]*)"', attr, page)


def tete_langues(chemin):
    fr, ar = URL_SITE + chemin, URL_SITE + "ar/" + chemin
    return (f'<link rel="alternate" hreflang="fr" href="{fr}">\n<link rel="alternate" hreflang="ar" href="{ar}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{fr}">\n')


def _sans_langues(page):
    page = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', "", page)
    return page


def finir(fr, ar, chemin):
    """Pages française et arabe d'un même chemin -> versions finales (hreflang, canonical, html lang/dir, bouton de langue,
    liens de la page arabe). Sans effet de bord ; refaire deux fois donne le même résultat (l'accueil est relu chaque nuit)."""
    prof = chemin.count("/")
    vers_ar = "../" * prof + "ar/" + chemin
    vers_fr = "../" * (prof + 1) + chemin
    tete = tete_langues(chemin)

    fr = _sans_langues(fr)
    fr = re.sub(r"<html\b[^>]*>", lambda m: f'<html lang="fr" translate="no" data-racine="{"../" * prof}" data-langue-fixe="fr" data-autre-langue="{vers_ar}">', fr, count=1)
    fr = fr.replace('<link rel="canonical"', tete + '<link rel="canonical"', 1)
    fr = BOUTON.sub(lambda m: bouton_langue("fr", vers_ar), fr, count=1)

    url_ar = URL_SITE + "ar/" + chemin
    ar = _sans_langues(ar)
    ar = _reecrire_liens(ar, chemin)
    ar = re.sub(r"<html\b[^>]*>", lambda m: f'<html lang="ar" dir="rtl" translate="no" data-racine="{"../" * (prof + 1)}" data-langue-fixe="ar" data-autre-langue="{vers_fr}">', ar, count=1)
    ar = re.sub(r'<link rel="canonical" href="[^"]*">', lambda m: tete + f'<link rel="canonical" href="{url_ar}">', ar, count=1)
    ar = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url_ar}">', ar, count=1)
    if '<meta property="og:url"' not in ar:
        ar = ar.replace('<meta property="og:title"', f'<meta property="og:url" content="{url_ar}">\n<meta property="og:title"', 1)
    if '<meta property="og:url"' not in fr:
        fr = fr.replace('<meta property="og:title"', f'<meta property="og:url" content="{URL_SITE + chemin}">\n<meta property="og:title"', 1)
    for page_lang in ("fr", "ar"):
        p = fr if page_lang == "fr" else ar
        p = re.sub(r'<meta property="og:locale(:alternate)?" content="[^"]*">\n?', "", p)
        loc = ('<meta property="og:locale" content="ar_AR">\n<meta property="og:locale:alternate" content="fr_FR">\n' if page_lang == "ar"
               else '<meta property="og:locale" content="fr_FR">\n<meta property="og:locale:alternate" content="ar_AR">\n')
        p = p.replace('<meta property="og:image"', loc + '<meta property="og:image"', 1)
        if page_lang == "fr":
            fr = p
        else:
            ar = p
    ar = BOUTON.sub(lambda m: bouton_langue("ar", vers_fr), ar, count=1)
    # police arabe (Noto Sans Arabic, Google Fonts : déjà permis par la CSP) ajoutée au lien des polices de la page arabe
    if POLICE_AR not in ar:
        ar = re.sub(r'(<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*?)(&amp;display=swap|&display=swap)"',
                    lambda m: m.group(1) + POLICE_AR + m.group(2) + '"', ar, count=1)
    ar = ar.replace('<meta name="apple-mobile-web-app-title" content="Prix Eaux">', '<meta name="apple-mobile-web-app-title" content="أسعار الماء">', 1)
    return fr, ar


def ajouter(chemin, fr, ar):
    """Retient une paire de pages ; elles sont écrites par ecrire_tout() quand toutes les pages arabes sont connues
    (un lien vers une page qui existe en arabe reste dans ar/)."""
    _A_ECRIRE.append((chemin, fr, ar))
    MIROIR.add(chemin)


def ecrire(racine, chemin, html):
    d = os.path.join(racine, chemin)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)


def ecrire_tout(racine):
    """Écrit toutes les paires retenues (français à <chemin>, arabe à ar/<chemin>) ; renvoie les chemins arabes écrits."""
    faits = []
    for chemin, fr, ar in _A_ECRIRE:
        fr2, ar2 = finir(fr, ar, chemin)
        ecrire(racine, chemin, fr2)
        ecrire(racine, "ar/" + chemin, ar2)
        faits.append(chemin)
    _A_ECRIRE.clear()
    return faits


def nettoyer(racine):
    """Retire chaque page arabe ar/<chemin> qui n'a pas été refaite à ce passage ET dont la page française a disparu
    (marque retirée de la liste…). Leçon d'Alerte Concours (08/11/2026) : jamais une page arabe dont la française existe encore."""
    retirees = []
    base = os.path.join(racine, "ar")
    if not os.path.isdir(base):
        return retirees
    for dossier, _sous, fichiers in os.walk(base, topdown=False):
        rel = os.path.relpath(dossier, base).replace(os.sep, "/")
        chemin = "" if rel == "." else rel + "/"
        if "index.html" in fichiers and chemin not in MIROIR:
            fr = os.path.join(racine, chemin, "index.html")
            if not os.path.exists(fr):
                os.remove(os.path.join(dossier, "index.html"))
                retirees.append(chemin)
        if dossier != base and not os.listdir(dossier):
            shutil.rmtree(dossier)
    return retirees


def page_unique(fichier):
    """Page qui garde UNE seule adresse (video/, avec ?lang=) : fabriquée à partir d'une page française, elle ne doit garder
    ni la langue fixe, ni le bouton de langue, ni les liens hreflang de sa page modèle."""
    if not os.path.exists(fichier):
        return
    with open(fichier, encoding="utf-8") as f:
        h = f.read()
    h2 = re.sub(r"<html\b[^>]*>", '<html lang="fr" translate="no">', h, count=1)
    h2 = _sans_langues(h2)
    h2 = BOUTON.sub("", h2)
    h2 = re.sub(r'<meta property="og:locale:alternate" content="[^"]*">\n?', "", h2)
    if h2 != h:
        with open(fichier, "w", encoding="utf-8", newline="\n") as f:
            f.write(h2)


# ------------------------------------------------------------------------------------------------------------------------------
# Accueil arabe (ar/index.html), tiré d'index.html (écrit à la main en français). Chaque paire = un morceau EXACT d'index.html et
# sa traduction. Un morceau absent (index.html modifié) est signalé dans MANQUES : le test du site trouvera le français restant.
# Les listes déroulantes du formulaire « Signaler un prix » gardent leur VALEUR française (lue par tools/signalements.py) :
# seul le texte affiché change.
# ------------------------------------------------------------------------------------------------------------------------------
ACCUEIL = [
    ('<title>Prix de l\'eau en Tunisie — comparateur gratuit, bouteille et stika</title>',
     '<title>أسعار الماء المعدني في تونس — مقارن مجاني، القارورة والستيكة</title>'),
    ('<meta property="og:title" content="Prix des Eaux de Tunisie — comparateur gratuit">',
     '<meta property="og:title" content="أسعار الماء المعدني في تونس — مقارن مجاني">'),
    ('aria-label="Prix des Eaux de Tunisie — accueil"', 'aria-label="أسعار الماء في تونس — الصفحة الرئيسية"'),
    ('<div class="titre-txt"><h1>Prix des Eaux de Tunisie</h1>', '<div class="titre-txt"><h1>أسعار الماء في تونس</h1>'),
    ('title="Recevoir les baisses de prix sur Telegram" aria-label="Recevoir les baisses de prix sur Telegram"',
     'title="تلقَّ تخفيضات الأسعار على تيليغرام" aria-label="تلقَّ تخفيضات الأسعار على تيليغرام"'),
    ('<span class="tg-txt">Alertes<b class="tg-promo">PROMO</b></span>', '<span class="tg-txt">تنبيهات<b class="tg-promo">تخفيضات</b></span>'),
    ('placeholder="Chercher une marque… (Safia, Marwa…)" aria-label="Chercher une marque"',
     'placeholder="ابحث عن علامة… (Safia، Marwa…)" aria-label="ابحث عن علامة"'),
    ('<span id="dd-mode-txt">Stika</span>', '<span id="dd-mode-txt">ستيكة</span>'),
    ('<p class="dd-titre">Prix affiché</p>', '<p class="dd-titre">السعر المعروض</p>'),
    ('aria-label="Unité de prix"', 'aria-label="وحدة السعر"'),
    ('alt="">Stika</button>', 'alt="">ستيكة</button>'),
    ('alt="">Bouteille</button>', 'alt="">قارورة</button>'),
    ('<span id="dd-type-txt">Type d\'eau</span>', '<span id="dd-type-txt">نوع الماء</span>'),
    ('<p class="dd-titre">Type d\'eau <small>(plusieurs choix possibles)</small></p>', '<p class="dd-titre">نوع الماء <small>(يمكن اختيار أكثر من نوع)</small></p>'),
    ('role="group" aria-label="Type d\'eau"', 'role="group" aria-label="نوع الماء"'),
    ('aria-pressed="false">Minérale</button>', 'aria-pressed="false">معدني</button>'),
    ('aria-pressed="false">Source</button>', 'aria-pressed="false">ماء عين</button>'),
    ('aria-pressed="false">Traitée</button>', 'aria-pressed="false">معالَج</button>'),
    ('aria-pressed="false">Gazeuses</button>', 'aria-pressed="false">غازي</button>'),
    ('aria-label="Comprendre les types d\'eau" title="Comprendre les types d\'eau"', 'aria-label="ما الفرق بين أنواع الماء؟" title="ما الفرق بين أنواع الماء؟"'),
    ('<span id="dd-format-txt">1,5 L</span>', '<span id="dd-format-txt">1,5 لتر</span>'),
    ('<p class="dd-titre">Format <small>(plusieurs choix possibles)</small></p>', '<p class="dd-titre">الحجم <small>(يمكن اختيار أكثر من حجم)</small></p>'),
    ('aria-label="Format de bouteille"', 'aria-label="حجم القارورة"'),
    ('aria-label="Les formats de bouteille"', 'aria-label="أحجام القوارير"'),
    ('aria-label="Fermer">×</button>\n      <h2>Les formats de bouteille</h2>', 'aria-label="إغلاق">×</button>\n      <h2>أحجام القوارير</h2>'),
    ('alt="Bouteille 0,25 L"', 'alt="قارورة 0,25 لتر"'), ('<figcaption>0,25 L</figcaption>', '<figcaption>0,25 لتر</figcaption>'),
    ('alt="Bouteille 0,5 L"', 'alt="قارورة 0,5 لتر"'), ('<figcaption>0,5 L</figcaption>', '<figcaption>0,5 لتر</figcaption>'),
    ('alt="Bouteille 1 L"', 'alt="قارورة 1 لتر"'), ('<figcaption>1 L</figcaption>', '<figcaption>1 لتر</figcaption>'),
    ('alt="Bouteille 1,5 L"', 'alt="قارورة 1,5 لتر"'), ('<figcaption>1,5 L<br><small>la classique</small></figcaption>', '<figcaption>1,5 لتر<br><small>الأكثر شيوعًا</small></figcaption>'),
    ('alt="Bouteille 2 L"', 'alt="قارورة 2 لتر"'), ('<figcaption>2 L</figcaption>', '<figcaption>2 لتر</figcaption>'),
    ('alt="Bidon 6 L"', 'alt="بيدون 6 لتر"'), ('<figcaption>6 L<br><small>bidon</small></figcaption>', '<figcaption>6 لتر<br><small>بيدون</small></figcaption>'),
    ('alt="Bonbonne 19 L"', 'alt="قارورة كبيرة 19 لتر"'), ('<figcaption>19 L<br><small>bonbonne</small></figcaption>', '<figcaption>19 لتر<br><small>قارورة كبيرة</small></figcaption>'),
    ('<p class="help-src">Le filtre « ≤ 0,75 L » regroupe les 0,25 et 0,5 L ; « ≥ 5 L » regroupe\n      les bidons de 6 L et les bonbonnes de 19 L. La <strong>stika</strong> = le pack de\n      6 bouteilles (12 pour les 50 cl) ; les grands formats se vendent à l\'unité.</p>',
     '<p class="help-src">الاختيار « ≤ 0,75 لتر » يجمع قوارير 0,25 و0,5 لتر، و« ≥ 5 لتر » يجمع بيدونات 6 لتر والقوارير الكبيرة 19 لتر. '
     '<strong>الستيكة</strong> = علبة من 6 قوارير (12 للقوارير الصغيرة 50 صل)، والأحجام الكبيرة تُباع بالوحدة.</p>'),
    ('aria-label="Les types d\'eau embouteillée"', 'aria-label="أنواع الماء المعبّأ"'),
    ('aria-label="Fermer">×</button>\n      <h2>Les types d\'eau embouteillée</h2>', 'aria-label="إغلاق">×</button>\n      <h2>أنواع الماء المعبّأ</h2>'),
    ('<p><strong>Eau minérale naturelle</strong> — issue d\'une source souterraine protégée, avec une\n      composition minérale <em>stable et garantie</em>. Aucun traitement chimique n\'est autorisé.</p>',
     '<p><strong>الماء المعدني الطبيعي</strong> — يأتي من عين جوفية محمية، وتركيبته المعدنية <em>ثابتة ومضمونة</em>. لا يُسمح بأي معالجة كيميائية.</p>'),
    ('<p><strong>Eau de source</strong> — souterraine et naturellement potable elle aussi, mais sa\n      composition peut varier dans le temps ; les exigences sont moins strictes.</p>',
     '<p><strong>ماء العين</strong> — جوفي وصالح للشرب طبيعيًا هو أيضًا، لكن تركيبته قد تتغير مع الوقت، وشروطه أقل صرامة.</p>'),
    ('<p><strong>Eau traitée (eau de table)</strong> — eau rendue potable par traitement,\n      quelle que soit son origine.</p>',
     '<p><strong>الماء المعالَج (ماء المائدة)</strong> — ماء أصبح صالحًا للشرب بعد معالجته، مهما كان مصدره.</p>'),
    ('<p><strong>Eau gazeuse</strong> — eau avec bulles, naturelles (comme Garci ou Aïn Oktor)\n      ou ajoutées.</p>',
     '<p><strong>الماء الغازي</strong> — ماء فيه فقاعات، طبيعية (مثل Garci أو Aïn Oktor) أو مضافة.</p>'),
    ('<p class="help-src">Classification et compositions transcrites du tableau de\n      l\'<strong>Office du Thermalisme</strong> (organisme officiel tunisien), publié par le\n      Dr Ing. Imed Houcine — <a href="https://www.babnet.net/festivaldetail-287073.asp" rel="noopener"\n      target="_blank" rel="noopener">voir la publication (mai 2024)</a>. Le détail par marque\n      (calcium, sodium, pH…) est dans « Composition » sur chaque fiche.</p>',
     '<p class="help-src">التصنيف والتركيبات منقولة من جدول <strong>ديوان المياه المعدنية والاستشفاء بالمياه</strong> (هيكل رسمي تونسي)، '
     'نشره الدكتور المهندس عماد حسين — <a href="https://www.babnet.net/festivaldetail-287073.asp" rel="noopener" target="_blank">'
     'انظر المنشور (ماي 2024)</a>. تفاصيل كل علامة (الكالسيوم، الصوديوم، الحموضة…) في « التركيبة » على بطاقتها.</p>'),
    ('alt="Eau versée d\'une bouteille en plastique dans un verre"', 'alt="ماء يُسكب من قارورة بلاستيكية في كأس"'),
    ('kitchen.jpg">Photo <a href=', 'kitchen.jpg">صورة <a href='),
    ('rel="noopener">Shixart1985</a> · <a href="https://creativecommons.org/licenses/by/2.0/deed.fr" rel="license noopener">CC BY 2.0</a> · Wikimedia Commons</figcaption>',
     'rel="noopener">Shixart1985</a> · <a href="https://creativecommons.org/licenses/by/2.0/deed.ar" rel="license noopener">CC BY 2.0</a> · ويكيميديا كومنز</figcaption>'),
    ('<p class="intro identite">Les <strong>prix de l\'eau dans les magasins tunisiens</strong>, comparés chaque jour. Gratuit, sans inscription.\n'
     '  <span class="identite-2">Prix <b>indicatifs</b> relevés sur les boutiques en ligne des grandes surfaces (Carrefour, Géant), complétés par les prix que vous signalez (<a href="#sources">sources citées</a>).\n'
     '  Pour la future commande, le <b>prix final</b> dépendra du fournisseur et du stock disponible au moment de la livraison.</span></p>',
     '<p class="intro identite"><strong>أسعار الماء في المغازات التونسية</strong>، نقارنها كل يوم. مجانًا ودون تسجيل.\n'
     '  <span class="identite-2">أسعار <b>تقريبية</b> نقرؤها في المتاجر الإلكترونية للمغازات الكبرى (Carrefour وGéant)، مع الأسعار التي تبلّغون عنها (<a href="#sources">المصادر مذكورة</a>).\n'
     '  بالنسبة للطلبية القادمة، <b>السعر النهائي</b> يحدّده المزوّد حسب المخزون المتوفر يوم التوصيل.</span></p>'),
    ('<label for="mon-carrefour">🛒 Mon Carrefour :</label>', '<label for="mon-carrefour">🛒 مغازة Carrefour متاعي:</label>'),
    ('<option value="">Tous les magasins</option>', '<option value="">كل المغازات</option>'),
    ('aria-label="Les moins chères aujourd\'hui"', 'aria-label="الأرخص اليوم"'),
    ('<h2>L\'eau préférée des clients</h2>\n      <span class="sum-cta">Voir</span>', '<h2>الماء المفضّل لدى الحرفاء</h2>\n      <span class="sum-cta">شاهد</span>'),
    ('<h2>Signaler un prix vu en magasin</h2>\n      <span class="sum-cta"><span class="sig-cta-txt">Voir</span>',
     '<h2>بلّغ عن سعر رأيته في المغازة</h2>\n      <span class="sum-cta"><span class="sig-cta-txt">شاهد</span>'),
    ('<h2>Commande &amp; livraison <span class="bientot">bientôt</span></h2>\n      <span class="sum-cta"><span class="sig-cta-txt">Voir</span>',
     '<h2>الطلب والتوصيل <span class="bientot">قريبًا</span></h2>\n      <span class="sum-cta"><span class="sig-cta-txt">شاهد</span>'),
    ('<p class="lien-comment"><a href="a-propos/">Comment fonctionne le site ?</a></p>', '<p class="lien-comment"><a href="a-propos/">كيف يعمل الموقع؟</a></p>'),
    ('<h2>Les prix, marque par marque</h2>', '<h2>الأسعار، علامة بعلامة</h2>'),
    ('aria-label="Trier les marques"', 'aria-label="ترتيب العلامات"'),
    ('<option value="nom">Tri : nom A→Z</option>', '<option value="nom">الترتيب: الاسم أبجديًا</option>'),
    ('<option value="prix15">Tri : prix 1,5 L croissant</option>', '<option value="prix15">الترتيب: سعر 1,5 لتر من الأرخص</option>'),
    ('<option value="prixL">Tri : prix au litre croissant</option>', '<option value="prixL">الترتيب: سعر اللتر من الأرخص</option>'),
    ('<option value="tds">Tri : minéralité (résidu sec)</option>', '<option value="tds">الترتيب: نسبة الأملاح (البقايا الجافة)</option>'),
    ('<p class="sub">La flèche ↓ marque l\'enseigne la moins chère.</p>', '<p class="sub">السهم ↓ يشير إلى المغازة الأرخص.</p>'),
    ('<div class="empty" id="empty" hidden>Aucune marque ne correspond à cette recherche.</div>', '<div class="empty" id="empty" hidden>لا توجد علامة تطابق هذا البحث.</div>'),
    ('<summary><h2>Évolution des prix</h2><span class="sub-inline">— la stika 1,5 L la moins chère, jour par jour</span></summary>',
     '<summary><h2>تطوّر الأسعار</h2><span class="sub-inline">— أرخص ستيكة 1,5 لتر، يومًا بيوم</span></summary>'),
    ('<p class="sub">L\'historique démarre le 25 septembre 2026 — la courbe s\'allonge jour après jour.</p>',
     '<p class="sub">يبدأ السجلّ يوم 25 سبتمبر 2026، والمنحنى يطول يومًا بعد يوم.</p>'),
    ('<summary><h2>Questions fréquentes</h2><span class="sub-inline">— stika, prix, marques, livraison…</span></summary>',
     '<summary><h2>أسئلة متكرّرة</h2><span class="sub-inline">— الستيكة، الأسعار، العلامات، التوصيل…</span></summary>'),
    ('<h3>Quelle est l\'eau minérale la moins chère en Tunisie ?</h3>\n    <p>Au dernier relevé, la bouteille de 1,5 L d\'eau plate la moins chère est à\n'
     '    <span id="faq-min">', '<h3>ما هو أرخص ماء معدني في تونس؟</h3>\n    <p>حسب آخر قراءة، أرخص قارورة ماء عادي 1,5 لتر سعرها\n    <span id="faq-min">'),
    ('</span> (<span id="faq-winners">', '</span> (<span id="faq-winners">'),
    ('</span>),\n    soit <span id="faq-min-stika">', '</span>)،\n    أي <span id="faq-min-stika">'),
    ('</span> la stika de 6 bouteilles. Le classement complet\n    des marques est mis à jour chaque jour en haut de cette page.</p>',
     '</span> للستيكة من 6 قوارير. الترتيب الكامل للعلامات يُحدَّث كل يوم في أعلى هذه الصفحة.</p>'),
    ('<h3>Quel est le prix d\'une stika d\'eau en Tunisie ?</h3>\n    <p>Au dernier relevé, la <strong>stika de 6 bouteilles de 1,5 L</strong> la moins chère coûte\n    <span id="faq-stika-prix">',
     '<h3>كم ثمن ستيكة الماء في تونس؟</h3>\n    <p>حسب آخر قراءة، أرخص <strong>ستيكة من 6 قوارير 1,5 لتر</strong> سعرها\n    <span id="faq-stika-prix">'),
    ('</span> en grande surface (<span id="faq-stika-marques">', '</span> في المغازات الكبرى (<span id="faq-stika-marques">'),
    ('</span>).\n    Selon la marque, la stika 1,5 L va de <span id="faq-stika-min">', '</span>).\n    حسب العلامة، ثمن ستيكة 1,5 لتر بين <span id="faq-stika-min">'),
    ('</span> à\n    <span id="faq-stika-max">', '</span> و\n    <span id="faq-stika-max">'),
    ('</span>. Activez le bouton « Stika » en haut de la page pour\n    voir tous les prix en stika, marque par marque et enseigne par enseigne.</p>',
     '</span>. اختر « ستيكة » في أعلى الصفحة لترى كل الأسعار بالستيكة، علامة بعلامة ومغازة بمغازة.</p>'),
    ('<h3>C\'est quoi une « stika » ?</h3>\n    <p>En Tunisie, la <strong>stika</strong> est le pack de 6 bouteilles d\'eau (12 pour les petites\n    bouteilles de 50 cl), le format le plus acheté par les familles. Sur ce site, chaque produit\n    affiche le prix de la bouteille et celui de la stika.</p>',
     '<h3>ما هي « الستيكة »؟</h3>\n    <p>في تونس، <strong>الستيكة</strong> هي علبة من 6 قوارير ماء (12 للقوارير الصغيرة 50 صل)، وهي الأكثر شراءً عند العائلات. '
     'في هذا الموقع، كل منتوج يعرض سعر القارورة وسعر الستيكة.</p>'),
    ('<h3>D\'où viennent les prix affichés ?</h3>\n    <p>Les prix sont relevés automatiquement chaque jour sur les boutiques en ligne des grandes\n    surfaces tunisiennes (Géant Drive, Carrefour). Ils sont indicatifs et\n    peuvent varier selon le magasin et les promotions du moment.</p>',
     '<h3>من أين تأتي الأسعار المعروضة؟</h3>\n    <p>تُقرأ الأسعار آليًا كل يوم من المتاجر الإلكترونية للمغازات الكبرى في تونس (Géant Drive وCarrefour). '
     'هي أسعار تقريبية وقد تتغيّر حسب المغازة والتخفيضات.</p>'),
    ('<h3>Comment fonctionne la commande avec livraison ?</h3>\n    <p>Ajoutez vos produits avec le bouton <strong>+</strong>, indiquez votre téléphone et votre\n    adresse (ou localisez-vous d\'un clic), puis envoyez la commande — elle nous arrive sur WhatsApp.\n    Nous revenons vers vous avec le prix total et les frais de livraison pour confirmer. Vous ne\n    payez qu\'à la livraison, et l\'envoi de la commande ne vous engage à rien.</p>',
     '<h3>كيف سيعمل الطلب مع التوصيل؟</h3>\n    <p>الطلب غير مفتوح بعد. عند فتحه: تضيف منتوجاتك بزر <strong>+</strong>، تكتب رقم هاتفك وعنوانك (أو تحدّد موقعك بنقرة)، '
     'ثم ترسل الطلب على واتساب. نعود إليك بالسعر الجملي ومصاريف التوصيل لتؤكّد. الدفع عند التوصيل فقط، وإرسال الطلب لا يُلزمك بشيء.</p>'),
    ('<h3>Quelle eau minérale est la moins minéralisée ?</h3>\n    <p>D\'après les fiches de l\'Office du Thermalisme (2024), l\'eau embouteillée la moins\n    minéralisée de Tunisie est <strong>Hayet</strong> (résidu sec de 238 mg/L), suivie de\n    Jannet (272), Sabrine (303) et Safia Aïn Mizeb (308). Les plus minéralisées sont les eaux\n    gazeuses <strong>Garci</strong> (1 677 mg/L) et <strong>Aïn Oktor</strong> (1 680 mg/L).\n    Ouvrez « Composition » sur la carte d\'une marque pour le détail (calcium, sodium, pH…),\n    ou triez par minéralité avec le menu en haut de page.</p>',
     '<h3>ما هو الماء المعدني الأقل أملاحًا؟</h3>\n    <p>حسب جداول ديوان المياه المعدنية (2024)، أقل ماء معبّأ أملاحًا في تونس هو <strong>Hayet</strong> '
     '(بقايا جافة 238 مغ/لتر)، ثم Jannet (272) وSabrine (303) وSafia Aïn Mizeb (308). الأكثر أملاحًا هما الماءان الغازيان '
     '<strong>Garci</strong> (1677 مغ/لتر) و<strong>Aïn Oktor</strong> (1680 مغ/لتر). افتح « التركيبة » في بطاقة أي علامة للتفاصيل '
     '(الكالسيوم، الصوديوم، الحموضة…)، أو رتّب حسب نسبة الأملاح من القائمة في أعلى الصفحة.</p>'),
    ('<h3>Quelle différence entre eau minérale, eau de source et eau de table ?</h3>\n    <p>L\'<strong>eau minérale naturelle</strong> vient d\'une source souterraine protégée et a une\n    composition stable et garantie, sans aucun traitement. L\'<strong>eau de source</strong> est\n    aussi souterraine et naturellement potable, mais sa composition peut varier. L\'<strong>eau de\n    table (traitée)</strong> est rendue potable par traitement. Utilisez les boutons Minérale /\n    Source / Traitée en haut de la page pour filtrer les marques — classification issue du tableau\n    officiel de l\'Office du Thermalisme.</p>',
     '<h3>ما الفرق بين الماء المعدني وماء العين وماء المائدة؟</h3>\n    <p><strong>الماء المعدني الطبيعي</strong> يأتي من عين جوفية محمية وتركيبته ثابتة ومضمونة دون أي معالجة. '
     '<strong>ماء العين</strong> جوفي وصالح للشرب طبيعيًا أيضًا، لكن تركيبته قد تتغيّر. <strong>ماء المائدة (المعالَج)</strong> '
     'يصبح صالحًا للشرب بعد المعالجة. استعمل أزرار معدني / ماء عين / معالَج في أعلى الصفحة لتصفية العلامات — التصنيف مأخوذ من الجدول الرسمي لديوان المياه المعدنية.</p>'),
    ('<h3>Quelles marques d\'eau sont comparées ?</h3>\n    <p><span id="faq-nb-marques">', '<h3>ما هي العلامات التي نقارنها؟</h3>\n    <p><span id="faq-nb-marques">'),
    ('</span> marques vendues en Tunisie :\n    <span id="faq-marques-liste">', '</span> علامة تُباع في تونس:\n    <span id="faq-marques-liste">'),
    ('</span> — eaux plates et gazeuses.</p>', '</span> — مياه عادية وغازية.</p>'),
    ('<h2 class="h2-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>Votre avis</h2>\n    <p class="sub">Une remarque, un prix à corriger, une marque manquante, une idée ? Écrivez-nous.</p>',
     '<h2 class="h2-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>رأيك</h2>\n    <p class="sub">ملاحظة، سعر يجب تصحيحه، علامة ناقصة، فكرة؟ اكتب لنا.</p>'),
    ('placeholder="Votre nom (facultatif)"', 'placeholder="اسمك (اختياري)"'),
    ('placeholder="Votre email (obligatoire, pour vous répondre)" aria-label="Votre email (obligatoire, pour vous répondre)"',
     'placeholder="بريدك الإلكتروني (إجباري، لنجيبك)" aria-label="بريدك الإلكتروني (إجباري، لنجيبك)"'),
    ('placeholder="Votre message…"', 'placeholder="رسالتك…"'),
    ('<button type="submit" class="avis-send">Envoyer</button>\n        <span id="avis-status"', '<button type="submit" class="avis-send">أرسل</button>\n        <span id="avis-status"'),
    ('aria-label="Prix par marque"', 'aria-label="الأسعار حسب العلامة"'),
    ('<summary><h2>Prix de l\'eau par marque</h2><span class="sub-inline">— la page détaillée de chaque marque</span></summary>',
     '<summary><h2>سعر الماء حسب العلامة</h2><span class="sub-inline">— الصفحة المفصّلة لكل علامة</span></summary>'),
    ('Prix des Eaux de Tunisie</p>\n    <p class="pied-desc">Comparateur indépendant des prix de l\'eau en bouteille en Tunisie.\n    Site non officiel, sans lien avec les enseignes ni avec les marques citées.</p>',
     'أسعار الماء في تونس</p>\n    <p class="pied-desc">مقارن مستقل لأسعار الماء المعبّأ في تونس. موقع غير رسمي، لا علاقة له بالمغازات ولا بالعلامات المذكورة.</p>'),
    ('aria-label="Liens utiles"><a href="./">Accueil</a>', 'aria-label="روابط مفيدة"><a href="./">الرئيسية</a>'),
    ('<a href="prix-stika/">Prix de la stika d\'eau aujourd\'hui</a>', '<a href="prix-stika/">سعر ستيكة الماء اليوم</a>'),
    ('<a href="rapports/">Rapports du mois (prix par marque)</a>', '<a href="rapports/">تقارير الشهر (الأسعار حسب العلامة)</a>'),
    ('<a href="quelle-eau/">Quelle eau minérale choisir ?</a>', '<a href="quelle-eau/">أي ماء معدني تختار؟</a>'),
    ('<a href="a-propos/">Comment fonctionne le site ?</a>\n    <a href="https://eau.clicvia.com/"', '<a href="a-propos/">كيف يعمل الموقع؟</a>\n    <a href="https://eau.clicvia.com/"'),
    ('rel="noopener">Où trouver de l\'eau (sources, majels)</a>', 'rel="noopener">أين تجد الماء (عيون، مواجل)</a>'),
    ('<a href="https://clicvia.com/" rel="noopener">Tous nos services</a>', '<a href="https://clicvia.com/" rel="noopener">كل خدماتنا</a>'),
    ('<a href="https://clicvia.com/confidentialite/" rel="noopener">Confidentialité</a>', '<a href="https://clicvia.com/ar/confidentialite/" rel="noopener">الخصوصية</a>'),
    ('<a href="https://clicvia.com/conditions/" rel="noopener">Conditions d\'utilisation</a>', '<a href="https://clicvia.com/ar/conditions/" rel="noopener">شروط الاستعمال</a>'),
    ('<a href="prix-eau-carrefour/">Prix de l\'eau chez Carrefour</a>', '<a href="prix-eau-carrefour/">سعر الماء في Carrefour</a>'),
    ('<a href="prix-eau-geant/">Prix de l\'eau chez Géant</a>', '<a href="prix-eau-geant/">سعر الماء في Géant</a>'),
    ('rel="noopener">Alertes promo (Telegram)</a>', 'rel="noopener">تنبيهات التخفيضات (تيليغرام)</a>'),
    ('<a href="#avis">Votre avis</a></nav>', '<a href="#avis">رأيك</a></nav>'),
    ('<h2 class="pied-titre" id="sources">Sources des prix</h2>', '<h2 class="pied-titre" id="sources">مصادر الأسعار</h2>'),
    ('<p class="credit-pied">Photo du bandeau : eau versée dans un verre, <a href="https://commons.wikimedia.org/wiki/File:Person_pours_water_from_a_bottle_into_a_glass_in_a_kitchen.jpg" rel="noopener">Shixart1985</a>, <a href="https://creativecommons.org/licenses/by/2.0/deed.fr" rel="license noopener">CC BY 2.0</a>, Wikimedia Commons ; recadrée en bandeau.</p>',
     '<p class="credit-pied">صورة الشريط العلوي: ماء يُسكب في كأس، <a href="https://commons.wikimedia.org/wiki/File:Person_pours_water_from_a_bottle_into_a_glass_in_a_kitchen.jpg" rel="noopener">صورة Shixart1985</a>، <a href="https://creativecommons.org/licenses/by/2.0/deed.ar" rel="license noopener">CC BY 2.0</a>، ويكيميديا كومنز، مقصوصة لتناسب الشريط.</p>'),
    ('<p class="credit-pied">Photos de bouteilles des marques absentes des boutiques suivies : <a href="https://world.openfoodfacts.org/" rel="noopener">Open Food Facts</a>, <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.fr" rel="license noopener">CC BY-SA 3.0</a> (crédit et lien sous chaque photo ; recadrées sur fond blanc).</p>',
     '<p class="credit-pied">صور قوارير العلامات غير الموجودة في المغازات المتابَعة: <a href="https://world.openfoodfacts.org/" rel="noopener">Open Food Facts</a>، <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.ar" rel="license noopener">CC BY-SA 3.0</a> (المصدر والرابط تحت كل صورة، مقصوصة على خلفية بيضاء).</p>'),
    ('<p class="copyright">© 2026 Prix des Eaux de Tunisie — tous droits réservés. Reproduction du site,\n    de son code ou de ses données interdite sans autorisation.</p>',
     '<p class="copyright">© 2026 أسعار الماء في تونس — جميع الحقوق محفوظة. يُمنع نسخ الموقع أو برمجته أو بياناته دون إذن.</p>'),
    ('<button type="button" class="cartbar-btn" id="cart-open">Commander 🛒</button>', '<button type="button" class="cartbar-btn" id="cart-open">اطلب 🛒</button>'),
    ('aria-label="Fermer">×</button>\n    <h2 id="match-titre">❤️ L\'eau préférée des clients</h2>', 'aria-label="إغلاق">×</button>\n    <h2 id="match-titre">❤️ الماء المفضّل لدى الحرفاء</h2>'),
    ('<p class="sub">Votez pour votre eau préférée ! Un vote par personne ; classement mis à jour toutes les 2h.</p>',
     '<p class="sub">صوّت لمائك المفضّل! صوت واحد لكل شخص، والترتيب يُحدَّث كل ساعتين.</p>'),
    ('<select id="vote-marque" aria-label="Mon eau préférée"></select>\n        <button type="button" class="sig-bouton" id="vote-btn">❤️ Voter</button>',
     '<select id="vote-marque" aria-label="مائي المفضّل"></select>\n        <button type="button" class="sig-bouton" id="vote-btn">❤️ صوّت</button>'),
    ('aria-label="Fermer">×</button>\n    <h2 id="livraison-titre">🚚 Commande et livraison — bientôt</h2>', 'aria-label="إغلاق">×</button>\n    <h2 id="livraison-titre">🚚 الطلب والتوصيل — قريبًا</h2>'),
    ('<p class="livraison-cle"><strong>Ce ne sont pas les grandes surfaces qui livrent</strong> : vous commanderez\n    directement auprès de <strong>grossistes et dépôts partenaires</strong> de votre région, à <strong>leurs propres\n    prix</strong>, livraison comprise.</p>',
     '<p class="livraison-cle"><strong>ليست المغازات الكبرى هي التي توصّل</strong>: ستطلب مباشرة من <strong>تجّار جملة ومخازن شريكة</strong> في جهتك، '
     '<strong>بأسعارهم الخاصة</strong>، مع التوصيل.</p>'),
    ('<p>Voici comment la commande fonctionnera :</p>', '<p>هكذا سيعمل الطلب:</p>'),
    ('<li><b>Vous commandez</b> sur le site : marques, nombre de stikas, adresse.</li>', '<li><b>تطلب</b> في الموقع: العلامات، عدد الستيكات، العنوان.</li>'),
    ('<li><b>Un fournisseur de votre région vous propose son prix</b>, livraison comprise.</li>', '<li><b>مزوّد من جهتك يقترح عليك سعره</b>، مع التوصيل.</li>'),
    ('<li><b>Vous acceptez</b> (ou non) : rien n\'est engagé avant votre accord.</li>', '<li><b>توافق</b> (أو لا): لا شيء يُلزمك قبل موافقتك.</li>'),
    ('<li><b>Vous suivez la livraison</b> jusqu\'à votre porte. Paiement à la livraison.</li>', '<li><b>تتابع التوصيل</b> حتى باب دارك. الدفع عند التوصيل.</li>'),
    ('<p class="help-src">Les prix affichés sur ce site sont ceux des <b>grandes surfaces</b>, à titre indicatif.\n    Le <b>prix final d\'une commande</b> est celui du fournisseur : il dépend du <b>stock disponible au moment\n    de la livraison</b> et peut donc être différent. Vous le connaissez et l\'acceptez avant toute livraison.</p>',
     '<p class="help-src">الأسعار المعروضة في هذا الموقع هي أسعار <b>المغازات الكبرى</b>، للإرشاد فقط. <b>السعر النهائي للطلبية</b> هو سعر المزوّد: '
     'يتغيّر حسب <b>المخزون المتوفر يوم التوصيل</b> وقد يكون مختلفًا. تعرفه وتوافق عليه قبل أي توصيل.</p>'),
    ('<span class="cloche-vibre" aria-hidden="true">🔔</span> Être prévenu de l\'ouverture</a>', '<span class="cloche-vibre" aria-hidden="true">🔔</span> أعلِمني عند الافتتاح</a>'),
    ('aria-label="Fermer">×</button>\n    <h2 id="sig-titre">📍 Signaler un prix</h2>', 'aria-label="إغلاق">×</button>\n    <h2 id="sig-titre">📍 بلّغ عن سعر</h2>'),
    ('<h2>Signaler un prix</h2>\n        <span class="sum-cta"><span class="cta-closed">Remplir</span><span class="cta-open">Fermer</span>',
     '<h2>بلّغ عن سعر</h2>\n        <span class="sum-cta"><span class="cta-closed">املأ</span><span class="cta-open">أغلق</span>'),
    ('<p class="help-src">Vous avez vu un prix en magasin ? Partagez-le : après une vérification\n    automatique, il est publié sur la fiche de la marque (avec sa date) et sur notre canal Telegram.</p>',
     '<p class="help-src">رأيت سعرًا في مغازة؟ شاركه: بعد تثبّت آلي، يُنشر في بطاقة العلامة (مع تاريخه) وفي قناتنا على تيليغرام.</p>'),
    ('<label>Marque <select name="marque"', '<label>العلامة <select name="marque"'),
    ('<label>Format <select name="format" required>\n          <option>0,5 L</option><option>1 L</option><option selected>1,5 L</option><option>2 L</option>\n          <option>6 L</option><option>19 L</option><option>Autre</option></select></label>',
     '<label>الحجم <select name="format" required>\n          <option value="0,5 L">0,5 لتر</option><option value="1 L">1 لتر</option><option value="1,5 L" selected>1,5 لتر</option><option value="2 L">2 لتر</option>\n'
     '          <option value="6 L">6 لتر</option><option value="19 L">19 لتر</option><option value="Autre">حجم آخر</option></select></label>'),
    ('<label>Eau <select name="eau"><option>Plate</option><option>Gazeuse</option></select></label>',
     '<label>الماء <select name="eau"><option value="Plate">عادي</option><option value="Gazeuse">غازي</option></select></label>'),
    ('<label>Prix (DT) <input type="text" name="prix" inputmode="decimal" required placeholder="Tapez le prix"></label>',
     '<label>السعر (د.ت) <input type="text" name="prix" inputmode="decimal" required placeholder="اكتب السعر"></label>'),
    ('<label>Pour <select name="unite"><option>une stika</option><option>une bouteille</option></select></label>',
     '<label>لـ <select name="unite"><option value="une stika">ستيكة</option><option value="une bouteille">قارورة</option></select></label>'),
    ('<label>Magasin <select name="magasin" required>\n          <option value="">— choisir —</option><option>Aziza</option><option>Monoprix</option>\n          <option>Magasin Général</option><option>Carrefour</option><option>Géant</option>\n          <option>Épicerie de quartier</option><option>Autre</option></select></label>',
     '<label>المغازة <select name="magasin" required>\n          <option value="">— اختر —</option><option value="Aziza">Aziza</option><option value="Monoprix">Monoprix</option>\n'
     '          <option value="Magasin Général">Magasin Général</option><option value="Carrefour">Carrefour</option><option value="Géant">Géant</option>\n'
     '          <option value="Épicerie de quartier">عطّار الحومة</option><option value="Autre">مغازة أخرى</option></select></label>'),
    ('<label>Ville / quartier <input type="text" name="lieu" placeholder="Facultatif"></label>', '<label>المدينة / الحي <input type="text" name="lieu" placeholder="اختياري"></label>'),
    ('<label>Vu le <input type="date"', '<label>رأيته يوم <input type="date"'),
    ('<button type="submit" class="avis-send">Envoyer</button>\n        <span id="sig-status"', '<button type="submit" class="avis-send">أرسل</button>\n        <span id="sig-status"'),
    ('<h2 id="order-title">Votre commande</h2>\n      <button type="button" class="order-close" id="order-close" aria-label="Fermer">',
     '<h2 id="order-title">طلبيتك</h2>\n      <button type="button" class="order-close" id="order-close" aria-label="إغلاق">'),
    ('<label>Nom\n        <input id="o-nom" type="text" autocomplete="name" placeholder="Votre nom"></label>',
     '<label>الاسم\n        <input id="o-nom" type="text" autocomplete="name" placeholder="اسمك"></label>'),
    ('<label><span>Téléphone <span class="req">*</span></span>\n        <input id="o-tel" type="tel" required autocomplete="tel" placeholder="ex. 24 321 390"></label>',
     '<label><span>الهاتف <span class="req">*</span></span>\n        <input id="o-tel" type="tel" required autocomplete="tel" placeholder="مثلًا 24 321 390"></label>'),
    ('<label><span>Adresse de livraison <span class="req">*</span></span>\n        <textarea id="o-adr" rows="2" required placeholder="Rue, immeuble, ville…"></textarea></label>',
     '<label><span>عنوان التوصيل <span class="req">*</span></span>\n        <textarea id="o-adr" rows="2" required placeholder="النهج، العمارة، المدينة…"></textarea></label>'),
    ('<button type="button" class="chipbtn" id="o-geo">📍 Me localiser (GPS)</button>', '<button type="button" class="chipbtn" id="o-geo">📍 حدّد موقعي (GPS)</button>'),
    ('<p class="geo-hint">La position automatique n\'est pas toujours exacte : déplacez le repère\n        (ou touchez la carte) pour le mettre sur l\'endroit précis de la livraison — portail,\n        entrée d\'immeuble… — puis confirmez.</p>',
     '<p class="geo-hint">الموقع الآلي ليس دقيقًا دائمًا: حرّك العلامة (أو المس الخريطة) لتضعها في مكان التوصيل بالضبط — الباب، مدخل العمارة… — ثم أكّد.</p>'),
    ('<button type="button" class="chipbtn geo-confirm" id="o-geo-confirm">✔ Confirmer cette position</button>', '<button type="button" class="chipbtn geo-confirm" id="o-geo-confirm">✔ أكّد هذا الموقع</button>'),
    ('<label>Remarque\n        <input id="o-note" type="text" placeholder="ex. étage, horaire préféré…"></label>',
     '<label>ملاحظة\n        <input id="o-note" type="text" placeholder="مثلًا الطابق، الوقت المفضّل…"></label>'),
    ('<p class="order-note">Votre commande ne vous engage à rien : vous confirmez (ou non) une fois\n      le prix reçu sur WhatsApp. Paiement à la livraison.</p>',
     '<p class="order-note">طلبيتك لا تُلزمك بشيء: تؤكّد (أو لا) بعد أن يصلك السعر على واتساب. الدفع عند التوصيل.</p>'),
    ('Envoyer la commande sur WhatsApp</button>', 'أرسل الطلبية على واتساب</button>'),
    ('<span class="tampon-titre">🚧 En cours de développement</span>\n       <span class="tampon-sous">Commande en ligne disponible prochainement</span>\n       <a href="https://t.me/prixeautunisie" target="_blank" rel="noopener">Être prévenu sur Telegram</a>',
     '<span class="tampon-titre">🚧 قيد الإنجاز</span>\n       <span class="tampon-sous">الطلب عبر الإنترنت متاح قريبًا</span>\n       <a href="https://t.me/prixeautunisie" target="_blank" rel="noopener">أعلِمني على تيليغرام</a>'),
]
MANQUES = []


def _jsonld_accueil_ar(nb):
    d = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": NOM_AR, "alternateName": "Prix des Eaux de Tunisie", "url": URL_SITE + "ar/", "inLanguage": "ar",
         "description": "مقارن مجاني لأسعار الماء المعدني في تونس (القارورة والستيكة) في Géant وCarrefour، يُحدَّث كل يوم."},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": "ما هي الستيكة؟", "acceptedAnswer": {"@type": "Answer", "text":
             "في تونس، الستيكة هي علبة من 6 قوارير ماء (12 للقوارير الصغيرة 50 صل)، وسعرها 6 أضعاف سعر القارورة."}},
            {"@type": "Question", "name": "من أين تأتي الأسعار؟", "acceptedAnswer": {"@type": "Answer", "text":
             "تُقرأ الأسعار آليًا كل يوم من المتاجر الإلكترونية للمغازات الكبرى في تونس (Géant Drive وCarrefour). هي أسعار تقريبية."}},
            {"@type": "Question", "name": "كم علامة ماء نقارن؟", "acceptedAnswer": {"@type": "Answer", "text":
             f"{nb} علامة ماء تُباع في تونس، مياه عادية وغازية، مع سعر القارورة والستيكة."}}]}]}
    return '<script type="application/ld+json">\n' + json.dumps(d, ensure_ascii=False, indent=2) + "\n</script>"


def accueil_ar(fr, nb_marques):
    """ar/index.html (avant finir()) à partir d'index.html. nb_marques = nombre de marques du jour (texte de la description)."""
    MANQUES.clear()
    ar = fr
    for a, b in ACCUEIL:
        if a in ar:
            ar = ar.replace(a, b)
        else:
            MANQUES.append(a[:70])
    desc = (f"مقارن مجاني لأسعار الماء المعدني في تونس: {nb_marques} علامة ({iso('Safia')}، {iso('Marwa')}، {iso('Sabrine')}…)، "
            f"القارورة والستيكة في {iso('Géant')} و{iso('Carrefour')}، تُحدَّث كل يوم.")
    ogd = f"قارن مجانًا أسعار {nb_marques} علامة ماء معدني (القارورة والستيكة) في {iso('Géant')} و{iso('Carrefour')}. تُحدَّث كل يوم."
    ar = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{H.escape(desc)}">', ar, count=1)
    ar = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{H.escape(ogd)}">', ar, count=1)
    ar = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: _jsonld_accueil_ar(nb_marques), ar, count=1, flags=re.S)
    # chiffres de la FAQ (remplacés au chargement par app.js) : déjà écrits à l'arabe pour Google
    ar = re.sub(r'(<span id="faq-[a-z-]+">)([^<]*)(</span>)',
                lambda m: m.group(1) + m.group(2).replace(" DT", " د.ت").replace(" et ", " و").replace(", ", "، ") + m.group(3), ar)
    # liste des pages des marques (fabriquée par build_pages.py entre <!--MARQUES--> et <!--/MARQUES-->)
    ar = re.sub(r'(<li><a href="marque/[^"]+/">)Prix eau ([^<]+)(</a></li>)', lambda m: f"{m.group(1)}سعر ماء {m.group(2)}{m.group(3)}", ar)
    # textes et données en arabe pour app.js (notes des marques…), chargé avant app.js
    ar = ar.replace('<script src="app.js', '<script src="assets/textes-ar.js?v=' + _version(fr) + '"></script>\n<script src="app.js', 1)
    return ar


def _version(fr):
    m = re.search(r'app\.js\?v=([0-9a-z]+)', fr)
    return m.group(1) if m else "1"
