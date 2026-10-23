# -*- coding: utf-8 -*-
"""Simulateur de pannes : rejoue tout ce qui peut arriver au robot des prix et vérifie
qu'il réagit correctement (jamais de prix périmés affichés comme actuels, jamais de plantage).

Les sources sont simulées à partir des vraies données actuelles (data/eaux.json) ;
rien n'est téléchargé et rien n'est écrit dans le vrai dossier data/.

Usage : python tools/test_pannes.py
"""
import json
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# console Windows (cp1252) : sans ceci, l'affichage des ✅ / ❌ fait planter le test
for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "tools"))
import collect_prices as c  # noqa: E402

J0 = date(2026, 10, 1)
REEL = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
NOMS = {"carrefour": "Carrefour", "geant": "Géant"}
# Enseignes RETIRÉES le 23/10/2026 (décision d'Ahmed : site autonome) : ne doivent plus jamais revenir
RETIREES = {"otrity": "Otrity", "monoprix": "Monoprix"}


# ------------------------------------------------------------------ sources simulées
def offres_reelles(src):
    return c.anciennes_offres(REEL, {src})

def ok(src):            return lambda: offres_reelles(src)
def panne(msg="curl: (22) HTTP 403"):
    def f(): raise RuntimeError(msg)
    return f
def vide():             return lambda: []
def partiel(src, n=3):  return lambda: offres_reelles(src)[:n]
def millimes(src):      return lambda: [dict(o, prix=o["prix"] * 1000) for o in offres_reelles(src)]
def marques_inconnues(src):
    return lambda: [dict(o, marque=None) for o in offres_reelles(src)]


