# Mémoire du projet — Prix des Eaux de Tunisie

> ## 🔔 À MONTRER À AHMED DÈS LE DÉBUT DE LA PROCHAINE SESSION (demandé le 30/09/2026)
> Premier message de la session : lui donner ce lien et lui demander si le prépaiement Google est crédité :
> **https://console.cloud.google.com/billing?project=prix-eau-tunisie**
> - Si le message « Votre essai sans frais nécessite un prépaiement » a disparu (crédit de 30 $ visible) :
>   1. le guider pour le **plafond de requêtes par jour** : Places API (New) → Quotas (ex. 200 requêtes/jour) ;
>   2. recréer le **budget d'alerte** (échec le 30/09) ;
>   3. lancer le robot sur 5 grossistes : `gh workflow run telephones.yml -R Ah6259/dispatch-eau-prive -f max=5`,
>      vérifier, puis le passage complet.
> - Sinon : patienter, ne JAMAIS repayer ni cliquer « Créer un compte de facturation ».
> Supprimer ce bloc une fois ces étapes terminées.

Fichier lu automatiquement par Claude Code au début de chaque session dans ce dossier.
**À tenir à jour à chaque « update workflow »** (en même temps que le README et le guide).
Dépôt PUBLIC : ne rien écrire ici de personnel ni de secret.

## Qui et comment travailler
- Propriétaire : Ahmed (compte GitHub `Ah6259`), débutant en git/web. Expliquer simplement, **en français**.
- **Toujours demander avant d'installer un logiciel.**
- Ahmed veut que **tout soit automatique** (il ne veut rien vérifier à la main).
- Noter chaque nouvelle étape dans « les etapes de creation de ce site eaux tunisie.md » (guide réutilisable).
- « update workflow » = mettre à jour CLAUDE.md + README + guide, puis commit/push.

## Le site
- Public : https://ah6259.github.io/prix-eaux-tunisie/ — dépôt `Ah6259/prix-eaux-tunisie` (GitHub Pages, branche main).
  Doit rester **public** (Pages gratuit). `gh` : "C:\Program Files\GitHub CLI\gh.exe".
- `Ah6259/prix-eau-tunisie` = simple **redirection** à garder (liens partagés + référencement). Ne pas y remettre de noindex ni de scraping.
- 35 marques, prix bouteille + **stika** (6 × bouteille, 12 si ≤ 0,75 L).
- Cache des téléphones : **changer le `?v=` de style.css / app.js dans index.html à chaque modification (style.css et protection.js : 20261006b, aussi `CSS_V` de build_guides.py).**
- Image d'aperçu des liens partagés : `assets/og-image-v7.jpg` (05/10 : texte à gauche + nouvelle icône goutte + photo NEUTRE de l'eau versée à droite ; modèle `tools/og-image.html`, capture Edge 1200×630 puis JPEG qualité 88 ; aussi sur les 2 guides et les 35 pages marques, avec og:image:type JPEG), volontairement **sans nombre de marques ni noms de magasins**
  (l'ancienne affichait « 22 marques, Monoprix, Aziza »). Si on la change : nouveau nom de fichier (WhatsApp/Facebook gardent l'ancienne en cache).
- Tests d'affichage mobile : headless Chrome dans des iframes de 340/390 px (les petites fenêtres sont ignorées).

- **Photo du bandeau bleu (05/10)** — **RÈGLE (Ahmed) : photo SANS AUCUNE MARQUE, NEUTRE** (sinon les visiteurs croient à une
  publicité : l'ancienne montrait 5 marques), sans visage ni logo lisible, et NETTE (la photo floue du rayon n'était « pas claire »).
  Actuelle : eau versée d'une bouteille sans étiquette dans un verre (« Person pours water from a bottle into a glass in a kitchen.jpg »,
  Shixart1985, **CC BY 2.0** → crédit obligatoire), recadrée en bande AU-DESSUS du texte (`figure.hero-bande`,
  `assets/photo-neutre-eau-versee.jpg` 1440×173 + `-720.jpg` ; le test exige des fichiers `photo-neutre-*`).
  Rien par-dessus (pas de dégradé ni de flou) ; crédit en haut à droite de la photo (`.credit-photo`) et dans le pied de page ;
  preuve dans `preuves conditions d'utilisation/2026-10-05/photos/` (ignoré par git). La carte « La moins chère » ne doit pas descendre.
