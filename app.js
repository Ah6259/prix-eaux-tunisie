const DATA = window.EAUX_DATA;
const fmtDT = v => v.toLocaleString("fr-FR",{minimumFractionDigits:3, maximumFractionDigits:3}) + " DT";

/* helpers ---------------------------------------------------------------- */
const plain = p => !p.flavor;
// nombre de bouteilles par stika (fardeau) : 12 pour les petites, 6 sinon
const tailleStika = liters => (liters <= 0.75 ? 12 : 6);
const GRAND_FORMAT = 2.5;   // au-delà : bidons et bonbonnes, pas de stika
const FORMATS = [
  { id: "petit",    nom: "≤ 0,75 L", test: p => p.liters <= 0.75 },
  { id: "1",        nom: "1 L",      test: p => p.liters > 0.75 && p.liters < 1.25 },
  { id: "1.5",      nom: "1,5 L",    test: p => p.liters >= 1.25 && p.liters < 1.6 },
  { id: "2",        nom: "2 L",      test: p => p.liters >= 1.6 && p.liters <= GRAND_FORMAT },
  { id: "bonbonne", nom: "≥ 5 L",    test: p => p.liters > GRAND_FORMAT },
];
function minPrice(prod){ return Math.min(...Object.values(prod.prices)); }
function bestStores(prod){
  const m = minPrice(prod);
  return Object.entries(prod.prices).filter(([,v]) => v === m).map(([s]) => s);
}
function brand15(b){ // meilleur prix 1.5L eau plate
  const c = b.products.filter(p => plain(p) && p.category === "plate" && Math.abs(p.liters - 1.5) < .01);
  return c.length ? Math.min(...c.map(minPrice)) : null;
}
function brandPerL(b){ // meilleur prix au litre (eaux nature uniquement)
  const c = b.products.filter(p => plain(p) && p.liters >= 0.4);
  return c.length ? Math.min(...c.map(p => minPrice(p) / p.liters)) : null;
}

/* composition minéralogique (data/composition.js) ------------------------- */
const COMPO = window.EAUX_COMPO || { waters: {}, guide: {}, cats: {} };
const brandCompo = b => COMPO.waters[b.id] || null;
const brandTds = b => { const c = brandCompo(b); return c ? Math.min(...c.map(x => x.tds)) : null; };

function compoBlock(b){
  const entries = brandCompo(b);
  if (!entries) return "";
  const g = COMPO.guide;
  const ROWS = [
    ["tds", "Résidu sec (TDS)", "mg/L"], ["ca", "Calcium", "mg/L"], ["mg", "Magnésium", "mg/L"],
    ["na", "Sodium", "mg/L"], ["k", "Potassium", "mg/L"], ["hco3", "Bicarbonates", "mg/L"],
    ["so4", "Sulfates", "mg/L"], ["cl", "Chlorures", "mg/L"], ["no3", "Nitrates", "mg/L"],
    ["f", "Fluorures", "mg/L"], ["ph", "pH", ""],
  ];
  const over = (k, v) => k === "ph"
    ? (v < g.ph[0] || v > g.ph[1])
    : (g[k] != null && v > g[k]);
  const fmtv = v => v.toLocaleString("fr-FR", { maximumFractionDigits: 2 });
  const head = entries.length > 1
    ? `<tr><th></th>${entries.map(e => `<th>${e.src}</th>`).join("")}</tr>`
    : "";
  const rows = ROWS.map(([k, label, unit]) =>
    `<tr><td>${label}${unit ? ` <small>${unit}</small>` : ""}</td>` +
    entries.map(e => `<td class="cv${over(k, e[k]) ? " over" : ""}">${fmtv(e[k])}</td>`).join("") +
    `</tr>`).join("");
  const cats = [...new Set(entries.map(e => COMPO.cats[e.cat]))].join(" · ");
  const srcs = entries.length === 1 ? ` — ${entries[0].src}` : "";
  return `<details class="compo">
    <summary>Composition <small>· résidu sec ${entries.map(e => fmtv(e.tds)).join(" / ")} mg/L</small></summary>
    <table class="compo-table">${head}${rows}</table>
    <p class="compo-src">${cats}${srcs} · valeurs <span class="over-demo">surlignées</span> au-dessus du
    repère OMS/UE · source : <a href="${COMPO.credit.url}" target="_blank" rel="noopener">${COMPO.credit.name}</a></p>
  </details>`;
}

