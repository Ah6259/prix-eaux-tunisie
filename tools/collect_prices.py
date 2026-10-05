# -*- coding: utf-8 -*-
"""Collecte des prix des eaux minérales en Tunisie -> data/eaux.js + data/eaux.json

Remplace l'ancien trio geant_scrape.py / barka_scrape.py / build_data.py.
Repris du scraper du site jumeau « prix-eau-tunisie », adapté au format de données
de ce site (marques -> produits -> prix par enseigne).

Sources :
  - Carrefour Tunisie : API GraphQL (catégorie « Eaux ») — en direct
  - Géant Drive       : page catégorie « Eaux » (HTML PrestaShop) — en direct
  - Otrity            : épicerie en ligne, API WooCommerce — prix de la stika LIVRÉE (ajouté le 30/09/2026)
  - Barka.tn          : comparateur — N'EST PLUS UTILISÉ (fonction barka() gardée pour référence)
  (Monoprix retiré le 30/09/2026 : vérifié sur courses.monoprix.tn par Ahmed, barka.tn
   affichait en vente Safia/Marwa/Melina 1,5 L indisponibles et Sabrine 0,660 au lieu de 0,680 ;
   courses.monoprix.tn bloque les robots (403). Ne réintroduire qu'avec une source directe vérifiée.)
  (Aziza retiré le 30/09/2026 : barka.tn ne donne que les prix de l'ancienne boutique
   en ligne d'Aziza, fermée — prix périmés, ex. Bargou 0,590 au lieu de ~0,817 en magasin.
   Le site actuel d'Aziza ne publie que des catalogues promo, son API de prix est privée.)

Si une source est en panne, ses prix du dernier relevé réussi (data/eaux.json)
sont conservés au lieu de disparaître.

Usage : python tools/collect_prices.py
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
OUT_JS = ROOT / "data" / "eaux.js"
OUT_JSON = ROOT / "data" / "eaux.json"
IMG_CURATED = ROOT / "assets" / "img"          # photos choisies à la main (prioritaires)
IMG_AUTO = ROOT / "assets" / "img" / "produits"  # photos téléchargées des enseignes
# photos LIBRES (Open Food Facts, CC BY-SA...) pour les marques sans photo de magasin : dernier recours
PHOTOS_LIBRES = ROOT / "data" / "photos_libres.json"
RAW_DIR = ROOT / "tools" / "raw"
MAX_JOURS_REPRISE = 7   # une source en panne garde ses anciens prix 7 jours au plus

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"


def http_get(url, params=None, timeout=60):
    """GET via curl : les sites visés refusent python-requests (403 Carrefour,
    chaîne de certificats incomplète chez Géant) mais acceptent curl."""
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    cmd = ["curl", "-sSL", "--fail", "-A", UA, "-H", "Accept-Language: fr-FR,fr;q=0.9",
           "--max-time", str(timeout), url]
    r = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
    if r.returncode == 60:
        # chaîne de certificats incomplète (Géant, sur les serveurs GitHub) : on réessaie
        # sans vérification — acceptable ici, on ne fait que lire des prix publics
        r = subprocess.run(cmd[:1] + ["-k"] + cmd[1:], capture_output=True, timeout=timeout + 10)
    if r.returncode:
        raise RuntimeError(f"curl {r.returncode} {url}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


# Marques d'eau embouteillée connues sur le marché tunisien
MARQUES_EAU = {
    "AQUALINE", "AZIZ", "BARGOU", "BEYA", "BRIMA", "BULLA REGIA", "CRISTALINE", "DELICE", "DENYA",
    "DIMA", "ELIXIR", "FOURAT", "GARCI", "HAYET", "JANNET", "JEKTISS", "MAIN", "MARWA",
    "MAY", "MELINA", "MELLITI", "MIRA", "OKTOR", "PALMA", "PRIMAQUA", "PRISTINE", "RAYAN",
    "RIM", "ROYAL", "SABRINE", "SAFIA", "SAHA", "TIBA", "TIJEN", "VIVIAN",
}

# Orthographes différentes d'une même marque selon les enseignes
ALIAS_MARQUES = {
    "PRESTINE": "PRISTINE",
    "TIGEN": "TIJEN",
    "JEKTIS": "JEKTISS",
    "MAY TUNISIA": "MAY",
    "SAFIA AIN MIZEB": "SAFIA",
    "ROYAL BLEU": "ROYAL",
    "ROYAL_BLEU": "ROYAL",
    "ROYALE": "ROYAL",
}

# Fiche de chaque marque (affichée sur les cartes du site).
# « depuis » = date d'autorisation / de commercialisation d'après les fiches officielles
# de l'Office National du Thermalisme (hydrotherapie.tn) ; None quand non vérifiable.
META = {
    "SAFIA":     {"name": "Safia", "company": "SFBT (Sostem)", "source": "Aïn Mizeb & Aïn Ksiba, El Ksour (Le Kef)", "depuis": 1968, "note": "Marque historique d'eau plate en Tunisie (2e source autorisée en 1989)."},
    "SABRINE":   {"name": "Sabrine", "company": "Sabrine SA", "source": "Oued Kharroub, Chébika (Kairouan)", "depuis": 1990, "note": "Première eau certifiée ISO 22000 en Tunisie."},
    "MARWA":     {"name": "Marwa", "company": "Eaux Minérales Marwa", "source": "Kef Ghrab, Joumine (Bizerte)", "depuis": 1994, "note": None},
    "MELLITI":   {"name": "Melliti", "company": "SFBT (Sostem)", "source": "Aïn El Beidha, Téboursouk (Béja)", "depuis": 1977, "note": None},
    "GARCI":     {"name": "Garci", "company": "SFBT (Sostem)", "source": "Aïn Garci, Enfidha (Sousse)", "depuis": 1968, "note": "La plus ancienne eau gazeuse naturelle de Tunisie (source exploitée dès 1900)."},
    "OKTOR":     {"name": "Aïn Oktor", "company": None, "source": "Korbous, Soliman (Nabeul)", "depuis": 1963, "note": "Eau minérale naturelle gazeuse (source exploitée dès 1904).", "types": ["gazeuse"]},
    "CRISTALINE":{"name": "Cristaline", "company": None, "source": "Mogren (Zaghouan)", "depuis": 2002, "note": None},
    "FOURAT":    {"name": "Fourat", "company": None, "source": "Oueslatia (Kairouan)", "depuis": 2001, "note": None},
    "DIMA":      {"name": "Dima", "company": None, "source": "Tajerouine (Le Kef)", "depuis": 2009, "note": None},
    "MIRA":      {"name": "Mira", "company": None, "source": "Hajeb El Ayoun (Kairouan)", "depuis": 2018, "note": None},
    "PRISTINE":  {"name": "Pristine", "company": None, "source": "Henchir Kefia (Zaghouan)", "depuis": 2017, "note": None},
    "MAY":       {"name": "May", "company": None, "source": "Le Krib (Siliana)", "depuis": 2011, "note": None},
    "JANNET":    {"name": "Jannet", "company": None, "source": "Haffouz (Kairouan)", "depuis": 2002, "note": None},
    "JEKTISS":   {"name": "Jektiss", "company": None, "source": "Koutine (Médenine)", "depuis": 1989, "note": "Eau de table (traitée par osmose inverse)."},
    "MELINA":    {"name": "Melina", "company": None, "source": "Bargou (Siliana)", "depuis": 2007, "note": None},
    "AQUALINE":  {"name": "Aqualine", "company": None, "source": "Mogren (Zaghouan)", "depuis": 2009, "note": None},
    "BARGOU":    {"name": "Bargou", "company": None, "source": "Bargou (Siliana)", "depuis": 2015, "note": None},
    "RAYAN":     {"name": "Rayan", "company": None, "source": "Nefza (Béja)", "depuis": 2011, "note": "Devenue Élixir en 2015."},
    "ELIXIR":    {"name": "Élixir", "company": None, "source": "Nefza (Béja)", "depuis": 2015, "note": "Ex-Rayan (2011)."},
    "PRIMAQUA":  {"name": "Primaqua", "company": None, "source": "Koutine (Médenine)", "depuis": 2007, "note": "Eau de table (osmose inverse), grands formats et bonbonnes."},
    "DELICE":    {"name": "Délice", "company": "Groupe Délice", "source": "Jelma (Sidi Bouzid)", "depuis": 2020, "note": "Eau de source Délice."},
    "BEYA":      {"name": "Beya", "company": None, "source": "Cherichira, Haffouz (Kairouan)", "depuis": 2020, "note": "Eau de source naturelle."},
    "TIJEN":     {"name": "Tijen", "company": None, "source": "Labiadh (Sidi Bouzid)", "depuis": 2018, "note": None},
    "HAYET":     {"name": "Hayet", "company": None, "source": "Jelma (Sidi Bouzid)", "depuis": 1996, "note": None},
    "BULLA REGIA": {"name": "Bulla Régia", "company": None, "source": "Aïn Ghenaa (Jendouba)", "depuis": 1999, "note": "Eau de table, ex-Zullel."},
    "ROYAL":     {"name": "Royal", "company": "Royal Drinks", "source": "Aïn Sokra, Siliana sud", "depuis": 2016, "note": "Ex-Cristal."},
    "SAHA":      {"name": "Saha", "company": None, "source": "El Fahs (Zaghouan)", "depuis": 2017, "note": "Eau de table."},
    "TIBA":      {"name": "Tiba", "company": "Tiba Eaux Minérales", "source": "Tlebt (Kasserine)", "depuis": None, "note": None},
    "AZIZ":      {"name": "Aziz", "company": None, "source": "Le Krib (Siliana)", "depuis": None, "note": None},
    "BRIMA":     {"name": "Brima", "company": None, "source": None, "depuis": None, "note": None},
    "MAIN":      {"name": "Maïn", "company": None, "source": "Tataouine nord", "depuis": 2004, "note": None},
    "DENYA":     {"name": "Denya", "company": None, "source": "Hajeb El Ayoun (Kairouan)", "depuis": 2018, "note": None},
    "PALMA":     {"name": "Palma", "company": None, "source": "Sidi Aïch (Gafsa)", "depuis": 2011, "note": None},
    "VIVIAN":    {"name": "Vivian", "company": None, "source": "ex-Övia, Zaghouan", "depuis": 2011, "note": None},
    "RIM":       {"name": "Rim", "company": None, "source": None, "depuis": None, "note": None},
}

ENSEIGNES = {"carrefour": "Carrefour", "geant": "Géant", "otrity": "Otrity", "monoprix": "Monoprix", "aziza": "Aziza"}

# id de marque -> préfixe des photos choisies à la main dans assets/img
IMG_STEMS = {
    "safia": "safia", "sabrine": "sabrine", "marwa": "marwa", "melliti": "melliti",
    "garci": "garci", "ain-oktor": "oktor", "cristaline": "cristaline", "fourat": "fourat",
    "dima": "dima", "mira": "mira", "pristine": "pristine", "may": "may_tunisia",
    "jannet": "jannet", "jektiss": "jektiss", "melina": "melina", "aqualine": "aqualine",
    "bargou": "bargou", "rayan": "rayan", "elixir": "elixir", "primaqua": "primaqua",
    "delice": "delice", "beya": "beya", "tijen": "tijen",
}


# ---------------------------------------------------------------- utilitaires
def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", sans_accents(s).lower()).strip("-")


def norm_marque(s):
    s = sans_accents(html.unescape(s or "")).upper().strip()
    s = re.sub(r"\s+", " ", s)
    return ALIAS_MARQUES.get(s, s)


def parse_prix(s):
    """'0,640 DT' / '0.64 dt' / 0.64 -> 0.64"""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r"\d+(?:[.,]\d+)?", s.replace(" ", ""))
    return float(m.group().replace(",", ".")) if m else None


def parse_volume(*textes):
    """Cherche un volume (en litres) et un nombre d'unités dans les textes.
    Retourne (volume_litres, nb_unites) ; ex. 'Pack 6x1.5L' -> (1.5, 6)."""
    t = " ".join(sans_accents(html.unescape(x or "")) for x in textes).upper()
    t = t.replace(",", ".")
    nb = 1
    m = re.search(r"(\d+)\s*[X×]\s*(\d+(?:\.\d+)?)\s*(CL|ML|L)\b", t)
    if m:
        nb = int(m.group(1))
        v, u = float(m.group(2)), m.group(3)
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(CL|ML|L|LITRES?)\b", t)
        if not m:
            return None, nb
        v, u = float(m.group(1)), m.group(2)
        m2 = re.search(r"(?:PACK|LOT)\s*(?:DE\s*)?(\d+)|(\d+)\s*X\b|\bX\s*(\d+)\b", t)
        if m2:
            nb = int(next(g for g in m2.groups() if g))
    if u == "CL":
        v /= 100
    elif u == "ML":
        v /= 1000
    return round(v, 3), nb


def type_eau(*textes):
    t = sans_accents(" ".join(x or "" for x in textes)).lower()
    return "gazeuse" if re.search(r"gaz|petillant", t) else "plate"


def trouver_marque(marque, nom=""):
    """Marque normalisée si c'est une marque d'eau connue, sinon None.
    Si le champ marque est vide/générique, on la cherche dans le nom."""
    m = norm_marque(marque)
    if m in MARQUES_EAU:
        return m
    n = norm_marque(nom)
    for x in sorted(MARQUES_EAU, key=len, reverse=True):
        if re.search(rf"\b{x}\b", n):
            return x
    return None


def est_eau(nom, marque=""):
    t = sans_accents(f"{nom}").lower()
    if not re.search(r"\beaux?\b", t) and "primaqua" not in sans_accents(marque).lower():
        return False
    exclus = (r"verre|service|carafe|pichet|distributeur|geranium|senteur|aromatis|atomiseur|demineralis|bouillotte|micellaire"
              r"|fruit|citron|poire|pomme|peche|menthe|fraise|ananas|deli.?o|^consigne|avec consigne")
    return not re.search(exclus, t) and trouver_marque(marque, nom) is not None


def fmt_affiche(litres):
    return f"{int(round(litres * 1000))} ml" if litres < 1 else f"{litres:g} L"


def telecharger_image(url):
    if not url:
        return None
    ext = Path(url.split("?")[0]).suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    nom = hashlib.md5(url.encode()).hexdigest()[:12] + ext
    dest = IMG_AUTO / nom
    if not dest.exists():
        try:
            dest.write_bytes(http_get(url, timeout=30))
        except Exception as e:
            print(f"  ! image {url}: {e}", file=sys.stderr)
            return None
    return f"assets/img/produits/{nom}"


# ---------------------------------------------------------------- Carrefour
def carrefour():
    q = """{products(filter:{category_uid:{eq:"Mzc1Nw=="}},pageSize:200){items{
        name sku url_key short_description{html}
        small_image{url}
        price_range{minimum_price{final_price{value} regular_price{value}}}}}}"""
    q = re.sub(r"\s+", " ", q)  # le pare-feu de Carrefour rejette les requêtes multi-lignes
    items = json.loads(http_get("https://www.carrefour.tn/graphql", {"query": q}))["data"]["products"]["items"]
    (RAW_DIR / "carrefour.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    out = []
    for it in items:
        nom = it["name"].strip()
        desc = re.sub(r"<[^>]+>", " ", it["short_description"]["html"] or "")
        m = re.search(r"(?:minerale|gazeifiee|source)\s+(.+?)(?:\s+\d.*)?$", sans_accents(nom), re.I)
        marque = m.group(1) if m else nom
        marque = trouver_marque(re.sub(r"\b(avec|sans) consigne\b", "", marque, flags=re.I), nom)
        if not marque or not est_eau(nom, marque):
            continue
        vol, nb = parse_volume(nom, desc)
        out.append({
            "enseigne": "carrefour", "marque": marque, "nom": nom,
            "volume_l": vol, "nb_unites": nb, "type": type_eau(nom, desc),
            "prix": it["price_range"]["minimum_price"]["final_price"]["value"],
            "image_src": it["small_image"]["url"],
        })
    return out


# ---------------------------------------------------------------- Géant
def geant():
    h = http_get("https://www.geantdrive.tn/tunis-city/11-eaux?resultsPerPage=100").decode("utf-8", errors="replace")
    (RAW_DIR / "geant.html").write_text(h, encoding="utf-8")
    out = []
    for bloc in h.split('<article class="product-miniature')[1:]:
        g = lambda pat: (re.search(pat, bloc, re.S) or [None, None])[1]
        nom = html.unescape(g(r'itemprop="name"><a[^>]*>([^<]+)</a>') or "").strip()
        marque = html.unescape(g(r'class="manufacturer_product[^"]*">\s*([^<]+?)\s*</p>') or "")
        desc = re.sub(r"<[^>]+>", " ", g(r'itemprop="description"[^>]*>(.*?)</div>') or "")
        desc = html.unescape(re.sub(r"\s+", " ", desc)).strip()
        prix = parse_prix(g(r'class="price">([^<]+)<'))
        if not nom or prix is None or not est_eau(nom, marque):
            continue
        vol, nb = parse_volume(nom, desc)
        out.append({
            "enseigne": "geant", "marque": trouver_marque(marque, nom), "nom": nom,
            "volume_l": vol, "nb_unites": nb, "type": type_eau(nom, desc),
            "prix": prix,
            "image_src": g(r'data-full-size-image-url="([^"]+)"') or g(r'<img[^>]+src="([^"]+)"'),
        })
    return out


# ---------------------------------------------------------------- Otrity
def otrity():
    """otrity.com : épicerie en ligne (livraison le jour même), WooCommerce.
    API publique « Store API », catégorie Eaux = 1261. Les prix affichés sont ceux
    de la STIKA LIVRÉE (le conditionnement n'est pas écrit : « Safia 1.5L » à 5,000 DT) ;
    on les ramène au prix par bouteille (÷ 6, ou ÷ 12 pour ≤ 0,75 L) comme les autres
    enseignes. Les incohérences (ex. une bouteille vendue à l'unité) sont écartées
    ensuite par les garde-fous de prix au litre."""
    items = json.loads(http_get("https://otrity.com/wp-json/wc/store/v1/products",
                                {"category": 1261, "per_page": 100}))
    (RAW_DIR / "otrity.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    out = []
    for it in items:
        nom = html.unescape(it.get("name") or "").strip()
        desc = html.unescape(re.sub(r"<[^>]+>", " ", it.get("short_description") or ""))
        marque = trouver_marque("", nom)
        if not it.get("is_in_stock") or not marque or not est_eau(nom, marque):
            continue
        vol, _ = parse_volume(nom)
        pr = it.get("prices") or {}
        if not vol or not pr.get("price"):
            continue
        prix_pack = int(pr["price"]) / 10 ** int(pr.get("currency_minor_unit", 0))
        n = 12 if vol <= 0.75 else 6 if vol <= 2.5 else 1
        t = sans_accents(f"{nom} {desc}").lower()
        typ = "gazeuse" if re.search(r"gazeuse|gazeifiee|petillant", t) and not re.search(r"non gaz|plate", t) else "plate"
        out.append({
            "enseigne": "otrity", "marque": marque, "nom": nom,
            "volume_l": vol, "nb_unites": 1, "type": typ,
            "prix": round(prix_pack / n, 4),   # 4 décimales : 6 × 0,8333 = 5,000 (et non 4,998)
            "image_src": ((it.get("images") or [{}])[0]).get("src"),
        })
    return out


# ---------------------------------------------------------------- Barka (Monoprix)
def barka(requetes=("eau minerale", "eau gazeuse", "eau de source"), max_pages=40):
    vus, out, brut = set(), [], []

    def ajouter(bp):
        shop = sans_accents(bp.get("shop_name") or "").lower()
        prix = parse_prix(bp.get("product_price"))
        nom, marque = (bp.get("name") or "").strip(), bp.get("brand") or ""
        taille = " ".join(bp.get("size") or [])
        if shop != "monoprix":   # Aziza exclu : prix périmés (voir en tête)
            return
        # les packs/fardeaux sont écartés : le site affiche la stika comme 6 × la bouteille
        if re.search(r"fardeau|\blot\b|\bpack\b|\d\s*[x×*]\s*\d", sans_accents(f"{nom} {taille}").lower()):
            return
        if not prix or not est_eau(nom, marque):
            return
        cle = (shop, bp.get("_id") or bp.get("product_url"))
        if cle in vus:
            return
        vus.add(cle)
        vol, nb = parse_volume(taille, nom, bp.get("description") or "")
        out.append({
            "enseigne": shop, "marque": trouver_marque(marque, nom), "nom": nom,
            "volume_l": vol, "nb_unites": nb, "type": type_eau(nom, bp.get("category") or ""),
            "prix": prix,
            "image_src": bp.get("imageSrc"),
        })

    recherches = [(q, max_pages) for q in requetes] + [(f"eau {m.lower()}", 2) for m in sorted(MARQUES_EAU)]
    for q, n_pages in recherches:
        token, pages_sans_eau = None, 0
        for _ in range(n_pages):
            d = json.loads(http_get("https://barka.tn/api/search", {"q": q, "per_page": 20, "searchAfter": token}))
            brut.extend(d.get("products", []))
            eau_sur_page = False
            for p in d.get("products", []):
                bp = p["base_product"]
                if est_eau(bp.get("name") or "", bp.get("brand") or ""):
                    eau_sur_page = True
                for x in [bp] + (p.get("matches") or []):
                    ajouter(x)
            token = (d.get("meta") or {}).get("nextPageToken")
            pages_sans_eau = 0 if eau_sur_page else pages_sans_eau + 1
            if not token or pages_sans_eau >= 3:
                break
            time.sleep(0.5)
    (RAW_DIR / "barka.json").write_text(json.dumps(brut, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ---------------------------------------------------------------- images choisies à la main
def images_curated():
    """{préfixe de nom de fichier -> chemin} des photos de assets/img (hors produits/)."""
    return {f.stem: f for f in IMG_CURATED.glob("*.jpg")}


def find_img_curated(imgs, brand_id, litres):
    stem_prefix = IMG_STEMS.get(brand_id, brand_id).replace("-", "_")
    lit_tag = None
    if litres:
        lit_tag = ("%g" % litres).replace(".", "") + "l" if litres >= 1 else ("0" + ("%g" % litres).replace(".", "") + "l")
    cands = []
    for stem in imgs:
        if not stem.startswith(stem_prefix):
            continue
        score = 3 if (lit_tag and lit_tag in stem.replace("95l", "095l")) else 0
        cands.append((score, stem))
    if not cands:
        return None
    cands.sort(reverse=True)
    return "assets/img/" + cands[0][1] + ".jpg"


def appliquer_photos_libres(brands):
    """Marques SANS photo (ni choisie à la main, ni d'enseigne) : photo libre de data/photos_libres.json,
    avec son crédit (img_credit). Une photo de magasin, si elle existe, reste toujours prioritaire."""
    try:
        libres = json.loads(PHOTOS_LIBRES.read_text(encoding="utf-8")).get("photos", {})
    except (OSError, ValueError):
        return
    racine = PHOTOS_LIBRES.parent.parent
    for b in brands:
        b.pop("img_credit", None)
        if (b.get("img") or "").startswith("assets/img/libres/"):  # déjà appliquée : on la réévalue
            b["img"] = None
        ph = libres.get(b["id"])
        if b.get("img") or not ph or not (racine / ph["img"]).exists():
            continue
        b["img"] = ph["img"]
        b["img_credit"] = {k: ph[k] for k in ("credit", "source", "page", "licence", "licence_url")}


# ---------------------------------------------------------------- reprise en cas de panne
def anciennes_offres(ancien, enseignes_cibles):
    """Offres des enseignes données, reconstruites depuis un eaux.json précédent."""
    inv = {v: k for k, v in ENSEIGNES.items()}
    out = []
    for b in ancien.get("brands", []):
        marque = next((k for k, m in META.items() if m["name"] == b["name"]), norm_marque(b["name"]))
        for p in b["products"]:
            for store, prix in p["prices"].items():
                ens = inv.get(store)
                if ens in enseignes_cibles:
                    out.append({
                        "enseigne": ens, "marque": marque, "nom": f"{b['name']} {p['format']}",
                        "volume_l": p["liters"], "nb_unites": 1, "type": p["category"],
                        "prix": prix, "image_src": None, "image_locale": p.get("img"),
                    })
    return out


# ---------------------------------------------------------------- assemblage
def main():
    IMG_AUTO.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    ancien = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else None
    aujourdhui = date.today()
    # État de chaque source : date du dernier relevé réussi + nombre d'offres trouvées.
    # (au premier passage, on suppose que le relevé précédent était réussi)
    statut = dict((ancien or {}).get("statut_sources") or {})
    if ancien and not statut:
        statut = {k: {"dernier_ok": ancien.get("updated"), "nb": 0} for k in ("carrefour", "geant", "otrity")}
    offres = []
    sources = (("Carrefour", carrefour, "carrefour"), ("Géant", geant, "geant"),
               ("Otrity", otrity, "otrity"))
    for nom, f, cle_src in sources:
        prec = statut.get(cle_src) or {}
        try:
            res = f()
            if not res:
                raise RuntimeError("aucune offre trouvée")
            # site modifié : prix écrits autrement (millimes…), marques méconnaissables…
            valides = [o for o in res if o.get("marque") and o.get("volume_l") and o.get("prix")
                       and 0.25 <= o["prix"] / (o["volume_l"] * (o.get("nb_unites") or 1)) <= 2.5]
            if len(valides) < 0.5 * len(res):
                raise RuntimeError(f"données incohérentes : seulement {len(valides)} offres "
                                   f"plausibles sur {len(res)}")
            # site modifié qui ne renvoie plus qu'une partie des produits : on ne s'y fie pas
            if prec.get("nb") and len(res) < 0.3 * prec["nb"]:
                raise RuntimeError(f"résultat suspect : {len(res)} offres contre {prec['nb']} au dernier relevé réussi")
            print(f"{nom}: {len(res)} offres")
            offres += res
            statut[cle_src] = {"dernier_ok": aujourdhui.isoformat(), "nb": len(res)}
        except Exception as e:
            print(f"! {nom} en échec : {e}", file=sys.stderr)
            if cle_src == "otrity":
                # bloqué par Cloudflare sur GitHub : relevé fait depuis le PC d'Ahmed
                # (tools/otrity_local.py), utilisé seulement s'il a 3 jours ou moins
                fichier = ROOT / "data" / "otrity.json"
                if fichier.exists():
                    rel = json.loads(fichier.read_text(encoding="utf-8"))
                    age = (aujourdhui - date.fromisoformat(rel["date"])).days
                    if age <= 3 and rel.get("offres"):
                        print(f"  -> relevé local du {rel['date']} : {len(rel['offres'])} offres")
                        offres += rel["offres"]
                        statut[cle_src] = {"dernier_ok": rel["date"], "nb": len(rel["offres"])}
                    else:
                        print(f"  -> relevé local du {rel['date']} trop ancien ({age} j) : ignoré")
                continue
            # Source en panne : on reprend ses prix du dernier relevé réussi, mais JAMAIS
            # plus de MAX_JOURS_REPRISE jours (au-delà, ses prix disparaissent du site)
            dernier = prec.get("dernier_ok")
            age = (aujourdhui - date.fromisoformat(dernier)).days if dernier else None
            if ancien and age is not None and age <= MAX_JOURS_REPRISE:
                repris = anciennes_offres(ancien, {cle_src})
                print(f"  -> reprise de {len(repris)} offres du relevé du {dernier} ({age} j)")
                offres += repris
            else:
                print(f"  -> dernier relevé réussi : {dernier or 'jamais'} — prix {nom} retirés du site")
    # Même si TOUTES les sources échouent, on écrit le fichier : les prix trop vieux
    # disparaissent et le site affiche un avertissement (voir statut_sources dans app.js)

    # Regroupe les offres bouteille (les packs sont écartés) par marque + type + volume
    produits = {}
    for o in offres:
        if not o["marque"] or o["volume_l"] is None or o["nb_unites"] != 1:
            continue
        cle = (o["marque"], o["type"], o["volume_l"])
        p = produits.setdefault(cle, {"offres": {}, "images": {}})
        cur = p["offres"].get(o["enseigne"])
        if cur is None or o["prix"] < cur:
            p["offres"][o["enseigne"]] = o["prix"]
            if o.get("image_src"):
                p["images"][o["enseigne"]] = o["image_src"]
            elif o.get("image_locale"):
                p["images"].setdefault("locale", o["image_locale"])

    # Prix aberrants (packs vendus comme bouteilles unitaires, erreurs de saisie)
    PRIX_LITRE_MIN, PRIX_LITRE_MAX = 0.25, 2.5
    for cle, p in list(produits.items()):
        litres = cle[2]
        ok = {e: v for e, v in p["offres"].items() if PRIX_LITRE_MIN <= v / litres <= PRIX_LITRE_MAX}
        if ok:
            mini = min(ok.values())
            ok = {e: v for e, v in ok.items() if v <= 2 * mini}
        for e, v in p["offres"].items():
            if e not in ok:
                print(f"  ? prix aberrant écarté : {e} {cle[0]} {litres}L {v} DT")
        if ok:
            p["offres"] = ok
        else:
            del produits[cle]

    # Construit les marques au format du site
    imgs = images_curated()
    brands = {}
    for (marque, typ, litres), p in sorted(produits.items()):
        meta = META.get(marque) or {"name": marque.title(), "company": None, "source": None, "depuis": None, "note": None}
        b = brands.setdefault(meta["name"], {
            "id": slug(meta["name"]), "name": meta["name"],
            "company": meta["company"], "source": meta["source"],
            "depuis": meta.get("depuis"), "note": meta["note"],
            "img": None, "types": [], "products": [],
        })
        img = find_img_curated(imgs, b["id"], litres)
        if not img:  # pas de photo choisie à la main : celle de l'enseigne (Carrefour d'abord)
            for e in ("carrefour", "geant", "otrity"):
                if p["images"].get(e):
                    img = telecharger_image(p["images"][e])
                    if img:
                        break
        if not img and p["images"].get("locale") and (ROOT / p["images"]["locale"]).exists():
            img = p["images"]["locale"]
        b["products"].append({
            "liters": litres, "format": fmt_affiche(litres), "category": typ, "flavor": None,
            "img": img,
            "prices": {ENSEIGNES[e]: round(v, 4) for e, v in sorted(p["offres"].items(), key=lambda x: x[1])},
        })

    out_brands = []
    for name in sorted(brands):
        b = brands[name]
        b["types"] = sorted({p["category"] for p in b["products"]})
        b["img"] = next((p["img"] for p in b["products"] if p["img"] and abs(p["liters"] - 1.5) < .01 and p["category"] == "plate"),
                        next((p["img"] for p in b["products"] if p["img"]), None))
        out_brands.append(b)

    # Marques connues du marché tunisien sans prix relevé aujourd'hui :
    # affichées quand même sur le site (composition + « prix non disponible »)
    deja = {b["name"] for b in out_brands}
    for meta in META.values():
        if meta["name"] in deja:
            continue
        bid = slug(meta["name"])
        out_brands.append({
            "id": bid, "name": meta["name"],
            "company": meta["company"], "source": meta["source"],
            "depuis": meta.get("depuis"), "note": meta["note"],
            "img": find_img_curated(imgs, bid, None),
            "types": meta.get("types", ["plate"]),
            "products": [],
        })
    out_brands.sort(key=lambda b: b["name"])
    appliquer_photos_libres(out_brands)

    data = {
        "updated": date.today().isoformat(),
        "currency": "DT",
        "stores": ["Carrefour", "Géant", "Otrity"],
        "sources": [
            {"name": "Carrefour Tunisie", "url": "https://www.carrefour.tn"},
            {"name": "Géant Drive Tunisie", "url": "https://www.geantdrive.tn"},
            {"name": "Otrity (épicerie en ligne, livraison)", "url": "https://otrity.com/categorie-produit/boissons/eaux/"},
            {"name": "Wikipédia — Eaux minérales en Tunisie", "url": "https://fr.wikipedia.org/wiki/Eaux_min%C3%A9rales_en_Tunisie"},
        ],
        "brands": out_brands,
        "statut_sources": statut,
    }

    OUT_JS.write_text("window.EAUX_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    n_prod = sum(len(b["products"]) for b in out_brands)
    n_off = sum(len(p["prices"]) for b in out_brands for p in b["products"])
    print(f"\nmarques: {len(out_brands)} | produits: {n_prod} | offres prix: {n_off} -> {OUT_JSON}")
    for b in out_brands:
        print(f"  {b['name']:14} {len(b['products'])} produits, img={'oui' if b['img'] else 'NON'}")


if __name__ == "__main__":
    main()