class Bac:
    """Un « dossier data » temporaire + une horloge simulée."""
    def __init__(self, avec_historique=True):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "data").mkdir()
        c.ROOT = self.tmp
        c.OUT_JSON = self.tmp / "data" / "eaux.json"
        c.OUT_JS = self.tmp / "data" / "eaux.js"
        c.RAW_DIR = self.tmp / "raw"
        c.IMG_AUTO = self.tmp / "img"
        c.telecharger_image = lambda url: None
        self.jour = J0
        if avec_historique:
            self.passe({s: ok(s) for s in ("carrefour", "geant")}, avancer=False)

    def passe(self, comportements, avancer=True):
        """Un passage du robot (une nuit)."""
        if avancer:
            self.jour += timedelta(days=1)
        jour = self.jour
        class FausseDate(date):
            @classmethod
            def today(cls): return jour
        c.date = FausseDate
        c.carrefour = comportements.get("carrefour", ok("carrefour"))
        c.geant = comportements.get("geant", ok("geant"))
        sortie = sys.stdout
        sys.stdout = sys.stderr = open(self.tmp / "journal.txt", "a", encoding="utf-8")
        try:
            c.main()
        finally:
            sys.stdout.close()
            sys.stdout = sys.__stdout__; sys.stderr = sys.__stderr__
        return json.loads(c.OUT_JSON.read_text(encoding="utf-8"))

    def fin(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


# ------------------------------------------------------------------ ce que voit le visiteur
def vu_par_visiteur(data, aujourdhui):
    """Reproduit la logique d'avertissement d'app.js (alerteFraicheur)."""
    avec_prix = {s for b in data["brands"] for p in b["products"] for s in p["prices"]}
    st = data.get("statut_sources") or {}
    # relevés manuels : jamais d'alerte de retard (aucun depuis le 23/10/2026) ; enseigne inconnue d'app.js : ignorée
    st = {k: s for k, s in st.items() if not s.get("manuel") and k in NOMS}
    derniers = sorted(s["dernier_ok"] for k, s in st.items() if s.get("dernier_ok") and NOMS[k] in avec_prix)
    derniere = derniers[-1] if derniers else data["updated"]
    if not avec_prix:
        return "⚠️ prix momentanément indisponibles"
    if (aujourdhui - date.fromisoformat(derniere)).days >= 3:
        return f"⚠️ prix non mis à jour depuis le {derniere}"
    retard = [f"{NOMS[k]} du {s['dernier_ok']}" for k, s in st.items()
              if s.get("dernier_ok") and (aujourdhui - date.fromisoformat(s["dernier_ok"])).days >= 2
              and NOMS[k] in avec_prix]
    return f"ℹ️ prix {', '.join(retard)}" if retard else "(aucun avertissement)"


def enseignes(data):
    return sorted({s for b in data["brands"] for p in b["products"] for s in p["prices"]})


# ------------------------------------------------------------------ scénarios
resultats = []

def scenario(titre, attendu, verifie):
    def deco(fn):
        bac = None
        try:
            bac, data, jour = fn()
            ens = enseignes(data)
            msg = vu_par_visiteur(data, jour)
            reussi = verifie(ens, data, msg)
        except Exception as e:  # le robot ne doit JAMAIS planter
            ens, msg, reussi = [], f"PLANTAGE : {e!r}", False
        finally:
            if bac: bac.fin()
        resultats.append((reussi, titre, attendu, ", ".join(ens) or "aucune", msg))
        return fn
    return deco


@scenario("1. Tout fonctionne", "2 enseignes (Carrefour, Géant), aucun avertissement",
          lambda e, d, m: e == ["Carrefour", "Géant"] and m == "(aucun avertissement)")
def _():
    b = Bac(); d = b.passe({}); return b, d, b.jour

@scenario("2. Géant en panne 1 nuit", "prix Géant de la veille gardés, pas d'alerte (1 jour = normal)",
          lambda e, d, m: "Géant" in e and m == "(aucun avertissement)")
def _():
    b = Bac(); d = b.passe({"geant": panne("curl: (60) certificat")}); return b, d, b.jour

@scenario("2b. Géant en panne 2 nuits", "prix Géant gardés + mention « Géant du … »",
          lambda e, d, m: "Géant" in e and "Géant du" in m)
def _():
    b = Bac()
    for _ in range(2): d = b.passe({"geant": panne()})
    return b, d, b.jour

@scenario("3. Géant en panne 7 nuits", "prix Géant encore gardés (limite 7 jours)",
          lambda e, d, m: "Géant" in e)
def _():
    b = Bac()
    for _ in range(7): d = b.passe({"geant": panne()})
    return b, d, b.jour

@scenario("4. Géant en panne 8 nuits", "prix Géant RETIRÉS du site",
          lambda e, d, m: "Géant" not in e and "Carrefour" in e)
def _():
    b = Bac()
    for _ in range(8): d = b.passe({"geant": panne()})
    return b, d, b.jour

@scenario("5. Géant revient après 5 nuits de panne", "prix Géant du jour, plus d'avertissement",
          lambda e, d, m: "Géant" in e and d["statut_sources"]["geant"]["dernier_ok"] == "2026-10-07"
          and m == "(aucun avertissement)")
def _():
    b = Bac()
    for _ in range(5): b.passe({"geant": panne()})
    d = b.passe({}); return b, d, b.jour

@scenario("6. Carrefour renvoie une page vide (site refait)", "traité comme une panne : prix de la veille",
          lambda e, d, m: "Carrefour" in e and d["statut_sources"]["carrefour"]["dernier_ok"] == "2026-10-01")
def _():
    b = Bac(); d = b.passe({"carrefour": vide()}); return b, d, b.jour

@scenario("7. Carrefour ne renvoie que 3 produits", "« résultat suspect » : prix de la veille",
          lambda e, d, m: d["statut_sources"]["carrefour"]["dernier_ok"] == "2026-10-01"
          and sum(1 for b in d["brands"] for p in b["products"] if "Carrefour" in p["prices"]) > 10)
def _():
    b = Bac(); d = b.passe({"carrefour": partiel("carrefour")}); return b, d, b.jour

@scenario("8. Carrefour affiche ses prix en millimes (670 au lieu de 0,670)", "« incohérent » : prix de la veille, aucun prix ×1000",
          lambda e, d, m: d["statut_sources"]["carrefour"]["dernier_ok"] == "2026-10-01"
          and all(v < 50 for b in d["brands"] for p in b["products"] for v in p["prices"].values()))
def _():
    b = Bac(); d = b.passe({"carrefour": millimes("carrefour")}); return b, d, b.jour

@scenario("9. Carrefour renomme toutes ses marques", "« incohérent » : prix de la veille",
          lambda e, d, m: d["statut_sources"]["carrefour"]["dernier_ok"] == "2026-10-01" and "Carrefour" in e)
def _():
    b = Bac(); d = b.passe({"carrefour": marques_inconnues("carrefour")}); return b, d, b.jour

@scenario("10. Toutes les sources en panne 2 nuits", "prix gardés + mention du retard",
          lambda e, d, m: "Carrefour" in e and "Géant" in e and m.startswith(("ℹ️", "⚠️")))
def _():
    b = Bac()
    for _ in range(2): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("11. Toutes les sources en panne 3 nuits", "⚠️ « non mis à jour depuis le … »",
          lambda e, d, m: m.startswith("⚠️ prix non mis à jour"))
def _():
    b = Bac()
    for _ in range(3): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("12. Toutes les sources en panne 10 nuits", "aucun prix + ⚠️ « indisponibles »",
          lambda e, d, m: e == [] and m.startswith("⚠️ prix momentanément"))
def _():
    b = Bac()
    for _ in range(10): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("13. Robots arrêtés (GitHub en pause), visite 20 jours après", "⚠️ « non mis à jour depuis le … »",
          lambda e, d, m: m.startswith("⚠️ prix non mis à jour"))
def _():
    b = Bac(); d = b.passe({}); return b, d, b.jour + timedelta(days=20)

def avec_retirees(base):
    """eaux.json d'avant le 23/10/2026 : prix Otrity + Monoprix et leur statut (Monoprix « manuel »)."""
    d = json.loads(json.dumps(base))
    for b in d["brands"]:
        for p in b["products"]:
            if abs(p["liters"] - 1.5) < .01:
                p["prices"].update({"Otrity": 0.8333, "Monoprix": 0.7})
                p["non_dispo"] = ["Otrity"]
    d["stores"] = ["Carrefour", "Géant", "Otrity", "Monoprix"]
    d["statut_sources"].update({"otrity": {"dernier_ok": d["updated"], "nb": 4},
                                "monoprix": {"dernier_ok": d["updated"], "nb": 9, "manuel": True}})
    return d

def sans_retirees(d):
    """Aucune trace d'Otrity ni de Monoprix : prix, « non disponible », magasins, statut, liste des enseignes, sources."""
    texte = json.dumps({k: d[k] for k in ("brands", "stores", "sources", "statut_sources")}, ensure_ascii=False).lower()
    return (set(d["statut_sources"]) <= set(NOMS) and d["stores"] == ["Carrefour", "Géant"]
            and not any(n.lower() in texte or k in texte for k, n in RETIREES.items()))

@scenario("14. Ancien relevé avec Otrity et Monoprix (avant le 23/10/2026)",
          "après une nuit : seulement Carrefour et Géant, aucune trace des enseignes retirées (prix, statut, non disponible)",
          lambda e, d, m: e == ["Carrefour", "Géant"] and sans_retirees(d) and m == "(aucun avertissement)")
def _():
    b = Bac()
    c.OUT_JSON.write_text(json.dumps(avec_retirees(json.loads(c.OUT_JSON.read_text(encoding="utf-8")))), encoding="utf-8")
    d = b.passe({}); return b, d, b.jour

@scenario("14b. Même ancien relevé, Carrefour en panne (reprise des anciens prix)",
          "la reprise ne ramène JAMAIS Otrity ni Monoprix",
          lambda e, d, m: e == ["Carrefour", "Géant"] and sans_retirees(d))
def _():
    b = Bac()
    c.OUT_JSON.write_text(json.dumps(avec_retirees(json.loads(c.OUT_JSON.read_text(encoding="utf-8")))), encoding="utf-8")
    d = b.passe({"carrefour": panne()}); return b, d, b.jour

@scenario("14c. Vieux fichiers data/otrity.json et data/monoprix.json restés sur le disque",
          "ignorés : le robot ne lit plus que Carrefour et Géant",
          lambda e, d, m: e == ["Carrefour", "Géant"] and sans_retirees(d))
def _():
    b = Bac()
    offre = {"marque": "AQUALINE", "nom": "Eau minérale AQUALINE 1.5L", "volume_l": 1.5, "nb_unites": 1,
             "type": "plate", "prix": 0.6, "image_src": None}
    for k in RETIREES:
        (b.tmp / "data" / f"{k}.json").write_text(json.dumps({"date": b.jour.isoformat(),
                                                             "offres": [dict(offre, enseigne=k)]}), encoding="utf-8")
    d = b.passe({}); return b, d, b.jour

@scenario("15. Premier lancement, sans historique, Géant en panne", "pas de plantage, Carrefour seul",
          lambda e, d, m: "Carrefour" in e and "Géant" not in e)
def _():
    b = Bac(avec_historique=False); d = b.passe({"geant": panne()}, avancer=False); return b, d, b.jour

@scenario("15b. Premier lancement, Géant ne renvoie que 3 produits (lecteur cassé)",
          "« presque rien lu » : panne (robot rouge après 2 jours), jamais vert avec 3 produits",
          lambda e, d, m: "Géant" not in e and "geant" not in d["statut_sources"])
def _():
    b = Bac(avec_historique=False); d = b.passe({"geant": partiel("geant")}, avancer=False); return b, d, b.jour

# photos libres (Open Food Facts) des marques sans photo de magasin : doivent rester après chaque nuit
LIBRES = json.loads((ROOT / "data" / "photos_libres.json").read_text(encoding="utf-8"))["photos"]

def photos_ok(d):
    par_id = {b["id"]: b for b in d["brands"]}
    return all(par_id.get(i, {}).get("img") == ph["img"] and (par_id[i].get("img_credit") or {}).get("page") == ph["page"]
               for i, ph in LIBRES.items())

@scenario("16. Photos libres (Open Food Facts) après 2 nuits du robot", "photo + crédit gardés pour " + ", ".join(LIBRES),
          lambda e, d, m: bool(LIBRES) and photos_ok(d))
def _():
    b = Bac(); b.passe({}); d = b.passe({}); return b, d, b.jour

@scenario("16b. Une marque à photo libre arrive en magasin avec sa photo", "photo du magasin prioritaire, plus de crédit",
          lambda e, d, m: (lambda t: t["img"] == "assets/img/produits/test.webp" and "img_credit" not in t)(
              next(x for x in d["brands"] if x["id"] == next(iter(LIBRES)))))
def _():
    b = Bac()
    cible = next(iter(LIBRES))
    nom = next(m for m in c.META.values() if c.slug(m["name"]) == cible)["name"]
    marque = next(k for k, m in c.META.items() if m["name"] == nom)
    c.telecharger_image = lambda url: "assets/img/produits/test.webp" if url == "http://test/photo.webp" else None
    base = ok("carrefour")
    def avec_cible():
        return base() + [{"enseigne": "carrefour", "marque": marque, "nom": f"{nom} 1.5 L", "volume_l": 1.5,
                          "nb_unites": 1, "type": "plate", "prix": 0.75, "image_src": "http://test/photo.webp",
                          "image_locale": None}]
    d = b.passe({"carrefour": avec_cible}); return b, d, b.jour


# ------------------------------------------------------------------ rapport
print("\nSIMULATION DES PANNES DU ROBOT DES PRIX\n")
for reussi, titre, attendu, ens, msg in resultats:
    print(f"{'✅' if reussi else '❌'} {titre}")
    print(f"     attendu : {attendu}")
    print(f"     obtenu  : enseignes affichées = {ens} | visiteur voit : {msg}")
import sources_en_panne as SP  # noqa: E402
_st = {"statut_sources": {"carrefour": {"dernier_ok": "2026-10-01"}, "geant": {"dernier_ok": "2026-10-14"},
                          "releve_main": {"dernier_ok": "2026-09-01", "manuel": True}}}
_p = [k for k, _ in SP.en_panne(_st, date(2026, 10, 15))]
resultats.append((_p == ["carrefour"] and "sources_en_panne.py" in (ROOT / ".github" / "workflows" / "maj-prix.yml").read_text(encoding="utf-8"),
                  "Enseigne en panne depuis plus de 2 jours -> le robot passe en ÉCHEC (e-mail à Ahmed)",
                  "seule Carrefour signalée (source « manuel » ignorée)", str(_p), "—"))
# le code du robot ne lit plus aucune enseigne retirée (23/10/2026) : ni fonction, ni fichier de relevé
_src = (ROOT / "tools" / "collect_prices.py").read_text(encoding="utf-8")
_code = "\n".join(l for l in _src.splitlines() if not l.lstrip().startswith("#"))
_code = _code.split('"""', 2)[-1]   # sans le texte d'explication du haut du fichier
_lit = [k for k in RETIREES if f"def {k}(" in _code or f"{k}.json" in _code or f'"{k}"' in _code]
resultats.append((not _lit and set(c.ENSEIGNES) == set(NOMS) and set(c.MINIMUM_OFFRES) <= set(NOMS),
                  "Le robot ne lit plus Otrity ni Monoprix (retirés le 23/10/2026)",
                  "aucune fonction, aucun fichier, aucune clé d'enseigne retirée dans collect_prices.py", str(_lit or "rien"), "—"))
n_ok = sum(r[0] for r in resultats)
print(f"\n{n_ok}/{len(resultats)} scénarios réussis")
sys.exit(0 if n_ok == len(resultats) else 1)
