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
sys.path.insert(0, str(ROOT / "tools"))
import collect_prices as c  # noqa: E402

J0 = date(2026, 10, 1)
REEL = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
NOMS = {"carrefour": "Carrefour", "geant": "Géant", "otrity": "Otrity"}


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
    def __init__(self, avec_historique=True, otrity_local_age=0):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "data").mkdir()
        c.ROOT = self.tmp
        c.OUT_JSON = self.tmp / "data" / "eaux.json"
        c.OUT_JS = self.tmp / "data" / "eaux.js"
        c.RAW_DIR = self.tmp / "raw"
        c.IMG_AUTO = self.tmp / "img"
        c.telecharger_image = lambda url: None
        self.jour = J0
        if otrity_local_age is not None:
            self.otrity_local(otrity_local_age)
        if avec_historique:
            self.passe({s: ok(s) for s in ("carrefour", "geant")}, avancer=False)

    def otrity_local(self, age_jours):
        (self.tmp / "data" / "otrity.json").write_text(json.dumps({
            "date": (self.jour - timedelta(days=age_jours)).isoformat(),
            "offres": offres_reelles("otrity")}), encoding="utf-8")

    def passe(self, comportements, avancer=True):
        """Un passage du robot (une nuit). Otrity est toujours bloqué (comme sur GitHub)."""
        if avancer:
            self.jour += timedelta(days=1)
        jour = self.jour
        class FausseDate(date):
            @classmethod
            def today(cls): return jour
        c.date = FausseDate
        c.carrefour = comportements.get("carrefour", ok("carrefour"))
        c.geant = comportements.get("geant", ok("geant"))
        c.otrity = panne("403 Cloudflare")
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


@scenario("1. Tout fonctionne", "3 enseignes, aucun avertissement",
          lambda e, d, m: e == ["Carrefour", "Géant", "Otrity"] and m == "(aucun avertissement)")
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
    b = Bac(otrity_local_age=None)
    for _ in range(2): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("11. Toutes les sources en panne 3 nuits", "⚠️ « non mis à jour depuis le … »",
          lambda e, d, m: m.startswith("⚠️ prix non mis à jour"))
def _():
    b = Bac(otrity_local_age=None)
    for _ in range(3): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("12. Toutes les sources en panne 10 nuits", "aucun prix + ⚠️ « indisponibles »",
          lambda e, d, m: e == [] and m.startswith("⚠️ prix momentanément"))
def _():
    b = Bac(otrity_local_age=None)
    for _ in range(10): d = b.passe({"carrefour": panne(), "geant": panne()})
    return b, d, b.jour

@scenario("13. Robots arrêtés (GitHub en pause), visite 20 jours après", "⚠️ « non mis à jour depuis le … »",
          lambda e, d, m: m.startswith("⚠️ prix non mis à jour"))
def _():
    b = Bac(); d = b.passe({}); return b, d, b.jour + timedelta(days=20)

@scenario("14. PC d'Ahmed éteint 5 jours (Otrity)", "prix Otrity retirés, les autres intacts",
          lambda e, d, m: e == ["Carrefour", "Géant"])
def _():
    b = Bac(otrity_local_age=5); d = b.passe({}); return b, d, b.jour

@scenario("15. Premier lancement, sans historique, Géant en panne", "pas de plantage, Carrefour seul",
          lambda e, d, m: "Carrefour" in e and "Géant" not in e)
def _():
    b = Bac(avec_historique=False); d = b.passe({"geant": panne()}, avancer=False); return b, d, b.jour


# ------------------------------------------------------------------ rapport
print("\nSIMULATION DES PANNES DU ROBOT DES PRIX\n")
for reussi, titre, attendu, ens, msg in resultats:
    print(f"{'✅' if reussi else '❌'} {titre}")
    print(f"     attendu : {attendu}")
    print(f"     obtenu  : enseignes affichées = {ens} | visiteur voit : {msg}")
n_ok = sum(r[0] for r in resultats)
print(f"\n{n_ok}/{len(resultats)} scénarios réussis")
sys.exit(0 if n_ok == len(resultats) else 1)
