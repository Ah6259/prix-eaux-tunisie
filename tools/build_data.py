# -*- coding: utf-8 -*-
"""Consolide tools/geant_products.json + tools/barka_products.json en data/eaux.js.

Ordre de mise à jour : 1) python geant_scrape.py  2) python barka_scrape.py  3) python build_data.py"""
import json, re, shutil, pathlib, unicodedata

SCRATCH = pathlib.Path(__file__).parent
PROJECT = SCRATCH.parent
IMG_SRC = PROJECT / "assets" / "img"
IMG_DST = IMG_SRC

META = {
    "SAFIA":     {"name": "Safia", "company": "SFBT (Sostem)", "source": "Aïn Mizeb & Aïn Ksiba, El Ksour (Le Kef)", "note": "Marque historique d'eau plate en Tunisie."},
    "SABRINE":   {"name": "Sabrine", "company": "Sabrine SA", "source": "Oued Kharroub, Chebika (Kairouan)", "note": "Commercialisée depuis 1991, première eau certifiée ISO 22000 en Tunisie."},
    "MARWA":     {"name": "Marwa", "company": "Eaux Minérales Marwa", "source": "Kef Ghrab, Joumine (Bizerte)", "note": "Commercialisée depuis 1993."},
    "MELLITI":   {"name": "Melliti", "company": "SFBT (Sostem)", "source": "Aïn El Beidha, Téboursouk (Béja)", "note": None},
    "GARCI":     {"name": "Garci", "company": "SFBT (Sostem)", "source": "Aïn Garci, Enfidha (Sousse)", "note": "La plus ancienne eau gazeuse naturelle de Tunisie."},
    "OKTOR":     {"name": "Aïn Oktor", "company": None, "source": "Korbous (Cap Bon)", "note": "Eau minérale naturelle gazeuse."},
    "CRISTALINE":{"name": "Cristaline", "company": None, "source": None, "note": None},
    "FOURAT":    {"name": "Fourat", "company": None, "source": None, "note": None},
    "DIMA":      {"name": "Dima", "company": None, "source": None, "note": None},
    "MIRA":      {"name": "Mira", "company": None, "source": None, "note": None},
    "PRISTINE":  {"name": "Pristine", "company": None, "source": None, "note": None},
    "MAY TUNISIA":{"name": "May", "company": None, "source": None, "note": None},
    "JANNET":    {"name": "Jannet", "company": None, "source": None, "note": None},
    "JEKTISS":   {"name": "Jektiss", "company": None, "source": None, "note": None},
    "MELINA":    {"name": "Melina", "company": None, "source": None, "note": None},
    "AQUALINE":  {"name": "Aqualine", "company": None, "source": None, "note": None},
    "BARGOU":    {"name": "Bargou", "company": None, "source": "Bargou (Siliana)", "note": "Lancée en 2015."},
    "RAYAN":     {"name": "Rayan", "company": None, "source": None, "note": None},
    "ELIXIR":    {"name": "Élixir", "company": None, "source": None, "note": None},
    "PRIMAQUA":  {"name": "Primaqua", "company": None, "source": None, "note": "Eau de table, grands formats et bonbonnes."},
    "DELICE":    {"name": "Délice", "company": "Groupe Délice", "source": None, "note": "Eau de source Délice ; gamme gazeuse aromatisée Deli'O."},
    "DELICE DELI'O": {"name": "Délice", "company": "Groupe Délice", "source": None, "note": None},
    "BEYA":      {"name": "Beya", "company": None, "source": None, "note": "Eau de source naturelle."},
    "TIJEN":     {"name": "Tijen", "company": None, "source": None, "note": None},
}
GAZEUSES = {"GARCI", "OKTOR"}  # brands whose main line is sparkling (Garci also has flat)

def norm_price(s):
    if not s: return None
    s = s.lower().replace("dt", "").replace("tnd", "").strip().replace(",", ".")
    try:
        v = round(float(s), 3)
        return v if v > 0 else None
    except ValueError:
        return None

def parse_format(*texts):
    """Return (liters, display) parsed from free text."""
    blob = " ".join(t or "" for t in texts)
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ml|ML)", blob)
    if m:
        v = float(m.group(1).replace(",", "."))
        return v / 1000.0, f"{int(v)} ml"
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:l|L|litres?)", blob)
    if m:
        v = float(m.group(1).replace(",", "."))
        disp = f"{v:g} L"
        return v, disp
    return None, None

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

geant = json.load(open(SCRATCH / "geant_products.json", encoding="utf-8"))
_barka_all = json.load(open(SCRATCH / "barka_products.json", encoding="utf-8"))
# ne garder que les offres "eau" (les marques comme Délice ou Cristal vendent aussi d'autres produits)
barka = [r for r in _barka_all
         if re.search(r"\beau|eaux|water|gaz[eé]", " ".join(str(r.get(k, "")) for k in ("name", "description", "category")).lower())]

brands = {}  # key -> brand dict
def get_brand(key):
    meta = META.get(key)
    if not meta: return None
    name = meta["name"]
    b = brands.get(name)
    if not b:
        b = brands[name] = {
            "id": slug(name), "name": name,
            "company": meta["company"], "source": meta["source"], "note": meta["note"],
            "products": {},
        }
    # keep richest metadata
    for k in ("company", "source", "note"):
        if not b[k] and meta[k]: b[k] = meta[k]
    return b

def add_offer(brand_key, liters, disp, category, store, price, flavor=None):
    b = get_brand(brand_key)
    if not b or price is None or liters is None: return
    pkey = (liters, category, flavor or "")
    p = b["products"].get(pkey)
    if not p:
        p = b["products"][pkey] = {"liters": liters, "format": disp, "category": category,
                                   "flavor": flavor, "img": None, "prices": {}}
    # keep the lowest price seen per store
    cur = p["prices"].get(store)
    if cur is None or price < cur:
        p["prices"][store] = price

