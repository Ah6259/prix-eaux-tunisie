import { JSDOM } from "jsdom";
import { readFileSync } from "fs";

const root = "C:/Ahmed_2501_01/personnel/_claude code project/eau minerale Tunisienne Prix";
const html = readFileSync(root + "/index.html", "utf8")
  .replace(/<script[^>]*src="data\/eaux\.js"><\/script>/, "")
  .replace(/<script[^>]*src="app\.js"><\/script>/, "")
  .replace(/<script[^>]*goatcounter[^>]*><\/script>/, "");

const dom = new JSDOM(html, { url: "https://ah6259.github.io/prix-eaux-tunisie/", runScripts: "outside-only" });
const { window } = dom;
global.window = window;

const run = (file) => {
  const code = readFileSync(root + "/" + file, "utf8");
  window.eval(code);
};

let errors = 0;
try {
  run("data/eaux.js");
  run("data/composition.js");
  run("data/historique.js");
  run("app.js");
} catch (e) {
  errors++;
  console.error("ERREUR au chargement:", e.message, "\n", e.stack?.split("\n").slice(0,4).join("\n"));
}

const doc = window.document;
const check = (desc, cond) => { console.log((cond ? "OK " : "FAIL ") + desc); if (!cond) errors++; };

check("stats remplis (4 avec la date)", doc.getElementById("stats").children.length === 4);
check("date de maj en tete de site", doc.getElementById("stats").textContent.includes("prix mis à jour"));
const stikaBtn = doc.querySelector('#mode-controls [data-mode="stika"]');
check("bouton Stika present, colore, actif par defaut",
  stikaBtn && stikaBtn.className.includes("chip-stika") && stikaBtn.getAttribute("aria-pressed") === "true");
check("prix affiches en stika par defaut", doc.querySelector("#grid .card table.prices").textContent.includes("Prix stika par enseigne"));
check("icone stika sur le bouton", !!doc.querySelector(".chip-stika .ic-stika"));
check("icone stika en 3D (degrades)", doc.querySelectorAll(".ic-stika linearGradient").length >= 3);
check("Stika est le premier bouton", doc.querySelector("#mode-controls .chipbtn").className.includes("chip-stika"));

// courbe d'evolution des prix
const nJours = window.EAUX_HISTO.serie.length;
check("courbe des prix rendue", !!doc.querySelector("#histo svg .serie"));
check("un repere par jour", doc.querySelectorAll("#histo .pt").length === nJours);
check("dernier prix etiquete", doc.querySelector("#histo .val").textContent.includes("DT"));
check("vue tableau de la courbe", doc.querySelectorAll("#histo .histo-table tr").length === nJours + 1);
check("comparateur rempli", doc.getElementById("compare").innerHTML.includes("winner"));
check("cartes marques", doc.querySelectorAll("#grid .card").length > 12);
check("boutons + presents", doc.querySelectorAll("#grid .addbtn").length > 8);

// defauts au chargement : stika 1,5 L, tri prix croissant, marques sans prix a la fin
check("tri par defaut : prix croissant", doc.getElementById("sort").value === "prix15");
check("filtre par defaut : 1,5 L", doc.querySelector('#format-controls [data-format="1.5"]').getAttribute("aria-pressed") === "true");
const cards0 = [...doc.querySelectorAll("#grid .card")];
check("derniere carte = marque sans prix", cards0[cards0.length - 1].textContent.includes("non disponible"));
const hayet = cards0.find(c => c.querySelector("h3")?.textContent === "Hayet");
check("Hayet presente sans prix", !!hayet && hayet.textContent.includes("non disponible"));
check("Hayet avec composition", !!hayet && !!hayet.querySelector(".compo"));
check("Hayet sans bouton +", !!hayet && !hayet.querySelector(".addbtn"));
check("footer rempli", doc.getElementById("foot").textContent.includes("Sources"));
check("faq nb marques", doc.getElementById("faq-nb-marques").textContent === String(window.EAUX_DATA.brands.length));
check("faq liste marques", doc.getElementById("faq-marques-liste").textContent.includes(" et "));
check("cartbar cachee au depart", doc.getElementById("cartbar").hidden === true);

