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
- Cache des téléphones : **changer le `?v=` de style.css / app.js dans index.html à chaque modification.**
- Image d'aperçu des liens partagés : `assets/og-image-v2.png`, volontairement **sans nombre de marques ni noms de magasins**
  (l'ancienne affichait « 22 marques, Monoprix, Aziza »). Si on la change : nouveau nom de fichier (WhatsApp/Facebook gardent l'ancienne en cache).
- Tests d'affichage mobile : headless Chrome dans des iframes de 340/390 px (les petites fenêtres sont ignorées).

## Sources de prix
- **Carrefour** (API GraphQL) et **Géant Drive** (HTML) : lus en direct chaque nuit. Géant : `curl -k` en cas d'erreur de certificat (code 60).
- **Otrity** (épicerie en ligne, prix = stika livrée ÷ 6 ou 12) : Cloudflare bloque GitHub → relevé depuis le PC
  d'Ahmed par la tâche Windows « PrixEaux-Otrity » (12h, `tools/otrity_local.py` → `data/otrity.json`, ignoré après 3 jours).
  Nouveau PC : `tools/installer_pc.ps1`.
- **Aziza et Monoprix retirés** (30/09/2026) : barka.tn donnait des prix périmés / produits indisponibles.
  Monoprix et Jumia exigent une vérification « humain » : **pas de contournement** (demander l'autorisation ou prix signalés).
  Relevé depuis le PC seulement si le site laisse passer un particulier.

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
- « Votre avis » : Formspree (mwlpakqj). Statistiques : GoatCounter.
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
  Sous le titre (04/10) : `p.slogan` « Comparer les prix · Commander (bientôt) · Se faire livrer » — nom du site gardé
  (référencement Google). Retirer « (bientôt) » à la réouverture de la commande.
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
