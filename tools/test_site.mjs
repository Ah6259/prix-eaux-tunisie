// Test de la page d'accueil, simulée sans navigateur (jsdom).
// À lancer après chaque modification du site :  node tools/test_site.mjs
// jsdom s'installe une fois par PC :  npm install --no-save --no-package-lock jsdom
// Réécrit le 05/10/2026 pour le site actuel (carte « La moins chère », 4 fenêtres, menus de filtres, commande fermée).
import { JSDOM } from "jsdom";
import { readFileSync, existsSync } from "fs";
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
                 "data/votes.js", "data/signalements.js", "app.js"]) {
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

// ---- les 4 barres ouvrent leur fenêtre, la croix la ferme -------------------
for (const [bouton, fenetre, croix, texte] of [
  ["match-open", "match-pop", "match-close", "préférée"],
  ["hadith-open", "hadith-pop", "hadith-close", ""],
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

console.log(erreurs ? `\n${erreurs} PROBLÈME(S)` : "\nTOUT PASSE");
process.exit(erreurs ? 1 : 0);
