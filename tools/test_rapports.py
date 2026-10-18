"""Rapports du mois (tools/build_rapports.py) : python tools/test_rapports.py — règles § 25 (chiffres vrais, mois fini figé)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_rapports as R  # noqa: E402

ok = ko = 0


def check(nom, cond):
    global ok, ko
    ok, ko = (ok + 1, ko) if cond else (ok, ko + 1)
    print(("OK   " if cond else "ÉCHEC ") + nom)


j = lambda d, pm, st=3.6: {"date": d, "parMarque": pm, "stika15": st, "marques": [min(pm, key=pm.get)]}
serie = [j("2026-09-28", {"A": 0.60, "B": 0.70}), j("2026-09-29", {"A": 0.60, "B": 0.70}), j("2026-09-30", {"A": 0.62, "B": 0.70, "C": 0.5}),
         j("2026-10-01", {"A": 0.66, "B": 0.70}), j("2026-10-02", {"A": 0.66, "B": 0.70}), j("2026-10-03", {"A": 0.66, "B": 0.70})]
h = R.mettre_a_jour({"mois": {}}, serie)
check("une marque avec moins de 3 jours de prix dans le mois n'apparaît pas (C)", "C" not in h["mois"]["2026-09"]["marques"])
check("prix du mois = médiane des prix quotidiens", h["mois"]["2026-09"]["marques"]["A"]["med"] == 0.6 and h["mois"]["2026-10"]["marques"]["A"]["med"] == 0.66)
check("évolution d'une marque présente les deux mois : +10 %", R.variation(0.66, 0.6) == 10 and R.variation(1.0, 0.5) is None)
h["mois"]["2026-09"]["marques"]["A"]["med"] = 0.61          # valeur déjà écrite : un mois fini n'est plus recalculé
h = R.mettre_a_jour(h, serie + [j("2026-10-04", {"A": 0.70, "B": 0.70})])
check("un mois FINI n'est plus jamais modifié", h["mois"]["2026-09"]["marques"]["A"]["med"] == 0.61)
check("le mois en cours est recalculé chaque jour", h["mois"]["2026-10"]["au"] == "2026-10-04" and h["mois"]["2026-10"]["jours"] == 4)
check("date de publication gardée (1er jour où la page a existé)", h["mois"]["2026-10"]["debut"] == "2026-10-03")
check("mois précédent de janvier = décembre", R.mois_precedent("2027-01") == "2026-12")
import re as _re
from pathlib import Path as _P
_rac = _P(__file__).resolve().parent.parent
for _page in sorted(_rac.glob("rapports/[0-9][0-9][0-9][0-9]-[0-9][0-9]/index.html")):
    _h = _page.read_text(encoding="utf-8")
    _m = _re.search(r'og:image" content="https://prix-eau\.clicvia\.com/(rapports/\d{4}-\d{2}/apercu-[0-9a-f]{8}\.jpg)"', _h)
    _f = _rac / _m.group(1) if _m else None
    check(f"{_page.parent.name} : image d'aperçu propre à l'article (Facebook), présente et < 250 Ko",
          bool(_f and _f.exists() and _f.stat().st_size < 250_000 and _m.group(1) in _h.split('"@type": "Article"', 1)[-1]))
print(f"\n{ok} vérifications réussies, {ko} échec(s)")
sys.exit(1 if ko else 0)
