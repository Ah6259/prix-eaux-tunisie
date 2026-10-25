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
| 04/10/2026 | otrity.com | ⛔ (retiré le 23/10/2026) | Cloudflare bloque GitHub → était relevé depuis le PC ; retiré du comparateur le 23/10/2026 (site autonome) |
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
| 11/10/2026 | bazar.tn | ❌ | lisible (200) mais page quasi vide (1,5 Ko, sans titre ni prix) : pas de boutique d'eau |
| 11/10/2026 | batam.com.tn | ❌ | lisible (200), électroménager/multimédia : pas d'eau en bouteille (le mot anti-robot vient du code de la page, pas d'un vrai blocage) |
| 11/10/2026 | bolt.eu/fr-tn/food (Bolt Food) | ⛔ | application de livraison, page vitrine sans prix d'eau (0 prix) ; prix par commerçant dans l'appli — pas de lecture automatique |
| 11/10/2026 | combien-coute.net | ⛔ | Cloudflare « Just a moment » (403) ; c'est de toute façon un site d'estimations, pas un magasin — pas de contournement |
| 11/10/2026 | Recherche web (courses en ligne, grossistes, Talabat/Bolt/Eat) | ❌ | rien de nouveau : seulement la presse (Tuniscope 13/07, La Presse 19/08 : pénurie, plan du ministère en septembre) ; aucune boutique en ligne nouvelle trouvée |
| 12/10/2026 | talabat.com/tunisia | ⛔ | 404 + mot anti-robot détecté, 0 prix : pas de service Talabat lisible en Tunisie — pas de contournement |
| 12/10/2026 | glovoapp.com (accueil) | ⛔ | réponse vide (202, 0 octet) pour GitHub ; appli de livraison déjà écartée le 08/10 |
| 12/10/2026 | courses.tn, supermarche-en-ligne.tn, mgdrive.tn | ❌ | noms de domaine inexistants (introuvables) |
| 12/10/2026 | Recherche web (Safia/Marwa en ligne, grossistes en ligne) | ❌ | rien de nouveau : presse seulement (Tuniscope 13/07, Webdo 19/08 plafonds, saisies à Sousse) ; EspaceAgro = petites annonces B2B sans prix ni boutique |
| 13/10/2026 | merkado.tn | ⛔ | Cloudflare « Just a moment » (403) pour GitHub, 0 prix lisible — pas de contournement. Boutique en ligne (commande directe du magasin) : à regarder à la main depuis le PC d'Ahmed s'il vend de l'eau (🖥️ ?) |
| 13/10/2026 | lemarche.tn, bimo.tn, sidiboussaid.tn, tunisie.jumia.com | ❌ | noms de domaine inexistants (introuvables) ; lemarche.tn (fruits/légumes/épicerie fine) de toute façon peu probable pour l'eau |
| 13/10/2026 | mg.tn (revu) | ❌ | inchangé : certificat invalide, 0 mot « eau », promotions/catalogues seulement |
| 13/10/2026 | Recherche web (Safia/Marwa en ligne, supermarchés en ligne) | ❌ | rien de nouveau : presse seulement (Tuniscope 13/07, Webdo 19/08) ; Founa (fermé), Farm Trust (bio), lemarche.tn sans eau |
| 14/10/2026 | unigros.com | ❌ | marketplace B2B (grossistes → détaillants) citée par la presse ; lisible (certificat à ignorer) mais simple redirection, 0 prix, 0 « eau ». unigros.tn n'existe pas |
| 14/10/2026 | tunisiamarket.tn | ❌ | lisible (200) mais page quasi vide (1 Ko, titre « Tunisia-market.tn »), 0 prix, 0 « eau », pas de robots.txt |
| 14/10/2026 | Recherche web (Safia/Marwa en ligne, grossistes en ligne WooCommerce) | ❌ | rien de nouveau : presse seulement (Tuniscope 13/07, saisies Sousse, plafonds du 19/08, retour à la normale attendu en septembre) ; aucune boutique d'eau en ligne trouvée |
| 15/10/2026 | epicerie.tn | ❌ | lisible (200) mais page minuscule (5 Ko), 0 prix, 0 « eau », 0 Safia : pas de boutique d'eau |
| 15/10/2026 | sofrimarket.tn, supermarket.tn, eden.tn | ❌ | noms de domaine inexistants (introuvables) |
| 15/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives/courses en ligne) | ❌ | rien de nouveau : presse seulement (Tuniscope 13/07 et 28/07, AllAfrica 26/08 pénurie/non-respect des prix, Tuniscope 2025 sur carrefour.tn déjà utilisé) ; aucune nouvelle boutique d'eau en ligne |
| 16/10/2026 | intigo.tn | ❌ | lisible (200) mais plateforme logicielle (robots.txt « INTIGO intigo.net »), 0 « eau », 0 Safia : pas de boutique d'eau |
| 16/10/2026 | intigo.com.tn, farmtrust.tn | ❌ | injoignables pour GitHub (erreur de connexion) ; Farm Trust = bio, peu probable pour l'eau |
| 16/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et Webdo 19/08 (déjà notés), Founa (fermé) |
| 17/10/2026 | carrefourexpress.tn, tunisiamart.com | ❌ | injoignables pour GitHub (erreur de connexion / domaine inexistant) |
| 17/10/2026 | kamioun.com | ❌ | lisible (200) mais plateforme B2B pour épiceries de quartier (application), page « introuvable », noindex, 0 prix, 0 « eau » |
| 17/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, AllAfrica 26/08 (déjà notés), Founa (fermé) |
| 18/10/2026 | market.tn | ❌ | lisible (200) mais page vide (21 octets), 0 prix, 0 « eau » |
| 18/10/2026 | hypermarche.tn, grossiste.tn | ❌ | injoignables pour GitHub (erreur de connexion / domaine inexistant) |
| 18/10/2026 | baraka.tn | ❌ | lisible (200, 78 Ko) mais 0 mot « eau », 0 Safia, 1 « prix » : pas de boutique d'eau |
| 18/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07, Webdo 19/08, AllAfrica 26/08 (déjà notés), Founa (fermé) |
| 19/10/2026 | sfbt.com.tn, mgdrive.com.tn, epicerie-en-ligne.tn, ubuy.com.tn | ❌ | noms de domaine inexistants (introuvables pour GitHub) |
| 19/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, AllAfrica 26/08 (déjà notés), Founa (fermé), carrefour.tn déjà utilisé |
| 20/10/2026 | founa.com | ❌ | lisible (200) mais page minuscule (114 octets), 0 prix, 0 « eau » ; le drive Founa est fermé (déjà noté) |
| 20/10/2026 | kolchi.tn, souq.tn | ❌ | injoignables pour GitHub (erreur de connexion / domaine inexistant) |
| 20/10/2026 | livraison.tn | ❌ | 404 (19 octets), 0 prix, 0 « eau » |
| 20/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, Webdo 19/08 (déjà notés), Founa (fermé) |
| 21/10/2026 | shopping.tn | ❌ | lisible (200, certificat à ignorer) mais catalogue d'achats généraliste : 0 « eau », 0 Safia, 3 « prix » — pas de prix d'eau |
| 21/10/2026 | grocery.tn, dealmarket.tn | ❌ | noms de domaine inexistants (introuvables pour GitHub) |
| 21/10/2026 | superette.tn | ❌ | injoignable pour GitHub (délai dépassé) |
| 21/10/2026 | Recherche web (Safia/Marwa en ligne, supermarché en ligne pack 6 × 1,5 L) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, Webdo 19/08, La Presse 19/08 (déjà notés) ; combien-coute.net déjà écarté (Cloudflare) |
| 22/10/2026 | monoprix.tn (www) | ⛔ | lisible (200) mais page minuscule (3 Ko), 0 « eau » ; déjà écarté (vérification « humain » / relevé manuel) |
| 22/10/2026 | pharma-shop.tn | ❌ | lisible (200, PrestaShop) mais parapharmacie : 0 Safia, pas d'eau en bouteille |
| 22/10/2026 | tunisiamall.tn, expert-tunisie.tn, cdiscount.tn | ❌ | noms de domaine inexistants (introuvables pour GitHub) |
| 22/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, Webdo 19/08, WebManagerCenter 23/08 (pénurie, 31 usines), Nabeul saisies 12/08 — presse seulement |
| 23/10/2026 | foodealz.com, foodealz.tn, maxi-mg.tn, carrefourmarket.tn | ❌ | injoignables pour GitHub (erreur de connexion / domaine inexistant) ; Foodealz cité par la presse en 2020 (livraison de courses), probablement disparu |
| 23/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux supermarchés en ligne) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, Webdo 19/08, Founa (fermé), Carrefour Market Ben Arous (nov. 2024, déjà couvert par Carrefour) |
| 23/10/2026 | otrity.com (API wp-json/wc/store) | ⛔ | Cloudflare bloque aussi l'API wp-json pour GitHub (vérifié ce jour) : lisible seulement depuis le PC d'Ahmed → **retiré du comparateur** (décision d'Ahmed : site autonome, rien sur le PC). Pas de contournement. À reprendre seulement si GitHub peut le lire (robot `tester-source.yml`) |
| 23/10/2026 | courses.monoprix.tn | ⛔ | Cloudflare bloque même depuis le PC d'Ahmed ; le relevé à la main par captures (data/monoprix.json) est arrêté → **Monoprix retiré du comparateur** (décision d'Ahmed : rien à la main). Pas de contournement |
| 24/10/2026 | monmarche.tn, cityfood.tn, ecomarket.tn | ❌ | noms de domaine inexistants (introuvables pour GitHub) |
| 24/10/2026 | achatenligne.tn | ❌ | injoignable pour GitHub (délai dépassé) |
| 24/10/2026 | Recherche web (Safia/Marwa en ligne, nouveaux drives) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, Webdo 19/08, La Presse 19/08 (déjà notés), Founa (fermé) |
| 25/10/2026 | zenbio.tn, panierfrais.tn, epiceriedirecte.tn | ❌ | noms de domaine inexistants (introuvables pour GitHub) |
| 25/10/2026 | casamarket.tn | ❌ | lisible (200, 314 Ko) mais 0 mot « eau », 0 Safia, 1 « prix » : pas de boutique d'eau |
| 25/10/2026 | Recherche web (Safia/Marwa en ligne, courses en ligne pack 6 × 1,5 L) | ❌ | rien de nouveau : Tuniscope 13/07 et 28/07, La Presse 19/08 et 29/08, AllAfrica 26/08 (déjà notés), combien-coute.net déjà écarté (Cloudflare) |
