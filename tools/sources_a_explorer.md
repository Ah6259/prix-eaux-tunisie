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
