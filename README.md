# Prix des Eaux de Tunisie

Site web (et base d'une future app) qui liste les marques d'eau minérale vendues en Tunisie
avec leurs prix relevés chez les grandes surfaces : **Géant et Carrefour**
(Aziza et Monoprix retirés le 30/09/2026 : pas de source de prix fiable, voir « Mettre à jour les prix »).

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

**Automatique** : le workflow GitHub Actions (`.github/workflows/maj-prix.yml`) tourne
chaque nuit vers 1h du matin (heure de Tunis) sur les serveurs GitHub — PC éteint ou pas —
et publie directement sur le site. (L'ancienne tâche planifiée Windows locale
`PrixEauxTunisie-MAJ` a été supprimée le 28/09/2026 : elle était devenue redondante.)

**Manuel** (copie locale uniquement) : double-clic sur `tools/update_prix.bat`, ou :

```
python tools/collect_prices.py
```

Notes :
- Sources : Carrefour en direct (API GraphQL), Géant Drive en direct. **Monoprix n'est plus
  suivi** (30/09/2026) : barka.tn affichait des produits indisponibles et des prix faux
  (vérifié sur courses.monoprix.tn, qui bloque les robots). **Aziza n'est plus suivi** (30/09/2026) : barka.tn ne donne que les
  prix de l'ancienne boutique en ligne d'Aziza, fermée (prix périmés, signalés par un client) ;
  le site actuel d'Aziza ne publie que des catalogues promo et son API de prix est privée. Si une source est en panne, ses prix du dernier relevé
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

### Nouveaux services (liste du 29/09/2026, par ordre conseillé)

1. **« Quelle eau pour moi ? »** (priorité) : questionnaire (bébé, peu de sodium, sportif,
   calculs rénaux…) qui recommande des eaux d'après `data/composition.js` — bon pour le SEO.
2. ✅ **Alerte prix / promo** — FAIT le 29/09/2026 : bandeau « Baisses de prix aujourd'hui »
   sur le site + publication automatique sur le canal Telegram https://t.me/prixeautunisie
   (`tools/price_drops.py`, secret GitHub `TELEGRAM_BOT_TOKEN`). Plus tard : alerte email
   par marque, recopie éventuelle sur une chaîne WhatsApp.
3. **Calculateur de budget** : taille du foyer → stikas par mois, coût et économie par marque.
4. **Comparer 2 eaux côte à côte** : prix + composition.
5. **Livraison de bonbonnes 19 L** (maisons/bureaux) : livreurs par ville, abonnement,
   consigne — prolonge la fonction de commande.
6. ✅ **Prix signalés par les visiteurs** — FAIT le 30/09/2026 : bouton « 📍 Signaler un prix »
   sur chaque carte → email Formspree → après vérification, ajout dans `data/signalements.js`
   (prix d'une bouteille, date) → affiché 30 jours sur la carte, hors calcul du moins cher.
7. **Carte des magasins** : où trouver chaque marque.
8. **Commande groupée de quartier** : atteindre le minimum de livraison, meilleur prix.
9. **Espace marques / distributeurs** : promos mises à jour par les marques (lien avec la publicité).

### Projet futur : comparateur pour d'autres produits (idée du 29/09/2026, à reprendre)

Réutiliser toute la recette du site de l'eau (scrapers Carrefour/Géant/barka, page,
filtres, MAJ de nuit, historique, alertes Telegram, SEO, GoatCounter) pour d'autres produits.
- **Garder le site de l'eau tel quel** (il marche) ; créer un 2ᵉ site « Prix des courses en
  Tunisie », une page par catégorie, avec des liens croisés.
- **Candidats** : 🍼 lait infantile + couches (1er choix), ☕ café, 🫒 huile d'olive,
  🐟 thon / tomate concentrée / harissa, 🧴 lessive et ménager.
- **À éviter** : produits subventionnés ou à prix fixé (lait demi-écrémé, sucre, farine,
  semoule, pain, huile subventionnée) : même prix partout.
- **Méthode** : un seul produit pilote, mesurer 2-3 semaines sur GoatCounter, puis étendre.
  Fonction phare plus tard : **comparateur de couffin** (liste de courses → magasin le moins cher).
- **Difficultés** : prix à l'unité ou au kg (tailles et paquets variables), filtrage des faux
  produits trouvés par les scrapers.
- **Première action à la reprise** : vérifier (sans rien créer) combien de produits
  Carrefour et Géant ont en ligne pour le produit pilote choisi.

### Autres idées

- **Bannière publicitaire** si une marque d'eau le demande : encart image + lien,
  clairement marqué « Publicité », sans jamais toucher aux prix ni au classement
  (la neutralité du comparateur est toute la valeur du site). Argument de vente :
  les statistiques GoatCounter. Prévoir un statut pour facturer.
- **Nom de domaine + hébergement pro** — décision d'Ahmed (29/09/2026) : achat
  **différé jusqu'au premier annonceur** (pas de dépense avant). Le jour venu :
  un seul domaine suffit (prix-eau.tn en priorité, prix-eaux.tn en protection ;
  vérifiés disponibles au registre ATI le 29/09/2026, ~30-60 DT/an chez un
  registrar agréé type Oxahost — attention à ne pas confondre avec leurs packs
  d'hébergement facturés au mois, inutiles ici). Héberger sur
  Cloudflare Pages ou Netlify (gratuits, publicité autorisée). Migration SANS perte :
  l'ancien site GitHub Pages redirige page par page vers le nouveau domaine (comme
  fait pour le doublon prix-eau-tunisie) + outil « Changement d'adresse » de Search
  Console. Les liens déjà partagés (Facebook, WhatsApp…) continuent de fonctionner —
  rien à repartager.
- Listes privées fournisseurs / livreurs + suivi des commandes (Google Sheets pour commencer)
- Une page par marque (`/safia/`…) pour le référencement Google
- Vrais logos des marques (sites officiels / pages Facebook) à la place des photos de bouteilles
- Historique des prix (relevés datés, courbes d'évolution)
- Prix au litre affiché sur chaque produit
- Marques manquantes : Hayet, Jannet (autres formats), Aïn Mizeb, Bulla Régia…
- Version PWA installable sur téléphone (manifest + service worker impossible en artifact,
  mais possible une fois hébergé, ex. GitHub Pages)
