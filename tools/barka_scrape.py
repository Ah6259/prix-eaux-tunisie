"""Scrape barka.tn brand pages for Tunisian mineral water products and per-store prices."""
import re, json, time, pathlib, urllib.request

SCRATCH = pathlib.Path(__file__).parent
PAGES = SCRATCH / "pages" / "barka"
PAGES.mkdir(parents=True, exist_ok=True)

BRANDS = ["SAFIA", "SABRINE", "MARWA", "MELLITI", "DELICE", "BEYA", "TIJEN", "GARCI",
          "DIMA", "MIRA", "PRISTINE", "MAY TUNISIA", "CRISTALINE", "FOURAT", "PRIMAQUA",
          "AIN OKTOR", "OKTOR", "CRISTAL", "HAYET", "JANNET", "JEKTISS", "MAIN", "MELINA",
          "AQUALINE", "BULLA REGIA", "BARGOU", "EAU ROYALE", "OVIA", "RAYAN", "ELIXIR", "AQUA"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"}

def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 5000:
        return dest.read_text(encoding="utf-8", errors="ignore")
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
        dest.write_text(data, encoding="utf-8")
        time.sleep(0.8)
        return data
    except Exception as e:
        print(f"  !! {url}: {e}")
        return ""

def unesc(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")

FIELD_RE = re.compile(r'"(_id|brand|category|description|imageSrc|name|product_price|percentagePromo)":"((?:[^"\\]|\\.)*)"')

def extract_products(txt):
    """Extract product objects from Next.js flight data embedded in the HTML."""
    out = []
    plain = unesc(txt)
    # split on object starts; each product object begins with {"_id":"
    for chunk in plain.split('{"_id":"')[1:]:
        # stop at the object's closing brace (no nested objects in these product dicts)
        end = chunk.find('}')
        chunk = '{"_id":"' + (chunk[:end] if end > 0 else chunk[:1500])
        fields = {}
        for k, v in FIELD_RE.findall(chunk):
            fields.setdefault(k, v)
        if fields.get("product_price"):
            out.append(fields)
    return out

def store_from_img(src):
    s = (src or "").lower()
    if "monoprix" in s: return "Monoprix"
    if "aziza" in s: return "Aziza"
    if "carrefour" in s: return "Carrefour"
    if "geant" in s: return "Géant"
    if "mg" in s and ".tn" in s: return "MG"
    return None

all_rows = []
seen = set()
for brand in BRANDS:
    slug = urllib.request.quote(brand)
    txt = fetch(f"https://barka.tn/produit/{slug}", PAGES / f"{brand.replace(' ','_')}.html")
    if not txt:
        continue
    prods = extract_products(txt)
    n = 0
    for p in prods:
        key = (p.get("_id"), p.get("product_price"))
        if key in seen:
            continue
        seen.add(key)
        img = p.get("imageSrc", "")
        row = {
            "barka_id": p.get("_id"),
            "brand_query": brand,
            "brand": p.get("brand"),
            "name": p.get("name"),
            "description": p.get("description"),
            "price": p.get("product_price"),
            "store": store_from_img(img),
            "img": img,
        }
        all_rows.append(row)
        n += 1
    print(f"{brand:14} -> {n} offers")

(SCRATCH / "barka_products.json").write_text(json.dumps(all_rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nTOTAL: {len(all_rows)} offers saved")
