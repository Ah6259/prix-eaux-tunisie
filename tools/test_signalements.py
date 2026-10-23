# -*- coding: utf-8 -*-
"""Le robot des prix ignore les lignes du même Google Forms qui ne sont pas des prix (votes, Points d'eau, Mosquées en Tunisie).
python tools/test_signalements.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import signalements as S  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
erreurs = 0


def check(desc, ok):
    global erreurs
    print(("OK   " if ok else "FAIL ") + desc)
    erreurs += 0 if ok else 1


check("VOTE ignoré", S.autre_usage("VOTE") and S.autre_usage(" vote "))
check("POINT, POINT-OK, POINT-KO (Points d'eau Tunisie) ignorés", all(S.autre_usage(f) for f in ("POINT", "POINT-OK", "POINT-KO")))
check("LIEU-PRIERE, LIEU-PRIERE-OK, LIEU-PRIERE-KO (Mosquées en Tunisie) ignorés", all(S.autre_usage(f) for f in ("LIEU-PRIERE", "LIEU-PRIERE-OK", "lieu-priere-ko")))
check("un vrai format de prix n'est PAS ignoré", not any(S.autre_usage(f) for f in ("Pack 6 x 1,5 L", "1,5 L", "Bidon 5 L", "")))
# audit des robots du 10/10/2026 : un fichier dont SEULE la date « maj » change n'est pas réécrit
# (sinon un commit et une publication du site à chaque passage, pour rien)
import pathlib as _pl, tempfile as _tf
_f = _pl.Path(_tf.mkdtemp()) / "signalements.json"
check("1re écriture : fichier créé", S.ecrire_si_change(_f, '{"maj": "2026-10-10T08:05", "publies": 1}') and _f.exists())
check("même contenu, seule la date change : fichier NON réécrit (pas de commit inutile)",
      not S.ecrire_si_change(_f, '{"maj": "2026-10-10T10:05", "publies": 1}') and "08:05" in _f.read_text())
check("vrai changement : fichier réécrit avec la nouvelle date",
      S.ecrire_si_change(_f, '{"maj": "2026-10-10T12:05", "publies": 2}') and "12:05" in _f.read_text())
_j = _pl.Path(_tf.mkdtemp()) / "votes.js"
S.ecrire_si_change(_j, 'window.EAUX_VOTES = {"maj": "2026-10-10T08:05", "total": 3};\n')
check("votes.js : seule la date change → non réécrit", not S.ecrire_si_change(_j, 'window.EAUX_VOTES = {"maj": "2026-10-11T08:05", "total": 3};\n'))

# Feuille des signalements illisible (23/10/2026, règles § 17 et § 38) : relue 2 fois, rouge seulement après 2 jours ;
# une feuille lisible SANS nouveau signalement reste verte. Sans réseau : fausses réponses, attentes simulées.
import json as _json
from datetime import datetime as _dtm, timedelta as _td
_tmp = _pl.Path(_tf.mkdtemp())
S.OUT_JSON, S.OUT_JS, S.OUT_VOTES = _tmp / "signalements.json", _tmp / "signalements.js", _tmp / "votes.js"
S.telegram = lambda *a, **k: None
ENTETE = b"Horodateur,marque,format,eau,prix,unite,magazin,lieu,date\n"
HTML = b"<!DOCTYPE html><html><head><title>Google Sheets - connexion</title></head><body>Se connecter</body></html>"
_attentes = []
_att = _attentes.append
NOW = _dtm(2026, 10, 23, 10, 5)


def _lecteur(*reponses):
    it = iter(reponses)

    def lire():
        r = next(it)
        if isinstance(r, Exception):
            raise r
        return r
    return lire


def _etat():
    return _json.loads(S.OUT_JSON.read_text(encoding="utf-8")) if S.OUT_JSON.exists() else {}


for quoi, rep in (("page HTML de connexion", HTML), ("réponse vide", b""), ("erreur réseau", RuntimeError("curl 6 : hôte introuvable")),
                  ("CSV sans les bonnes colonnes", b"Nom,Valeur\nx,1\n")):
    _attentes.clear()
    try:
        S.lire_feuille(_lecteur(rep, rep, rep), _att, horloge=lambda: 0)
        check(f"{quoi} : refusée", False)
    except S.FeuilleIllisible as e:
        check(f"{quoi} : refusée après 3 lectures (attentes 2 puis 4 min) — « {e} »", _attentes == [120, 240])
_attentes.clear()
check("panne passagère : 1re lecture en échec, 2e bonne -> feuille lue, une seule attente de 2 min",
      S.lire_feuille(_lecteur(HTML, ENTETE), _att, horloge=lambda: 0) == ENTETE.decode() and _attentes == [120])
_attentes.clear()
try:
    S.lire_feuille(_lecteur(HTML, HTML, HTML), _att, horloge=iter([0, 7 * 60, 7 * 60]).__next__)
except S.FeuilleIllisible:
    pass
check("budget de 8 min dépassé : pas de nouvel essai", _attentes == [])

# Au niveau du robot entier (main)
check("feuille illisible (1er passage) -> robot VERT (code 0), début de la panne noté, site non touché",
      S.main(_lecteur(HTML, HTML, HTML), _att, NOW) == 0 and _etat().get("feuille_illisible_depuis") == "2026-10-23T10:05"
      and not S.OUT_JS.exists())
check("toujours illisible 1 jour après -> encore VERT, date de début gardée",
      S.main(_lecteur(HTML, HTML, HTML), _att, NOW + _td(days=1)) == 0 and _etat()["feuille_illisible_depuis"] == "2026-10-23T10:05")
check("illisible depuis plus de 2 jours -> robot ROUGE (code 1)", S.main(_lecteur(HTML, HTML, HTML), _att, NOW + _td(days=2, hours=1)) == 1)
check("feuille lisible sans aucun signalement -> robot VERT, panne effacée",
      S.main(_lecteur(ENTETE), _att, NOW + _td(days=3)) == 0 and "feuille_illisible_depuis" not in _etat() and S.OUT_JS.exists())
S.OUT_JSON.unlink()
check("feuille lisible sans nouveau signalement (1er passage) -> VERT", S.main(_lecteur(ENTETE), _att, NOW) == 0)

print("\nTOUT PASSE" if not erreurs else f"\n{erreurs} PROBLÈME(S)")
sys.exit(1 if erreurs else 0)
