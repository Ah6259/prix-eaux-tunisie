# -*- coding: utf-8 -*-
"""Récupère les produits 'eaux' de Géant Drive (geantdrive.tn) -> tools/geant_products.json"""
import re, json, html, pathlib, urllib.request

HERE = pathlib.Path(__file__).parent
URL = "https://www.geantdrive.tn/tunis-city/11-eaux?resultsPerPage=100"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"}

req = urllib.request.Request(URL, headers=UA)
txt = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="ignore")

blocks = txt.split("product-miniature js-product-miniature")[1:]
out = []
for b in blocks:
    def g(pat, flags=0):
        m = re.search(pat, b, flags)
        if not m:
            return None
        return html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)).replace(" ", " ")).strip()
    fmt = g(r"product-description-short-\d+[^>]*>(.*?)</div>", re.S)
    url = g(r'href="(https://[^"]+\.html)"')
    out.append({
        "brand": g(r"manufacturer_product[^>]*>\s*(.*?)</p>", re.S),
        "format": re.sub(r"\s+", " ", fmt).strip() if fmt else None,
        "price_dt": g(r'itemprop="price"[^>]*>([^<]+)<'),
        "category": "gazeuse" if url and "gazeifiees" in url else "plate",
        "img": g(r'src="(https://cdn\.geantdrive\.tn/[^"]+)"'),
        "url": url,
    })

dest = HERE / "geant_products.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(out)} produits -> {dest}")