/* stats ------------------------------------------------------------------ */
// fraîcheur des prix : date du dernier relevé RÉUSSI de chaque enseigne (statut_sources,
// écrit par collect_prices.py). Comparée à la date du jour du visiteur : même si tous les
// robots s'arrêtaient, le site préviendrait que les prix sont anciens.
const NOMS_SRC = { carrefour: "Carrefour", geant: "Géant", otrity: "Otrity" };
const STATUT = DATA.statut_sources || {};
const dateCourte = d => new Date(d + "T12:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
const joursDepuis = d => Math.floor((Date.now() - new Date(d + "T12:00:00")) / 864e5);
const enseignesAvecPrix = new Set(DATA.brands.flatMap(b => b.products.flatMap(p => Object.keys(p.prices))));
const derniersOk = Object.entries(STATUT)
  .filter(([k, s]) => s && s.dernier_ok && enseignesAvecPrix.has(NOMS_SRC[k]))
  .map(([, s]) => s.dernier_ok).sort();
const derniereMaj = derniersOk.length ? derniersOk[derniersOk.length - 1] : DATA.updated;
const majCourte = dateCourte(derniereMaj);
(function alerteFraicheur(){
  const el = document.getElementById("alerte-maj");
  if (!el) return;
  let msg = "";
  if (!enseignesAvecPrix.size) {
    msg = "⚠️ Les prix sont momentanément indisponibles : les sites des magasins n'ont pas pu être lus. Réessayez plus tard.";
  } else if (joursDepuis(derniereMaj) >= 3) {
    msg = `⚠️ Les prix n'ont pas pu être mis à jour depuis le ${majCourte} : ils sont peut-être dépassés.`;
  } else {
    const enRetard = Object.entries(STATUT)
      // en retard = dernier relevé réussi il y a 2 jours ou plus (1 jour est normal :
      // Otrity est relevé à midi depuis le PC d'Ahmed, les autres la nuit)
      .filter(([k, s]) => s && s.dernier_ok && joursDepuis(s.dernier_ok) >= 2 && enseignesAvecPrix.has(NOMS_SRC[k]))
      .map(([k, s]) => `${NOMS_SRC[k]} du ${dateCourte(s.dernier_ok)}`);
    if (enRetard.length)
      msg = `ℹ️ Prix ${enRetard.join(", ")} (site momentanément indisponible).`;
  }
  el.textContent = msg;
  el.hidden = !msg;
})();
// petite ligne sous le titre : « Mis à jour le 29 sept. · 35 marques · 4 enseignes »
const nEnseignes = new Set(DATA.brands.flatMap(b => b.products.flatMap(p => Object.keys(p.prices)))).size;
document.getElementById("stats").textContent =
  `Mis à jour le ${majCourte} · ${DATA.brands.length} marques · ${nEnseignes} enseignes`;

/* état global — au chargement : stikas de 1,5 L, les moins chères d'abord -- */
// filtres multi-sélection : listes vides = aucun filtre, tout est affiché
const state = { q:"", types:[], formats:["1.5"], sort:"prix15", mode:"stika", compareOpen:false };

// prix affiché selon l'unité choisie (stika = n × bouteille ; grands formats à l'unité)
const dispPrice = (v, liters) =>
  (state.mode === "stika" && liters <= GRAND_FORMAT) ? v * tailleStika(liters) : v;

/* comparateur 1.5L : seules les gagnantes (prix le moins cher) sont affichées,
   le classement complet se déroule à la demande ---------------------------- */
function renderCompare(){
  const rows = DATA.brands
    .map(b => ({name:b.name, p:brand15(b)}))
    .filter(r => r.p !== null)
    .sort((a,z) => a.p - z.p);
  const min = rows[0].p;
  const rankRow = (r, i) => `
    <div class="rank${r.p === min ? " cheapest" : ""}">
      <span class="rn">${i + 1}</span>
      <span class="rname">${r.name}</span>
      <span class="rprice">${fmtDT(dispPrice(r.p, 1.5))}</span>
    </div>`;
  const winners = rows.filter(r => r.p === min);
  const others = rows.filter(r => r.p !== min);
  const stika = state.mode === "stika";
  const winnerCard = r => `
    <div class="winner">
      <svg class="cup" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 3h12v2h3v3c0 2.5-2 4.5-4.4 4.9A6 6 0 0 1 13 16.9V19h3v2H8v-2h3v-2.1a6 6 0 0 1-3.6-3A5 5 0 0 1 3 8V5h3V3zm-1 4v1a3 3 0 0 0 1.6 2.6A9 9 0 0 1 6 7H5zm14 0h-1a9 9 0 0 1-.6 3.6A3 3 0 0 0 19 8V7z"/>
      </svg>
      <span class="winner-name">${r.name}</span>
      <span class="winner-price">${fmtDT(stika ? r.p * 6 : r.p)} <small>${stika ? "la stika (×6)" : "la bouteille"}</small></span>
    </div>`;
  const btnLabel = () => state.compareOpen
    ? "Masquer le classement complet"
    : `Voir le classement complet (${rows.length} marques)`;
  document.getElementById("compare").innerHTML =
    `<div class="winners">${winners.map(winnerCard).join("")}</div>` +
    (others.length ? `
      <div id="compare-rest" ${state.compareOpen ? "" : "hidden"}>${rows.map(rankRow).join("")}</div>
      <div class="compare-toggle">
        <button type="button" id="compare-more" class="chipbtn">${btnLabel()}</button>
      </div>` : "");
  const btn = document.getElementById("compare-more");
  if (btn) btn.addEventListener("click", () => {
    state.compareOpen = !state.compareOpen;
    document.getElementById("compare-rest").hidden = !state.compareOpen;
    btn.textContent = btnLabel();
  });
}

/* cartes marques --------------------------------------------------------- */

function prodRow(p, b){
  const best = bestStores(p);
  const multi = Object.keys(p.prices).length > 1;
  const offers = Object.entries(p.prices)
    .sort((a,z) => a[1] - z[1])
    .map(([s,v]) => `<span class="offer${multi && best.includes(s) ? " best" : ""}">
        <span class="store">${s}</span><span class="p">${fmtDT(dispPrice(v, p.liters))}</span></span>`)
    .join("");
  const label = p.format +
                (p.flavor ? ` <small>· ${p.flavor}</small>` : "") +
                (p.category === "gazeuse" ? ` <small>· gazeuse</small>` : "");
  const stika = state.mode === "stika" && p.liters <= GRAND_FORMAT;
  const unite = stika ? `<small class="nb">stika ×${tailleStika(p.liters)}</small>`
    : (state.mode === "stika" ? `<small class="nb">à l'unité</small>` : "");
  const add = `<button type="button" class="addbtn" title="Ajouter à la commande"
      aria-label="Ajouter ${b.name} ${p.format} à la commande"
      data-bid="${b.id}" data-liters="${p.liters}" data-category="${p.category}" data-flavor="${p.flavor || ""}">+</button>`;
  return `<tr><td class="addc">${add}</td><td class="fmt">${label}${unite ? "<br>" + unite : ""}</td>
    <td><span class="offer-list">${offers}</span></td></tr>`;
}

function card(b, prods){
  const meta = [];
  if (b.source) meta.push(`Source : <b>${b.source}</b>`);
  if (b.company) meta.push(`${b.company}`);
  if (b.depuis) meta.push(`Commercialisée depuis <b>${b.depuis}</b>`);
  if (b.note) meta.push(b.note);
  const badges = b.types.map(t =>
    `<span class="badge${t === "gazeuse" ? " gaz" : ""}">${t === "gazeuse" ? "Gazeuse" : "Plate"}</span>`).join("");
  return `<article class="card">
    <div class="card-head">
      ${b.img ? `<img src="${b.img}" alt="Bouteille ${b.name}" loading="lazy">` : ""}
      <div class="id"><h3><a class="marque-lien" href="marque/${b.id}/">${b.name}</a></h3><div class="badges">${badges}</div></div>
    </div>
    ${meta.length ? `<div class="meta">${meta.join(" · ")}</div>` : ""}
    ${compoBlock(b)}
    ${prods.length ? `<table class="prices">
      <tr><th></th><th>Format</th>${state.mode === "stika"
        ? "<th>Prix stika par enseigne</th>"
        : "<th>Prix bouteille par enseigne</th>"}</tr>
      ${prods.slice().sort((a,z) =>
          (a.liters - z.liters) ||
          ((a.category === "gazeuse") - (z.category === "gazeuse")) ||
          (a.flavor || "").localeCompare(z.flavor || "")
        ).map(p => prodRow(p, b)).join("")}
    </table>` : `<div class="noprice">
      <button type="button" class="addbtn" title="Commander (prix à confirmer)"
        aria-label="Ajouter ${b.name} à la commande, prix à confirmer sur WhatsApp"
        data-generic="${b.id}">+</button>
      <span>Prix non disponible pour le moment dans les enseignes suivies — commandez, le prix vous sera confirmé sur WhatsApp.</span>
    </div>`}
    ${signalesBlock(b)}
  </article>`;
}

/* prix signalés par les visiteurs (data/signalements.js, vérifiés à la main) :
   affichés 30 jours avec leur date, hors calcul du moins cher --------------- */
const SIGNALES = window.EAUX_SIGNALES || [];
const JOURS_SIGNALE = 30;
/* liste des derniers prix signalés (section « Signaler un prix vu en magasin ») */
function renderDerniersSignales(){
  const box = document.getElementById("sig-derniers");
  if (!box) return;
  const now = new Date(DATA.updated + "T12:00:00");
  const recents = SIGNALES
    .filter(s => (now - new Date(s.date + "T12:00:00")) / 864e5 <= JOURS_SIGNALE)
    .sort((a, z) => z.date.localeCompare(a.date));
  if (!recents.length){
    box.innerHTML = `<p class="sig-vide">Aucun prix signalé ces 30 derniers jours : soyez le premier !</p>`;
    return;
  }
  const nomMarque = id => (DATA.brands.find(b => b.id === id) || {}).name || id;
  box.innerHTML = `<p class="sig-titre">Derniers prix signalés par les visiteurs</p><ul>` + recents.map(s => {
    const stika = state.mode === "stika" && s.litres <= GRAND_FORMAT;
    const vu = new Date(s.date + "T12:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
    return `<li><b>${s.marque || nomMarque(s.id)} ${String(s.litres).replace(".", ",")} L${s.type === "gazeuse" ? " gazeuse" : ""}</b>
      · ${s.magasin}${s.lieu ? ` <small>(${s.lieu})</small>` : ""} :
      <b class="sig-prix">${fmtDT(dispPrice(s.prix, s.litres))}</b>${stika ? " la stika" : ""}
      <small>· vu le ${vu}${s.nb > 1 ? ` · confirmé par ${s.nb} visiteurs` : ""}</small></li>`;
  }).join("") + `</ul>`;
}

function signalesBlock(b){
  const now = new Date(DATA.updated + "T12:00:00");
  const recents = SIGNALES
    .filter(s => s.id === b.id && (now - new Date(s.date + "T12:00:00")) / 864e5 <= JOURS_SIGNALE)
    .sort((a, z) => z.date.localeCompare(a.date));
  const lignes = recents.map(s => {
    const stika = state.mode === "stika" && s.litres <= GRAND_FORMAT;
    const vu = new Date(s.date + "T12:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
    return `<li>${s.magasin}${s.lieu ? ` <small>(${s.lieu})</small>` : ""} · ${String(s.litres).replace(".", ",")} L${s.type === "gazeuse" ? " gazeuse" : ""} :
      <b>${fmtDT(dispPrice(s.prix, s.litres))}</b>${stika ? " la stika" : ""} <small>· vu le ${vu}${s.nb > 1 ? ` · confirmé par ${s.nb} visiteurs` : ""}</small></li>`;
  }).join("");
  return `<div class="signales">
    ${lignes ? `<p class="sig-titre">📍 Prix signalés par les visiteurs</p><ul>${lignes}</ul>` : ""}
    <button type="button" class="sig-btn" data-signaler="${b.id}">📍 Signaler un prix vu en magasin</button>
  </div>`;
}

// nature officielle de l'eau (Office du Thermalisme, via composition.js)
const NATURES = { "1": "minerale", "2": "source", "3": "table" };
function brandNature(b){
  const w = COMPO.waters[b.id];
  return w && w[0] ? NATURES[String(w[0].cat)] : null;
}

function render(){
  const q = state.q.trim().toLowerCase();
  const fmtsSel = FORMATS.filter(f => state.formats.includes(f.id));
  const fmtOk = p => !fmtsSel.length || fmtsSel.some(f => f.test(p));
  const natSel = state.types.filter(t => t !== "gazeuse");
  const gazSel = state.types.includes("gazeuse");
  const sansType = !state.types.length;
  let list = DATA.brands
    .map(b => {
      const parNature = sansType || natSel.includes(brandNature(b));
      // exception eau traitée : quand le filtre « Traitée » est actif, on montre
      // tous ses formats (aucune eau de table n'existe en 1,5 L, le format par défaut)
      const sansFmt = natSel.includes("table") && brandNature(b) === "table";
      return { b, parNature, prods: b.products.filter(p =>
        (sansFmt || fmtOk(p)) && (parNature || (gazSel && p.category === "gazeuse")) &&
        Object.keys(p.prices).length > 0) };
    })
    .filter(({ b, parNature, prods }) => {
      if (q && !b.name.toLowerCase().includes(q)) return false;
      const typeOk = parNature || (gazSel && b.types.includes("gazeuse"));
      if (!typeOk) return false;
      if (!b.products.length)  // marque sans prix relevé : toujours affichée
        return true;
      return prods.length > 0;
    });
  const key = { prix15: brand15, prixL: brandPerL, tds: brandTds }[state.sort];
  // les marques sans aucun prix affiché restent toujours en bas, quel que soit le tri
  list = list.slice().sort((a,z) =>
    (!a.prods.length - !z.prods.length) ||
    (key ? (key(a.b) ?? 9999) - (key(z.b) ?? 9999)
         : a.b.name.localeCompare(z.b.name, "fr")));
  document.getElementById("grid").innerHTML = list.map(({ b, prods }) => card(b, prods)).join("");
  document.getElementById("empty").hidden = list.length > 0;
  renderBaisses();
  renderDerniersSignales();
}

/* bandeau « Baisses de prix du jour » : affiché seulement si les baisses
   datent du relevé affiché (data/baisses.js, écrit par tools/price_drops.py) */
function renderBaisses(){
  const B = window.EAUX_BAISSES, box = document.getElementById("baisses-list");
  if (!B || B.date !== DATA.updated || !B.baisses.length){ box.hidden = true; return; }
  const ligne = x => {
    const nom = `${x.marque} ${x.format.replace(".", ",")}${x.gazeuse ? " gazeuse" : ""}${x.saveur ? " " + x.saveur : ""}`;
    // toujours le prix de la stika (bidons et bonbonnes : prix à l'unité)
    const n = x.litres <= GRAND_FORMAT ? tailleStika(x.litres) : 1;
    return `<li><b>${n > 1 ? "Stika " : ""}${nom}</b>${n > 1 ? ` <small>(×${n})</small>` : ""} chez ${x.enseigne} :
      <s>${fmtDT(x.avant * n)}</s> → <b class="bx-p">${fmtDT(x.prix * n)}</b>
      <span class="bx-pct">−${String(x.pct).replace(".", ",")} %</span></li>`;
  };
  const top = B.baisses.slice(0, 3), reste = B.baisses.slice(3);
  box.innerHTML = `<h2>📉 Baisses de prix aujourd'hui</h2><ul>${top.map(ligne).join("")}</ul>` +
    (reste.length ? `<details><summary>+ ${reste.length} autre${reste.length > 1 ? "s" : ""} baisse${reste.length > 1 ? "s" : ""}</summary><ul>${reste.map(ligne).join("")}</ul></details>` : "");
  box.hidden = false;
}

document.getElementById("q").addEventListener("input", e => { state.q = e.target.value; render(); });
document.getElementById("sort").addEventListener("change", e => { state.sort = e.target.value; render(); });
// filtres multi-sélection : chaque puce s'active/se désactive au clic ;
// aucune puce active = pas de filtre (tout est affiché)
document.querySelectorAll("#controls .chipbtn[data-type]").forEach(btn => btn.addEventListener("click", () => {
  btn.setAttribute("aria-pressed", btn.getAttribute("aria-pressed") !== "true");
  state.types = [...document.querySelectorAll('#controls .chipbtn[aria-pressed="true"]')]
    .map(x => x.dataset.type);
  render();
}));

// puces de filtre par format de bouteille (1,5 L actif au chargement)
document.getElementById("format-controls").innerHTML = FORMATS.map(f =>
  `<button class="chipbtn" data-format="${f.id}" aria-pressed="${state.formats.includes(f.id)}">${f.nom}</button>`).join("") +
  `<button class="chipbtn chip-help" id="format-help" aria-label="Comprendre les formats de bouteille" title="Comprendre les formats de bouteille">?</button>`;
document.querySelectorAll("#format-controls .chipbtn[data-format]").forEach(btn => btn.addEventListener("click", () => {
  btn.setAttribute("aria-pressed", btn.getAttribute("aria-pressed") !== "true");
  state.formats = [...document.querySelectorAll('#format-controls .chipbtn[data-format][aria-pressed="true"]')]
    .map(x => x.dataset.format);
  render();
}));

// bascule Stika / Bouteille (stika par défaut : l'eau s'achète en stika)
document.querySelectorAll("#mode-controls .chipbtn").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll("#mode-controls .chipbtn").forEach(x => x.setAttribute("aria-pressed", x === btn));
  state.mode = btn.dataset.mode;
  renderCompare(); render();
}));

