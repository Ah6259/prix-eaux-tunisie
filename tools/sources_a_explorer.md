# Recherche de nouvelles sources de prix d'eau — carnet

Tenu à jour chaque jour par la recherche automatique (Routine Claude « Nouvelles sources de prix »).
Une ligne par site examiné, pour ne pas refaire deux fois le même travail.
Règles : jamais de contournement d'une protection anti-robot (Cloudflare, captcha, « êtes-vous humain ») ;
respecter robots.txt ; aucune nouvelle source ajoutée au site sans l'accord d'Ahmed ;
chaque enseigne ajoutée reçoit son logo (robot `logos.yml`).

Statuts : ✅ déjà utilisée · 🟢 prometteuse (à proposer) · 🖥️ lisible seulement depuis le PC · ⛔ bloquée / interdite · ❌ pas de prix d'eau

| Date | Site | Statut | Notes |
|---|---|---|---|
| 04/10/2026 | carrefour.tn | ✅ | API GraphQL, chaque nuit |
| 04/10/2026 | geantdrive.tn | ✅ | HTML, chaque nuit (`curl -k`) |
| 04/10/2026 | otrity.com | ✅ 🖥️ | Cloudflare bloque GitHub → relevé depuis le PC |
| 30/09/2026 | barka.tn (Aziza, Monoprix) | ⛔ | prix périmés / produits indisponibles, retiré |
| 30/09/2026 | monoprix.tn | ⛔ | vérification « humain » |
| 30/09/2026 | jumia.com.tn | ⛔ | vérification « humain » |
| 04/10/2026 | geant.tn | 🟢 ? | site principal de Géant Tunisie, lisible par GitHub — vérifier s'il a des prix en ligne (en plus de geantdrive.tn) |
| 08/10/2026 | geant.tn | ❌ | lisible par GitHub (certificat à ignorer), mais site vitrine : 0 prix, 0 « eau ». Seul geantdrive.tn a des prix (déjà utilisé) |
| 08/10/2026 | mg.tn (Magasin Général) | ❌ | lisible (certificat à ignorer), mais seulement promotions/catalogues (pas de boutique, 0 « eau »). À revoir si une boutique en ligne apparaît |
| 08/10/2026 | founa.com | 🖥️ ? | répond 200 mais page vide pour GitHub (114 octets, probablement chargée par JavaScript). robots.txt permissif. À tester depuis le PC d'Ahmed : premier supermarché en ligne tunisien, drive via mg La Marsa |
| 08/10/2026 | glovoapp.com/tn | ⛔ | mot anti-robot détecté dans la page, appli de livraison (prix par commerçant) — pas de contournement |
| 08/10/2026 | commerce.gov.tn (ministère du Commerce) | ❌ | page d'accueil sans prix ; plafonds de l'eau en vigueur depuis le 19/08/2026 (presse : Webdo), à chercher en PDF/communiqué plutôt qu'à lire par robot |
| 09/10/2026 | founa.com | ❌ | la presse (Tunisie Numérique) indique que Founa a fermé (pertes, rachat par MG) : inutile de le tester depuis le PC |
| 09/10/2026 | yassir.com (Yassir Market) | ⛔ | lisible (200) mais c'est une application : page d'accueil sans prix d'eau, prix par commerçant (partenaires Monoprix / Magasin Général) dans l'appli seulement — pas de lecture automatique |
| 09/10/2026 | uniprix.tn | ❌ | le nom de domaine n'existe pas (www.uniprix.tn introuvable) |
| 09/10/2026 | jibli.tn | ❌ | certificat invalide, page par défaut « site web » vide : pas de boutique |
| 09/10/2026 | tunimarket.tn | ❌ | certificat expiré, 0 mot « eau », 0 Safia : pas de prix d'eau lisibles. À ne pas refaire sauf nouvelle boutique |
| 09/10/2026 | supermarche.tn | ❌ | test non concluant (erreur, le résultat affiché venait du site précédent) ; rien de trouvé par la recherche web |
| 09/10/2026 | Recherche web (Safia/Marwa en ligne) | ❌ | aucune boutique en ligne nouvelle trouvée ; seuls des comparatifs de presse (Tuniscope 13/07/2026 : 0,5 L Fourat 0,360 · Safia 0,410 · Marwa 0,430 ; 1,5 L Bargou 0,610 · Marwa 0,640 · Safia 0,720), antérieurs aux plafonds du 19/08 |
| 10/10/2026 | aziza.tn | ❌ | lisible (200) mais site vitrine des magasins (0 prix, 0 « eau »), pas de boutique en ligne |
| 10/10/2026 | tunisianet.com.tn | ❌ | lisible (200) mais informatique/électronique : pas d'eau en bouteille |
| 10/10/2026 | mytek.tn | ⛔ | Cloudflare « Just a moment » (403) ; informatique de toute façon — pas de contournement |
| 10/10/2026 | ouedkniss.com | ❌ | site algérien d'annonces, pas une source de prix en magasin tunisien |
| 10/10/2026 | Recherche web (grossistes en ligne, drive, Aqualine/Melliti) | ❌ | rien de nouveau : seulement la presse (pénurie, plafonds du 19/08/2026, Webdo / La Presse) ; aucune boutique en ligne de grossiste trouvée |
