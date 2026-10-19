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
17. **Recueillir les avis des visiteurs** : un site statique n'a pas de serveur
    pour recevoir des messages — passer par un service de formulaire comme
    **Formspree** (gratuit jusqu'à 50 messages/mois) : créer un compte, créer
    un formulaire, mettre son adresse (`https://formspree.io/f/…`) dans
    l'attribut `action` d'un `<form>` sur le site. Les messages arrivent par
    email, l'adresse email reste invisible pour les visiteurs. Envoi en
    JavaScript (fetch + `Accept: application/json`) pour rester sur la page,
    et un champ caché « honeypot » (`_gotcha`) contre le spam

## Phase 7 — Faire revenir les visiteurs (alertes automatiques)

18. **Créer un canal Telegram public** (5 min, sur téléphone) : Discussions →
    bouton nouveau message (crayon ✏️, au-dessus de la barre du bas ou en haut
    à droite) → « Nouveau canal » → nom + description (avec le lien du site) →
    type **Public** + un lien `t.me/mon_canal` → ✔, puis encore ✔.
    **Vérifier** en ouvrant `https://t.me/mon_canal` dans un navigateur : on doit
    voir le nom du canal et « 1 subscriber ». Si on voit « If you have Telegram,
    you can contact @… », le canal n'est pas vraiment public (il est resté privé,
    ou le lien n'a pas été enregistré) → Modifier → Type de canal → Public
19. **Créer un robot Telegram** : ouvrir `https://t.me/BotFather` (badge bleu ✔)
    → Démarrer → `/newbot` → un nom → un identifiant finissant par `bot`
    → BotFather donne un **code secret (token)**. Ce code = mot de passe du
    canal : ne jamais le publier ni l'envoyer dans une discussion
20. **Faire du robot un administrateur du canal** avec le droit « Publier des
    messages ». Si la recherche « Ajouter un administrateur » ne trouve rien :
    ouvrir la fiche du robot → ⋮ → « Ajouter à un groupe ou un canal »
21. **Ranger le token dans le coffre-fort de GitHub** : dépôt → Settings →
    Secrets and variables → Actions → New repository secret
    (ex. `TELEGRAM_BOT_TOKEN`). Le workflow le lit avec
    `${{ secrets.TELEGRAM_BOT_TOKEN }}`, personne ne peut le voir
22. **Publier automatiquement** : dans le workflow quotidien, un script compare
    les données du jour à celles de la veille (`git show HEAD:data/…`) et, s'il
    y a du nouveau (ici : baisse de prix ≥ 1 %), envoie un message via
    `https://api.telegram.org/bot<TOKEN>/sendMessage` (chat_id = `@mon_canal`).
    Rien de nouveau → rien n'est publié (pas de messages inutiles). Le même
    résultat sert à un bandeau sur le site. Un petit workflow manuel « message
    de bienvenue » sert à tester le robot
23. **Mettre le lien du canal sur le site** et le partager avec le site
    (WhatsApp : la publication automatique n'y est pas gratuite — une « chaîne
    WhatsApp » ne peut être alimentée qu'à la main)

24. **Prix signalés par les visiteurs** : un bouton « Signaler un prix » sur chaque fiche ouvre
    un petit formulaire (marque, format, prix, magasin, ville, date) envoyé par email via
    un **Google Forms** (gratuit ; ses réponses vont dans un Google Sheets « publié sur le Web »
    en CSV, que le robot peut lire). Formspree ne convient pas : lire ses réponses par
    programme est payant. Trois fois par jour, un robot GitHub lit le tableau, **décide seul**
    (prix au litre plausible, écart aux prix connus, doublons = « confirmé »), publie le prix
    sur la fiche avec sa date pendant 30 jours — hors classement, contre les faux prix — et
    l'annonce sur le canal Telegram. Google Forms : questions « Réponse courte » (le contrôle
    se fait côté robot), ne pas collecter les e-mails, « Publier » avec accès « toute personne
    disposant du lien ». Couvre les magasins sans site internet ou qui bloquent les robots

25. **Rendre le site autonome pour des années** : limiter la durée de vie des prix d'une
    source en panne (7 jours), détecter les données incohérentes, avertir le visiteur en
    comparant la date des prix à SA date du jour (fonctionne même si les robots s'arrêtent),
    un robot « battement de cœur » mensuel (GitHub met en pause les tâches d'un dépôt inactif
    60 jours), un simulateur de pannes qui rejoue tous les scénarios, un script de
    réinstallation pour un nouveau PC, et un successeur désigné (GitHub, Telegram, Google)

26. **Trouver des fournisseurs dans le registre officiel** : le Registre National des Entreprises
    (registre-entreprises.tn) permet de chercher par **activité** (ex. « المياه المعدنية بالجملة »,
    « commerce de gros de boissons ») : nom, adresse, forme juridique, état (actif/radié), dépôt des
    états financiers. Pas de téléphone ni de chiffre d'affaires (e-bilan payant). Classer ensuite par
    gouvernorat et noter la fiabilité (société > commerçant, états financiers déposés…)
27. **Garder secrète sa liste de fournisseurs** : un **dépôt GitHub privé** (gratuit) séparé du site
    public, pour la sauvegarder en ligne et y faire tourner ses robots sans que personne ne la voie
28. **Téléphones automatiques avec Google Maps (API « Places (New) »)** : projet Google Cloud, facturation
    (en Tunisie : **prépaiement de 30 $** crédité sous 24 h), activer « Places API (New) », créer une
    clé **restreinte à cette seule API**, la ranger dans les **secrets GitHub** (ne jamais la coller
    ailleurs — sinon la supprimer et en créer une nouvelle), mettre un **plafond de requêtes/jour** et
    un budget d'alerte. Le robot limite le nombre de recherches et garde un cache

29. **Vote des visiteurs** (« mon eau préférée ») sans serveur : le vote part dans le même Google Forms
    avec un marqueur (format = VOTE) et un jeton anonyme gardé dans le navigateur ; le robot compte un
    vote par jeton (le plus récent) et publie le classement. Vote indicatif (non infalsifiable)
30. **Fenêtres (pop-up)** plutôt que sections dépliables pour les contenus secondaires (gagnant, hadith,
    signalement) : la page reste courte et les prix arrivent plus vite
31. **Protéger son travail** : fichier LICENSE « tous droits réservés » + mention © en bas du site ;
    l'historique git prouve l'antériorité. Pour cacher aussi le code : dépôt privé (GitHub Pro payant)
    ou hébergement Cloudflare Pages (gratuit) — le contenu affiché reste toujours téléchargeable

32. **Visibilité** : savoir d'où viennent les visiteurs (GoatCounter : ici 50 % Google, 50 % Instagram) ;
    bouton « Partager sur WhatsApp » avec un message tout prêt ; pages « guides » qui répondent aux
    questions tapées dans Google (prix de la stika aujourd'hui, quelle eau choisir), régénérées chaque nuit ;
    le prix dans le titre des pages (donne envie de cliquer) ; quelques phrases en arabe pour les
    recherches en arabe ; une image Instagram fabriquée automatiquement chaque semaine (Chrome
    « headless » photographie une page HTML) et envoyée sur Telegram pour être repostée
33. **Dire clairement ce qu'est le site dès le premier écran** (retour des visiteurs) : ce qu'on fait,
    d'où viennent les prix, qu'ils sont indicatifs, et ce qui arrive bientôt (commande)
34. **Un menu du haut le plus mince possible sur téléphone** : la barre qui reste fixée en haut
    prend de la place à chaque écran. Les filtres (Stika/Bouteille, type d'eau, format) sont devenus
    **3 boutons sur une seule ligne** ; chacun ouvre un petit panneau, et le bouton affiche le choix
    en cours (« Bouteille », « Minérale », « 1,5 L »). Le tri, moins utilisé, est descendu au-dessus
    de la liste. Même idée pour la carte « la moins chère » : un **petit bouton « Partager »** (flèche)
    sous le prix plutôt qu'un gros bouton, et un texte court (« Stika (6 × 1,5 L) – Géant »)

## 05/10/2026 — Installation complète sur le téléphone (service worker)
- `sw.js` à la racine (portée `/prix-eaux-tunisie/`), enregistré par `protection.js` (chargé par toutes les pages ; https seulement).
- Stratégie prudente : **réseau d'abord** pour les pages et les prix (jamais de vieux prix quand Internet marche ; cache seulement
  hors connexion, sinon page « Hors connexion » FR + AR) ; fichiers `?v=` : cache puis mise à jour en arrière-plan.
- Jamais en cache : envois (non-GET), autres sites (Google Forms, GoatCounter…), autres sites d'Ahmed sur la même adresse.
- Manifeste, icône iPhone et meta `apple-mobile-web-app-capable` / `-title` sur toutes les pages (gabarits compris).
- Test `node tools/test_sw.mjs` (faux navigateur) + nouveau robot `tests.yml` à chaque push ; sabotage vérifié.
- Vieille version bloquée sur un téléphone : changer `CACHE_VERSION` dans `sw.js`.

## 07-08/10/2026 — Travailler depuis le téléphone ET l'ordinateur sans conflit
- Tout le travail hors sites est maintenant sur GitHub, dans un dépôt PRIVÉ (`projets-ahmed`) : rien n'est perdu si le PC tombe
  en panne, et une session sur le téléphone voit les mêmes fichiers.
- Règle : **récupérer (git pull) → modifier → renvoyer (git push)**, sur le PC comme sur le téléphone.
- Les routines Claude dans le cloud doivent avoir leurs dépôts dans leurs SOURCES, être testées une fois tout de suite, et
  être surveillées sur ce qu'elles ENREGISTRENT (la vérification du matin le contrôle).

## Pièges rencontrés et leçons (à réutiliser)

- **Une routine « réussie » peut n'avoir rien enregistré** (04-08/10) : vérifier ses commits, pas seulement son statut.
- **Recopier un fichier depuis le PC peut effacer un travail fait depuis le téléphone** (07/10, moteur des annuaires) :
  toujours `git pull` avant ; le script de synchronisation refuse maintenant d'écraser.
- **Cache des téléphones** : après une mise à jour, un téléphone peut garder
  l'ancien `style.css` avec la nouvelle page → affichage cassé (ex. icône géante).
  Solution : charger `style.css?v=NUMERO` et `app.js?v=NUMERO` et **changer le
  numéro à chaque modification** ; donner `width`/`height` aux icônes SVG
- **Horaires des robots GitHub** : les heures rondes (0h00, 9h30) sont retardées
  de plusieurs heures → choisir une minute décalée (ex. 1h07). Toujours faire
  `git pull --rebase` avant `git push` dans le workflow (collision possible)
- **Sites .tn** : certificats SSL incomplets → prévoir un repli dans les scripts
- **Vérifier que chaque source est vivante** : un comparateur (barka.tn) donnait pour Aziza
  les prix de son ancienne boutique en ligne, fermée → prix périmés (stika affichée 3,540 DT,
  4,900 DT en magasin, signalé par un client). Contrôler que les liens des produits mènent à
  une boutique actuelle, et faire des vérifications en magasin de temps en temps ;
  au moindre doute, retirer l'enseigne plutôt qu'afficher un faux prix
- **Lire les journaux du robot** : quand une source échoue, le robot réaffiche les prix
  d'avant sans rien dire. Géant a ainsi échoué 3 jours (certificat) sans qu'on le voie
- **Sites qui bloquent les robots** : certains (Otrity) bloquent seulement les serveurs
  (GitHub) mais laissent passer un PC de particulier → relevé depuis son PC par une
  tâche planifiée Windows, qui envoie un fichier au robot (ignoré s'il a plus de 3 jours).
  D'autres (Monoprix, Jumia) exigent une vérification « humain » : on ne force pas,
  on demande l'autorisation ou on utilise des prix signalés
- **Un seul site** : ne pas créer deux dépôts pour le même projet. Si c'est
  arrivé, transformer le doublon en **redirection** (sans `noindex`) pour que
  Google transfère le référencement vers le bon site
- **Sessions Claude sur téléphone** : elles travaillent sur des branches
  `claude/…` → fusionner dans `main`, sinon rien n'apparaît en ligne
- **Nom de domaine** : inutile au début (GitHub Pages est gratuit) ; l'acheter
  seulement quand il rapporte (premier annonceur). Migration possible plus tard
  sans perte, avec des redirections page par page
- **Premier canal de trafic qui marche** : un partage Instagram (10 → 100 visites
  par jour). Google prend plus de temps
- **Toujours vérifier sur son propre téléphone** et envoyer une capture d'écran
  en cas de doute : c'est comme ça qu'on repère les problèmes réels
- **Toujours demander avant d'installer un logiciel** sur le PC
- **Les Tunisiens écrivent souvent les prix en millimes** (« 3900 » = 3,900 DT) : le robot doit le
  comprendre, sinon il rejette de vrais signalements
- **Facebook** bloque toute lecture automatique, même des pages publiques : trouver les pages par
  la recherche web, puis copier soi-même la partie « À propos ». Ne jamais utiliser sa session
- **Excel ouvert = fichier verrouillé** : fermer Excel avant qu'un programme le modifie
- **Pénurie d'eau (été 2026)** : ne pas stocker pour revendre (saisies pour spéculation)

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
| Formspree | formulaire d'avis / contact (messages reçus par email) |
| Telegram (canal + robot BotFather) | alertes automatiques aux abonnés |
| GitHub Secrets | coffre-fort pour les codes secrets (tokens) |

- **Coran et hadith sur l'eau (04/10/2026)** : la barre du hadith devient « الماء في القرآن الكريم والحديث النبوي » ;
  le bouton « اقرأ » ouvre une fenêtre avec d'abord des versets du Coran sur l'eau (sourate et numéro du verset),
  puis des paroles du Prophète ﷺ (avec leur source). Toujours vérifier le texte arabe et la référence avant d'en ajouter.
- **Vraie photo dans le bandeau (05/10/2026)** : photo libre de droits trouvée sur Wikimedia Commons (API publique),
  licence vérifiée sur sa page (CC0), preuve sauvegardée (HTML, métadonnées, empreintes sha256, copie Internet Archive)
  dans `preuves conditions d'utilisation/` (jamais publié). Recadrage + compression + léger flou avec Python Pillow
  (≤ 150 Ko), placée derrière le texte avec un dégradé bleu pour rester lisible ; crédit affiché. Nouvelle image d'aperçu
  `og-image-v3.png` faite avec Chrome sans écran à partir d'une page HTML temporaire.
- **Protection contre les robots d'IA et la copie (05/10/2026)** : robots.txt (robots d'IA interdits, Google permis),
  meta noai, Content-Security-Policy, `protection.js` (anti clic droit sur les photos, source ajoutée au texte copié,
  anti-iframe). Le test `tools/test_site.mjs` vérifie tout, et un sabotage volontaire d'une copie le fait bien sonner.
- **Photo du bandeau rendue nette (05/10/2026)** : retour d'Ahmed « l'image n'est pas claire ». Une photo floue sous un
  dégradé ne sert à rien : on prend une vraie photo prise en Tunisie (bouteilles de marques tunisiennes, domaine public),
  on découpe les étiquettes avec Pillow pour en faire une bande fine, posée AU-DESSUS du texte (rien par-dessus).
  Vérifier sur captures 340/390 px que la réponse principale ne descend pas (resserrer un peu le texte si besoin).
  Nouvelle image d'aperçu `og-image-v4.png`.
- **Empêcher Chrome de traduire le site (05/10/2026)** : une page FR + AR trompe Chrome, qui proposait l'anglais.
  `translate="no"` sur `<html>` et `<meta name="google" content="notranslate">` sur toutes les pages ; vérifié par le test.
- **Photo du bandeau NEUTRE, sans marque (05/10/2026)** : retour d'Ahmed « on voit 5 marques, les visiteurs vont croire
  que c'est de la publicité ». Règle : la photo d'un comparateur ne montre **aucune marque ni logo lisible**, ni visage.
  Recherche sur Wikimedia Commons (API, mots « water poured into glass »…), choix d'une photo nette d'eau versée d'une
  bouteille sans étiquette dans un verre (CC BY 2.0 : crédit obligatoire, « recadrée »), preuve de licence sauvegardée
  (HTML, PDF, métadonnées, SHA-256, Internet Archive). Bande 1440×173 + 720 px recadrée avec Pillow (fichiers `photo-neutre-*`,
  ~25 Ko), crédit déplacé en haut à droite pour ne pas cacher le verre. Captures 340/390 px avant/après : la carte
  « La moins chère » reste au même endroit. Nouvelle image d'aperçu `og-image-v6.jpg` (texte + photo neutre, 84 Ko),
  ajoutée aussi aux 35 pages marques (qui n'en avaient pas). Le test vérifie le nom `photo-neutre-*` et le crédit.
- **Gestionnaire « onerror » bloqué par la CSP (05/10/2026)** : depuis l'ajout de la Content-Security-Policy, un attribut
  `onerror="…"` écrit dans le HTML est refusé (erreur dans la console). Remplacé par un écouteur global
  `document.addEventListener("error", …, true)` ; le test refuse tout attribut `on…=` dans les pages et dans app.js.
- **Mise à jour générale (05/10/2026)** : voir la section « Mise à jour du 05/10/2026 » de CLAUDE.md. Pour un NOUVEAU
  site, suivre `_claude code project
ouveau site - procedure.md` (toutes les leçons du site de l'eau y sont).

- **05/10/2026 (soir)** : nouvelle icône goutte (même famille que les autres sites, logo d'en-tête compris) ; « comparateur gratuit » dans les titres Google. Envoyer les liens WhatsApp depuis le téléphone pour avoir la grande image.

## Pages par magasin pour Google (08/10/2026)
- Une page par recherche : « prix eau Carrefour », « prix eau Géant »… → `build_guides.py` (`page_magasin`) fabrique chaque nuit `prix-eau-<magasin>/` avec les prix du jour, comparés aux autres magasins, et les ajoute au sitemap et aux pieds de page.

## Économiser les minutes des robots GitHub (10/10/2026)
- Mesurer d'abord : liste des lancements de chaque robot sur 7 jours (durée arrondie à la minute supérieure), × 30/7.
  Les dépôts publics ne comptent pas ; les dépôts privés ont 2 000 min/mois gratuites.
- Un robot ne doit commiter que si le contenu change vraiment : comparer l'ancien fichier au nouveau en ignorant la date « maj »
  (`ecrire_si_change` dans `tools/signalements.py`, testé dans `tools/test_signalements.py`).
- `tests.yml` : `paths-ignore: ["**.md"]` (pas de tests pour une simple note) + `concurrency … cancel-in-progress: true`
  (un nouvel envoi annule l'ancien). Un changement commun à plusieurs sites = un seul commit par dépôt.
- Rapport complet : `audit des robots 2026-10-10.md` dans le dépôt privé projets-ahmed.

## Passer un site sur son propre nom de domaine (10-11/10/2026)
1. Acheter le domaine chez Cloudflare (clicvia.com, environ 10 $/an, renouvellement automatique, nom caché du public).
2. Cloudflare → DNS → Add record : `CNAME`, Name = sous-domaine (ex. `prix-eau`), Target = `ah6259.github.io`, nuage GRIS (« DNS only »).
3. Dans le dépôt : fichier `CNAME` (une ligne : `prix-eau.clicvia.com`), remplacer partout l'ancienne adresse github.io
   (pages, plan du site, robots.txt, partages, robots, tests), `"id": "/"` dans le manifeste, service worker enregistré sur le
   dossier du site (`BASE_SITE`), GoatCounter qui garde l'ancien préfixe (`window.goatcounter.path`) ; tests verts, puis envoi.
4. Attendre le cadenas (quelques minutes à 1 h), puis cocher « Enforce HTTPS » dans Settings → Pages du dépôt.
5. L'ancienne adresse redirige seule (GitHub). Le site racine (portail) en DERNIER, sinon il entraîne les autres.
6. Google Search Console : propriété « Domaine » (Cloudflare ajoute la ligne TXT d'un clic), puis envoyer les plans du site.

## Leçons du 11/10/2026 (site immobilier, valables pour tous les sites)
- **Image de partage WhatsApp** : à chaque changement, NOUVEAU nom de fichier (`og-image-v2.jpg`…) ; modèle HTML 1200 × 630,
  capture Chromium sans écran DANS UN CADRE (iframe) puis `convert -crop 1200x630` (la capture directe coupe le bas), JPEG < 250 Ko.
- **Photos libres** : Wikimedia Commons refuse les requêtes directes des sessions Claude en ligne (« 429 ») → chercher avec WebFetch
  de l'API Commons, télécharger par `Special:FilePath/<fichier>?width=900`, citer auteur + licence sous l'image et au pied de page.
- **Vidéo de présentation** depuis une session en ligne : l'outil du PC (`videos (outil)/fabriquer.py`) marche avec
  `FFMPEG=/usr/bin/ffmpeg NAVIGATEUR=/opt/pw-browsers/chromium` et le site servi en local (`python -m http.server`), car Chromium
  refuse le certificat du proxy ; Pillow s'installe avec l'accord d'Ahmed.
- **Tests = garde-fou** : un test du site qui échoue bloque la publication du robot (vu le 11/10 avec un nouveau type d'annonce) :
  corriger le test ou le code, jamais forcer la publication.
- **Règle d'Ahmed : ne contacter personne** (brouillons seulement, c'est lui qui envoie).

## Leçons du 11/10/2026 (soir) — partage, photos qui bougent, en-tête
- **Petite vignette WhatsApp** alors que l'image est bonne (1200 × 630, < 250 Ko) : il manquait `og:url`. Chaque page porte
  `og:type`, `og:url` (= adresse canonique), `og:site_name`, `og:locale` ; puis nouveau nom d'image. Les anciens messages
  WhatsApp ne changent pas : renvoyer le lien pour vérifier.
- **Photos qui défilent** : rangée de photos → 2 visibles, défilement seul de droite à gauche ≈ 3 s/photo (copie `li.copie`
  + animation CSS, `direction:ltr` même en arabe) ; photo unique → diaporama en fondu toutes les 3 s, crédit sous chaque photo.
  Toujours : pause au toucher, arrêt si « réduire les animations », rien qui bouge sur ordinateur si tout tient à l'écran.
- **En-tête** : nom du site en 17 px sur téléphone (comme Points d'eau) ; texte d'accueil de 3 lignes au plus.
- **Donnée manquante un jour** (Hayet absente du relevé Otrity) : la marque garde sa dernière photo (`garder_anciennes_photos`).
- Toutes ces règles sont aussi dans `regles communes a tous les sites.md` § 14 (dépôt privé projets-ahmed) pour les prochains sites.

## Leçons du 13-14/10/2026 — une partie payante à partir des données d'un site
- **Idée d'Ahmed** : les 10 000 annonces de l'immobilier servent à calculer le rendement locatif → page gratuite (pour Google)
  + contenu payant (tableau complet, alertes « bonne affaire ») livré par le robot Telegram d'un dépôt PRIVÉ.
- **Comparer à pièces égales** (S+1, S+2…) quand la surface manque ; **au m²** sinon ; écarter les chiffres invraisemblables
  (un local à 23 % de rendement = fonds de commerce, pas les murs) et les zones de vacances (loyers meublés).
- **Toujours dire « prix demandés, chiffres indicatifs, pas un conseil financier »**.
- **Paiement sans PC** : code client (motif du transfert D17 / IZI) + bouton GitHub « activer-… » depuis le téléphone.
- **Plus de données sans nouvelle source** : lire la surface écrite dans les titres, lire d'abord les fiches des biens rares,
  inviter les professionnels à publier gratuitement.
- Un test qui vérifie « aucune promesse non tenue » doit savoir quelle partie est tenue par un AUTRE dépôt (le rappel du Pass).

## Leçons du 15/10/2026 — des chiffres sûrs avant tout (erreur « 120 DT la nuit »)
- **Comment l'erreur est arrivée** : une location à 120 DT la nuit (écrit seulement dans le texte) ; le robot ne lisait que le titre ;
  une règle de correction a supposé « 120 = 120 000 DT » ; ce faux prix est devenu une « bonne affaire » sur Telegram.
- **Règle** : on ne devine JAMAIS une valeur ni son unité. Contrôler chaque information (devise, loyer au mois, total ou au m², m²,
  pièces, étage, date) ; valeur pas sûre = mise de côté (« voir la source »), jamais utilisée dans un calcul ni une alerte.
- **Une seule porte d'entrée** des données sûres pour TOUTES les IA et tous les calculs, et un test qui bloque un nouveau module
  qui ne l'utilise pas ; des annonces « pièges » dans les tests vérifient que rien ne change.
- **Vieux prix** : plus de 6 mois depuis la 1re apparition = jamais utilisé (annonce republiée : garder la date de 1re apparition).
- **Mesurer avant de garder une règle** : un contrôle trop sévère (prix 4 fois loin du quartier) retirait de vrais prix et l'IA se
  trompait plus ; à 6 fois elle se trompe moins qu'avant (ventes 27,9 -> 26,0 %).
- Chaque erreur vue par Ahmed devient un test de régression.

## Leçons du 15/10/2026 (nuit) — une offre payante qui vaut son prix, et qui marche vraiment
- **Pourquoi payer si l'estimation est gratuite ?** (question d'Ahmed) : la partie payante doit donner ce que le gratuit ne donne pas
  et qui fait gagner du temps ou de l'argent : la valeur de chaque atout, un texte d'annonce prêt (FR + AR), une mise en avant,
  un suivi chaque semaine. Le gratuit reste gratuit.
- **Test croisé obligatoire** : un code payé était « empreinté » d'une façon par le robot (Python) et d'une autre par la page (JS) :
  le client aurait payé sans jamais rien voir. Tout calcul fait à deux endroits a maintenant un test avec la même valeur attendue
  des deux côtés.
- **Un jeton plutôt qu'un code** : ce qui part dans une feuille publique (mise en avant) est un jeton qui ne révèle pas le code payé.
- **Deux robots en même temps** : si l'enregistrement d'un robot échoue (« conflict »), ses données sont perdues pour ce passage :
  le relancer (vu avec Century 21).

## Étape : une image d'aperçu par article (18/10/2026)
- **Problème** : en partageant un « rapport du mois » sur Facebook, l'aperçu montrait l'image générale du site, pas l'article.
- **Solution** : le robot dessine une image 1200 × 630 pour chaque rapport (Pillow : `tools/apercus.py`, polices dans `tools/polices/`),
  avec le mois, le titre et le chiffre clé ; son nom change quand les chiffres changent (Facebook prend alors la nouvelle image).
- **Facebook garde les aperçus en mémoire** : un robot du portail (`facebook-rafraichir`) lui demande chaque matin de relire les pages.
  Un partage déjà fait garde l'ancienne image. À la main : outil « Débogueur de partage » de Facebook → « Récupérer à nouveau ».

## Étape : le visiteur simulé (18/10/2026)
- Un robot fait le visiteur avant les vrais visiteurs : il ouvre chaque page comme un téléphone (390 px), vérifie que rien ne dépasse
  de l'écran, qu'aucune image n'est cassée, qu'aucun lien interne n'est mort, qu'aucun « NaN » ne s'affiche, et lit les prix affichés.
- Lancer : `python3 tools/visiteur_simule.py` (aussi à chaque envoi sur GitHub). Scénarios propres au site : `tools/scenarios-visiteur.json`.
- Il a trouvé dès le 1er passage le tableau du rapport du mois trop large sur téléphone (corrigé).

## Étape : revérifier toutes les pages après une amélioration (18/10/2026)
- Quand un calcul change (prix le moins cher, rapport du mois…), relire TOUTES les pages qui l'affichent : elles doivent dire la même
  chose. Leçon de l'immobilier : une page « bonnes affaires » contredisait l'avis affiché sur l'annonce elle-même.

## Étape : ne jamais deviner un lieu (18/10/2026)
- Leçon de l'immobilier : « Tunis » seul rangeait 981 annonces au centre-ville. Un lieu vague n'est jamais précis ; une seule fonction
  vérifie les lieux de toutes les sources, et un robot de garde signale chaque jour une concentration anormale.

## Étape : une seule règle pour tous les filtres (18/10/2026)
- Leçon de l'immobilier : la recherche proposait « Pièces » pour un local commercial alors que la page Estimer les cachait. Une règle
  écrite une seule fois, appliquée par tous les formulaires ; un champ caché est vidé ; un test vérifie chaque formulaire.

## Étape : une ligne par élément au téléphone (18/10/2026)
- Chaque ligne d'une liste de résultats tient sur une ligne à 390 px (le texte secondaire se coupe par « … ») ; les messages sont
  courts et en pleine largeur. Mesurer dans un vrai navigateur (Chromium sans écran) avant de publier.

## Étape : une partie payante avec un code (règle du 18/10/2026)
- Si ce site a un jour un Pass : la case du code toujours visible, le code tapé remplace l'ancien, aucun texte faux (« essai gratuit »),
  encart court avec un bouton « Copier mon lien », et une ligne ajoutée dans `pass.json` du robot commun des Pass (projets-ahmed).
  Le robot vérifie aussi (P8) que la case du code est dans le HAUT de la page, ou qu'un lien en haut (« 🔑 J'ai déjà un code ») y mène.

## Étape : des listes de lieux justes (règle du 18/10/2026)
- Si ce site classe un jour par lieu (magasins par ville) : chaque « délégation » affichée vient de la liste officielle de La Poste ;
  un lieu est rattaché par un fait (même nom écrit autrement, ou position sur OpenStreetMap), jamais deviné ; un nom qui couvre
  plusieurs délégations (Djerba, Kairouan…) devient un groupe « toute l'île / toute la ville ».
- Test dans les deux sens (toutes les officielles présentes ET rien d'autre), dans TOUS les gouvernorats ; si une carte existe,
  elle va sur le lieu choisi et donne le même nombre que la liste.
- Un test qui compare nos données à elles-mêmes ne trouve rien : comparer aussi à une AUTRE source (ex. le rangement donné par le site
  d'origine). Paiement d'un Pass (si un jour) : motif = le code personnel, jamais le nom.

## Étape : une recherche qui comprend toutes les écritures (règle du 18/10/2026)
- Copier l'outil commun `son.js` (dépôt projets-ahmed, `outils communs/recherche-au-son/`) dans `assets/`, le charger avant le script
  de la page, et chercher avec `sonRecherche.cle()` (la liste) et `sonRecherche.trouve()` (ce que tape le visiteur) : « Maroua » trouve
  « Marwa ». Ne jamais modifier la copie : corriger l'outil commun puis recopier partout. Test : 3 paires d'écritures + « zzzzqqq » = 0.
- Carte (si un jour) : `.leaflet-container{isolation:isolate;z-index:0}` et menus au z-index 1000 ; la carte suit le lieu choisi.
- Carte avec plusieurs niveaux de zoom (si un jour) : à chaque niveau, les bulles comptent TOUT (ce qui n'a pas de position plus
  précise garde une bulle « reste ») ; test : le total est le même à chaque niveau.

## Étape : vérifier les espaces comme un œil (règle du 19/10/2026)
- Le visiteur simulé (`python3 tools/visiteur_simule.py`, copie identique de l'outil commun) signale deux éléments qui se touchent,
  un petit élément aux espaces inégaux, un bouton pris entre deux autres qui n'est pas centré. Rouge = corriger le CSS avant d'envoyer.
- Avant d'envoyer un changement d'en-tête, de recherche ou de boutons : capture agrandie (×2) de la zone, regardée.
- Chaque dépôt a son `CLAUDE.md` (mémoire lue automatiquement au début d'une session) : sans lui, une session démarre sans connaître
  les règles (cas du portail, corrigé le 19/10/2026).
- Le visiteur simulé regarde aussi les pages sur un écran d'ordinateur (1280 px) et signale deux blocs posés l'un sur l'autre (l'un est
  caché) : une page peut être parfaite sur téléphone et cassée sur PC (cas de l'immobilier, 19/10/2026).
- Pas de faux boutons : une case qui ressemble à un bouton (fond, bordure, chiffre) doit mener quelque part, sinon le visiteur clique pour rien.
- Après chaque envoi, regarder le résultat du robot « Tests » sur GitHub : un robot rouge non regardé peut le rester des jours
  (cas du site Mosquées, 18-19/10/2026 : une page fabriquée n'avait pas été enregistrée).