# --- Géant direct scrape (authoritative for Géant) ---
for g in geant:
    key = g["brand"]
    if not key or key not in META: continue
    price = norm_price(g["price_dt"])
    fmt_txt = g["format"] or ""
    flavor = None
    if key == "DELICE DELI'O":
        flavor = fmt_txt.replace("250ML", "").strip() or None
        if flavor: flavor = flavor.capitalize()
    if "consigne" in fmt_txt.lower():  # bonbonne + consigne = même produit, prix différent
        continue
    liters, disp = parse_format(fmt_txt)
    category = "gazeuse" if g["category"] == "gazeuse" else "plate"
    if key in GAZEUSES and g["category"] == "gazeuse": category = "gazeuse"
    add_offer(key, liters, disp, category, "Géant", price, flavor)

GEANT_DIRECT_BRANDS = {g["brand"] for g in geant if g["brand"]}

# --- barka.tn (Carrefour / Monoprix / Aziza; skip its Géant rows, we have fresher) ---
for r in barka:
    key = r["brand_query"]
    if key not in META: continue
    store = r.get("store")
    if store is None:
        continue
    # skip barka's Géant rows when the brand is already covered by the fresher direct Géant scrape
    if "ant" in store:
        if key in GEANT_DIRECT_BRANDS:
            continue
        store = "Géant"
    price = norm_price(r.get("price"))
    blob = f"{r.get('name','')} {r.get('description','')}"
    if re.search(r"pack|x6|6x|fardeau", blob, re.I): continue
    liters, disp = parse_format(r.get("description"), r.get("name"))
    category = "gazeuse" if (key in GAZEUSES or re.search(r"gaz", blob, re.I)) else "plate"
    add_offer(key, liters, disp, category, store, price)

# --- attach local images ---
img_map = {}
for f in IMG_SRC.glob("*.jpg"):
    img_map[f.stem] = f
def find_img(brand_id, liters, flavor):
    cands = []
    lit_tag = None
    if liters:
        lit_tag = ("%g" % liters).replace(".", "") + "l" if liters >= 1 else ("0" + ("%g" % liters).replace(".", "") + "l")
    for stem, f in img_map.items():
        parts = stem.split("_")
        bslug = slug(META_NAME_TO_STEM.get(brand_id, brand_id)).replace("-", "_")
        if not stem.startswith(bslug): continue
        score = 0
        if flavor and slug(flavor) in stem: score += 5
        if lit_tag and lit_tag in stem.replace("95l","095l"): score += 3
        cands.append((score, stem, f))
    if not cands: return None
    cands.sort(reverse=True)
    return cands[0][1] + ".jpg", cands[0][2]

META_NAME_TO_STEM = {  # brand id -> image filename prefix
    "safia": "safia", "sabrine": "sabrine", "marwa": "marwa", "melliti": "melliti",
    "garci": "garci", "ain-oktor": "oktor", "cristaline": "cristaline", "fourat": "fourat",
    "dima": "dima", "mira": "mira", "pristine": "pristine", "may": "may_tunisia",
    "jannet": "jannet", "jektiss": "jektiss", "melina": "melina", "aqualine": "aqualine",
    "bargou": "bargou", "rayan": "rayan", "elixir": "elixir", "primaqua": "primaqua",
    "delice": "delice", "beya": "beya", "tijen": "tijen",
}

used_imgs = set()
out_brands = []
for name, b in sorted(brands.items()):
    prods = []
    for (liters, category, flavor), p in sorted(b["products"].items()):
        if not p["prices"]: continue
        res = find_img(b["id"], liters, flavor)
        if res:
            p["img"] = "assets/img/" + res[0]
            used_imgs.add(res[1])
        p.pop("flavor") if False else None
        prods.append(p)
    if not prods: continue
    # brand card image = image of the flagship product (1.5L si possible)
    b["img"] = next((p["img"] for p in prods if p["img"] and abs(p["liters"] - 1.5) < .01 and not p["flavor"]),
                    next((p["img"] for p in prods if p["img"]), None))
    types = sorted({p["category"] for p in prods})
    b["types"] = types
    b["products"] = prods
    out_brands.append(b)

# images déjà dans assets/img (copie inutile si source = destination)
for f in used_imgs:
    if f.parent != IMG_DST:
        shutil.copy2(f, IMG_DST / f.name)

data = {
    "updated": __import__("datetime").date.today().isoformat(),
    "currency": "DT",
    "stores": ["Géant", "Carrefour", "Monoprix", "Aziza"],
    "sources": [
        {"name": "Géant Drive Tunisie", "url": "https://www.geantdrive.tn"},
        {"name": "barka.tn (comparateur : Carrefour, Monoprix, Aziza, Géant)", "url": "https://barka.tn"},
        {"name": "Wikipédia — Eaux minérales en Tunisie", "url": "https://fr.wikipedia.org/wiki/Eaux_min%C3%A9rales_en_Tunisie"},
    ],
    "brands": out_brands,
}

(PROJECT / "data").mkdir(exist_ok=True)
js = "window.EAUX_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
(PROJECT / "data" / "eaux.js").write_text(js, encoding="utf-8")
(PROJECT / "data" / "eaux.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

n_prod = sum(len(b["products"]) for b in out_brands)
n_off = sum(len(p["prices"]) for b in out_brands for p in b["products"])
print(f"marques: {len(out_brands)} | produits: {n_prod} | offres prix: {n_off} | images copiées: {len(used_imgs)}")
for b in out_brands:
    print(f"  {b['name']:12} {len(b['products'])} produits, img={'oui' if b['img'] else 'NON'}")
