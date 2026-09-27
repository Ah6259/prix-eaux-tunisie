# Prix des Eaux de Tunisie

Site web (et base d'une future app) qui liste les marques d'eau minérale vendues en Tunisie
avec leurs prix relevés chez les grandes surfaces : **Géant, Carrefour, Monoprix, Aziza**.

**Site public : https://ah6259.github.io/prix-eaux-tunisie/**
Dépôt GitHub : https://github.com/Ah6259/prix-eaux-tunisie
(Ancienne version privée Claude : https://claude.ai/artifact/N4YgHUrDQegTPn69Z77DCv)

## Contenu actuel (27/09/2026)

- 26 marques, 73 produits, 132 prix relevés (Carrefour, Géant, Monoprix, Aziza)
- Visuels de bouteilles : photos choisies à la main (`assets/img/`) + photos des enseignes
  téléchargées automatiquement (`assets/img/produits/`)
- Comparateur du format 1,5 L, recherche, filtres plate/gazeuse, tri par prix ou par minéralité
- **Commande avec livraison** : bouton + sur chaque produit, panier, adresse + localisation GPS,
  envoi de la commande par WhatsApp (numéro dans `WHATSAPP` en tête de la section commande d'`app.js`)
- **Composition minéralogique** (résidu sec, calcium, sodium, pH…) de 32 eaux, dépliable sur
  chaque carte, valeurs hors repère OMS/UE surlignées — données dans `data/composition.js`
  (statique, entretenu à la main, source : Office du Thermalisme / article Babnet mai 2024)

## Structure

| Chemin | Rôle |
|---|---|
| `index.html` | La page (HTML seul — structure et textes) |
| `style.css` | Tout le style (thème clair/sombre) |
| `app.js` | Tout le JavaScript : rendu, filtres, panier et commande WhatsApp |
| `data/eaux.js` | Données chargées par la page (`window.EAUX_DATA`) — généré, ne pas éditer à la main |
| `data/eaux.json` | Mêmes données en JSON pur (pour une future app / API) |
| `assets/img/` | Photos de bouteilles |
| `tools/collect_prices.py` | Script unique de collecte des prix (remplace l'ancien trio geant/barka/build) |

Ouvrir simplement `index.html` dans un navigateur (fonctionne en local, sans serveur).

## Mettre à jour les prix

**Automatique** : la tâche planifiée Windows `PrixEauxTunisie-MAJ` lance `tools/update_prix.ps1`
tous les jours à 9h30 (ou dès que le PC est allumé si l'heure est passée) et écrit le détail
dans `tools/update_log.txt`. Gérer la tâche : `taskschd.msc` → « PrixEauxTunisie-MAJ ».

**Manuel** : double-clic sur `tools/update_prix.bat`, ou :

```
python tools/collect_prices.py
```

Notes :
- Sources : Carrefour en direct (API GraphQL), Géant Drive en direct, Monoprix et Aziza
  via le comparateur barka.tn. Si une source est en panne, ses prix du dernier relevé
  réussi sont conservés.
- Garde-fous : marques d'eau connues uniquement (`MARQUES_EAU`), packs/fardeaux écartés
  (la stika est affichée comme 6 × la bouteille), prix hors 0,25–2,5 DT/L ou supérieurs
  au double de l'offre la moins chère écartés.
- Les métadonnées des marques (source, société, notes) sont dans `META` en tête de
  `tools/collect_prices.py`.
- Les anciens scripts `geant_scrape.py`, `barka_scrape.py` et `build_data.py` sont conservés
  pour référence mais ne sont plus utilisés.

## Déploiement (GitHub Pages)

Le site est un site statique déployé sur GitHub Pages (branche `main`, racine).
Le workflow [`.github/workflows/maj-prix.yml`](.github/workflows/maj-prix.yml) tourne
tous les jours à 9h30 (heure de Tunis) sur les serveurs GitHub : il re-scrape les prix,
commit `data/` si quelque chose a changé, et GitHub Pages redéploie automatiquement.
Il peut aussi être lancé à la main : onglet **Actions** → « Mise à jour des prix » → *Run workflow*.

## Sources

- [Géant Drive Tunisie](https://www.geantdrive.tn) — prix et images
- [barka.tn](https://barka.tn) — comparateur multi-enseignes
- [Wikipédia — Eaux minérales en Tunisie](https://fr.wikipedia.org/wiki/Eaux_min%C3%A9rales_en_Tunisie) — liste des marques et sources

## Idées pour la suite

- Listes privées fournisseurs / livreurs + suivi des commandes (Google Sheets pour commencer)
- Une page par marque (`/safia/`…) pour le référencement Google
- Vrais logos des marques (sites officiels / pages Facebook) à la place des photos de bouteilles
- Historique des prix (relevés datés, courbes d'évolution)
- Prix au litre affiché sur chaque produit
- Marques manquantes : Hayet, Jannet (autres formats), Aïn Mizeb, Bulla Régia…
- Version PWA installable sur téléphone (manifest + service worker impossible en artifact,
  mais possible une fois hébergé, ex. GitHub Pages)
