# Mémoire du projet — Prix des Eaux de Tunisie

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
- Public : **https://prix-eau.clicvia.com/** (depuis le 11/10/2026 ; domaine clicvia.com d'Ahmed chez Cloudflare, ligne DNS
  `CNAME prix-eau → ah6259.github.io` nuage GRIS, fichier `CNAME` du dépôt). L'ancienne adresse https://ah6259.github.io/prix-eaux-tunisie/
  redirige seule vers la nouvelle (GitHub). Le site est à la RACINE « / » : `BASE_SITE` de protection.js (sw.js, vidéo) ; GoatCounter
  garde le préfixe `/prix-eaux-tunisie` (`window.goatcounter.path`). Si l'outil vidéo du PC réécrit le bloc VIDEO_SITE, remettre
  `"base": BASE_SITE` et l'ORIGINE prix-eau.clicvia.com. Dépôt `Ah6259/prix-eaux-tunisie` (GitHub Pages, branche main).
  Doit rester **public** (Pages gratuit). `gh` : "C:\Program Files\GitHub CLI\gh.exe".
- `Ah6259/prix-eau-tunisie` = simple **redirection** à garder (liens partagés + référencement). Ne pas y remettre de noindex ni de scraping.
- 35 marques, prix bouteille + **stika** (6 × bouteille, 12 si ≤ 0,75 L).
- Cache des téléphones : **changer le `?v=` de style.css / app.js dans index.html à chaque modification (protection.js et `CSS_V` de build_guides.py : 20261018b ; style.css / app.js : 20261015a).**
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
- **Monoprix revenu (06/10/2026) par relevé MANUEL** : Ahmed envoie des captures de l'application Monoprix,
  Claude écrit `data/monoprix.json` (date + offres, même format qu'otrity.json) ; `collect_prices.py` les met
  DANS LE CLASSEMENT **30 jours** (`MAX_JOURS_MANUEL`, décision d'Ahmed) puis les retire ; `statut_sources.monoprix.manuel`
  = pas d'alerte de retard ; la date du relevé n'est PAS affichée (choix d'Ahmed, 06/10). Logo `assets/logos/monoprix.png` envoyé par Ahmed (mot blanc sur rouge).
  Jamais de lecture automatique de l'application (contournement refusé).

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
  Depuis le 10/10/2026 : fichiers réécrits (donc commit + publication) SEULEMENT si un vrai signalement change (`ecrire_si_change`).
- **Audit des robots du 10/10/2026** (rapport : `audit des robots 2026-10-10.md` du dépôt privé projets-ahmed) : dans TOUS les dépôts,
  `tests.yml` ne tourne plus pour un envoi qui ne change que des `.md`, et un nouvel envoi annule le précédent ; ménage du gendarme
  le lundi seulement ; annuaires relus le 1er du mois ; ma-voiture : presse chaque jour, passage complet le lundi ;
  controle-matin ne refait plus les tests du site Documents.
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
- **`python tools/test_pannes.py` (21 scénarios) à relancer après toute modification du robot.**
- **`node tools/test_site.mjs` (139 vérifications de la page d'accueil) à relancer après toute modification du site.**
- Affichage (06/10/2026) : `[hidden]{display:none!important}` dans style.css + **pas de faux boutons** (badges « Prix relevés / Sources citées / Gratuit » supprimés, info gardée en texte dans le bandeau avec le lien « sources citées ») ; test_site.mjs vérifie les deux (accueil, guides, marques).
  Il faut jsdom, installé une fois par PC : `npm install --no-save --no-package-lock jsdom` (node_modules ignoré par git).
- **`node tools/test_sw.mjs`** (service worker, faux navigateur ; accepte un dossier en argument pour tester une copie sabotée).
  `tests.yml` lance à chaque push : YAML des robots + test_site.mjs + test_sw.mjs + test_pannes.py (e-mail de GitHub si échec).
- **Service worker** (05/10/2026, installation complète Chrome/Android + iPhone) : `sw.js` à la racine, portée = dossier du site (`/` sur prix-eau.clicvia.com, `BASE_SITE` de protection.js),
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
  aux autres sites d'Ahmed (outils pratiques, appels d'offres, code de la route, documents, portail), séparés par chemin. Depuis le 11/10/2026, réglage GoatCounter « Votre site » = `clicvia.com` ; chaque site garde son ancien préfixe (`/prix-eaux-tunisie/…`) : les liens du tableau de bord redirigent vers le bon sous-domaine (les lignes `partage/…` sont des clics, pas des pages).
- Grossistes : 494 grossistes actifs trouvés au Registre National des Entreprises (API publique `rne-api`, recherche par activité),
  classés par gouvernorat et fiabilité ★. Téléphones : robot Google Places du dépôt privé (clé dans ses secrets),
  **EN PAUSE depuis le 07/10/2026** (décision d'Ahmed : commande fermée ; lancement à la main seulement ;
  détails dans le CLAUDE.md du dépôt privé).
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
- **Installation sur téléphone** : `manifest.webmanifest` avec `"id": "/"` (depuis le 11/10/2026), service worker `sw.js`
  (réseau d'abord, cache seulement hors connexion), meta iPhone ; testé (`tools/test_sw.mjs`).
- **Partage** : image d'aperçu JPEG < 250 Ko (`og-image-v7.jpg`, sinon WhatsApp montre une petite vignette), aussi sur
  les 35 pages marques ; pas de traduction automatique (`translate="no"` + meta notranslate).
- **Statistiques** GoatCounter sur toutes les pages (le même compteur sert aux 5 sites, séparés par chemin).
- **Tests** : `node tools/test_site.mjs`, `node tools/test_sw.mjs`, `python tools/test_pannes.py` (21 scénarios), lancés
  aussi par `tests.yml` à chaque envoi.
- **Reste à faire (audit du 05/10)** : alerte quand une source de prix tombe en panne ; `data/baisses.js` manquant (404) ;
  texte Google « livrer à domicile » alors que la commande est fermée ; logo Otrity 404 ; `.gitattributes`.

## Visibilité (03/10/2026)
- Trafic : ~50 % Google, ~50 % Instagram. Partage WhatsApp : petit bouton « Partager » sur l'accueil ; gros bouton sur les pages marques et guides.
- **Pages par magasin (08/10/2026, plan Google « une page par recherche »)** : `prix-eau-carrefour/`, `prix-eau-geant/`, `prix-eau-monoprix/`,
  `prix-eau-otrity/` (`page_magasin` de build_guides.py, `MAGASINS`) : bouteille + stika + « ailleurs dès », FAQ JSON-LD, liens dans tous les pieds de page.
  Plan complet : `plan referencement google.md` du dépôt privé projets-ahmed.
- Pages guides générées chaque nuit par `tools/build_guides.py` (appelé par build_pages) : `prix-stika/` (FR+AR, FAQ JSON-LD)
  et `quelle-eau/` (sodium, légèreté, calcium, magnésium d'après composition.js). Dans le sitemap et le pied de page.
- Titres des pages marques avec le prix de la stika ; lignes en arabe (mots latins isolés par U+2068/U+2069).
- Encore à faire par Ahmed : lien du site dans la bio Instagram ; demander l'indexation des 2 guides dans Search Console.
  Proposé : message aux journalistes (pénurie d'eau) et textes pour groupes Facebook.

## Décisions et idées en attente
- **Nom de domaine clicvia.com : ACHETÉ et EN PLACE (10-11/10/2026)** chez Cloudflare (renouvellement automatique, expire 10/10/2027).
  Portail = https://clicvia.com/ ; un sous-domaine par site (CNAME → ah6259.github.io, nuage GRIS, fichier `CNAME` dans chaque dépôt,
  « Enforce HTTPS » coché partout) : prix-eau, eau, mosquees, concours, documents, code, voiture, outils, appels-offres, comptes,
  conferences, auto-ecoles, avocats, comptables, mariage, pros ; à venir : immobilier. Google Search Console : propriété « Domaine »
  clicvia.com validée (NE PAS supprimer la ligne TXT google-site-verification). Détails : `memoire claude/domaine-et-depots-prives.md`
  du dépôt privé projets-ahmed. Passage éventuel en dépôts privés + Cloudflare Pages : plus tard (voir l'audit des minutes).
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

## Mise à jour du 11/10/2026 (autres projets d'Ahmed, à savoir)
- **Immobilier Tunisie** https://immobilier.clicvia.com/ (dépôt `Ah6259/immobilier-tunis`) : 4 297 annonces, alertes Telegram,
  dépôt gratuit, vidéo ; mémoire dans son CLAUDE.md et `memoire claude/projet-immobilier.md` (dépôt privé projets-ahmed).
- **Code de la route** : code Pass partagé OFFERT aux élèves d'Ahmed (1 an, action `offert` du robot privé code-route-pass).
- **Portail clicvia.com** : aperçu de partage `og-image-v3.jpg` (18 services). Le site « Le message » (islam) est sur un
  AUTRE compte GitHub (lemessagelemessage8-lab.github.io) : carte sur la page clicvia.com (11/10), pas de sous-domaine.
- **Règle d'Ahmed : ne contacter personne** (agences, portails…) : Claude prépare des brouillons, Ahmed décide d'envoyer.

## Mise à jour du 07-08/10/2026 (à lire en début de session)
- **Toujours `git pull` avant de travailler** (ici ET dans `../` = dépôt PRIVÉ `Ah6259/projets-ahmed`) : Ahmed modifie aussi
  ses dépôts depuis le téléphone (sessions Claude en ligne). Ne jamais écraser ces changements en recopiant ou régénérant.
- **Dépôt PRIVÉ `Ah6259/projets-ahmed` (08/10)** = le dossier parent `_claude code project\` : règles communes, études,
  listes d'idées, liste de travail (`liste de ce qu'on va developper.md`, rubrique « 🧑 À faire par Ahmed »), preuves,
  moteur commun des annuaires + robot `annuaires.yml`. Les dépôts des sites sont exclus (`.gitignore`).
- **E-mail des commits** : dans tout nouveau dépôt, régler `user.email` sur l'adresse « noreply » de GitHub du compte
  AVANT le premier commit (le réglage général du PC n'est pas le bon).
- **Routine « Nouvelles sources de prix d'eau »** (chaque jour 9h47) : n'avait AUCUN dépôt dans ses sources du 04 au 08/10
  (push refusé, 403, recherche perdue, alors qu'elle se disait « réussie »). Corrigé le 08/10 : dépôt prix-eaux-tunisie
  branché en écriture, test des sites par `gh workflow run tester-source.yml …`, message « ⚠️ ÉCHEC : » en cas de problème ;
  1er enregistrement réussi le 08/10 (carnet `tools/sources_a_explorer.md`). La vérification du matin contrôle maintenant
  qu'elle a bien COMMITÉ. Piste en attente d'un « fais » : afficher les prix maximum officiels de l'eau (depuis le
  19/08/2026 : 0,5 L 0,600 · 1 L 0,800 · 1,5 L 0,850 · 2 L 0,950 DT).
- **Robot des téléphones des grossistes** (dépôt privé dispatch) : passage complet fait le 07/10 (494/494, 11 téléphones
  seulement), puis remis en PAUSE ; Google Cloud en essai gratuit, alerte de budget à 1 $, 900 recherches/mois au plus.
- **Nouveau site « Mes comptes »** (07/10) : https://ah6259.github.io/mes-comptes-tunisie/ (budget familial, gratuit 3 mois,
  chiffres gardés dans le téléphone, alarmes dans l'agenda du téléphone) — dossier `../mes comptes/site/`.
- **Tous les sites d'Ahmed** : bouton de paiement commun (or, contour brun, relief, reflet) ; ce site n'a pas de paiement.
- Indexation Google : les 13 sites sont prêts (plans du site lisibles, Google autorisé) ; statut réel = Search Console
  (tâches A.1 à A.3 d'Ahmed dans la liste de travail).

## Mise à jour du 11/10/2026 (soir)
- **En-tête** : titre 17 px sur téléphone (comme Points d'eau, demande d'Ahmed), ligne « Mis à jour… » 12 px ; version 20261011b.
- **`garder_anciennes_photos()`** (collect_prices.py) : une marque sans photo aujourd'hui (Hayet, absente du relevé Otrity du 11/10)
  garde sa dernière photo de magasin connue ; sinon test_site.mjs échoue (« chaque marque a une photo »).
- **Aperçu WhatsApp** : ce site avait déjà `og:url` / `og:locale` (grand aperçu) ; Points d'eau, Mosquées, Ma voiture et Outils
  ne l'avaient pas (petite vignette) → corrigés le 11/10. Règles communes : § 14 de `regles communes a tous les sites.md` (projets-ahmed).
- Autres sites le même jour : Points d'eau (5 photos qui défilent), Mosquées (photo du bandeau qui change toutes les 3 s,
  paragraphe d'accueil raccourci), GoatCounter de l'immobilier (préfixe `/immobilier-tunis`, filtrer par ce mot).

- **Visibilité Google (12/10/2026, règle commune § 8)** : liens vers nos autres sites en `https://<site>.clicvia.com/` (jamais `ah6259.github.io`), lien « Tous nos services » → https://clicvia.com/ dans le pied de page, `robots.txt` avec ligne Sitemap, `sitemap.xml` daté, JSON-LD sur l'accueil, clé IndexNow `377f054ba9c5ed40d6796adc8d87d1e8.txt` à la racine (ne pas supprimer : robot `indexnow` du portail). Contrôle : `node "outils visibilite/controle.mjs"` (dépôt projets-ahmed). Sitemap envoyé dans Search Console par Ahmed le 12/10/2026.

- **Google + Bing (12/10/2026)** : sitemap envoyé par Ahmed dans Google Search Console et dans Bing Webmaster Tools (site clicvia.com/), indexation de l'accueil demandée. Pour un nouveau site : mêmes gestes, voir `nouveau site - procedure.md` § 4 étape 5 (dépôt projets-ahmed).

- **Page Facebook Clicvia (12/10/2026)** : https://www.facebook.com/1327283777142447 — le robot `facebook` du dépôt du portail (`Ah6259.github.io`, `tools/facebook.mjs`, chaque jour 18h05) publie tout seul une page de ce site à son tour (titre, description et image `og:image` lus sur la page : les garder soignés). Ahmed ne publie rien à la main. Détail et dépannage : `nouveau site - procedure.md` § 4 étape 6 (dépôt projets-ahmed).

## Mise à jour du 13-14/10/2026 (autres projets d'Ahmed, à savoir)
- **Immobilier Tunisie** : 10 207 annonces (Tayara lu depuis le 13/10) ; page gratuite **« Où investir ? »**
  (https://immobilier.clicvia.com/investir/ : rendement des appartements par quartier, maisons/bureaux au m², terrains au m²,
  calculateur) + **Pass Investisseur payant** (19 DT/mois ou 99 DT/an, essai 7 jours, robot Telegram du dépôt privé
  immobilier-abonnes, bouton `activer-investisseur`). Modèle d'une partie payante « analyse de données » : règle commune § 11.9.
- **GoatCounter** : les 18 sites envoient bien leur préfixe et leur titre (vérifié le 13/10) ; « (inconnu) » dans les sources =
  visiteurs venus de WhatsApp / Instagram / Telegram ou adresse tapée (normal) ; « yahoo.io », « bing.io », « baidu.io » = robots.
- Liste de travail : 1.12 tester « One MCP » (rétro-ingénierie), 1.13 Pass Investisseur fait.

## Mise à jour du 15/10/2026 (immobilier : fiabilité des chiffres, à savoir pour tous les sites)
- Erreur grave vue par Ahmed : une location Tayara « 120 DT par nuit » envoyée sur Telegram comme vente à 120 000 DT (correction
  « × 1 000 » devinée). Règles générales ajoutées (`regles communes a tous les sites.md`, dépôt projets-ahmed) : **on ne devine
  jamais un chiffre ni son unité** (valeur pas sûre = mise de côté) ; **une seule porte d'entrée des données sûres pour toutes les
  IA** (test qui bloque un module qui ne l'utilise pas) ; **données propres et récentes : un prix de plus de 6 mois n'est jamais
  utilisé** ; les erreurs vues par Ahmed deviennent des tests de régression. Ce site-ci : prix relevés chaque nuit en magasin
  (pas de vieux prix) ; la règle s'applique si une IA ou une estimation y est ajoutée.
- Immobilier : estimation par délégation -> localité officielles ; carte IA du téléphone ; mot « IA » de notre modèle toujours
  blanc sur bleu #2C5872 (règle générale) ; une seule carte « Voir les annonces » sur l'accueil.
- **15/10/2026 (nuit) — Immobilier, Pass Propriétaire (29 DT / 30 j)** : 4 avantages ajoutés à l'analyse payée (« Fais 1, 2, 3 et 4 »
  d'Ahmed ; partie gratuite inchangée) : valeur de chaque atout calculée par l'IA, annonce prête à publier FR + AR, annonce mise en
  avant 30 jours sur le site (jeton vérifié par le robot), suivi de la concurrence chaque semaine sur Telegram. Détails : CLAUDE.md
  de immobilier-tunis. **Leçons pour tous les sites** : (1) un calcul fait à DEUX endroits (robot Python + page JS : empreinte d'un
  code payé) doit avoir un test croisé avec la MÊME valeur attendue — sinon un client payant n'est jamais servi (bug des codes VEN
  trouvé et corrigé) ; (2) quand un module du site change ses imports, les tests du dépôt privé qui copient ce module doivent copier
  ses nouvelles dépendances (tests privés rouges sinon) ; (3) deux robots qui écrivent les mêmes pages en même temps : le 2e
  échoue à l'enregistrement (Century 21 perdu une fois) -> relancer le robot.
- **Règle générale d'Ahmed (15/10/2026) : tout exemple montré au visiteur porte le tampon « EXEMPLE » / « مثال »** (modèle `.tg-tampon`
  de l'immobilier ; un vrai résultat calculé n'en porte pas et le dit). Ce site n'a pas d'exemple aujourd'hui ; à appliquer s'il en a un.
- **Règles générales d'expérience du visiteur (Ahmed, 15/10/2026)** : § 19 de `regles communes a tous les sites.md` (projets-ahmed) :
  « 1. À remplir » (cadre pointillé bleu) / « 2. Le résultat » (cadre vert), cartes compactes repliables, gratuit / payant clairs,
  tampon EXEMPLE, code facile à trouver, vrais boutons, un test par règle. À appliquer à ce site lors de sa prochaine modification.

## Mise à jour du 15/10/2026 (soir) — Immobilier : règles à appliquer à TOUTE analyse d'IA (aussi ce site s'il en a une)
- **Comparer des choses comparables** (« une pomme et une orange ») : même lieu fin (quartier, au plus délégation officielle), même
  type ET même sorte (duplex ≠ appartement ordinaire, villa ≠ maison), taille proche, au m² quand la surface est connue ; peu de
  points très dispersés = pas de verdict. Chaque remarque d'Ahmed sur une contradiction = une règle d'un contrôle quotidien + un test.
- **Contrôleurs d'une IA** : contrôle de cohérence quotidien (règles écrites), juge par les faits (le verdict s'est-il vérifié ?),
  IA critique (tâche Claude du matin qui relit un échantillon). La mesure décide de tous les paramètres, même ceux demandés.
- **% d'erreur d'une IA = interne** : jamais affiché aux visiteurs ; tableau envoyé à Ahmed chaque matin.
- **Fichier de données chargé avec ?v= : versionné par son CONTENU, jamais par la date** (sinon le téléphone garde l'ancien toute la
  journée). Ce site : vérifier `data/*.js` (chargés sans ?v= : réseau d'abord, donc OK).
- Détails : § 18 de `regles communes a tous les sites.md` et `memoire claude/projet-immobilier.md` (dépôt projets-ahmed).
- **Immobilier, noms de quartier (15/10 soir)** : le nom officiel d'une localité est aussi lu dans le LIEN et le titre de l'annonce
  (Ariana Essoghra rangée dans « Raoued ») ; quartier créé dès 1 annonce si le nom officiel est exact, jamais dans une autre délégation.
- **Règle commune (15/10 soir, Ahmed)** : le classement donné par le SITE SOURCE est sûr (lu en premier, utilisé dès 1 annonce si c'est
  exactement le nom officiel) ; ce qui manque vient d'un autre FAIT (délégation d'« Agba » lue sur la carte OpenStreetMap à sa position),
  jamais deviné. Ce site : les prix viennent déjà des sites des magasins eux-mêmes (même principe). Règles communes, fin du § 18.
- **Règles communes du 15/10 soir (§ 19, à appliquer ici à la prochaine modification)** : phrase d'accueil sur UNE ligne au téléphone,
  pas de grand espace autour des boutons du haut, « Comment ça marche ? » compact, espace insécable avant « ? ! : ; » dans les titres ;
  toute page qui calcule suit « 1. À remplir » -> « 2. Votre résultat » (gratuit + payant) -> carte du payant. Leçons immobilier :
  tester aussi sans les données internes (cache privé vide sur GitHub), ne jamais envoyer de pages pendant que le robot de relevé tourne.
- **Règle commune (15/10 soir)** : un robot de relevé enregistre ses données AVANT de refaire les pages et de lancer les tests (un test
  qui échoue bloque la publication, jamais la sauvegarde) ; GitHub ne garde qu'UN robot en attente par groupe de concurrence (ici
  `maj-prix`) : ce qui doit suivre un relevé se fait dans le même robot. À vérifier dans maj-prix.yml à la prochaine modification.
- **Règle commune (15/10 soir) pour TOUTE source, aussi ici (Carrefour, Géant… et toute nouvelle enseigne)** : sources lues en parallèle,
  chacune enregistrée dès qu'elle a fini, 1 s entre deux pages d'un même site (ou son Crawl-delay), réseau par un module commun, test
  qui le vérifie. collect_prices.py lit encore les enseignes l'une après l'autre : à adapter à sa prochaine modification.


## Mise à jour du 18/10/2026 — règles communes § 22 (retours des premiers visiteurs de l'immobilier, valables ici aussi)
- Haut de page sans image décorative (on croit devoir la toucher) ; après chaque envoi, vérifier le site EN LIGNE (une publication
  bloquée par un test rouge ne se voit pas) ; la carte et la recherche montrent les mêmes données ; pas de chiffre (moyenne, estimation,
  classement) sans un minimum écrit de données du même genre au même endroit ; un chiffre contesté par un visiteur est revérifié sur les
  vraies données et la règle trouvée devient un test. Détail : § 22 de `regles communes a tous les sites.md` (projets-ahmed).

## Mise à jour du 18/10/2026 (nuit) — règles communes § 23 (immobilier, valables ici aussi)
- **Le type d'une donnée se vérifie comme un prix** : la catégorie choisie par une source n'est pas une preuve ; elle est comparée au
  titre et au texte (corrigée si deux disent la même autre chose, écartée si un seul la contredit). Ici : un produit rangé dans
  « eau » par un magasin doit être vérifié par son nom (pas de soda ni de lot mixte dans le classement).
- **Un nom de lieu générique ne vaut que dans sa ville** (« centre ville » seul ne dit pas quelle ville).
- **Listes d'autres sites** (famma-dhaw.com…) : lues comme un visiteur pour VÉRIFIER nos listes, jamais leur base privée ;
  agrégateurs (bigdatis.tn) : jamais extraits sans accord écrit. Détail : § 23 de `regles communes a tous les sites.md` (projets-ahmed).
- **Un chiffre affiché dit exactement ce qu'il compte** (§ 23.9) : ici, « N marques · N enseignes » et tout nombre du site doivent
  être sans ambiguïté (ex. « 35 marques comparées », pas un total qui mélange autre chose).
- **Une IA ou une estimation se contrôle par une référence indépendante** (§ 23.10) : si ce site affiche un jour une estimation,
  la comparer chaque jour à un second calcul d'autres sources (rapport interne, écart ≥ 25 % = à regarder, jamais affiché).

## Mise à jour du 19/10/2026 — règle commune § 24 (immobilier, valable ici aussi)
- **Listes déroulantes lisibles et en couleurs** : la liste native du téléphone ignore les couleurs ; on affiche notre propre liste
  (catégories en bandeau de couleur, une ligne par choix, une seule langue, nombres « 8 453 »), la vraie `<select>` reste lue.
  Ce site utilise surtout des boutons-panneaux (`.dd`) : appliquer la même logique s'il ajoute une liste déroulante.

## Mise à jour du 18/10/2026 — règle commune § 25 (immobilier, valable ici aussi)
- **Visibilité : pas d'articles d'IA en masse ni de liens achetés** (risque de sanction Google pour tout clicvia.com). À la place, des pages
  écrites par nos robots à partir de nos données (immobilier : « Rapports du mois », https://immobilier.clicvia.com/rapports/). Ici, idée
  possible plus tard : un « rapport du mois » des prix de l'eau (évolution par marque, vrais relevés), avec l'accord d'Ahmed.
- **Rapports du mois de l'eau (18/10/2026, demande d'Ahmed)** : `tools/build_rapports.py` (appelé par build_pages.py, donc chaque nuit par
  maj-prix.yml) écrit `rapports/` et `rapports/AAAA-MM/` à partir de `data/historique.json` : prix MÉDIAN de la bouteille d'eau plate 1,5 L
  par marque (au moins 3 jours de prix dans le mois), stika ×6, prix le plus bas, stika la moins chère du mois, évolution (≤ 60 %, même
  marque les deux mois). Mois en cours recalculé chaque nuit ; mois fini figé (`data/rapports.json`). JSON-LD Article + FAQ, « Citer ces
  chiffres », bouton Partager ; lien dans les pieds de page (accueil + gabarit `pied()`). `_gabarit` accepte `racine` (pages à 2 niveaux).
  Tests : `python tools/test_rapports.py` (dans tests.yml) + bloc de test_site.mjs (médianes recalculées depuis l'historique).
- **Image d'aperçu PROPRE à chaque rapport (18/10/2026, Ahmed : au partage, Facebook montrait l'image du site)** : `tools/apercus.py`
  (Pillow, polices `tools/polices/`) dessine `rapports/AAAA-MM/apercu-<empreinte>.jpg` (titre, mois, marque la moins chère) ; og:image
  (paramètre `og_image` de `_gabarit`) + JSON-LD ; `pip install pillow` dans maj-prix.yml ; repli og-image-v7 sans Pillow ; test dans
  test_rapports.py. Robot `facebook-rafraichir` du portail : Facebook relit chaque matin les pages rapports/ (règle § 25.9).
- **`og:locale` = `fr_FR` / `ar_AR`, JAMAIS `fr_TN`** (18/10/2026) : Facebook rejetait toute la page (vraie cause du mauvais aperçu) ;
  corrigé sur tous les sites, test dans test_rapports.py (règle § 25.10).
- **Robot Facebook du portail** (`Ah6259.github.io/tools/facebook.mjs`) : chaque ARTICLE `rapports/AAAA-MM/(…/)?` des sites (immobilier,
  prix de l'eau, concours, appels d'offres, conférences) est publié UNE fois, deux passages par jour (10h10, 19h10), mémoire
  `donnees/facebook-articles.json` du portail ; bilans d'abord ; sous-pages d'un mois fini jamais rattrapées.

## Mise à jour du 18/10/2026 — Immobilier : annonces Facebook via Apify (à savoir)
- Procédure complète (connecteur Apify, accord d'Ahmed avant chaque run payant, budget 5 $/mois, scripts, règles Facebook /
  données personnelles) : `immobilier/facebook-apify/PROCEDURE.md` du dépôt privé projets-ahmed. Prochaine collecte : 18/11/2026.
- **Partage des rapports (18/10/2026, Ahmed)** : UN seul bouton « Partager ce rapport » (sous la signature « Un rapport de Prix des Eaux
  de Tunisie » et en bas) : `button[data-partage-rapport]` géré par protection.js (menu de partage du téléphone, sinon lien copié) —
  il partage la page du RAPPORT ; ne pas utiliser un lien wa.me sur ces pages (protection.js le transforme en partage de la page VIDÉO).
  Groupes Facebook : jamais par un robot ; Ahmed partage lui-même.
- **18/10/2026 (soir) — partage des rapports, les 5 sites** (immobilier, eau, concours, appels d'offres, conférences) : un seul bouton
  « Partager ce rapport » sous la signature et en bas, sans phrase d'aide, texte partagé SANS adresse (Facebook prenait l'adresse du
  texte et montrait l'accueil). Règle commune § 25.7-8 (projets-ahmed).

## Mise à jour du 18/10/2026 (soir) — VISITEUR SIMULÉ (règle générale, tous les sites)
- `tools/visiteur_simule.py` + `tools/visiteur_simule.html` (copie IDENTIQUE dans chaque dépôt ; source : règles communes § 26, projets-ahmed) :
  liens/images internes morts sur toutes les pages, puis Chromium à 390 px sur les pages du plan du site : page plus large que l'écran,
  image cassée, « NaN / undefined », page vide ; scénarios du site dans `tools/scenarios-visiteur.json` (prix affichés de l'accueil, guides,
  rapport du mois). Lancé par `tests.yml` à chaque envoi (rouge = e-mail). 1re trouvaille : tableau du rapport du mois trop large sur
  téléphone (436 px) -> `.tableau-defile` + tableau serré sous 480 px (gabarit de build_guides.py).

- **Test CSP des images (18/10/2026, VS.9, tous les sites qui affichent des images d'autres sites)** : test_site.mjs vérifie que
  chaque image d'un autre site (balise `<img>`, fond de carte OpenStreetMap, image citée par un script ou par `data/*.js`) est autorisée
  par la CSP `img-src` de SA page (cas vu sur Mosquées : 144 photos bloquées). Aucune violation ici (photos des bouteilles locales).
  Nouvelle image externe (ex. photo d'un magasin) = l'ajouter à `img-src` (gabarits de build_guides.py / build_pages.py aussi).

## Mise à jour du 18/10/2026 (soir) — règle commune « même chiffre, même verdict partout » (immobilier, valable ici aussi)
- Toute page qui juge ou compare (ici : « la moins chère », baisses Telegram, rapports du mois, pages magasins/marques) utilise le MÊME
  calcul ; deux pages ne donnent jamais deux chiffres différents pour la même chose. Après chaque amélioration d'un calcul, revérifier
  TOUTES les pages qui l'utilisent. Doublon retiré seulement s'il est SÛR. Détail : § 18 de `regles communes a tous les sites.md`.
- Ailleurs le même jour : immobilier modèle v10 (m² appris), favoris, médianes contradictoires corrigées, page investisseur vérifiée,
  rendement avec les loyers non meublés (IM.17), lieux de même nom expliqués (niveau écrit dans « Où ? »).
- **Règle commune du 18/10/2026 (soir), lieux** : un lieu VAGUE donné par une source (vide, « Autres villes », nom du gouvernorat seul) n'est
  jamais un lieu précis ; une seule porte de vérification pour toutes les sources ; un garde quotidien signale une source qui range
  anormalement beaucoup au même endroit ; une erreur trouvée = toutes celles de la même cause réparées. Ici : les prix viennent des sites
  des magasins (enseigne sûre) ; à appliquer si une source ou un lieu (magasin, ville) est ajouté. Détail : § 23 des règles communes.
- **Règle commune du 18/10/2026 (nuit), formulaires** : la liste « quel champ pour quel type » est écrite UNE fois pour tout le site ;
  un champ caché est vidé et ignoré ; un test parcourt tous les formulaires. Ici : filtres Stika/Bouteille · Type d'eau · Format —
  à appliquer si un filtre ne vaut que pour certains choix. Détail : § 23 des règles communes (immobilier : `CHAMPS_TYPE`).
- **Règle commune du 18/10/2026 (nuit), résultats au téléphone** : une ligne par élément d'une liste (texte secondaire coupé par « … »,
  jamais le prix), messages courts en pleine largeur, mesuré à 390 px dans un vrai navigateur. Ici : top 5 « La moins chère », classement
  complet, rapports du mois — à vérifier à la prochaine modification. Détail : règles communes (projets-ahmed).
- **Règle commune du 18/10/2026 (nuit), Pass** (§ 11.10 des règles communes) : la case pour taper un code est TOUJOURS visible (même si le
  téléphone a gardé un autre code), le code tapé remplace l'ancien, pas d'« essai gratuit » faux, encart du code court ; robot commun
  `verif-pass.yml` (projets-ahmed) qui contrôle chaque jour les pages Pass en ligne. Ce site n'a pas de Pass : à appliquer s'il en a un.
