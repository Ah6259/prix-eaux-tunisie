# -*- coding: utf-8 -*-
"""Prix signalés par les visiteurs : lecture, décision automatique, publication.

Le formulaire « Signaler un prix » du site dépose les réponses dans un Google Forms
(tableau Google Sheets d'Ahmed, publié en CSV — lecture seule). Ce script, lancé
toutes les 2 h de 8h à 22h (workflow signalements.yml) :
  1. lit toutes les réponses ;
  2. décide seul de publier ou de rejeter chaque signalement (règles ci-dessous) ;
  3. écrit data/signalements.js (lu par le site) + data/signalements.json (état) ;
  4. annonce chaque NOUVEAU prix publié sur le canal Telegram.

Règles de décision (garde-fous : un robot ne peut pas prouver qu'un prix est vrai,
il écarte seulement l'invraisemblable) :
  - marque suivie par le site, format connu, prix > 0 ;
  - date vue : pas dans le futur, 30 jours maximum ;
  - prix au litre plausible (0,25–2,5 DT/L ; 0,10–1,5 DT/L pour les bidons ≥ 5 L) ;
  - écart ≤ 40 % avec la médiane des prix connus du même produit (enseignes + autres
    signalements publiés) ; sans référence : ≤ 60 % avec la médiane du même format ;
  - doublons fusionnés ; un prix signalé ≥ 2 fois (à 5 % près, même produit et même
    magasin) est marqué « confirmé ».

Les entrées manuelles (data/signalements_manuels.json) sont toujours publiées.

Usage : python tools/signalements.py        (TELEGRAM_BOT_TOKEN pour publier sur le canal)
"""
import csv
import io
import json
import re
import statistics
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from collect_prices import http_get  # noqa: E402
from price_drops import telegram, dt, SITE  # noqa: E402

CSV_URL = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vRI0naKTfS10a5cUe8Fz9lVDlvKaBtz7J56Yk"
           "Bo4oD-Ev2Al78sCw8zAGe3nyjCehhMdJ6c1C-yEXsn/pub?gid=287357703&single=true&output=csv")
OUT_JS = ROOT / "data" / "signalements.js"
OUT_JSON = ROOT / "data" / "signalements.json"
MANUELS = ROOT / "data" / "signalements_manuels.json"
OUT_VOTES = ROOT / "data" / "votes.js"
JOURS_MAX = 30
GRAND_FORMAT = 2.5


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip().lower()


def taille_stika(litres):
    return 12 if litres <= 0.75 else 6


def parse_nombre(s):
    m = re.search(r"\d+(?:[.,]\d+)?", (s or "").replace(" ", ""))
    return float(m.group().replace(",", ".")) if m else None


def cle_produit(s):
    return (s["id"], s["litres"], s["type"])


def lire_reponses():
    txt = http_get(CSV_URL).decode("utf-8")
    lignes = list(csv.reader(io.StringIO(txt)))
    entete = [norm(x) for x in lignes[0]]
    col = {nom: i for i, nom in enumerate(entete)}
    col.setdefault("magasin", col.get("magazin"))   # la question s'appelle « magazin » dans le formulaire
    out = []
    for l in lignes[1:]:
        g = lambda k: l[col[k]].strip() if col.get(k) is not None and col[k] < len(l) else ""
        out.append({k: g(k) for k in ("horodateur", "marque", "format", "eau", "prix", "unite",
                                     "magasin", "lieu", "date")})
    return out


def references(data):
    """Prix connus des enseignes : par produit, et par format (prix au litre)."""
    par_produit, par_format = {}, {}
    for b in data["brands"]:
        for p in b["products"]:
            if p.get("flavor"):
                continue
            for v in p["prices"].values():
                par_produit.setdefault((b["id"], p["liters"], p["category"]), []).append(v)
                par_format.setdefault(p["liters"], []).append(v)
    return par_produit, par_format


def decider(r, marques, par_produit, par_format, publies):
    """Renvoie (signalement normalisé, None) ou (None, raison du rejet)."""
    b = marques.get(norm(r["marque"]))
    if not b:
        return None, f"marque non suivie « {r['marque']} »"
    litres = parse_nombre(r["format"])
    if not litres or norm(r["format"]) == "autre":
        return None, f"format inconnu « {r['format']} »"
    prix = parse_nombre(r["prix"])
    if not prix or prix <= 0:
        return None, f"prix invalide « {r['prix']} »"
    try:
        vu = date.fromisoformat(r["date"][:10])
    except ValueError:
        return None, f"date invalide « {r['date']} »"
    aujourdhui = date.today()
    if vu > aujourdhui + timedelta(days=1):
        return None, "date dans le futur"
    if (aujourdhui - vu).days > JOURS_MAX:
        return None, "prix vu il y a plus de 30 jours"
    if "stika" in norm(r["unite"]) and litres <= GRAND_FORMAT:
        prix = prix / taille_stika(litres)          # prix d'une bouteille
    au_litre = prix / litres
    mini, maxi = (0.25, 2.5) if litres <= GRAND_FORMAT else (0.10, 1.5)
    if not mini <= au_litre <= maxi:
        return None, f"prix au litre invraisemblable ({au_litre:.2f} DT/L)"
    typ = "gazeuse" if "gaz" in norm(r["eau"]) else "plate"
    ref = par_produit.get((b["id"], litres, typ), []) + \
        [p["prix"] for p in publies if cle_produit(p) == (b["id"], litres, typ)]
    if ref:
        med = statistics.median(ref)
        if abs(prix - med) / med > 0.40:
            return None, f"trop loin des prix connus ({prix:.3f} contre ~{med:.3f} DT la bouteille)"
    elif par_format.get(litres):
        med = statistics.median(par_format[litres])
        if abs(prix - med) / med > 0.60:
            return None, f"trop loin des prix du format ({prix:.3f} contre ~{med:.3f} DT la bouteille)"
    return {
        "id": b["id"], "marque": b["name"], "litres": litres, "type": typ,
        "prix": round(prix, 4), "magasin": r["magasin"][:40] or "Magasin",
        "lieu": r["lieu"][:40], "date": vu.isoformat(), "nb": 1,
        "cle": r["horodateur"],
    }, None