- **CSP : aucun gestionnaire en ligne** (`onerror=`, `onclick=`… interdits, bloqués par la CSP) : app.js utilise un écouteur
  global (ex. logo d'enseigne introuvable → `document.addEventListener("error", …, true)`) ; vérifié par test_site.mjs.
- **Pas de traduction automatique (05/10)** : `translate="no"` sur `<html>` + `<meta name="google" content="notranslate">`
  sur toutes les pages (index.html et gabarits de build_guides.py / build_pages.py) — Chrome traduisait en anglais les pages FR/AR.
- **Sécurité / anti-copie (05/10, consigne d'Ahmed)** : robots.txt interdit les robots d'IA et aspirateurs (moteurs de recherche permis) ;
  sur toutes les pages (accueil, guides, 35 marques — via les gabarits de `build_guides.py` / `build_pages.py`) : meta `noai, noimageai`,
  referrer, **CSP** (scripts : le site + gc.zgo.at + cdnjs ; envois : docs.google.com, formspree.io, goatcounter ; tuiles OpenStreetMap)
  et `protection.js` (pas de clic droit/glisser sur les photos, source ajoutée au texte copié, anti-iframe). **Aucun script
  en ligne ni `onerror=` dans les pages** (la CSP les bloque). Nouveau service externe dans app.js → l'ajouter à la CSP (le test le vérifie).

## Sources de prix
- **Carrefour** (API GraphQL) et **Géant Drive** (HTML) : lus en direct chaque nuit. Géant : `curl -k` en cas d'erreur de certificat (code 60).
- **Otrity** (épicerie en ligne, prix = stika livrée ÷ 6 ou 12) : Cloudflare bloque GitHub → relevé depuis le PC
  d'Ahmed par la tâche Windows « PrixEaux-Otrity » (12h, `tools/otrity_local.py` → `data/otrity.json`, ignoré après 3 jours).
  Nouveau PC : `tools/installer_pc.ps1`.
- **Aziza et Monoprix retirés** (30/09/2026) : barka.tn donnait des prix périmés / produits indisponibles.
  Monoprix et Jumia exigent une vérification « humain » : **pas de contournement** (demander l'autorisation ou prix signalés).
  Relevé depuis le PC seulement si le site laisse passer un particulier.

- **Photos libres des marques sans magasin** (05/10) : `data/photos_libres.json` (Open Food Facts, CC BY-SA ; images
  `assets/img/libres/`) appliquées par `collect_prices.appliquer_photos_libres` seulement si aucune photo de magasin ;
  crédit sous la photo + pied de page ; `sans_image_libre` = marques cherchées sans résultat. Hors ligne : `python tools/apply_meta.py`.
- **Règle (Ahmed, 04/10)** : chaque nouvelle enseigne ajoutée doit avoir **son logo officiel, dans ses couleurs**
  (robot `logos.yml` avec le champ « sites », puis recadrage dans `assets/logos/` + entrée dans `LOGOS` d'app.js).
- **Recherche quotidienne de nouvelles sources** (demande d'Ahmed, 04/10) : Routine Claude « Nouvelles sources de prix »
  chaque matin ; carnet `tools/sources_a_explorer.md` ; test de lecture depuis GitHub par le robot `tester-source.yml`.
  Elle propose, elle n'ajoute rien au site sans l'accord d'Ahmed.

## Robots (GitHub Actions)
- `maj-prix.yml` ≈ 1h07 Tunis : collect_prices → price_drops (Telegram) → build_history → build_pages → commit.
- `signalements.yml` toutes les 2 h de 8h05 à 22h05 : prix signalés (Google Forms → CSV) → site + Telegram.
- `battement-de-coeur.yml` le 1er du mois (évite la pause GitHub après 60 jours sans activité).
- `instagram.yml` chaque lundi 9h05 : `tools/image_semaine.py` → image 1080×1350 « les 5 stikas les moins chères »
  + texte (assets/instagram/) envoyés sur le canal Telegram ; Ahmed les repost sur Instagram.
- `logos.yml` (manuel) : télécharge les logos d'une enseigne ; `tester-source.yml` (manuel) : vérifie si GitHub peut lire un site.
- `telegram-bienvenue.yml` manuel. Groupe de concurrence commun `maj-prix`. Secret : `TELEGRAM_BOT_TOKEN`.
- Relancer à la main : `gh workflow run maj-prix.yml -R Ah6259/prix-eaux-tunisie`.

## Robustesse
- `statut_sources` dans data/eaux.json ; source en panne → anciens prix gardés **7 jours** max puis retirés ;
  panne aussi si < 50 % d'offres plausibles ou < 30 % du nombre précédent.
- Le site avertit selon la date du **visiteur** (ℹ️ enseigne ≥ 2 j, ⚠️ tout ≥ 3 j ou aucun prix).
- **`python tools/test_pannes.py` (16 scénarios) à relancer après toute modification du robot.**
- **`node tools/test_site.mjs` (139 vérifications de la page d'accueil) à relancer après toute modification du site.**
- Affichage (06/10/2026) : `[hidden]{display:none!important}` dans style.css + **pas de faux boutons** (badges « Prix relevés / Sources citées / Gratuit » supprimés, info gardée en texte dans le bandeau avec le lien « sources citées ») ; test_site.mjs vérifie les deux (accueil, guides, marques).
  Il faut jsdom, installé une fois par PC : `npm install --no-save --no-package-lock jsdom` (node_modules ignoré par git).
- **`node tools/test_sw.mjs`** (service worker, faux navigateur ; accepte un dossier en argument pour tester une copie sabotée).
  `tests.yml` lance à chaque push : YAML des robots + test_site.mjs + test_sw.mjs + test_pannes.py (e-mail de GitHub si échec).
- **Service worker** (05/10/2026, installation complète Chrome/Android + iPhone) : `sw.js` à la racine, portée `/prix-eaux-tunisie/`,
  enregistré à la fin de `protection.js` (chargé par TOUTES les pages ; https seulement, try/catch ; app.js non touché).
  **Réseau d'abord** pour les pages HTML et les données (`data/*.js` sans ?v=, JSON : le visiteur voit toujours les prix du jour ;
  le cache ne sert que hors connexion, sinon page « Hors connexion » FR+AR) ; CSS/JS/images avec `?v=` : cache puis mise à jour.
  Jamais en cache : non-GET, autres origines (Google Forms, Formspree, GoatCounter, Telegram, OpenStreetMap, polices), autres sites d'Ahmed.
  Caches `prix-eaux-tunisie-<CACHE_VERSION>` (on ne supprime QUE les nôtres : origine partagée). Vieille version bloquée → changer
  `CACHE_VERSION`. Manifeste + apple-touch-icon + meta iPhone (`apple-mobile-web-app-capable`, `-title` « Prix Eaux ») sur l'accueil
  ET dans les gabarits de build_pages.py / build_guides.py (`CSS_V` de build_guides.py = même ?v= que index.html).
- Toujours lire les « échec » dans les journaux des robots (la reprise des anciens prix masque les pannes).

## Fonctions
- Canal Telegram https://t.me/prixeautunisie : baisses ≥ 1 % (prix stika) + prix signalés. Bouton « Alertes / PROMO ».
- Prix signalés 100 % automatiques : Google Forms (SIG_FORM dans app.js, champ « magazin » [sic]) → `tools/signalements.py`
  (plausibilité, ≤ 40 % de la médiane, doublons = « confirmé ») → affichés 30 jours, hors classement.
  Ajouts manuels : `data/signalements_manuels.json`.
  Prix ≥ 100 lu en millimes (3900 = 3,900 DT). Les barres « Gagnant du match », hadith et « Signaler un prix »
  ouvrent chacune une FENÊTRE (help-pop) ; celle de Signaler = section formulaire dépliable + derniers prix signalés.
- Vote « mon eau préférée » (fenêtre Gagnant du match) : envoyé au même Google Forms avec format = VOTE et un jeton
  anonyme du navigateur dans « lieu » ; `tools/signalements.py` compte un vote par navigateur → `data/votes.js`.
- **Commande FERMÉE** (pas encore de fournisseur) : `fieldset.order-fields` disabled + tampon `div.tampon`.
  Rouvrir : retirer `disabled` + le tampon, remettre « prix et livraison confirmés sur WhatsApp » dans app.js.
  À la réouverture : ajouter aussi la carte publique des gouvernorats desservis (nombre de fournisseurs PARTENAIRES
  par gouvernorat, jamais de noms ni d'adresses) — décision d'Ahmed, pas avant.
- « Votre avis » : Formspree (mwlpakqj). Statistiques : GoatCounter (sans cookies) sur l'accueil, les pages marques et
  les guides (balise dans `pied()` de build_guides.py). Le même compteur `prix-eaux-tunisie.goatcounter.com` sert aussi
  aux autres sites d'Ahmed (outils pratiques, appels d'offres, code de la route, documents, portail), séparés par chemin.
- Grossistes : 494 grossistes actifs trouvés au Registre National des Entreprises (API publique `rne-api`, recherche par activité),
  classés par gouvernorat et fiabilité ★. Téléphones : robot Google Places du dépôt privé (clé dans ses secrets).
- Fournisseurs / livreurs : **dépôt PRIVÉ `Ah6259/dispatch-eau-prive`** (dossier local `../dispatch-eau-prive`,
  Excel `fournisseurs/fournisseurs-livreurs.xlsx`, données RNE dans `data/rne/`) — ne jamais les mettre dans ce dépôt public.
  Suivi quotidien : application Claude « Dispatch Eau ».
  Contexte : pénurie d'eau en bouteille été 2026 (saisies pour spéculation) → rôle d'intermédiaire plutôt que stockage.

## Commande automatisée — cahier des charges d'Ahmed (30/09/2026, à construire à la réouverture)
1. Le client passe commande sur le site (produits, adresse, position).
2. Le fournisseur partenaire de la zone reçoit la demande, **indique SES prix** et **confirme d'un clic**.
3. Le client reçoit ce prix et **confirme** (ou refuse).
4. Le fournisseur confirme le départ → le client voit « **en cours de livraison** » ; puis « livrée ».
Tout automatique (Dispatch Eau = tableau de bord d'Ahmed). Liste des fournisseurs = secret (dépôt privé proposé).
Pistes techniques proposées : robots dans un dépôt GitHub PRIVÉ ; téléphones via l'API Google Places (clé d'Ahmed,
quota gratuit, carte bancaire exigée par Google → plafond de dépense) + Pages Jaunes / OpenStreetMap en complément.

## Interface (état au 04/10/2026)
- En haut : titre + bouton « Alertes / PROMO » (Telegram), ligne « Mis à jour le… · N marques · N enseignes ».
- **Identité** (retour des visiteurs : le site doit dire ce qu'il est) : prix des magasins tunisiens, **indicatifs**,
  relevés dans les grandes surfaces et épiceries en ligne + prix signalés ; pour la future commande, **le prix final
  dépendra du fournisseur et du stock au moment de la livraison**.
- **La réponse sans clic** : carte verte « 💧 La moins chère aujourd'hui » (stika ou bouteille 1,5 L ; ligne courte
  « Stika (6 × 1,5 L) – Géant » ; petit bouton vert « ➦ Partager » WhatsApp sous le prix, 04/10) + top 5, puis
  « Voir le classement complet » (renderCompare dans #compare). Le prix le moins cher n'est affiché QU'ICI.
- Quatre barres (même style, une ligne sur téléphone) qui ouvrent une FENÊTRE : « ❤️ L'eau préférée des clients » (vote seul),
  « ۞ الماء في القرآن الكريم والحديث النبوي » (bouton « اقرأ » → versets du Coran puis hadiths sur l'eau, en arabe, 04/10), « 📍 Signaler un prix vu en magasin », « 🚚 Commande & livraison BIENTÔT » (explique la future commande :
  ce ne sont PAS les grandes surfaces qui livrent, grossistes/dépôts partenaires à leurs prix, 4 étapes, alerte d'ouverture).
  Les petits boutons-étiquettes ont été retirés (03/10 : en double et hors du premier écran).
- Telegram des prix signalés : UN message court par passage (une ligne par prix + lien « Signaler un prix »).
- `COMMANDE_OUVERTE = false` dans app.js. Boutons « + » et barre « Commander 🛒 » **visibles** (Ahmed les veut, 03/10) ;
  le panier mène au formulaire grisé + tampon.
- Droits : LICENSE « tous droits réservés » + mention © en pied de page.
- **Barre des filtres (04/10, demande d'Ahmed)** : 3 boutons sur une ligne (Stika/Bouteille · Type d'eau · Format),
  chacun ouvre un petit panneau (`.dd` / `.dd-panel`) ; le bouton affiche le choix actuel. Le tri est au-dessus de la liste des marques.
- **Logos des enseignes (04/10)** devant le nom du magasin (`LOGOS` / `enseigne()` dans app.js, fichiers `assets/logos/`) :
  Carrefour = icône + nom ; Géant = logo de geant.tn (figurine verte + « Géant » rouge) à la place du texte. Téléchargés depuis les sites par le robot
  manuel `logos.yml` (`tools/chercher_logos.py`). Otrity : bloqué pour GitHub → `tools/otrity_local.py` rapporte une fois
  `assets/logos/otrity.png` depuis le PC (sinon le nom reste en texte).
- Prochaine amélioration conseillée : cartes compactes.
- **Règle** : demander l'accord d'Ahmed avant de modifier le site (sauf s'il dit « fais »).

## Mise à jour du 05/10/2026 (design pro, photos, sécurité, installation)
- **Design pro** : en-tête blanc avec logo, bandeau bleu avec la photo NEUTRE (eau versée dans un verre, sans aucune
  marque : sinon les visiteurs croient à de la publicité), badges de confiance, icônes SVG, pied de page complet.
  Retour en arrière possible : tag git `avant-design-pro`.
- **Photos des bouteilles** : catalogues des magasins ; pour les marques sans magasin, photos LIBRES d'Open Food Facts
  (`data/photos_libres.json`, appliquées par `appliquer_photos_libres()` dans collect_prices.py, crédit affiché) :
  Tiba, Royal. Sans photo libre : Aziz, Bulla Régia, Saha, Rayan (Rayan serait devenue Élixir en 2015 → à confirmer).
- **Tri par résidu sec** : le filtre de format ne retire aucune marque (Hayet, vendue seulement en 1 L, est 1re).
- **Sécurité** : CSP stricte en meta (aucun script en ligne ni attribut `on…=`), meta noai, `protection.js`
  (anti-copie légère, anti-iframe), robots.txt COMMUN au site racine ah6259.github.io (robots d'IA interdits).
- **Installation sur téléphone** : `manifest.webmanifest` avec `"id": "/prix-eaux-tunisie/"`, service worker `sw.js`
  (réseau d'abord, cache seulement hors connexion), meta iPhone ; testé (`tools/test_sw.mjs`).
- **Partage** : image d'aperçu JPEG < 250 Ko (`og-image-v7.jpg`, sinon WhatsApp montre une petite vignette), aussi sur
  les 35 pages marques ; pas de traduction automatique (`translate="no"` + meta notranslate).
- **Statistiques** GoatCounter sur toutes les pages (le même compteur sert aux 5 sites, séparés par chemin).
- **Tests** : `node tools/test_site.mjs`, `node tools/test_sw.mjs`, `python tools/test_pannes.py` (18 scénarios), lancés
  aussi par `tests.yml` à chaque envoi.
- **Reste à faire (audit du 05/10)** : alerte quand une source de prix tombe en panne ; `data/baisses.js` manquant (404) ;
  texte Google « livrer à domicile » alors que la commande est fermée ; logo Otrity 404 ; `.gitattributes`.

## Visibilité (03/10/2026)
- Trafic : ~50 % Google, ~50 % Instagram. Partage WhatsApp : petit bouton « Partager » sur l'accueil ; gros bouton sur les pages marques et guides.
- Pages guides générées chaque nuit par `tools/build_guides.py` (appelé par build_pages) : `prix-stika/` (FR+AR, FAQ JSON-LD)
  et `quelle-eau/` (sodium, légèreté, calcium, magnésium d'après composition.js). Dans le sitemap et le pied de page.
- Titres des pages marques avec le prix de la stika ; lignes en arabe (mots latins isolés par U+2068/U+2069).
- Encore à faire par Ahmed : lien du site dans la bio Instagram ; demander l'indexation des 2 guides dans Search Console.
  Proposé : message aux journalistes (pénurie d'eau) et textes pour groupes Facebook.

## Décisions et idées en attente
- Nom de domaine (prix-eau.tn) acheté **seulement au premier annonceur** — ne pas le proposer avant.
- Reporté : publication immédiate des prix signalés (Apps Script onFormSubmit → workflow_dispatch).
- Idées : README « Nouveaux services » (prochain conseillé : « Quelle eau pour moi ? ») ; comparateur d'autres produits (mis de côté) ;
  vrais logos ; marques manquantes (Ovia…).
- Plan de continuité : voir README.

## Autres sites d'Ahmed (05/10/2026) — même méthode, mêmes règles
Outils pratiques, Appels d'offres, Code de la route, Documents Tunisie, + site racine ah6259.github.io (robots.txt COMMUN,
vérification Google Search Console). Dans le dossier parent `_claude code project\` : `nouveau site - procedure.md`
(procédure pour tout nouveau site), `regles communes a tous les sites.md`, `securite commune - consigne.md`,
`liste des idees de sites.md`. Toute remarque d'Ahmed sur un site s'applique à tous.

## Mise à jour du 05/10/2026 (soir)
- **Icône (famille commune des 5 sites)** : un seul symbole en aplats 2-3 tons, accent doré `#F2B33D`, sans texte ni brillance (règle d'Ahmed : jamais d'effet « image IA » ni de clip-art). Ce site : **goutte (blanc / bleu clair, eau en bas)**. Source = `assets/icons/icon.svg` ; PNG 192/512 = dessin arrondi, maskable 512 et iPhone 180 = même dessin sur carré plein, symbole à 78 %. Générateur (hors dépôt) : `_claude code project/icones des sites - generateur.py`. Changer l'icône → renouveler `CACHE_VERSION` de `sw.js`.
- **« Gratuit » mis en avant** (titres Google, descriptions, aperçus de partage, manifeste), seulement là où c'est vrai. La future partie payante n'est jamais annoncée à l'avance (décision d'Ahmed).
- **Aperçus WhatsApp** : tous les sites sont réglés pareil (1200 × 630, JPEG léger). WhatsApp sur PC fait de petites vignettes : envoyer les liens depuis le téléphone (ou transférer un message préparé sur le téléphone).
- **Règle d'Ahmed : tout tourne sur internet (GitHub), sans son PC ni son intervention, « même s'il meurt ».**
- Logo d'en-tête = même goutte, en ligne dans index.html et dans `LOGO_SVG` de `tools/build_guides.py` (pages marques et guides).
- Icône adaptative Android dédiée : `assets/icons/icon-maskable-512.png` (le manifeste ne réutilise plus icon-512).
- Titres : « comparateur gratuit » (accueil, 35 pages marques via build_pages.py, guides via build_guides.py).
- Reste dépendant du PC : relevé Otrity (Cloudflare bloque GitHub) → chercher une autre source accessible depuis GitHub.
- **Boutons « Partager » harmonisés** (06/10/2026, demande d'Ahmed, pas de doublon dans l'en-tête : le site avait déjà ses boutons) : `protection.js` intercepte tout lien `https://wa.me/?text=` (petit bouton de l'accueil, gros boutons des pages marques et guides) → clic compté `partage/<page>` dans GoatCounter, menu de partage du téléphone (`navigator.share`) s'il existe, sinon le lien WhatsApp s'ouvre normalement. Testé dans test_site.mjs.

- **Vidéo de présentation** (06/10/2026) : `assets/video/presentation.mp4`, 1080 × 1920, + couverture et aperçu 1200 × 630 (`apercu-video.jpg`). Son de fond : un vrai ruisseau (enregistré par jackthemurray, Freesound 433589, CC0, via Wikimedia Commons ; preuve dans le dossier privé `videos (outil)/preuves musique/`) — demande d'Ahmed, au lieu de la musique des autres sites. Page **`video/`** (lecteur + gros bouton « Ouvrir le site » + Partager, og:video / og:image) : réglages `tools/page_video.json`, fabriquée par node tools/page_video.mjs, à partir de quelle-eau/ (à relancer si cette page change). Le bouton « Partager » envoie un LIEN : la page vidéo + l'adresse du site dans le texte (`window.partagerLien`, bloc « vidéo de présentation » en fin du JS commun), jamais le fichier. Test `node tools/test_video.mjs`.
  Pour la refaire : `python fabriquer.py eau` puis `python brancher_partage.py eau` dans le dossier PRIVÉ du PC `videos (outil)/`.
