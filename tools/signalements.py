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

Feuille illisible (23/10/2026, règles communes § 17 et § 38 : aucun robot vert qui ne fait rien) : erreur réseau, page HTML
(connexion Google) au lieu du CSV, réponse vide ou sans les bonnes colonnes. La feuille est relue 2 fois (2 min puis 4 min) ;
toujours illisible : rien n'est modifié sur le site, la date de début de la panne est notée dans data/signalements.json
(« feuille_illisible_depuis ») et le robot passe au ROUGE quand la panne dure plus de 2 jours (comme sources_en_panne.py).
Une feuille lisible sans nouveau signalement reste VERTE.

Usage : python tools/signalements.py        (TELEGRAM_BOT_TOKEN pour publier sur le canal)
"""
import csv
import io
import json
import re
import statistics
import sys
import time
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
COLONNES = ("horodateur", "marque", "format", "prix", "date")   # colonnes sans lesquelles la feuille est inutilisable
ATTENTES = (120, 240)       # § 38 : relire 2 min puis 4 min plus tard
BUDGET_S = 8 * 60           # § 38 : pas de nouvel essai au-delà de 8 min de relectures
JOURS_PANNE = 2             # § 17 : rouge si la feuille est illisible depuis plus de 2 jours



MOTIF_MAJ = re.compile(r'"maj": "[^"]*"')


def ecrire_si_change(chemin, texte):
    """Écrit le fichier seulement si son contenu change AUTREMENT que par la date « maj » (audit des robots du 10/10/2026 :
    la seule date changeait à chaque passage → un commit et une publication du site toutes les 2 h, pour rien)."""
    try:
        ancien = chemin.read_text(encoding="utf-8")
    except FileNotFoundError:
        ancien = None
    if ancien is not None and MOTIF_MAJ.sub('"maj": ""', ancien) == MOTIF_MAJ.sub('"maj": ""', texte):
        return False
    chemin.write_text(texte, encoding="utf-8", newline="\n")
    return True

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


class FeuilleIllisible(Exception):
    pass


def verifier_csv(brut):
    """Texte du CSV, ou FeuilleIllisible si ce n'est pas le tableau attendu (page HTML, vide, colonnes manquantes)."""
    try:
        txt = brut.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise FeuilleIllisible("réponse qui n'est pas du texte UTF-8")
    debut = txt.lstrip()[:300].lower()
    if not debut:
        raise FeuilleIllisible("réponse vide")
    if debut.startswith("<") or "<html" in debut:
        raise FeuilleIllisible("page web (HTML) reçue au lieu du tableau CSV (feuille dépubliée ou page de connexion Google ?)")
    lignes = list(csv.reader(io.StringIO(txt)))
    entete = {norm(x) for x in (lignes[0] if lignes else [])}
    manque = [c for c in COLONNES if c not in entete]
    if manque:
        raise FeuilleIllisible("colonnes manquantes : " + ", ".join(manque))
    return txt


def lire_feuille(lecteur, attendre=time.sleep, horloge=time.monotonic):
    """Lit et vérifie la feuille ; relit 2 fois (2 min puis 4 min) si elle est illisible (§ 38). FeuilleIllisible sinon."""
    debut = horloge()
    for i in range(len(ATTENTES) + 1):
        try:
            return verifier_csv(lecteur())
        except Exception as e:
            erreur = e
        if i == len(ATTENTES) or horloge() - debut + ATTENTES[i] > BUDGET_S:
            break
        print(f"  Feuille illisible ({erreur}) : nouvel essai dans {ATTENTES[i] // 60} min")
        attendre(ATTENTES[i])
    raise FeuilleIllisible(str(erreur))


def analyser(txt):
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


def lire_reponses(lecteur=None, attendre=time.sleep):
    return analyser(lire_feuille(lecteur or (lambda: http_get(CSV_URL)), attendre))


def panne_feuille(etat, erreur, maintenant):
    """Feuille illisible : note le début de la panne dans l'état, renvoie (code de sortie, message)."""
    depuis = etat.get("feuille_illisible_depuis") or maintenant.isoformat(timespec="minutes")
    etat["feuille_illisible_depuis"] = depuis
    jours = (maintenant - datetime.fromisoformat(depuis)).total_seconds() / 86400
    if jours >= JOURS_PANNE:
        return 1, (f"ÉCHEC Feuille des signalements illisible : {erreur} — depuis le {depuis.replace('T', ' à ')} "
                   f"(plus de {JOURS_PANNE} jours). Rien n'est modifié sur le site ; vérifier que le tableau Google des "
                   f"réponses est toujours « publié sur le Web » en CSV.")
    return 0, (f"! Feuille des signalements illisible : {erreur} — rien n'est modifié (panne depuis le "
               f"{depuis.replace('T', ' à ')} ; robot rouge si elle dure plus de {JOURS_PANNE} jours).")


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
    if prix >= 100:            # prix écrit en millimes, à la tunisienne : 3900 = 3,900 DT
        prix = prix / 1000
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


