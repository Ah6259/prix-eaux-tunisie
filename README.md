# Prix des Eaux de Tunisie

Site web (et base d'une future app) qui compare les prix des marques d'eau minérale vendues
en Tunisie (bouteille et **stika**), relevés automatiquement chez **Carrefour**, **Géant** et
l'épicerie en ligne **Otrity**, complétés par les **prix signalés par les visiteurs**.
(Aziza et Monoprix retirés le 30/09/2026 : pas de source de prix fiable, voir « Mettre à jour les prix ».)

**Site public : https://ah6259.github.io/prix-eaux-tunisie/**

> © 2026 — **Tous droits réservés** (voir [LICENSE](LICENSE)). Ce dépôt est public uniquement pour l'hébergement
> gratuit du site : aucune réutilisation du code ou des données sans autorisation écrite.
Dépôt GitHub : https://github.com/Ah6259/prix-eaux-tunisie
(Ancienne version privée Claude : https://claude.ai/artifact/N4YgHUrDQegTPn69Z77DCv)

## Contenu actuel (30/09/2026)

- 35 marques (26 avec prix), ~95 prix relevés chaque jour (Carrefour, Géant, Otrity)
- Comparateur « Gagnant du match 1,5 L », recherche, filtres multi-sélection (minérale / source /
  traitée / gazeuse, formats), tri ; mode **Stika** (6 × bouteille, 12 pour ≤ 0,75 L) ou Bouteille
- **Composition minéralogique** de 32 eaux (Office du Thermalisme, `data/composition.js`)
- **Historique des prix**, pages par marque (`marque/<slug>/`), FAQ, SEO, PWA
- **Alertes** : baisses de prix ≥ 1 % publiées chaque nuit sur le canal Telegram
  https://t.me/prixeautunisie + bandeau « Baisses de prix aujourd'hui »
- **Prix signalés par les visiteurs** (Google Forms → robot toutes les 2 h → site + Telegram)
- **Commande** : panier et formulaire présents mais **fermés** (pas encore de fournisseur) —
  formulaire grisé + tampon « En cours de développement ». Pour rouvrir : retirer
  `disabled` du `fieldset.order-fields` et le bloc `div.tampon` dans `index.html`,
  et remettre le texte de la barre panier dans `app.js`
- **Gagnant du match** (fenêtre) : par le prix (stika 1,5 L la moins chère) et **par le vote des clients**
  (un vote par navigateur via le Google Forms, décompte automatique toutes les 2 h → `data/votes.js`)
- **Votre avis** (Formspree), hadith de la sqya (fenêtre), statistiques privées GoatCounter

## Plan de continuité — si Ahmed n'est plus disponible

Le site tourne **seul** sur les serveurs de GitHub, gratuitement, sans nom de domaine à
renouveler. Ce qui se passe en cas de problème (simulé par `python tools/test_pannes.py`,
16 scénarios) :

| Risque | Ce que fait le système tout seul | À faire par un humain |
|---|---|---|
| Un magasin change son site / tombe en panne | Garde ses derniers prix **7 jours** au plus (mention « Prix Géant du … » dès 2 jours), puis les **retire** | Demander à Claude : « lis le README et répare la collecte des prix de <magasin> » |
| Un site renvoie des prix absurdes (millimes, produits manquants, marques inconnues) | Détecté (« incohérent » / « suspect ») : traité comme une panne | Idem |
| Toutes les sources en panne | Bandeau ⚠️ « prix non mis à jour depuis le … » dès 3 jours ; plus aucun prix après 7 jours | Idem, ou chercher de nouvelles sources |
| Robots GitHub arrêtés | Le site compare la date des prix à la date du visiteur : ⚠️ affiché quand même. Un « battement de cœur » mensuel empêche GitHub de mettre les robots en pause (60 jours sans activité) | Onglet **Actions** du dépôt → réactiver les workflows |
| PC d'Ahmed éteint, volé ou en panne | Seuls les prix **Otrity** disparaissent (après 3 jours) ; tout le reste continue | Sur un nouveau PC : `tools/installer_pc.ps1`. En cas de **vol** : changer le mot de passe GitHub et révoquer les sessions (github.com → Settings → Sessions / Applications), fermer les sessions Telegram et Google de l'appareil volé |
| Compte Google inactif (supprimé après 2 ans) | Les prix signalés ne sont plus lus ; les anciens disparaissent après 30 jours ; rien ne casse | Gestionnaire de compte inactif Google → personne de confiance |
| Compte Telegram inactif | Les alertes s'arrêtent si le canal perd son robot | Telegram → Confidentialité → « Supprimer mon compte si absent » : durée maximale ; ajouter un 2ᵉ administrateur |
| Telegram en panne | Prix publiés quand même ; annonce retentée au passage suivant, sans doublon | — |

**Données privées** : la liste des fournisseurs, livreurs et grossistes (et leurs robots) est dans un dépôt
GitHub **privé** séparé (`dispatch-eau-prive`), jamais dans ce dépôt public.

**Successeur** : ajouter une personne de confiance comme collaboratrice du dépôt GitHub
(Settings → Collaborators), administratrice du canal Telegram et éditrice du Google Forms
« Prix signalés ». Pour toute réparation, ouvrir une session Claude Code dans ce dossier
et lui demander de lire ce README.

## Structure

| Chemin | Rôle |
|---|---|
| `index.html` | La page (structure et textes) — **changer les `?v=` de style.css / app.js à chaque modification** (cache des téléphones) |
| `style.css` | Tout le style (thème clair/sombre) |
| `app.js` | Rendu, filtres, avertissement de fraîcheur, prix signalés, panier |
| `data/eaux.js` / `eaux.json` | Prix (généré — ne pas éditer), avec `statut_sources` |
| `data/otrity.json` | Relevé Otrity fait depuis le PC d'Ahmed |
| `data/signalements*.js/json`, `data/votes.js` | Prix signalés et votes (générés) ; `signalements_manuels.json` = ajouts à la main |
| `data/baisses.*`, `historique.*`, `composition.js` | Baisses du jour, historique, composition |
| `tools/collect_prices.py` | Collecte des prix (Carrefour, Géant, Otrity) + garde-fous |
| `tools/price_drops.py` | Baisses de prix → site + Telegram |
| `tools/signalements.py` | Décision automatique sur les prix signalés → site + Telegram |
| `tools/otrity_local.py`, `tools/installer_pc.ps1` | Relevé Otrity depuis le PC / réinstallation sur un nouveau PC |
| `tools/test_pannes.py` | **Simulateur de pannes (16 scénarios) — à relancer après toute modification du robot** |
| `tools/build_history.py`, `tools/build_pages.py` | Historique, pages par marque, sitemap |

## Robots (GitHub Actions)

| Workflow | Quand | Rôle |
|---|---|---|
| `maj-prix.yml` | chaque nuit ≈ 1h07 (Tunis) | collecte → baisses/Telegram → historique → pages → publication |
| `signalements.yml` | toutes les 2 h, 8h05–22h05 | prix signalés → site + Telegram ; décompte des votes |
| `battement-de-coeur.yml` | le 1er du mois | empêche GitHub de mettre les robots en pause (60 j) |
| `telegram-bienvenue.yml` | à la main | message de présentation sur le canal |
| Tâche Windows « PrixEaux-Otrity » (PC d'Ahmed) | chaque jour 12h | relevé Otrity (bloqué par Cloudflare sur GitHub) |

## Mettre à jour les prix

**Automatique** : le workflow GitHub Actions (`.github/workflows/maj-prix.yml`) tourne
chaque nuit vers 1h du matin (heure de Tunis) sur les serveurs GitHub — PC éteint ou pas —
et publie directement sur le site. Lancement immédiat :
`gh workflow run maj-prix.yml -R Ah6259/prix-eaux-tunisie`.

**Manuel** (copie locale uniquement) : double-clic sur `tools/update_prix.bat`, ou :

```
python tools/collect_prices.py
```

Notes :
- Sources : Carrefour en direct (API GraphQL), Géant Drive en direct. **Monoprix n'est plus
  suivi** (30/09/2026) : barka.tn affichait des produits indisponibles et des prix faux
  (vérifié sur courses.monoprix.tn, qui bloque les robots). **Aziza n'est plus suivi** (30/09/2026) : barka.tn ne donne que les
  prix de l'ancienne boutique en ligne d'Aziza, fermée (prix périmés, signalés par un client) ;
  le site actuel d'Aziza ne publie que des catalogues promo et son API de prix est privée.
  **Otrity** : épicerie en ligne (prix de la stika livrée), lue depuis le PC d'Ahmed car
  Cloudflare bloque GitHub. Monoprix et Jumia exigent une vérification « humain » :
  on ne contourne pas (demander l'autorisation, ou prix signalés).
- Source en panne : ses derniers prix sont gardés **7 jours au plus**, puis retirés ; un résultat
  incohérent (prix en millimes, marques inconnues, trop peu de produits) compte comme une panne.
- Garde-fous : marques d'eau connues uniquement (`MARQUES_EAU`), packs/fardeaux écartés
  (la stika est affichée comme 6 × la bouteille), prix hors 0,25–2,5 DT/L ou supérieurs
  au double de l'offre la moins chère écartés.
- Les métadonnées des marques (source, société, notes) sont dans `META` en tête de
  `tools/collect_prices.py`.
- Les anciens scripts `geant_scrape.py`, `barka_scrape.py` et `build_data.py` sont conservés
  pour référence mais ne sont plus utilisés.

## Déploiement (GitHub Pages)

Site statique servi par GitHub Pages (branche `main`, racine) : chaque commit des robots
redéploie le site en ~1 minute. Le dépôt doit rester **public** (Pages gratuit).
Le dépôt `Ah6259/prix-eau-tunisie` n'est qu'une **redirection** vers ce site : à garder.

## Sources

- [Carrefour Tunisie](https://www.carrefour.tn) — prix (API GraphQL) et images
- [Géant Drive Tunisie](https://www.geantdrive.tn) — prix et images
- [Otrity](https://otrity.com/categorie-produit/boissons/eaux/) — épicerie en ligne (stika livrée)
- Prix signalés par les visiteurs (Google Forms d'Ahmed)
- [Office du Thermalisme via Babnet](https://www.babnet.net/festivaldetail-287073.asp) — composition des eaux
- [Wikipédia — Eaux minérales en Tunisie](https://fr.wikipedia.org/wiki/Eaux_min%C3%A9rales_en_Tunisie) — liste des marques

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
   sur chaque carte → Google Forms d'Ahmed (tableau Google Sheets publié en CSV) → robot
   `tools/signalements.py` toutes les 2 h de 8h à 22h (workflow `signalements.yml`) qui décide seul
   (vraisemblance, écart aux prix connus, doublons = « confirmé ») → affiché 30 jours sur la
   carte (hors calcul du moins cher) + annoncé sur le canal Telegram. Tout est automatique.
   **Plus tard (pas urgent, ~15 min avec Ahmed)** : publication quasi immédiate (2-3 min) —
   script Google Apps Script attaché au formulaire, déclencheur « à l'envoi », qui lance le
   workflow `signalements.yml` via l'API GitHub (`workflow_dispatch`) avec une clé GitHub
   limitée (fine-grained token, Actions : write sur ce seul dépôt) rangée dans le script.
   Garder alors un passage de secours toutes les 2 h.
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