// simulation : ajout au panier
const btn = doc.querySelector("#grid .addbtn");
btn.click();
check("cartbar visible apres ajout", doc.getElementById("cartbar").hidden === false);
check("compteur d articles sur le bouton Commander", doc.getElementById("cart-open").textContent.includes("1"));
check("cartbar sans prix d enseigne", !doc.getElementById("cartbar-info").textContent.includes("DT"));
check("cartbar renvoie vers WhatsApp", doc.getElementById("cartbar-info").textContent.includes("WhatsApp"));

// second ajout du meme produit -> quantite 2
btn.click();
check("quantite cumulee", doc.getElementById("cartbar-info").textContent.includes("2 articles"));

// ouvrir le panneau
doc.getElementById("cart-open").click();
check("panneau ouvert", doc.getElementById("order-overlay").hidden === false);
check("article dans le panneau", doc.querySelectorAll(".order-item").length === 1);
check("pas de prix dans le panneau", !doc.getElementById("order-items").textContent.includes("DT"));
check("mention prix confirme WhatsApp", doc.getElementById("order-total").textContent.includes("WhatsApp"));

// quantite +1 puis -3 -> panier vide
doc.querySelector("[data-inc]").click();
check("qty=3 apres +", doc.querySelector(".qty b").textContent === "3");
doc.querySelector("[data-dec]").click();
doc.querySelector("[data-dec]").click();
doc.querySelector("[data-dec]").click();
check("panier vide apres -3", doc.getElementById("cartbar").hidden === true);

// re-ajout puis message WhatsApp
btn.click();
doc.getElementById("cart-open").click();
doc.getElementById("o-tel").value = "24 321 390";
doc.getElementById("o-adr").value = "12 rue de Marseille, Tunis";
doc.getElementById("o-nom").value = "Test Client";