def ecrire_votes(reponses, marques):
    """Votes « mon eau préférée » : lignes du formulaire avec format = VOTE.
    Champ lieu = jeton anonyme du navigateur (« vote:… ») : un seul vote compté par
    navigateur (le plus récent, on peut changer d'avis). Vote indicatif, non infalsifiable."""
    par_jeton = {}
    for r in reponses:
        if r["format"].strip().upper() != "VOTE":
            continue
        b = marques.get(norm(r["marque"]))
        jeton = (r["lieu"] or "").strip()
        if not b or not jeton.startswith("vote:"):
            continue
        par_jeton[jeton] = b          # les réponses sont dans l'ordre d'arrivée : la dernière gagne
    compte = {}
    for b in par_jeton.values():
        compte[b["id"]] = compte.get(b["id"], {"id": b["id"], "marque": b["name"], "votes": 0})
        compte[b["id"]]["votes"] += 1
    classement = sorted(compte.values(), key=lambda x: (-x["votes"], x["marque"]))
    OUT_VOTES.write_text(
        "// GÉNÉRÉ par tools/signalements.py — votes « mon eau préférée » (un vote par navigateur)\n"
        "window.EAUX_VOTES = " + json.dumps({"maj": datetime.now().isoformat(timespec="minutes"),
                                             "total": len(par_jeton), "classement": classement},
                                            ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"Votes : {len(par_jeton)} votant(s), {len(classement)} marque(s)")


def message(s):
    n = taille_stika(s["litres"]) if s["litres"] <= GRAND_FORMAT else 1
    quoi = f"{'Stika ' if n > 1 else ''}{s['marque']} {str(s['litres']).replace('.', ',').rstrip('0').rstrip(',')} L"
    if s["type"] == "gazeuse":
        quoi += " gazeuse"
    lieu = f" ({s['lieu']})" if s["lieu"] else ""
    vu = datetime.fromisoformat(s["date"]).strftime("%d/%m")
    return (f"📍 <b>Prix signalé par un visiteur</b>\n"
            f"<b>{quoi}</b> : <b>{dt(s['prix'] * n)}</b> chez {s['magasin']}{lieu}, vu le {vu}\n\n"
            f"Vous aussi, signalez un prix vu en magasin : {SITE}")


def main():
    data = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
    marques = {norm(b["name"]): b for b in data["brands"]}
    marques.update({norm(b["id"]): b for b in data["brands"]})
    par_produit, par_format = references(data)
    etat = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    deja_annonces = set(etat.get("annonces", []))

    try:
        reponses = lire_reponses()
    except Exception as e:
        # tableau Google supprimé / dépublié / Google en panne : on ne touche à rien.
        # Les prix déjà publiés disparaissent seuls du site après 30 jours (app.js).
        print(f"! Tableau des signalements illisible ({e}) : rien n'est modifié.")
        return
    publies, rejets = [], []
    ecrire_votes(reponses, marques)
    for r in reponses:
        if not r["marque"] or r["marque"].upper().startswith("TEST") or r["format"].strip().upper() == "VOTE":
            continue
        s, raison = decider(r, marques, par_produit, par_format, publies)
        if raison:
            rejets.append({"horodateur": r["horodateur"], "marque": r["marque"], "prix": r["prix"],
                           "raison": raison})
            print(f"  ✗ {r['marque']} {r['format']} {r['prix']} {r['unite']} : {raison}")
            continue
        # doublon / confirmation : même produit, même magasin, prix à 5 % près
        pareil = next((p for p in publies if cle_produit(p) == cle_produit(s)
                       and norm(p["magasin"]) == norm(s["magasin"])
                       and abs(p["prix"] - s["prix"]) / p["prix"] <= 0.05), None)
        if pareil:
            pareil["nb"] += 1
            pareil["date"] = max(pareil["date"], s["date"])
            print(f"  = {s['marque']} {s['litres']} L chez {s['magasin']} : confirmé ({pareil['nb']}×)")
            continue
        publies.append(s)
        print(f"  ✓ {s['marque']} {s['litres']} L chez {s['magasin']} : {s['prix']:.3f} DT la bouteille")

    manuels = json.loads(MANUELS.read_text(encoding="utf-8")) if MANUELS.exists() else []
    affiches = manuels + [{k: v for k, v in s.items() if k != "cle"} for s in publies]
    OUT_JS.write_text(
        "// GÉNÉRÉ par tools/signalements.py (3×/jour) — ne pas modifier à la main :\n"
        "// ajouter les prix manuels dans data/signalements_manuels.json\n"
        "window.EAUX_SIGNALES = " + json.dumps(affiches, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8")

    nouveaux = [s for s in publies if s["cle"] not in deja_annonces]
    for s in nouveaux:
        try:
            telegram(message(s))
            deja_annonces.add(s["cle"])
        except Exception as e:   # Telegram en panne : on réessaiera au prochain passage
            print("Échec Telegram :", e)
    OUT_JSON.write_text(json.dumps({
        "maj": datetime.now().isoformat(timespec="minutes"),
        "publies": len(publies), "rejetes": rejets,
        "annonces": sorted(deja_annonces),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(publies)} publié(s), {len(rejets)} rejeté(s), {len(nouveaux)} nouveau(x) annoncé(s)")


if __name__ == "__main__":
    main()
