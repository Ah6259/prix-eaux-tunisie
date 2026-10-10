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
print("\nTOUT PASSE" if not erreurs else f"\n{erreurs} PROBLÈME(S)")
sys.exit(1 if erreurs else 0)
