// Test de la page d'accueil, simulée sans navigateur (jsdom).
// À lancer après chaque modification du site :  node tools/test_site.mjs
// jsdom s'installe une fois par PC :  npm install --no-save --no-package-lock jsdom
// Réécrit le 05/10/2026 pour le site actuel (carte « La moins chère », 4 fenêtres, menus de filtres, commande fermée).
import { JSDOM } from "jsdom";
import { readFileSync, existsSync, readdirSync, statSync } from "fs";
import { execSync } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const lire = f => readFileSync(join(root, f), "utf8");
// les scripts de la page sont lancés un par un ci-dessous ; GoatCounter est retiré
const html = lire("index.html").replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/g, "");

const dom = new JSDOM(html, { url: "https://ah6259.github.io/prix-eaux-tunisie/", runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
const doc = window.document;
window.open = () => null;
window.fetch = async () => ({ ok: true, json: async () => ({}), text: async () => "" });

let erreurs = 0;
const check = (desc, cond) => { console.log((cond ? "OK   " : "FAIL ") + desc); if (!cond) erreurs++; };
const clic = el => el.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
const cartes = () => [...doc.querySelectorAll("#grid .card")];
const carte = nom => cartes().find(c => c.querySelector("h3")?.textContent === nom);

// ---- chargement : mêmes fichiers et même ordre que index.html -------------
for (const f of ["data/eaux.js", "data/composition.js", "data/historique.js", "data/baisses.js",
                 "data/votes.js", "data/signalements.js", "protection.js", "app.js"]) {
  if (!existsSync(join(root, f))) continue;
  try { window.eval(lire(f)); }
  catch (e) { erreurs++; console.log(`FAIL chargement de ${f} : ${e.message}`); }
}
const DATA = window.EAUX_DATA;

// ---- en haut de page -------------------------------------------------------
const stats = doc.getElementById("stats").textContent;
check("ligne « Mis à jour le … · N marques · N enseignes »",
  stats.startsWith("Mis à jour le") && stats.includes(`${DATA.brands.length} marques`) && /\d enseignes/.test(stats));

// carte verte « La moins chère aujourd'hui » = vraiment la moins chère (stika 1,5 L)
const top = doc.getElementById("top-reponse");
check("carte « La moins chère » affichée", !top.hidden && top.textContent.includes("La moins chère aujourd'hui"));
const prix15 = b => {
  const v = b.products.filter(p => p.category !== "gazeuse" && !p.flavor && Math.abs(p.liters - 1.5) < .01)
    .flatMap(p => Object.values(p.prices));
  return v.length ? Math.min(...v) : null;
};
const minimum = Math.min(...DATA.brands.map(prix15).filter(v => v !== null));
const gagnants = DATA.brands.filter(b => prix15(b) === minimum).map(b => b.name);
check(`gagnant = la moins chère (${gagnants.join(" / ")})`, gagnants.includes(top.querySelector(".top-nom")?.textContent));
check("prix de la carte en stika (×6)", top.querySelector(".top-prix")?.textContent.includes((minimum * 6).toFixed(3).replace(".", ",")));
check("top 2 à 5 affiché", top.querySelectorAll(".top-liste li").length === Math.min(4, DATA.brands.filter(b => prix15(b) !== null).length - 1));
check("bouton Partager WhatsApp", top.querySelector(".top-partage")?.href.startsWith("https://wa.me/?text="));
const plus = doc.getElementById("compare-more");
check("bouton « Voir le classement complet »", !!plus && plus.textContent.includes("classement complet"));
clic(plus);
check("classement complet déplié", doc.getElementById("compare-rest") && !doc.getElementById("compare-rest").hidden);
clic(doc.getElementById("compare-more"));

// ---- verset : une seule ligne, SUR la photo du bandeau (vu en premier), sans bouton ni fenêtre (09/10/2026) ----
check("verset « وَجَعَلْنَا مِنَ الْمَاءِ كُلَّ شَيْءٍ حَيٍّ » sur la photo du bandeau, une seule fois, sans bouton ni fenêtre ; lien vers Points d'eau Tunisie",
  doc.querySelectorAll("p.verset-ligne").length === 1 && !!doc.querySelector(".hero-bande p.verset-photo") && /كُلَّ شَيْءٍ حَيٍّ/.test(doc.querySelector("p.verset-ligne").textContent)
  && !doc.getElementById("hadith-open") && !doc.getElementById("hadith-pop") && !!doc.querySelector('a[href="https://ah6259.github.io/points-eau-tunisie/"]'));
// ---- les 3 barres ouvrent leur fenêtre, la croix la ferme -------------------
for (const [bouton, fenetre, croix, texte] of [
  ["match-open", "match-pop", "match-close", "préférée"],
  ["sig-open", "sig-pop", "sig-close", "Signaler"],
  ["livraison-open", "livraison-pop", "livraison-close", "grandes surfaces"]]) {
  const pop = doc.getElementById(fenetre);
  check(`fenêtre ${fenetre} cachée au départ`, pop.hidden === true);
  clic(doc.getElementById(bouton));
  check(`${bouton} ouvre la fenêtre`, pop.hidden === false && pop.textContent.includes(texte));
  clic(doc.getElementById(croix));
  check(`la croix ferme ${fenetre}`, pop.hidden === true);
}
clic(doc.getElementById("sig-open"));
check("Signaler : liste des marques remplie", doc.querySelectorAll("#sig-marque option").length > DATA.brands.length);
doc.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape" }));
check("Échap ferme la fenêtre Signaler", doc.getElementById("sig-pop").hidden === true);

// ---- barre des filtres : 3 menus -------------------------------------------
check("menu Stika/Bouteille affiche « Stika »", doc.getElementById("dd-mode-txt").textContent === "Stika");
check("menu Format affiche « 1,5 L » au chargement", doc.getElementById("dd-format-txt").textContent.includes("1,5"));
clic(doc.getElementById("dd-format-btn"));
check("le menu Format s'ouvre", doc.getElementById("dd-format").hidden === false);
clic(doc.getElementById("dd-type-btn"));
check("ouvrir un autre menu ferme le premier", doc.getElementById("dd-format").hidden === true && doc.getElementById("dd-type").hidden === false);
clic(doc.body);
check("clic ailleurs : menus fermés", doc.getElementById("dd-type").hidden === true);

// ---- cartes des marques -----------------------------------------------------
check("cartes des marques affichées", cartes().length > 12);
check("tri par défaut : prix croissant", doc.getElementById("sort").value === "prix15");
const fmts = [...doc.querySelectorAll("#grid .fmt")].map(td => td.textContent.trim());
check("au chargement : uniquement du 1,5 L", fmts.length > 5 && fmts.every(f => f.startsWith("1.5 L")));
check("prix affichés en stika par défaut", doc.querySelector("#grid .card table.prices").textContent.includes("Prix stika par enseigne"));
check("boutons + présents", doc.querySelectorAll("#grid .addbtn").length > 8);
check("dernière carte = marque sans prix", cartes().at(-1).textContent.includes("non disponible"));
check("blocs composition présents", doc.querySelectorAll("#grid .compo").length > 10);
check("valeurs hors norme surlignées", doc.querySelectorAll("#grid .cv.over").length > 0);

// Stika -> Bouteille -> Stika
clic(doc.querySelector('#mode-controls [data-mode="bouteille"]'));
check("mode bouteille : en-tête des prix", doc.querySelector("#grid .card table.prices").textContent.includes("Prix bouteille par enseigne"));
check("mode bouteille : bouton du menu mis à jour", doc.getElementById("dd-mode-txt").textContent === "Bouteille");
check("mode bouteille : carte du haut en bouteille", top.textContent.includes("Bouteille 1,5 L"));
clic(doc.querySelector('#mode-controls [data-mode="stika"]'));
check("retour en stika", doc.querySelector("#grid .card table.prices").textContent.includes("Prix stika par enseigne"));

// formats : choix multiples
const bonbonne = doc.querySelector('#format-controls [data-format="bonbonne"]');
clic(bonbonne);
check("ajout des grands formats : vendus à l'unité", doc.getElementById("grid").textContent.includes("à l'unité"));
check("menu Format : « 2 formats »", doc.getElementById("dd-format-txt").textContent === "2 formats");
clic(bonbonne);

// ---- recherche : une marque cherchée s'affiche avec tous ses formats -------
const q = doc.getElementById("q");
const tape = t => { q.value = t; q.dispatchEvent(new window.Event("input", { bubbles: true })); };
tape("hayet");
check("recherche « hayet » : la carte Hayet s'affiche", !!carte("Hayet") && cartes().length === 1);
tape("géant");  // aucune marque ne s'appelle ainsi
check("recherche sans résultat : message « aucune »", cartes().length === 0 && !doc.getElementById("empty").hidden);
tape("SAFIA");
check("recherche sans tenir compte des majuscules", !!carte("Safia"));
tape("");
check("recherche effacée : toutes les cartes reviennent", cartes().length > 12);

// tri par minéralité (TDS)
const sort = doc.getElementById("sort");
sort.value = "tds"; sort.dispatchEvent(new window.Event("change"));
const tds = cartes().map(c => c.querySelector("h3").textContent);
check("tri par minéralité : cartes réordonnées", tds.length > 12);
// la 1re carte doit être l'eau AVEC PRIX la moins minéralisée, quel que soit son format (Hayet n'existe qu'en 1 L)
// résidu sec AFFICHÉ sur chaque carte (« résidu sec 238 mg/L », 1re valeur si plusieurs sources)
const tdsCarte = c => {
  const m = (c.querySelector(".compo summary")?.textContent || "").replace(/[\s  ]/g, "").match(/résidusec([\d,]+)/);
  return m ? parseFloat(m[1].replace(",", ".")) : null;
};
const avecPrix = DATA.brands.filter(b => b.products.some(p => Object.keys(p.prices).length));
const cartesPrix = cartes().filter(c => c.querySelector("table.prices")).map(c => ({ n: c.querySelector("h3").textContent, t: tdsCarte(c) }))
  .filter(x => x.t != null);
const plusPetit = Math.min(...cartesPrix.map(x => x.t));
const hayet = cartesPrix.find(x => x.n === "Hayet");
check(`tri par résidu sec : 1re carte avec prix = la plus petite valeur (${cartesPrix[0]?.n} ${cartesPrix[0]?.t} mg/L)${hayet ? ", et c'est Hayet" : ""}`,
  cartesPrix.length > 5 && cartesPrix[0].t === plusPetit && (!hayet || cartesPrix[0].n === "Hayet"));
check("tri par minéralité : Hayet présente (vendue seulement en 1 L)", !avecPrix.some(b => b.name === "Hayet") || tds.includes("Hayet"));
sort.value = "prix15"; sort.dispatchEvent(new window.Event("change"));

// ---- panier et commande (FERMÉE : formulaire grisé + tampon) ----------------
check("barre du panier cachée au départ", doc.getElementById("cartbar").hidden === true);
const btnPlus = doc.querySelector("#grid .addbtn");
clic(btnPlus);
check("barre du panier visible après un +", doc.getElementById("cartbar").hidden === false);
check("compteur 1 sur « Commander »", doc.getElementById("cart-open").textContent.includes("1"));
check("barre du panier sans prix d'enseigne", !doc.getElementById("cartbar-info").textContent.includes("DT"));
clic(btnPlus);
check("même produit ajouté deux fois : 2 articles", doc.getElementById("cartbar-info").textContent.includes("2 articles"));
clic(doc.getElementById("cart-open"));
check("panneau de commande ouvert", doc.getElementById("order-overlay").hidden === false);
check("un seul article dans le panneau", doc.querySelectorAll(".order-item").length === 1);
check("commande fermée : formulaire grisé", doc.querySelector("fieldset.order-fields").disabled === true);
check("commande fermée : tampon « En cours de développement »", doc.getElementById("order-soon").textContent.includes("En cours de développement"));
clic(doc.querySelector("[data-inc]"));
check("quantité 3 après +", doc.querySelector(".qty b").textContent === "3");
for (let i = 0; i < 3; i++) clic(doc.querySelector("[data-dec]"));
check("panier vide après 3 × −", doc.getElementById("cartbar").hidden === true);

// ---- bas de page -------------------------------------------------------------
const pied = doc.getElementById("foot").textContent;
check("pied de page : sources Carrefour, Géant, Otrity", ["Carrefour", "Géant", "Otrity"].every(s => pied.includes(s)));
check("pied de page : marques et logos à leurs propriétaires", pied.includes("appartiennent à leurs propriétaires"));
check("FAQ : nombre de marques", doc.getElementById("faq-nb-marques").textContent === String(DATA.brands.length));
check("courbe d'évolution des prix", !!doc.querySelector("#histo svg"));

// ---- vraie photo du bandeau : fichier, crédit + licence affichés, preuve de licence ------------------
const LICENCE = /CC BY-SA \d\.\d|CC BY \d\.\d|CC0|domaine public/;
const css = lire("style.css");
const hero = doc.querySelector(".hero.hero-photo");
const imgBande = hero?.querySelector(".hero-bande img");
const fichiersBande = imgBande ? [imgBande.getAttribute("src"), ...(imgBande.getAttribute("srcset") || "").split(",").map(s => s.trim().split(/\s+/)[0])].filter(Boolean) : [];
const photo = fichiersBande[0];
check("bandeau : vraie photo NETTE au-dessus du texte (fichiers présents, texte alternatif)", !!hero && fichiersBande.length >= 1 &&
  fichiersBande.every(f => /\.(jpe?g|webp)$/.test(f) && existsSync(join(root, f))) && (imgBande.getAttribute("alt") || "").length > 10);
check("bandeau : photo légère (≤ 150 Ko chaque fichier)", fichiersBande.length >= 1 && fichiersBande.every(f => existsSync(join(root, f)) && statSync(join(root, f)).size <= 150_000));
check("bandeau : photo pas noyée (aucun dégradé ni flou par-dessus)", !/\.hero-photo\{[^}]*url\(/.test(css) && !/\.hero-bande[^{]*\{[^}]*(filter|blur)/.test(css));
const credit = hero?.querySelector(".credit-photo");
check("bandeau : crédit et licence de la photo affichés", !!credit && /Photo/.test(credit.textContent) && LICENCE.test(credit.textContent)
      && credit.textContent.includes("Wikimedia Commons") && !!credit.querySelector('a[rel~="license"]'));
const creditPied = doc.querySelector("footer .credit-pied")?.textContent || "";
check("pied de page : crédit de la photo", creditPied.includes("Photo") && LICENCE.test(creditPied));
// photo du bandeau NEUTRE (aucune marque : sinon les visiteurs croient à une publicité) — déclarée par le nom de fichier
check("bandeau : photo déclarée NEUTRE, sans marque (fichiers photo-neutre-*)", fichiersBande.length >= 2 && fichiersBande.every(f => /^assets\/photo-neutre-[a-z0-9-]+\.jpg$/.test(f)));
check("bandeau : crédit de l'auteur affiché sur la photo et dans le pied de page", !!credit && /Shixart1985/.test(credit.textContent) && /Shixart1985/.test(creditPied));
check("plus aucune ancienne photo de marques (photo-eaux-tunisie*) dans le dépôt ni dans la page", !existsSync(join(root, "assets/photo-eaux-tunisie.jpg"))
  && !existsSync(join(root, "assets/photo-eaux-tunisie-720.jpg")) && !lire("index.html").includes("photo-eaux-tunisie"));
// preuves (dossier ignoré par git) : vérifiées sur le PC d'Ahmed, absentes sur GitHub
const dossierPreuves = join(root, "preuves conditions d'utilisation");
const lisezMoi = existsSync(dossierPreuves) ? readdirSync(dossierPreuves).map(d => join(dossierPreuves, d, "photos", "LISEZ-MOI.md"))
  .filter(existsSync).map(f => readFileSync(f, "utf8")).join("\n") : null;
if (lisezMoi === null) console.log("SAUTÉ preuve de licence de la photo (dossier des preuves absent, normal sur GitHub)");
else check("preuve de licence de la photo sauvegardée", !!credit?.dataset.source && lisezMoi.includes(credit.dataset.source));

// ---- image d'aperçu des liens partagés : v4, sans nombre de marques ni noms de magasins -------------
const guides = ["prix-stika/index.html", "quelle-eau/index.html"];
const marques = readdirSync(join(root, "marque")).map(m => `marque/${m}/index.html`).filter(f => existsSync(join(root, f)));
// WhatsApp n'affiche la GRANDE image d'aperçu que si le fichier pèse moins d'environ 300 Ko : JPEG léger obligatoire
const og = existsSync(join(root, "assets/og-image-v7.jpg")) ? readFileSync(join(root, "assets/og-image-v7.jpg")) : Buffer.alloc(0);
check("image d'aperçu og-image-v7.jpg : JPEG de moins de 250 Ko (grande image sur WhatsApp)", og.length > 0 && og.length < 250 * 1024 && og[0] === 0xFF && og[1] === 0xD8);
check("accueil, guides et pages marques : image d'aperçu v7 en JPEG (og:image:type)", ["index.html", ...guides, ...marques].every(f => lire(f).includes("assets/og-image-v7.jpg")
  && lire(f).includes('<meta property="og:image:type" content="image/jpeg">')));
check("plus aucune référence aux anciennes images d'aperçu (v2 à v5)", ["index.html", ...guides, ...marques, "tools/build_guides.py", "tools/build_pages.py"].every(f => !/og-image-v[2345]/.test(lire(f)))
  && !existsSync(join(root, "assets/og-image-v5.jpg")));

// ---- sécurité, robots d'IA et anti-copie (consigne d'Ahmed du 05/10/2026) --------------------------
const robots = lire("robots.txt");
const blocs = robots.split(/\n\s*\n/).filter(b => /User-agent/i.test(b));
const regle = ua => { const b = blocs.find(b => new RegExp(`^User-agent: ${ua}\\s*$`, "mi").test(b));
  return b ? (/^Disallow: \/\s*$/m.test(b) ? "interdit" : "permis") : "absent"; };
const ROBOTS_IA = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-Web", "anthropic-ai", "CCBot", "Google-Extended",
  "Applebot-Extended", "PerplexityBot", "Bytespider", "Amazonbot", "Meta-ExternalAgent", "FacebookBot", "Diffbot", "Omgilibot",
  "cohere-ai", "ImagesiftBot", "HTTrack", "WebCopier", "WebZIP", "Offline Explorer", "wget", "SiteSnagger"];
for (const ua of ROBOTS_IA) check(`robots.txt interdit ${ua}`, regle(ua) === "interdit");
check("robots.txt laisse passer Googlebot, Bingbot et les autres", regle("Googlebot") === "permis" && regle("Bingbot") === "permis" && regle("\\*") === "permis");
const toutesPages = ["index.html", ...guides, ...marques];
const sur = (desc, test) => { const ko = toutesPages.filter(f => !test(lire(f), f));
  check(`${desc} (${toutesPages.length} pages)${ko.length ? " — manque : " + ko.slice(0, 3).join(", ") : ""}`, ko.length === 0); };
sur("meta noai, noimageai", s => s.includes('<meta name="robots" content="noai, noimageai">'));
sur("pas de traduction automatique (translate=\"no\" + meta google notranslate)", s => /<html lang="fr" translate="no">/.test(s) && s.includes('<meta name="google" content="notranslate">'));
sur("referrer strict-origin-when-cross-origin", s => s.includes('<meta name="referrer" content="strict-origin-when-cross-origin">'));
sur("script anti-copie protection.js chargé", s => /<script src="(\.\.\/)*protection\.js\?v=/.test(s));
sur("CSP présente, sans script en ligne permis", s => /http-equiv="Content-Security-Policy" content="[^"]*script-src 'self'/.test(s) && !/script-src[^;]*unsafe/.test(s));
sur("aucun script dans la page (bloqué par la CSP)", s => !/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>/.test(s) && !/<[a-z]+ [^>]*\son(error|load|click)=/.test(s));
sur("aucun gestionnaire d'événement en ligne (attribut on…=, bloqué par la CSP)", s => !/<[a-z][^>]*\son[a-z]+\s*=/i.test(s));
check("app.js ne génère aucun attribut on…= dans son HTML (bloqué par la CSP)", !/\son[a-z]+=["'`]/.test(lire("app.js")));
sur("statistiques GoatCounter (sans cookies) chargées, CSP compatible", s => s.includes('<script data-goatcounter="https://prix-eaux-tunisie.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>')
  && /script-src[^;]*https:\/\/gc\.zgo\.at/.test(s) && /connect-src[^;]*https:\/\/prix-eaux-tunisie\.goatcounter\.com/.test(s) && /img-src[^;]*https:\/\/prix-eaux-tunisie\.goatcounter\.com/.test(s));
// manifeste : id UNIQUE = chemin du site (tous les sites d'Ahmed partagent ah6259.github.io ; sinon « déjà installée »)
let man = {}; try { man = JSON.parse(lire("manifest.webmanifest")); } catch (e) {}
check("manifeste présent, id unique = chemin du site, icônes existantes", man.id === "/prix-eaux-tunisie/" && !!man.name && man.display === "standalone"
  && man.icons?.length > 0 && man.icons.every(i => existsSync(join(root, i.src))) && lire("index.html").includes('rel="manifest"'));
sur("liens externes en rel=\"noopener\"", s => [...s.matchAll(/<a [^>]*href="https?:\/\/[^"]+"[^>]*>/g)].every(m => /rel="[^"]*noopener/.test(m[0])));
// la CSP autorise tout ce qu'utilisent la page et app.js (sinon formulaires, statistiques ou carte cassés)
const csp = lire("index.html").match(/Content-Security-Policy" content="([^"]+)"/)[1];
const dir = n => (csp.match(new RegExp(`${n} ([^;]+)`)) || [, ""])[1];
check("CSP : Google Forms (signaler, vote) autorisé", dir("connect-src").includes("https://docs.google.com") && dir("form-action").includes("https://docs.google.com"));
check("CSP : Formspree (votre avis) autorisé", dir("connect-src").includes("https://formspree.io") && dir("form-action").includes("https://formspree.io"));
check("CSP : GoatCounter autorisé", dir("script-src").includes("https://gc.zgo.at") && dir("connect-src").includes("goatcounter.com"));
check("CSP : Google Fonts autorisées", dir("style-src").includes("https://fonts.googleapis.com") && dir("font-src").includes("https://fonts.gstatic.com"));
check("CSP : carte Leaflet (cdnjs + tuiles OpenStreetMap) autorisée", dir("script-src").includes("https://cdnjs.cloudflare.com") && dir("img-src").includes("tile.openstreetmap.org"));
const domainesAppJs = [...new Set([...lire("app.js").matchAll(/(?:url|src|href)\s*[:=]\s*["'`](https:\/\/[^/"'`$]+)/g)].map(m => m[1]))]
  .filter(d => !/wa\.me|t\.me|maps\.google|ah6259\.github\.io/.test(d));   // simples liens, rien n'est chargé
check(`CSP : chaque domaine chargé par app.js est autorisé (${domainesAppJs.join(", ")})`, domainesAppJs.length > 1 && domainesAppJs.every(d => csp.includes(d)));
const prot = lire("protection.js");
check("anti-copie : clic droit et glisser bloqués sur les photos", prot.includes('"contextmenu"') && prot.includes('"dragstart"') && /img\{[^}]*-webkit-touch-callout:none/.test(css));
check("anti-copie : source ajoutée au texte copié", prot.includes('"copy"') && prot.includes("© tous droits réservés"));
check("anti-copie : anti-iframe d'un autre site", prot.includes("window.top !== window.self"));
check("champs, formulaires, liens et boutons restent sélectionnables", /input, select, textarea, form, form \*, a, button\{user-select:text/.test(css));
// formulaires toujours utilisables avec la protection chargée
clic(doc.getElementById("sig-open"));
const champsSig = [...doc.querySelectorAll("#sig-form input, #sig-form select")];
check("Signaler un prix : champs utilisables", champsSig.length > 2 && champsSig.every(x => !x.disabled));
doc.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape" }));
check("Votre avis (Formspree) : formulaire présent", !!doc.getElementById("avis-form")?.getAttribute("action")?.startsWith("https://formspree.io/"));
tape("safia");
check("recherche toujours utilisable", !!carte("Safia"));
tape("");
// photos des bouteilles : chaque marque a une photo, OU est notée « sans image libre trouvée » ;
// chaque photo libre (Open Food Facts…) a son crédit sous la photo (accueil + page marque) et en pied de page
const LIBRES = JSON.parse(lire("data/photos_libres.json"));
const sansPhoto = DATA.brands.filter(b => !(b.img && existsSync(join(root, b.img))) && !(b.id in LIBRES.sans_image_libre));
check(`chaque marque a une photo ou est notée sans image libre${sansPhoto.length ? " : " + sansPhoto.map(b => b.name).join(", ") : ""}`, sansPhoto.length === 0);
for (const [id, ph] of Object.entries(LIBRES.photos)) {
  check(`photo libre ${id} : fichier présent, ≤ 60 Ko, page et licence notées`,
    existsSync(join(root, ph.img)) && statSync(join(root, ph.img)).size <= 60000 && /^https:\/\//.test(ph.page) && /^https:\/\/creativecommons\.org\//.test(ph.licence_url) && !!ph.credit);
}
const avecCredit = DATA.brands.filter(b => b.img_credit);
for (const b of DATA.brands.filter(b => Object.values(LIBRES.photos).some(ph => ph.img === b.img)))
  check(`${b.name} : la photo libre a son crédit dans les données`, !!b.img_credit && b.img_credit.page.startsWith("https://"));
tape("");
for (const b of avecCredit) {
  const c = carte(b.name);
  const fig = c?.querySelector(".card-head figure.photo-libre");
  check(`${b.name} : crédit « Photo : ${b.img_credit.source}, CC BY-SA » sous la photo (accueil)`,
    !!fig && fig.querySelector("img")?.getAttribute("src") === b.img && fig.querySelector(".credit-photo")?.textContent.includes(`Photo : ${b.img_credit.source}, CC BY-SA`)
    && !!fig.querySelector(`a[href="${b.img_credit.page}"]`));
  const pm = existsSync(join(root, "marque", b.id, "index.html")) ? lire(`marque/${b.id}/index.html`) : "";
  check(`${b.name} : photo + crédit sur la page marque`, pm.includes(`../../${b.img}`) && pm.includes(`Photo : ${b.img_credit.source}</a>, `) && pm.includes(b.img_credit.page));
}
check("photos sans crédit : aucune (chaque photo libre est créditée)",
  DATA.brands.every(b => !b.img || !b.img.startsWith("assets/img/libres/") || b.img_credit));
if (avecCredit.length)
  check("pied de page : crédit Open Food Facts CC BY-SA", doc.querySelector("footer").textContent.includes("Open Food Facts") && doc.querySelector("footer").textContent.includes("CC BY-SA"));
// aucun secret ni e-mail privé dans les fichiers suivis par git
const suivis = execSync("git ls-files", { cwd: root, encoding: "utf8" }).split("\n").filter(f => /\.(html|js|mjs|py|yml|md|txt|json|css|ps1|bat)$/.test(f));
const fuite = suivis.filter(f => /(api[_-]?key|secret|token|password)\s*[:=]\s*["'][A-Za-z0-9_\-]{16,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{30,}|\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}|[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook)\.[a-z]+/i.test(lire(f)));
check(`aucun secret ni e-mail privé dans le dépôt${fuite.length ? " : " + fuite.join(", ") : ""}`, fuite.length === 0);

// ---- Affichage : éléments cachés et faux boutons (06/10/2026) ----
check("style : [hidden]{display:none!important} (un élément caché par le JS ne réapparaît jamais à cause d'un display:flex/grid)",
      /\[hidden\]\{display:none!important\}/.test(lire("style.css").replace(/\s+/g, "")));
// Tuiles « icône + petit texte » qui ont l'air de boutons mais ne mènent nulle part (supprimées le 06/10/2026, demande d'Ahmed)
// (une étiquette en gras dans un encadré qui donne une vraie information, ex. « Coût : 50 DT », n'est pas une tuile)
const tuilesSansLien = doc => [...doc.body.querySelectorAll("*")].filter(el => {
  if (/^(a|button|label|summary|svg|h[1-6]|b|strong|em|small|i|option|select|input|textarea|form|header|footer|nav|main|figure|img|section|article)$/i.test(el.tagName)) return false;
  if (el.closest("a,button,label,summary,header,footer,nav,form,svg,[hidden],template")) return false;
  const f = el.firstElementChild;
  if (!f || f.tagName.toLowerCase() !== "svg" || el.querySelector("a,button,input,select,textarea")) return false;
  const t = el.textContent.replace(/\s+/g, " ").trim();
  return t.length > 0 && t.length < 90;
}).map(el => el.textContent.replace(/\s+/g, " ").trim().slice(0, 40));
{
  const morts = ["index.html", ...guides, ...marques].flatMap(f => tuilesSansLien(new JSDOM(lire(f)).window.document).map(t => f + " → " + t));
  check(`accueil, guides et pages marques : aucune carte avec une icône sans lien (pas de faux bouton) ${morts.join(" | ")}`, !morts.length);
}
check("accueil : plus de badges ; « Gratuit, sans inscription » dans l'intro, lien vers les sources gardé", !/badge-c|class="confiance"/.test(lire("index.html"))
  && /Gratuit, sans inscription/.test(lire("index.html")) && /<a href="#sources">sources citées<\/a>/.test(lire("index.html")));

// ---- Boutons « Partager » existants, harmonisés avec les autres sites (06/10/2026) ----
// sans navigator.share : le lien wa.me (avec l'adresse de la page) s'ouvre normalement ; avec : menu de partage du téléphone ; clic compté
{
  const essai = async (chemin, sel, adresse, avecShare) => {
    const h = lire(chemin).replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/g, "");
    const w = new JSDOM(h, { url: adresse, runScripts: "outside-only" }).window;
    w.eval(lire("protection.js"));
    const comptes = [], partages = [], ouverts = [];
    w.goatcounter = { count: o => comptes.push(o) };
    w.open = u => { ouverts.push(u); return null; };
    if (avecShare) Object.defineProperty(w.navigator, "share", { value: d => { partages.push(d); return Promise.resolve(); } });
    const a = w.document.querySelector(sel);
    if (!a) return null;
    const ev = new w.MouseEvent("click", { bubbles: true, cancelable: true });
    a.dispatchEvent(ev);
    await new Promise(ok => setTimeout(ok, 0));
    return { a, ouvert: !ev.defaultPrevented, comptes, partages, ouverts };
  };
  const URLS = "https://ah6259.github.io/prix-eaux-tunisie/";
  for (const [chemin, sel, adresse] of [["marque/aqualine/index.html", "a.bouton-wa", URLS + "marque/aqualine/"], ["prix-stika/index.html", "a.bouton-wa", URLS + "prix-stika/"], ["quelle-eau/index.html", "a.bouton-wa", URLS + "quelle-eau/"]]) {
    const r = await essai(chemin, sel, adresse, false);
    // partage par lien (demande d'Ahmed, octobre 2026) : la page vidéo du site + l'adresse de la page dans le texte
    check(`${chemin} : sans navigator.share, « Partager » ouvre WhatsApp avec la page vidéo + l'adresse de la page et compte le clic (partage/…)`, !!r && r.ouverts.length === 1
      && r.ouverts[0].startsWith("https://wa.me/?text=") && decodeURIComponent(r.ouverts[0]).includes(adresse) && decodeURIComponent(r.ouverts[0]).includes(URLS + "video/")
      && r.comptes.length === 1 && r.comptes[0].path.startsWith("partage/") && r.comptes[0].event === true);
    const r2 = await essai(chemin, sel, adresse, true);
    check(`${chemin} : avec navigator.share, menu de partage : page vidéo (url) + adresse de la page (texte), WhatsApp pas ouvert en plus`, !!r2 && !r2.ouvert
      && r2.partages.length === 1 && r2.partages[0].url === URLS + "video/" && r2.partages[0].text.includes(adresse) && !r2.ouverts.length);
  }
  // accueil : le petit bouton sous le prix (fabriqué par app.js) passe par le même code
  const ev = new window.MouseEvent("click", { bubbles: true, cancelable: true }), comptes = [], ouv = [];
  window.goatcounter = { count: o => comptes.push(o) };
  const ancienOpen = window.open; window.open = u => { ouv.push(u); return null; };
  top.querySelector(".top-partage").dispatchEvent(ev);
  window.open = ancienOpen;
  check("accueil : sans navigator.share, le petit bouton « Partager » ouvre WhatsApp avec la page vidéo + l'adresse du site et compte le clic", ev.defaultPrevented
    && ouv.length === 1 && decodeURIComponent(ouv[0]).includes(URLS + "video/") && decodeURIComponent(ouv[0]).includes(URLS) && comptes.length === 1 && comptes[0].path === "partage/");
  check("un seul bouton « Partager » par page (pas de doublon)", (lire("marque/aqualine/index.html").match(/href="https:\/\/wa\.me\/\?text=/g) || []).length === 1
    && (lire("prix-stika/index.html").match(/href="https:\/\/wa\.me\/\?text=/g) || []).length === 1);
  // bouton Partager de l'EN-TÊTE sur toutes les pages (règle commune à tous les sites ; oubli corrigé le 09/10/2026)
  const sansBouton = [];
  for (const chemin of ["index.html", "video/index.html", ...guides, ...marques]) {
    const r = await essai(chemin, "header.site .partager[data-partager-video]", URLS + chemin.replace(/index\.html$/, ""), false);
    if (!r || r.a.ownerDocument.querySelectorAll("header.site .partager").length !== 1 || r.ouverts.length !== 1
      || !decodeURIComponent(r.ouverts[0]).includes(URLS + "video/")) sansBouton.push(chemin);
  }
  check(`toutes les pages : un bouton Partager dans l'en-tête qui partage la page vidéo ${sansBouton.join(" | ")}`, !sansBouton.length);
}

console.log(erreurs ? `\n${erreurs} PROBLÈME(S)` : "\nTOUT PASSE");
process.exit(erreurs ? 1 : 0);
