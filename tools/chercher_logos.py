"""Va chercher les logos officiels des enseignes sur leurs propres sites
(lancé à la main par le robot logos.yml, car ces sites ne sont joignables que depuis GitHub).
Tout ce qui ressemble à un logo est rangé dans assets/logos/brut/ ; on choisit ensuite le bon."""
import re, subprocess, pathlib, urllib.parse

import os
# Sites à visiter : par défaut les enseignes suivies ; sinon la liste donnée au lancement
# (champ « sites » du robot logos.yml, ex. « geant=https://www.geant.tn/ monoprix=https://www.monoprix.tn/ »).
SITES = dict(x.split("=", 1) for x in os.environ.get("SITES", "").split()) or {
    "carrefour": "https://www.carrefour.tn/",
    "geant": "https://www.geantdrive.tn/",
    "otrity": "https://otrity.com/",
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
DOSSIER = pathlib.Path("assets/logos/brut")
DOSSIER.mkdir(parents=True, exist_ok=True)


def telecharger(url, sortie=None):
    """curl, puis curl -k en cas d'erreur de certificat (cas de Géant)."""
    for extra in ([], ["-k"]):
        cmd = ["curl", "-sSL", "-m", "30", "-A", UA, *extra, url]
        if sortie:
            cmd += ["-o", str(sortie)]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0:
            return r.stdout
    print("  échec :", url, r.stderr.decode(errors="ignore")[:200])
    return None


for nom, base in SITES.items():
    nom = nom + "-" + urllib.parse.urlparse(base).netloc.replace("www.", "").replace(".", "_")
    print("==", nom, base)
    html = telecharger(base)
    if not html:
        continue
    html = html.decode("utf-8", errors="ignore")
    (DOSSIER / f"{nom}-page.html").write_text(html[:400000])
    urls = []
    # icônes du site, image de partage, et toute image dont le nom/alt/classe contient « logo »
    for m in re.finditer(r'<link[^>]+rel="[^"]*icon[^"]*"[^>]*>', html, re.I):
        h = re.search(r'href="([^"]+)"', m.group(0))
        if h: urls.append(h.group(1))
    for m in re.finditer(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html, re.I):
        urls.append(m.group(1))
    for m in re.finditer(r'<img[^>]+>', html, re.I):
        tag = m.group(0)
        if "logo" in tag.lower():
            s = re.search(r'(?:data-src|src)="([^"]+)"', tag)
            if s: urls.append(s.group(1))
    for m in re.finditer(r'["\'(]([^"\'()\s]*logo[^"\'()\s]*\.(?:svg|png|webp|jpg|jpeg))', html, re.I):
        urls.append(m.group(1))
    urls.append("/favicon.ico")
    vus = []
    for u in urls:
        u = urllib.parse.urljoin(base, u.replace("&amp;", "&"))
        if u in vus or u.startswith("data:"):
            continue
        vus.append(u)
    for i, u in enumerate(vus[:15]):
        ext = pathlib.Path(urllib.parse.urlparse(u).path).suffix.lower() or ".bin"
        if ext not in (".svg", ".png", ".webp", ".jpg", ".jpeg", ".ico", ".gif"):
            ext = ".bin"
        f = DOSSIER / f"{nom}-{i}{ext}"
        print(f"  {f.name} <- {u}")
        telecharger(u, f)
