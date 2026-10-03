# -*- coding: utf-8 -*-
"""Image Instagram de la semaine : « Les 5 stikas d'eau les moins chères » (1080×1350).

Chaque lundi (workflow instagram.yml) :
  1. fabrique une page HTML aux couleurs du site et la photographie avec Chrome (headless) ;
  2. écrit le texte à copier sous la photo (assets/instagram/legende.txt) ;
  3. envoie image + texte sur le canal Telegram : Ahmed les y récupère pour Instagram.

Usage : python tools/image_semaine.py [--sans-telegram]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "instagram"
CANAL = "@prixeautunisie"
SITE = "https://ah6259.github.io/prix-eaux-tunisie/"


def dt(v):
    return f"{v:.3f}".replace(".", ",") + " DT"


def top5():
    data = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
    rows = []
    for b in data["brands"]:
        c = [p for p in b["products"] if p["category"] == "plate" and not p.get("flavor")
             and abs(p["liters"] - 1.5) < .01 and p["prices"]]
        if c:
            p = min(c, key=lambda p: min(p["prices"].values()))
            m = min(p["prices"].values())
            rows.append((m * 6, b["name"], [s for s, v in p["prices"].items() if v == m]))
    return sorted(rows)[:5], data["updated"]


def html_image(rows, maj):
    jour = date.fromisoformat(maj).strftime("%d/%m/%Y")
    lignes = "".join(f"""
      <div class="l{' g' if i == 0 else ''}">
        <span class="r">{i + 1}</span><span class="n">{nom}</span>
        <span class="p">{dt(prix)}</span><span class="m">{', '.join(mags)}</span>
      </div>""" for i, (prix, nom, mags) in enumerate(rows))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Figtree:wght@500;600;700&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden}}
body{{background:linear-gradient(160deg,#1597C6 0%,#0E7FA8 45%,#0A5F82 100%);font-family:Figtree,sans-serif;color:#fff;
  display:flex;flex-direction:column;padding:80px 70px;box-sizing:border-box}}
h1{{font-family:"Bricolage Grotesque",sans-serif;font-size:76px;line-height:1.05;margin:0}}
.sous{{font-size:34px;opacity:.9;margin:18px 0 50px}}
.l{{display:grid;grid-template-columns:60px 1fr auto;grid-template-rows:auto auto;align-items:baseline;
  background:rgba(255,255,255,.12);border-radius:26px;padding:22px 30px;margin-bottom:22px}}
.l.g{{background:#fff;color:#0F2B3D}}
.r{{grid-row:1/3;font-family:"Bricolage Grotesque",sans-serif;font-size:52px;opacity:.6}}
.n{{font-family:"Bricolage Grotesque",sans-serif;font-size:50px}}
.p{{font-family:"Bricolage Grotesque",sans-serif;font-size:50px;text-align:right}}
.l.g .p{{color:#128A52}}
.m{{grid-column:2/4;font-size:26px;opacity:.75}}
.pied{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:28px}}
.site{{font-weight:700;font-size:34px}}
</style></head><body>
<h1>Les stikas d'eau<br>les moins chères</h1>
<div class="sous">Stika 6 × 1,5 L · prix en grandes surfaces · relevés le {jour}</div>
{lignes}
<div class="pied"><div>Prix indicatifs, comparés chaque jour<br><span class="site">Prix des Eaux de Tunisie</span></div>
<div style="text-align:right">Lien dans la bio<br>Alertes : t.me/prixeautunisie</div></div>
</body></html>"""


def chrome():
    for c in ("google-chrome", "chromium", "chromium-browser",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if shutil.which(c) or Path(c).exists():
            return shutil.which(c) or c
    sys.exit("Chrome introuvable.")


def photographier(html, sortie):
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "image.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        f"--user-data-dir={d}/profil", "--virtual-time-budget=6000", "--window-size=1080,1350",
                        f"--screenshot={sortie}", page.as_uri()], check=True, capture_output=True, timeout=120)


def legende(rows, maj):
    """Texte court, le même pour Telegram et Instagram : la liste des prix est déjà dans l'image."""
    return ("💧 Les stikas d'eau les moins chères cette semaine en Tunisie\n"
            "Tous les prix, chaque jour 👉 ah6259.github.io/prix-eaux-tunisie\n"
            "#eau #stika #prix #tunisie #ستيكة #ماء #تونس")


def envoyer_telegram(image, texte):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN absent : rien envoyé sur Telegram.")
        return
    limite = uuid.uuid4().hex
    parties = []
    for nom, valeur in (("chat_id", CANAL), ("caption", texte[:1024])):
        parties.append(f'--{limite}\r\nContent-Disposition: form-data; name="{nom}"\r\n\r\n{valeur}\r\n'.encode())
    parties.append(f'--{limite}\r\nContent-Disposition: form-data; name="photo"; filename="semaine.png"\r\n'
                   f'Content-Type: image/png\r\n\r\n'.encode() + Path(image).read_bytes() + b"\r\n")
    parties.append(f"--{limite}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendPhoto", b"".join(parties),
                                 {"Content-Type": f"multipart/form-data; boundary={limite}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        print("Telegram :", json.loads(r.read()).get("ok"))


def main():
    rows, maj = top5()
    if len(rows) < 3:
        sys.exit("Pas assez de prix pour l'image de la semaine.")
    OUT.mkdir(parents=True, exist_ok=True)
    image = OUT / "semaine.png"
    photographier(html_image(rows, maj), image)
    texte = legende(rows, maj)
    (OUT / "legende.txt").write_text(texte, encoding="utf-8")
    print(f"Image : {image} ({image.stat().st_size // 1024} Ko)\n\n{texte}")
    if "--sans-telegram" not in sys.argv:
        envoyer_telegram(image, texte)


if __name__ == "__main__":
    main()