document.getElementById("sort").value = state.sort;   // tri par prix croissant au chargement
renderCompare();
render();

/* FAQ : garder les chiffres à jour avec les données du jour ---------------- */
(function(){
  const rows = DATA.brands
    .map(b => ({name:b.name, p:brand15(b)}))
    .filter(r => r.p !== null)
    .sort((a,z) => a.p - z.p);
  if (!rows.length) return;
  const min = rows[0].p;
  const winners = rows.filter(r => r.p === min).map(r => r.name);
  const list = winners.length > 1
    ? winners.slice(0, -1).join(", ") + " et " + winners[winners.length - 1]
    : winners[0];
  const el = (id, txt) => { const e = document.getElementById(id); if (e) e.textContent = txt; };
  el("faq-min", fmtDT(min));
  el("faq-min-stika", fmtDT(min * 6));
  el("faq-winners", list);
  // question « prix d'une stika » : mêmes données, exprimées en stika
  const max = rows[rows.length - 1].p;
  el("faq-stika-prix", fmtDT(min * 6));
  el("faq-stika-marques", list);
  el("faq-stika-min", fmtDT(min * 6));
  el("faq-stika-max", fmtDT(max * 6));
})();

/* évolution des prix (data/historique.js, régénéré chaque jour) ----------- */
(function renderHisto(){
  const box = document.getElementById("histo");
  const H = window.EAUX_HISTO;
  if (!box) return;
  if (!H || !H.serie || !H.serie.length){ document.getElementById("histo-section").hidden = true; return; }
  const pts = H.serie;
  const W = 640, HT = 210, m = { t: 24, r: 20, b: 30, l: 48 };
  const iw = W - m.l - m.r, ih = HT - m.t - m.b;
  const vals = pts.map(p => p.stika15);
  const vLo = Math.min(...vals), vHi = Math.max(...vals);
  const pad = Math.max((vHi - vLo) * 0.35, 0.15);
  const lo = vLo - pad, hi = vHi + pad;
  const x = i => m.l + (pts.length === 1 ? iw / 2 : i * iw / (pts.length - 1));
  const y = v => m.t + ih - (v - lo) / (hi - lo) * ih;
  const dShort = s => new Date(s + "T12:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
  const ticks = [vLo, (vLo + vHi) / 2, vHi].filter((v, i, a) => a.indexOf(v) === i);
  const grid = ticks.map(v => `
    <line class="gline" x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/>
    <text class="ax" x="${m.l - 6}" y="${y(v) + 3.5}" text-anchor="end">${v.toLocaleString("fr-FR", {minimumFractionDigits: 2})}</text>`).join("");
  const step = Math.max(1, Math.ceil(pts.length / 7));
  const xlabels = pts.map((p, i) => (i % step === 0 || i === pts.length - 1)
    ? `<text class="ax" x="${x(i)}" y="${HT - 8}" text-anchor="middle">${dShort(p.date)}</text>` : "").join("");
  const path = pts.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(p.stika15).toFixed(1)}`).join(" ");
  const marks = pts.map((p, i) => `<circle class="pt" data-i="${i}" cx="${x(i).toFixed(1)}" cy="${y(p.stika15).toFixed(1)}" r="4"/>`).join("");
  const last = pts[pts.length - 1];
  box.innerHTML = `
    <svg viewBox="0 0 ${W} ${HT}" role="img" aria-label="Prix de la stika 1,5 L la moins chère, jour par jour">
      ${grid}
      <path class="serie" d="${path}"/>
      ${marks}
      <text class="val" x="${x(pts.length - 1).toFixed(1)}" y="${(y(last.stika15) - 10).toFixed(1)}"
        text-anchor="${pts.length > 3 ? "end" : "middle"}">${fmtDT(last.stika15)}</text>
      ${xlabels}
    </svg>
    <div class="histo-tip" id="histo-tip" hidden></div>
    <details class="histo-table">
      <summary>Voir les valeurs</summary>
      <table>
        <tr><th>Date</th><th>Stika 1,5 L la moins chère</th><th>Marque(s)</th></tr>
        ${pts.map(p => `<tr><td>${dShort(p.date)}</td><td>${fmtDT(p.stika15)}</td><td>${p.marques.join(", ")}</td></tr>`).join("")}
      </table>
    </details>`;
  const tip = document.getElementById("histo-tip");
  box.querySelectorAll(".pt").forEach(c => {
    const show = () => {
      const p = pts[+c.dataset.i];
      tip.innerHTML = `<b>${fmtDT(p.stika15)}</b> la stika · ${dShort(p.date)}<br><small>${p.marques.join(", ")}</small>`;
      const r = c.getBoundingClientRect(), b = box.getBoundingClientRect();
      tip.hidden = false;
      tip.style.left = Math.min(Math.max(r.left - b.left, 60), b.width - 80) + "px";
      tip.style.top = (r.top - b.top - 8) + "px";
    };
    c.addEventListener("mouseenter", show);
    c.addEventListener("click", show);
    c.addEventListener("mouseleave", () => { tip.hidden = true; });
  });
})();

/* intro + FAQ : nombre et liste des marques suivant les données du jour ---- */
(function(){
  const noms = DATA.brands.map(b => b.name);
  const el = (id, txt) => { const e = document.getElementById(id); if (e) e.textContent = txt; };
  el("intro-autres", `${Math.max(noms.length - 5, 0)} autres marques`);
  el("faq-nb-marques", noms.length);
  el("faq-marques-liste", noms.length > 1
    ? noms.slice(0, -1).join(", ") + " et " + noms[noms.length - 1]
    : noms.join(""));
})();

/* footer ----------------------------------------------------------------- */
document.getElementById("foot").innerHTML =
  `Prix indicatifs relevés le ${new Date(DATA.updated + "T12:00:00").toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"})}
   sur les boutiques en ligne — ils peuvent varier selon le magasin et la date. Sources :
   ${DATA.sources.map(s => `<a href="${s.url}" target="_blank" rel="noopener">${s.name}</a>`).join(" · ")}.
   Projet personnel — les visuels de bouteilles proviennent des catalogues des enseignes.`;

/* ========================================================================= */
/* Commande : panier + envoi WhatsApp                                        */
/* ========================================================================= */
const WHATSAPP = "21624321390";
const CART_KEY = "eaux_commande";

let cart = [];
try { cart = JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch (e) {}
const saveCart = () => { try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch (e) {} };

function findProduct(bid, liters, category, flavor){
  const b = DATA.brands.find(x => x.id === bid);
  if (!b) return null;
  if (liters == null) return { b, p: null };  // commande générique : marque sans prix relevé
  const p = b.products.find(x =>
    Math.abs(x.liters - liters) < .001 && x.category === category && (x.flavor || "") === (flavor || ""));
  return p ? {b, p} : null;
}

function addToCart(bid, liters, category, flavor){
  const found = findProduct(bid, liters, category, flavor);
  if (!found) return;
  // unité : celle du mode affiché (stika par défaut) ; bouteille pour les grands formats
  const unit = (liters <= GRAND_FORMAT && state.mode === "stika") ? "stika" : "bouteille";
  const key = [bid, liters, category, flavor || "", unit].join("|");
  const item = cart.find(x => x.key === key);
  if (item) item.qty += 1;
  else cart.push({ key, bid, liters, category, flavor: flavor || "", unit, qty: 1 });
  saveCart(); renderCartBar(); renderOrderItems();
}

// marque sans prix relevé : on commande quand même, le prix sera confirmé sur WhatsApp
function addGenericToCart(bid){
  const b = DATA.brands.find(x => x.id === bid);
  if (!b) return;
  const key = [bid, "generique"].join("|");
  const item = cart.find(x => x.key === key);
  if (item) item.qty += 1;
  else cart.push({ key, bid, liters: null, category: null, flavor: "", unit: "generique", qty: 1 });
  saveCart(); renderCartBar(); renderOrderItems();
}

function unitLabel(item){
  if (item.unit === "generique") return "au choix";
  return item.unit === "stika" ? `stika (${tailleStika(item.liters)} bouteilles)` : "bouteille";
}

function cartLines(){
  return cart.map(item => {
    const found = findProduct(item.bid, item.liters, item.category, item.flavor);
    if (!found) return null;
    return { ...item, nom: found.b.name, format: found.p ? found.p.format : "(format à confirmer)",
             gaz: item.category === "gazeuse", unitLabel: unitLabel(item) };
  }).filter(Boolean);
}

function renderCartBar(){
  const bar = document.getElementById("cartbar");
  const lines = cartLines();
  const n = lines.reduce((s, l) => s + l.qty, 0);
  bar.hidden = n === 0;
  document.body.classList.toggle("has-cart", n > 0);
  if (n){
    document.getElementById("cartbar-info").innerHTML =
      `${n} article${n > 1 ? "s" : ""} · commande bientôt disponible`;
    document.getElementById("cart-open").innerHTML =
      `Commander 🛒 <span class="cart-count">${n}</span>`;
  }
}

function renderOrderItems(){
  const box = document.getElementById("order-items");
  const lines = cartLines();
  if (!lines.length){
    box.innerHTML = `<p class="order-empty">Votre commande est vide — ajoutez des produits avec le bouton +.</p>`;
    document.getElementById("order-total").textContent = "";
    return;
  }
  box.innerHTML = lines.map(l => `
    <div class="order-item">
      <span class="oi-name">${l.nom} ${l.format}${l.gaz ? " gazeuse" : ""}${l.flavor ? " " + l.flavor : ""}
        ${l.liters != null && l.liters <= GRAND_FORMAT ? `<select class="oi-unit" data-unit="${l.key}" aria-label="Unité">
          <option value="stika"${l.unit === "stika" ? " selected" : ""}>stika (${tailleStika(l.liters)} bouteilles)</option>
          <option value="bouteille"${l.unit === "bouteille" ? " selected" : ""}>bouteille à l'unité</option>
        </select>` : `<small>${l.unitLabel}</small>`}</span>
      <span class="qty">
        <button type="button" data-dec="${l.key}" aria-label="Une ${l.unitLabel} de moins">−</button>
        <b>${l.qty}</b>
        <button type="button" data-inc="${l.key}" aria-label="Une ${l.unitLabel} de plus">+</button>
      </span>
    </div>`).join("");
  document.getElementById("order-total").innerHTML =
    `Les prix affichés sur le site sont ceux des grandes surfaces, mis à jour chaque jour,
     à titre indicatif. Le prix final peut varier selon la disponibilité : nous vous le
     confirmons sur WhatsApp avec les frais de livraison.`;
}

let geoPos = null;          // position CONFIRMÉE par le client (sinon null)
let geoMap = null, geoMarker = null;

// Leaflet (carte OpenStreetMap) chargé seulement au premier clic sur « Me localiser »
function loadLeaflet(){
  if (window.L) return Promise.resolve();
  return new Promise((ok, ko) => {
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css";
    document.head.appendChild(css);
    const js = document.createElement("script");
    js.src = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";
    js.onload = ok; js.onerror = ko;
    document.head.appendChild(js);
  });
}

function showGeoMap(lat, lng, zoom){
  document.getElementById("geo-box").hidden = false;
  geoPos = null;  // toute nouvelle position doit être reconfirmée par le client
  if (!geoMap){
    geoMap = L.map("geo-map").setView([lat, lng], zoom);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      { maxZoom: 19, attribution: "© OpenStreetMap" }).addTo(geoMap);
    geoMarker = L.marker([lat, lng], { draggable: true }).addTo(geoMap);
    geoMap.on("click", e => geoMarker.setLatLng(e.latlng));
  } else {
    geoMap.setView([lat, lng], zoom);
    geoMarker.setLatLng([lat, lng]);
  }
  // le conteneur vient d'apparaître : recalculer la taille de la carte
  setTimeout(() => geoMap.invalidateSize(), 150);
}

function messageWhatsApp(){
  const lines = cartLines();
  const nom = document.getElementById("o-nom").value.trim();
  const tel = document.getElementById("o-tel").value.trim();
  const adr = document.getElementById("o-adr").value.trim();
  const note = document.getElementById("o-note").value.trim();
  const txt = [
    "🚰 Commande — Prix des Eaux de Tunisie",
    "",
    ...lines.map(l => `• ${l.qty} × ${l.unitLabel} ${l.nom} ${l.format}${l.gaz ? " gazeuse" : ""}`),
    "",
    nom ? `Nom : ${nom}` : null,
    `Tél : ${tel}`,
    `Adresse : ${adr}`,
    geoPos ? `Position exacte confirmée par le client : https://maps.google.com/?q=${geoPos.lat},${geoPos.lng}` : null,
    note ? `Remarque : ${note}` : null,
  ].filter(x => x !== null).join("\n");
  return `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(txt)}`;
}

/* écouteurs --------------------------------------------------------------- */
document.getElementById("grid").addEventListener("click", e => {
  const btn = e.target.closest(".addbtn");
  if (!btn) return;
  if (btn.dataset.generic) addGenericToCart(btn.dataset.generic);
  else addToCart(btn.dataset.bid, parseFloat(btn.dataset.liters), btn.dataset.category, btn.dataset.flavor);
  btn.textContent = "✓";
  setTimeout(() => { btn.textContent = "+"; }, 700);
});

const overlay = document.getElementById("order-overlay");
document.getElementById("cart-open").addEventListener("click", () => {
  renderOrderItems();
  overlay.hidden = false;
});
document.getElementById("order-close").addEventListener("click", () => { overlay.hidden = true; });
overlay.addEventListener("click", e => { if (e.target === overlay) overlay.hidden = true; });
document.addEventListener("keydown", e => { if (e.key === "Escape") overlay.hidden = true; });

document.getElementById("order-items").addEventListener("change", e => {
  const sel = e.target.closest("[data-unit]");
  if (!sel) return;
  const item = cart.find(x => x.key === sel.dataset.unit);
  if (!item) return;
  item.unit = sel.value;
  const newKey = [item.bid, item.liters, item.category, item.flavor, item.unit].join("|");
  const doublon = cart.find(x => x !== item && x.key === newKey);
  if (doublon){ doublon.qty += item.qty; cart = cart.filter(x => x !== item); }
  else item.key = newKey;
  saveCart(); renderCartBar(); renderOrderItems();
});

document.getElementById("order-items").addEventListener("click", e => {
  const inc = e.target.closest("[data-inc]"), dec = e.target.closest("[data-dec]");
  if (!inc && !dec) return;
  const key = (inc || dec).dataset.inc || (inc || dec).dataset.dec;
  const item = cart.find(x => x.key === key);
  if (!item) return;
  item.qty += inc ? 1 : -1;
  if (item.qty <= 0) cart = cart.filter(x => x !== item);
  saveCart(); renderCartBar(); renderOrderItems();
});

document.getElementById("o-geo").addEventListener("click", async () => {
  const status = document.getElementById("o-geo-status");
  status.textContent = "Localisation…";
  try { await loadLeaflet(); }
  catch (e) { status.textContent = "Carte indisponible — décrivez précisément l'adresse."; return; }
  const manuel = () => {   // GPS refusé ou en échec : placement du repère à la main
    status.textContent = "Placez le repère sur la carte, puis confirmez.";
    showGeoMap(36.8065, 10.1815, 11);  // Tunis par défaut
  };
  if (!navigator.geolocation) return manuel();
  navigator.geolocation.getCurrentPosition(
    pos => {
      status.textContent = "Vérifiez le repère, ajustez-le si besoin, puis confirmez.";
      showGeoMap(pos.coords.latitude, pos.coords.longitude, 17);
    },
    manuel,
    { enableHighAccuracy: true, timeout: 12000 });
});

document.getElementById("o-geo-confirm").addEventListener("click", () => {
  if (!geoMarker) return;
  const ll = geoMarker.getLatLng();
  geoPos = { lat: ll.lat.toFixed(6), lng: ll.lng.toFixed(6) };
  document.getElementById("geo-box").hidden = true;
  document.getElementById("o-geo-status").textContent = "Position confirmée ✓ (cliquez pour modifier)";
});

document.getElementById("order-form").addEventListener("submit", e => {
  e.preventDefault();
  if (!cartLines().length){ renderOrderItems(); return; }
  const tel = document.getElementById("o-tel").value.replace(/\D/g, "");
  if (tel.length < 8){
    document.getElementById("o-tel").focus();
    document.getElementById("o-tel").setCustomValidity("Numéro de téléphone incomplet");
    document.getElementById("order-form").reportValidity();
    document.getElementById("o-tel").setCustomValidity("");
    return;
  }
  window.open(messageWhatsApp(), "_blank", "noopener");
});

renderCartBar();

/* formulaire d'avis (Formspree) : envoi sans quitter la page ---------------- */
(function(){
  const form = document.getElementById("avis-form");
  if (!form) return;
  const status = document.getElementById("avis-status");
  const btn = form.querySelector(".avis-send");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;
    status.className = ""; status.textContent = "Envoi…";
    try {
      const r = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "Accept": "application/json" },
      });
      if (r.ok) {
        form.reset();
        status.className = "ok";
        status.textContent = "Merci ! Votre message a bien été envoyé.";
      } else {
        throw new Error();
      }
    } catch {
      status.className = "err";
      status.textContent = "Échec de l'envoi — réessayez, ou plus tard.";
    } finally {
      btn.disabled = false;
    }
  });
})();

