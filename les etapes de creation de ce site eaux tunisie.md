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

## Pièges rencontrés et leçons (à réutiliser)

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