let opened = null;
window.open = (url) => { opened = url; return null; };
doc.getElementById("order-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
check("lien wa.me genere", opened && opened.startsWith("https://wa.me/21624321390?text="));
if (opened) {
  const msg = decodeURIComponent(opened.split("text=")[1]);
  console.log("--- message WhatsApp genere ---\n" + msg + "\n-------------------------------");
  check("message contient produit en stika par defaut", /• 1 × stika \(\d+ bouteilles\)/.test(msg));
  check("message sans prix d enseigne", !msg.includes("DT") && !msg.includes("Carrefour"));
  check("message contient tel", msg.includes("24 321 390"));
  check("message contient adresse", msg.includes("rue de Marseille"));
}

// changement d'unite stika -> bouteille dans le panier
const unitSel = doc.querySelector(".oi-unit");
check("menu d unite present", !!unitSel);
unitSel.value = "bouteille";
unitSel.dispatchEvent(new window.Event("change", { bubbles: true }));
check("unite passee en bouteille", doc.querySelector(".oi-unit").value === "bouteille");

// bascule Stika <-> Bouteille : une seule unite affichee a la fois
doc.querySelector('#mode-controls [data-mode="bouteille"]').click();
check("mode bouteille : en-tete change", doc.querySelector("#grid .card table.prices").textContent.includes("Prix bouteille par enseigne"));
check("mode bouteille : pas de mention stika dans l en-tete", !doc.querySelector("#grid .card table.prices tr").textContent.includes("stika"));
doc.querySelector('#mode-controls [data-mode="stika"]').click();
check("retour mode stika", doc.querySelector("#grid .card table.prices").textContent.includes("Prix stika par enseigne"));
check("le + est en premiere colonne", doc.querySelector("#grid .card table.prices tr:nth-child(2) td").className.includes("addc"));

// filtre par format
const chip15 = doc.querySelector('#format-controls [data-format="1.5"]');
check("puces de format presentes", doc.querySelectorAll("#format-controls .chipbtn").length === 6);
chip15.click();
const fmts = [...doc.querySelectorAll("#grid .fmt")].map(td => td.textContent.trim());
check("filtre 1,5 L : uniquement du 1,5 L", fmts.length > 5 && fmts.every(f => f.startsWith("1.5 L")));
doc.querySelector('#format-controls [data-format="bonbonne"]').click();
check("filtre grands formats : vendus a l unite", doc.getElementById("grid").textContent.includes("à l'unité"));
doc.querySelector('#format-controls [data-format=""]').click();

// composition
check("blocs composition presents", doc.querySelectorAll("#grid .compo").length > 15);
const safia = [...doc.querySelectorAll("#grid .card")].find(c => c.querySelector("h3")?.textContent === "Safia");
check("Safia a 2 colonnes de composition", safia && safia.querySelectorAll(".compo-table th").length === 3);
check("valeurs hors norme surlignees", doc.querySelectorAll("#grid .cv.over").length > 0);
const garci = [...doc.querySelectorAll("#grid .card")].find(c => c.querySelector("h3")?.textContent === "Garci");
check("Garci TDS 1677 affiche", garci && /1\D677/.test(garci.querySelector(".compo summary").textContent));

// localisation : carte + confirmation obligatoire
let markerPos = { lat: 36.100001, lng: 10.200001 };
window.L = {
  map: () => ({ setView(){ return this; }, on(){}, invalidateSize(){} }),
  tileLayer: () => ({ addTo(){} }),
  marker: (ll) => ({ addTo(){ return this; }, setLatLng(p){ markerPos = p; }, getLatLng: () => markerPos, on(){} }),
};
Object.defineProperty(window.navigator, "geolocation", {
  value: { getCurrentPosition: (ok) => ok({ coords: { latitude: 36.100001, longitude: 10.200001 } }) },
  configurable: true,
});
doc.getElementById("o-geo").click();
await new Promise(r => setTimeout(r, 250));
check("carte affichee apres localisation", doc.getElementById("geo-box").hidden === false);
check("statut demande de verifier", doc.getElementById("o-geo-status").textContent.includes("Vérifiez"));

// avant confirmation : la position ne part PAS dans le message
opened = null;
doc.getElementById("o-tel").value = "24 321 390";
doc.getElementById("o-adr").value = "12 rue de Marseille, Tunis";
doc.getElementById("order-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
let msg2 = opened ? decodeURIComponent(opened.split("text=")[1]) : "";
check("position absente si non confirmee", !msg2.includes("maps.google.com"));

// le client ajuste le repere puis confirme
markerPos = { lat: 36.123456, lng: 10.654321 };
doc.getElementById("o-geo-confirm").click();
check("carte repliee apres confirmation", doc.getElementById("geo-box").hidden === true);
check("statut position confirmee", doc.getElementById("o-geo-status").textContent.includes("confirmée"));
opened = null;
doc.getElementById("order-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
msg2 = opened ? decodeURIComponent(opened.split("text=")[1]) : "";
check("position confirmee dans le message", msg2.includes("Position exacte confirmée par le client : https://maps.google.com/?q=36.123456,10.654321"));

// tri par mineralite
doc.getElementById("sort").value = "tds";
doc.getElementById("sort").dispatchEvent(new window.Event("change"));
const firstCards = [...doc.querySelectorAll("#grid .card h3")].map(h => h.textContent);
check("tri TDS : Hayet (238 mg/L) en premier", firstCards[0] === "Hayet");
const anyCard = [...doc.querySelectorAll("#grid .card")].find(c => c.querySelector("h3")?.textContent === "Marwa");
check("fiche marque : Commercialisée depuis affiche", anyCard && anyCard.textContent.includes("Commercialisée depuis 1994"));

console.log(errors ? `\n${errors} PROBLEME(S)` : "\nTOUT PASSE");
process.exit(errors ? 1 : 0);