/* « Signaler un prix vu en magasin » : fenêtre + envoi au Google Forms d'Ahmed.
   Les réponses arrivent dans son tableau Google Sheets ; tools/signalements.py
   les lit 3 fois par jour, décide seul et publie (site + canal Telegram) ------ */
const SIG_FORM = {
  url: "https://docs.google.com/forms/d/e/1FAIpQLSd7sR4KmzqrCi-Yjw0WV9SmT_3sZfKJtPmkGnDjMRHl4Q78PA/formResponse",
  champs: { marque: "entry.897098257", format: "entry.1939823394", eau: "entry.86622726",
            prix: "entry.1187219157", unite: "entry.107804725", magasin: "entry.1043442008",
            lieu: "entry.506707149", date: "entry.1622032670" },
};
(function(){
  const pop = document.getElementById("sig-pop");
  const form = document.getElementById("sig-form");
  if (!pop || !form) return;
  const sel = document.getElementById("sig-marque");
  sel.innerHTML = `<option value="">— choisir —</option>` + DATA.brands.slice().sort((a, z) => a.name.localeCompare(z.name, "fr"))
    .map(b => `<option value="${b.name}">${b.name}</option>`).join("") + `<option>Autre marque</option>`;
  const status = document.getElementById("sig-status");
  const ouvrir = id => {
    const b = DATA.brands.find(x => x.id === id);
    sel.value = b ? b.name : "";       // depuis la barre du haut : marque à choisir
    // depuis la carte d'une marque : formulaire ouvert directement ; depuis la barre : fermé
    document.getElementById("sig-form-sec").open = !!b;
    document.getElementById("sig-date").value = new Date().toISOString().slice(0, 10);
    status.className = ""; status.textContent = "";
    pop.hidden = false;
  };
  document.getElementById("sig-open").addEventListener("click", () => ouvrir(null));
  document.getElementById("grid").addEventListener("click", e => {
    const btn = e.target.closest("[data-signaler]");
    if (btn) ouvrir(btn.dataset.signaler);
  });
  const fermer = () => { pop.hidden = true; };
  document.getElementById("sig-close").addEventListener("click", fermer);
  pop.addEventListener("click", e => { if (e.target === pop) fermer(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") fermer(); });
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const f = new FormData(form);
    const btn = form.querySelector(".avis-send");
    btn.disabled = true;
    status.className = ""; status.textContent = "Envoi…";
    try {
      if (!f.get("_gotcha")) {          // champ piège rempli = robot : on ne transmet pas
        const corps = new URLSearchParams();
        Object.entries(SIG_FORM.champs).forEach(([nom, entry]) => corps.append(entry, f.get(nom) || ""));
        // Google Forms ne renvoie pas de réponse lisible (mode no-cors) : seule une
        // panne réseau déclenche l'erreur
        await fetch(SIG_FORM.url, { method: "POST", mode: "no-cors", body: corps });
      }
      form.reset();
      status.className = "ok";
      status.textContent = "Merci ! Le prix sera vérifié puis publié dans quelques heures.";
      setTimeout(() => { document.getElementById("sig-form-sec").open = false; }, 2500);
      setTimeout(fermer, 2500);
    } catch {
      status.className = "err";
      status.textContent = "Échec de l'envoi — réessayez plus tard.";
    } finally {
      btn.disabled = false;
    }
  });
})();

/* « Gagnant du match » par le vote des clients -------------------------------
   Vote envoyé au Google Forms (format = VOTE, jeton anonyme du navigateur dans « lieu ») ;
   tools/signalements.py compte un vote par navigateur (le plus récent) toutes les 2 h. */
(function(){
  const sel = document.getElementById("vote-marque");
  if (!sel) return;
  const VOTES = window.EAUX_VOTES || { total: 0, classement: [] };
  const lire = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const ecrire = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  let jeton = lire("vote-jeton");
  if (!jeton){ jeton = "vote:" + Math.random().toString(36).slice(2) + Date.now().toString(36); ecrire("vote-jeton", jeton); }
  const box = document.getElementById("vote-classement");
  const status = document.getElementById("vote-status");
  const total = VOTES.total || 0;
  if (!total){
    box.innerHTML = "";          // pas encore de vote : rien à afficher
  } else {
    // comme pour le prix : le(s) gagnant(s) sur une ligne, puis le classement complet à la demande
    const cl = VOTES.classement;
    const nb = v => `${v.votes} vote${v.votes > 1 ? "s" : ""} · ${Math.round(v.votes * 100 / total)} %`;
    const gagnants = cl.filter(v => v.votes === cl[0].votes);
    box.innerHTML =
      `<div class="winners">` + gagnants.map(v => `<div class="winner vote-win">
        <span class="vote-coeur" aria-hidden="true">❤️</span>
        <span class="winner-name">${v.marque}</span>
        <span class="winner-price">${nb(v)}</span></div>`).join("") + `</div>` +
      `<ol class="vote-liste" id="vote-rest" hidden>` + cl.map((v, i) =>
        `<li><span class="vote-rang">${i + 1}</span><b>${v.marque}</b><span class="vote-nb">${nb(v)}</span></li>`
      ).join("") + `</ol>` +
      `<div class="compare-toggle"><button type="button" class="chipbtn" id="vote-more">Voir le classement des votes (${total} votant${total > 1 ? "s" : ""})</button></div>`;
    const btn = document.getElementById("vote-more");
    btn.addEventListener("click", () => {
      const rest = document.getElementById("vote-rest");
      rest.hidden = !rest.hidden;
      btn.textContent = rest.hidden ? `Voir le classement des votes (${total} votant${total > 1 ? "s" : ""})` : "Masquer le classement des votes";
    });
  }
  sel.innerHTML = `<option value="">— mon eau préférée —</option>` + DATA.brands.slice()
    .sort((a, z) => a.name.localeCompare(z.name, "fr"))
    .map(b => `<option value="${b.name}">${b.name}</option>`).join("");
  const mien = lire("vote-marque");
  if (mien){ sel.value = mien; status.textContent = `Votre vote : ${mien}.`; }
  document.getElementById("vote-btn").addEventListener("click", async () => {
    const marque = sel.value;
    if (!marque){ status.textContent = "Choisissez d'abord une marque."; return; }
    const corps = new URLSearchParams();
    const vide = { marque, format: "VOTE", eau: "", prix: "", unite: "", magasin: "", lieu: jeton,
                   date: new Date().toISOString().slice(0, 10) };
    Object.entries(SIG_FORM.champs).forEach(([nom, entry]) => corps.append(entry, vide[nom] || ""));
    status.textContent = "Envoi…";
    try {
      await fetch(SIG_FORM.url, { method: "POST", mode: "no-cors", body: corps });
      ecrire("vote-marque", marque);
      status.textContent = `Merci ! Votre vote pour ${marque} sera compté au prochain décompte (dans les 2 heures).`;
    } catch (e) {
      status.textContent = "Échec de l'envoi — réessayez plus tard.";
    }
  });
})();

/* fenetres d'aide : types d'eau et formats de bouteille -------------------- */
[["type-help", "type-help-pop", "type-help-close"],
 ["format-help", "format-help-pop", "format-help-close"],
 ["match-open", "match-pop", "match-close"],
 ["hadith-open", "hadith-pop", "hadith-close"]].forEach(([b, p2, c]) => {
  const btn = document.getElementById(b);
  const pop = document.getElementById(p2);
  if (!btn || !pop) return;
  btn.addEventListener("click", () => { pop.hidden = false; });
  document.getElementById(c).addEventListener("click", () => { pop.hidden = true; });
  pop.addEventListener("click", (e) => { if (e.target === pop) pop.hidden = true; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") pop.hidden = true; });
});
