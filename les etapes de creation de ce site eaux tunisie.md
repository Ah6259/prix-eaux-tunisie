# Guide : créer et publier un site web (recette réutilisable)

Les étapes exactes suivies pour « Prix des Eaux de Tunisie », généralisées
pour créer n'importe quel autre site.

## Phase 1 — Le contenu

1. **Définir l'idée** : quel problème le site résout-il, pour qui ?
   (ex. : comparer les prix de l'eau pour les Tunisiens)
2. **Collecter les données** : à la main, ou avec des scripts Python qui
   extraient les infos de sites existants (scraping), images comprises
3. **Organiser les données** dans un fichier JSON propre (`data/…`)

## Phase 2 — La page web

4. **Créer `index.html`** : HTML pour la structure, CSS pour le style,
   JavaScript pour l'interactivité (recherche, filtres, tri…).
   Un seul fichier suffit, pas besoin de framework compliqué
5. **Tester en local** : double-clic sur `index.html` → vérifier dans le
   navigateur, sur PC et en largeur téléphone

## Phase 3 — Mise en ligne (gratuite, GitHub Pages)

6. **Créer un dépôt git** dans le dossier : `git init`, `git add -A`, `git commit`
7. **Compte GitHub** (github.com, gratuit) + installer GitHub CLI (`gh`)
   et se connecter : `gh auth login`
8. **Publier** : `gh repo create mon-site --public --source . --push`
9. **Activer GitHub Pages** (Settings → Pages → branche main, ou
   `gh api repos/USER/REPO/pages -X POST -f "source[branch]=main" -f "source[path]=/"`)
   → le site est public sur `https://USER.github.io/mon-site/`

## Phase 4 — Automatisation (si les données changent)

10. **Workflow GitHub Actions** (`.github/workflows/…yml`) : un robot qui
    tourne chaque jour sur les serveurs GitHub, relance les scripts de
    données et re-publie — même PC éteint. Gratuit

## Phase 5 — Finitions professionnelles

11. **Logo / favicon** : icônes 512/192/180/32 px + `manifest.webmanifest`
    → belle icône dans l'onglet et à l'installation sur téléphone
12. **Partage social** : balises Open Graph + image 1200×630 px
    → le lien partagé sur Facebook/WhatsApp affiche une belle carte

## Phase 6 — Visibilité et mesure

13. **Statistiques privées** : compte GoatCounter (gratuit) + une ligne de
    script invisible → voir ses visiteurs (pays, appareils, provenance)
14. **SEO sur la page** : titre riche en mots-clés, meta description,
    vrai texte visible (intro + section FAQ avec les questions que les gens
    tapent dans Google), données structurées JSON-LD (WebSite, FAQPage),
    balise canonical, attributs alt sur les images
15. **Google Search Console** : déclarer le site (balise de vérification),
    soumettre `sitemap.xml`, « Demander une indexation »
    → apparaît dans Google sous quelques jours
16. **Faire connaître (liens externes)** : partager dans les groupes Facebook
    ciblés, WhatsApp, Reddit… Chaque lien vers le site depuis un autre site
    (backlink) et chaque visite font monter le site dans Google

## Les outils utilisés (tous gratuits)

| Outil | Rôle |
|---|---|
| Python | scripts de collecte de données |
| HTML/CSS/JavaScript | la page elle-même |
| git + GitHub | historique du code et hébergement |
| GitHub Pages | serveur public gratuit |
| GitHub Actions | automatisation quotidienne |
| GoatCounter | statistiques de visite privées |
| Google Search Console | référencement Google |
