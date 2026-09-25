# Prix des Eaux de Tunisie

Site web (et base d'une future app) qui liste les marques d'eau minérale vendues en Tunisie
avec leurs prix relevés chez les grandes surfaces : **Géant, Carrefour, Monoprix, Aziza**.

**Site public : https://ah6259.github.io/prix-eaux-tunisie/**
Dépôt GitHub : https://github.com/Ah6259/prix-eaux-tunisie
(Ancienne version privée Claude : https://claude.ai/artifact/N4YgHUrDQegTPn69Z77DCv)

## Contenu actuel (25/09/2026)

- 22 marques, 60 produits, 116 prix relevés
- Visuels de bouteilles (36 images) extraits des catalogues des enseignes
- Comparateur du format 1,5 L, recherche, filtres plate/gazeuse, tri par prix

## Structure

| Chemin | Rôle |
|---|---|
| `index.html` | La page web complète (HTML/CSS/JS vanilla, aucune dépendance) |
| `data/eaux.js` | Données chargées par la page (`window.EAUX_DATA`) — généré, ne pas éditer à la main |
| `data/eaux.json` | Mêmes données en JSON pur (pour une future app / API) |
| `assets/img/` | Photos de bouteilles téléchargées des CDN des enseignes |
| `tools/` | Scripts Python de collecte et de consolidation |

Ouvrir simplement `index.html` dans un navigateur (fonctionne en local, sans serveur).

## Mettre à jour les prix

**Automatique** : la tâche planifiée Windows `PrixEauxTunisie-MAJ` lance `tools/update_prix.ps1`
tous les jours à 9h30 (ou dès que le PC est allumé si l'heure est passée). Elle vide le cache,
relance les 3 scripts et écrit le détail dans `tools/update_log.txt`.
Gérer la tâche : `taskschd.msc` (Planificateur de tâches) → « PrixEauxTunisie-MAJ »,
ou la supprimer avec `Unregister-ScheduledTask -TaskName "PrixEauxTunisie-MAJ"`.

**Manuel** : double-clic sur `tools/update_prix.bat`, ou :

```
cd tools
python geant_scrape.py    # 1. scrape Géant Drive  -> geant_products.json
python barka_scrape.py    # 2. scrape barka.tn     -> barka_products.json (quelques minutes)
python build_data.py      # 3. consolide           -> ../data/eaux.js + eaux.json
```

Notes :
- `barka_scrape.py` met les pages HTML en cache dans `tools/pages/barka/`.
  Le script automatique supprime ce dossier ; en manuel, le **supprimer avant une mise à jour**
  pour forcer un re-téléchargement.
- La version en ligne (artifact) ne se met pas à jour toute seule : demander à Claude
  « mets à jour les prix en ligne » pour la republier avec les données fraîches.
- barka.tn est un comparateur qui agrège Carrefour, Monoprix, Aziza et Géant ;
  les prix Géant viennent en direct de geantdrive.tn (plus frais).
- Les métadonnées des marques (source, société, notes) sont dans `META` en tête de `build_data.py`.
- Certaines marques (Hayet, Cristal Chaâbi, Aïn Mizeb…) ne sont pas encore couvertes :
  barka.tn renvoie une erreur 500 pour elles, il faudra une autre source.

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

- **Fonction de commande** (priorité — la vraie raison de revenir sur le site) :
  permettre au visiteur de composer sa commande (marque, format, bouteille/stika,
  quantité) puis l'envoyer vers l'enseigne la moins chère ou le drive
  (lien direct produit Géant Drive / panier), voire livraison locale à terme

- Vrais logos des marques (sites officiels / pages Facebook) à la place des photos de bouteilles
- Historique des prix (relevés datés, courbes d'évolution)
- Prix au litre affiché sur chaque produit
- Marques manquantes : Hayet, Jannet (autres formats), Aïn Mizeb, Bulla Régia…
- Version PWA installable sur téléphone (manifest + service worker impossible en artifact,
  mais possible une fois hébergé, ex. GitHub Pages)