def autre_usage(fmt):
    """Lignes du même Google Forms qui ne sont PAS des prix : VOTE (eau préférée), POINT… (site Points d'eau Tunisie),
    LIEU-PRIERE… (site Mosquées en Tunisie, 09/10/2026). Le robot des prix les ignore."""
    f = (fmt or "").strip().upper()
    return f == "VOTE" or f.startswith("POINT") or f.startswith("LIEU-PRIERE")


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
    ecrire_si_change(OUT_VOTES,
        "// GÉNÉRÉ par tools/signalements.py — votes « mon eau préférée » (un vote par navigateur)\n"
        "window.EAUX_VOTES = " + json.dumps({"maj": datetime.now().isoformat(timespec="minutes"),
                                             "total": len(par_jeton), "classement": classement},
                                            ensure_ascii=False, indent=1) + ";\n")
    print(f"Votes : {len(par_jeton)} votant(s), {len(classement)} marque(s)")


def ligne(s):
    """Une ligne courte par prix : « 📍 Stika Aziz 1,5 L : 3,900 DT · Aziza (Omrane) · 30/09 »."""
    n = taille_stika(s["litres"]) if s["litres"] <= GRAND_FORMAT else 1
    quoi = f"{'Stika ' if n > 1 else ''}{s['marque']} {str(s['litres']).replace('.', ',').rstrip('0').rstrip(',')} L"
    if s["type"] == "gazeuse":
        quoi += " gazeuse"
    lieu = f" ({s['lieu']})" if s["lieu"] else ""
    vu = datetime.fromisoformat(s["date"]).strftime("%d/%m")
    return f"<b>{quoi}</b> : <b>{dt(s['prix'] * n)}</b> · {s['magasin']}{lieu} · {vu}"


def message(nouveaux):
    """UN seul message par passage, court, pour tous les nouveaux prix."""
    lien = f'👉 <a href="{SITE}">Signaler un prix : prix-eaux-tunisie</a>'
    if len(nouveaux) == 1:
        return f"📍 {ligne(nouveaux[0])}\n{lien}"
    return "📍 <b>Prix signalés par les visiteurs</b>\n" + "\n".join("• " + ligne(s) for s in nouveaux) + "\n" + lien


def main(lecteur=None, attendre=time.sleep, maintenant=None):
    for _f in (sys.stdout, sys.stderr):
        if hasattr(_f, "reconfigure"):
            _f.reconfigure(encoding="utf-8", errors="replace")
    data = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
    marques = {norm(b["name"]): b for b in data["brands"]}
    marques.update({norm(b["id"]): b for b in data["brands"]})
    par_produit, par_format = references(data)
    etat = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    deja_annonces = set(etat.get("annonces", []))

    try:
        reponses = lire_reponses(lecteur, attendre)
    except FeuilleIllisible as e:
        # tableau Google supprimé / dépublié / Google en panne : on ne touche pas au site (les prix déjà publiés
        # disparaissent seuls après 30 jours, app.js) ; seule la date de début de la panne est notée.
        code, texte = panne_feuille(etat, e, maintenant or datetime.now())
        print(texte)
        ecrire_si_change(OUT_JSON, json.dumps(etat, ensure_ascii=False, indent=1))
        return code
    publies, rejets = [], []
    ecrire_votes(reponses, marques)
    for r in reponses:
        if not r["marque"] or r["marque"].upper().startswith("TEST") or autre_usage(r["format"]):
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
    ecrire_si_change(OUT_JS,
        "// GÉNÉRÉ par tools/signalements.py (3×/jour) — ne pas modifier à la main :\n"
        "// ajouter les prix manuels dans data/signalements_manuels.json\n"
        "window.EAUX_SIGNALES = " + json.dumps(affiches, ensure_ascii=False, indent=1) + ";\n")

    nouveaux = [s for s in publies if s["cle"] not in deja_annonces]
    if nouveaux:
        try:
            telegram(message(nouveaux))
            deja_annonces.update(s["cle"] for s in nouveaux)
        except Exception as e:   # Telegram en panne : on réessaiera au prochain passage
            print("Échec Telegram :", e)
    ecrire_si_change(OUT_JSON, json.dumps({
        "maj": datetime.now().isoformat(timespec="minutes"),
        "publies": len(publies), "rejetes": rejets,
        "annonces": sorted(deja_annonces),
    }, ensure_ascii=False, indent=1))
    print(f"Feuille lue : {len(reponses)} réponse(s). {len(publies)} publié(s), {len(rejets)} rejeté(s), "
          f"{len(nouveaux)} nouveau(x) annoncé(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
