# -*- coding: utf-8 -*-
"""Alerte « enseigne en panne » (15/10/2026, règle commune § 17 : aucun robot vert qui ne fait rien).

Quand une enseigne ne répond plus, collect_prices.py reprend ses anciens prix quelques jours puis les retire : c'est voulu,
mais le robot restait VERT et personne n'était prévenu (même défaut que Century 21 sur le site Immobilier, 12-15/10/2026).
Lancé APRÈS la publication par maj-prix.yml : une enseigne automatique dont le dernier relevé réussi date de plus de JOURS
jours -> échec (GitHub prévient Ahmed par e-mail). Monoprix (relevé à la main, « manuel ») n'est pas concerné.
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

JOURS = 2
ATTENDUES = ("carrefour", "geant")   # enseignes relevées par le robot sur GitHub (15/10/2026)
ROOT = Path(__file__).resolve().parent.parent


def en_panne(d, jour):
    lim = (jour - timedelta(days=JOURS)).isoformat()
    st = dict(d.get("statut_sources") or {})
    for k in ATTENDUES:                    # enseigne qui n'a JAMAIS réussi un relevé (absente du statut) : en panne aussi
        st.setdefault(k, {})
    return [(k, v.get("dernier_ok")) for k, v in sorted(st.items())
            if not v.get("manuel") and (v.get("dernier_ok") or "") < lim]


if __name__ == "__main__":
    for _f in (sys.stdout, sys.stderr):
        if hasattr(_f, "reconfigure"):
            _f.reconfigure(encoding="utf-8", errors="replace")
    d = json.loads((ROOT / "data" / "eaux.json").read_text(encoding="utf-8"))
    p = en_panne(d, date.today())
    for k, r in p:
        print(f"ÉCHEC enseigne {k} : dernier relevé réussi le {r or 'jamais'} — à réparer (ses prix disparaissent du site)")
    sys.exit(1 if p else 0)
