const DATA = window.EAUX_DATA;
const fmtDT = v => v.toLocaleString("fr-FR",{minimumFractionDigits:3, maximumFractionDigits:3}) + " DT";

/* helpers ---------------------------------------------------------------- */
const plain = p => !p.flavor;
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

/* stats ------------------------------------------------------------------ */
const nProd = DATA.brands.reduce((n,b) => n + b.products.length, 0);
const nOff  = DATA.brands.reduce((n,b) => n + b.products.reduce((m,p) => m + Object.keys(p.prices).length, 0), 0);
document.getElementById("stats").innerHTML = [
  [DATA.brands.length, "marques"],
  [nProd, "produits"],
  [nOff, "prix relevés"],
].map(([b,s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join("");

/* état global ------------------------------------------------------------ */
const state = { q:"", type:"toutes", sort:"nom", mode:"bouteille", compareOpen:false };

// prix affiché : en mode stika, 6 × le prix bouteille (grands formats à l'unité)
const dispPrice = (v, liters) => (state.mode === "stika" && liters <= 2) ? v * 6 : v;

/* comparateur 1.5L : seules les gagnantes (prix le moins cher) sont affichées,
   le classement complet se déroule à la demande ---------------------------- */
function renderCompare(){
  const rows = DATA.brands
    .map(b => ({name:b.name, p:brand15(b)}))
    .filter(r => r.p !== null)
    .sort((a,z) => a.p - z.p);
  const min = rows[0].p;
  const show = p => fmtDT(dispPrice(p, 1.5));
  const rankRow = (r, i) => `
    <div class="rank${r.p === min ? " cheapest" : ""}">
      <span class="rn">${i + 1}</span>
      <span class="rname">${r.name}</span>
      <span class="rprice">${show(r.p)}</span>
    </div>`;
  const winners = rows.filter(r => r.p === min);
  const others = rows.filter(r => r.p !== min);
  const unit = state.mode === "stika" ? "la stika" : "la bouteille";
  const winnerCard = r => `
    <div class="winner">
      <svg class="cup" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 3h12v2h3v3c0 2.5-2 4.5-4.4 4.9A6 6 0 0 1 13 16.9V19h3v2H8v-2h3v-2.1a6 6 0 0 1-3.6-3A5 5 0 0 1 3 8V5h3V3zm-1 4v1a3 3 0 0 0 1.6 2.6A9 9 0 0 1 6 7H5zm14 0h-1a9 9 0 0 1-.6 3.6A3 3 0 0 0 19 8V7z"/>
      </svg>
      <span class="winner-name">${r.name}</span>
      <span class="winner-price">${show(r.p)} <small>${unit}</small></span>
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

function prodRow(p){
  const best = bestStores(p);
  const multi = Object.keys(p.prices).length > 1;
  const offers = Object.entries(p.prices)
    .sort((a,z) => a[1] - z[1])
    .map(([s,v]) => `<span class="offer${multi && best.includes(s) ? " best" : ""}">
        <span class="store">${s}</span><span class="p">${fmtDT(dispPrice(v, p.liters))}</span></span>`)
    .join("");
  const stika = state.mode === "stika" && p.liters <= 2;
  const label = p.format + (stika ? ` <small>· stika ×6</small>` : "") +
                (p.flavor ? ` <small>· ${p.flavor}</small>` : "") +
                (p.category === "gazeuse" ? ` <small>· gazeuse</small>` : "");
  return `<tr><td class="fmt">${label}</td><td><span class="offer-list">${offers}</span></td></tr>`;
}

function card(b){
  const meta = [];
  if (b.source) meta.push(`Source : <b>${b.source}</b>`);
  if (b.company) meta.push(`${b.company}`);
  if (b.note) meta.push(b.note);
  const badges = b.types.map(t =>
    `<span class="badge${t === "gazeuse" ? " gaz" : ""}">${t === "gazeuse" ? "Gazeuse" : "Plate"}</span>`).join("");
  return `<article class="card">
    <div class="card-head">
      ${b.img ? `<img src="${b.img}" alt="Bouteille ${b.name}" loading="lazy">` : ""}
      <div class="id"><h3>${b.name}</h3><div class="badges">${badges}</div></div>
    </div>
    ${meta.length ? `<div class="meta">${meta.join(" · ")}</div>` : ""}
    <table class="prices">
      <tr><th>Format</th><th>Prix par enseigne</th></tr>
      ${b.products.slice().sort((a,z) =>
          (a.liters - z.liters) ||
          ((a.category === "gazeuse") - (z.category === "gazeuse")) ||
          (a.flavor || "").localeCompare(z.flavor || "")
        ).map(prodRow).join("")}
    </table>
  </article>`;
}

function render(){
  const q = state.q.trim().toLowerCase();
  let list = DATA.brands.filter(b => {
    if (q && !b.name.toLowerCase().includes(q)) return false;
    if (state.type !== "toutes" && !b.types.includes(state.type)) return false;
    return true;
  });
  const key = { prix15: brand15, prixL: brandPerL }[state.sort];
  list = list.slice().sort(key
    ? (a,z) => (key(a) ?? 99) - (key(z) ?? 99)
    : (a,z) => a.name.localeCompare(z.name, "fr"));
  document.getElementById("grid").innerHTML = list.map(card).join("");
  document.getElementById("empty").hidden = list.length > 0;
}

document.getElementById("q").addEventListener("input", e => { state.q = e.target.value; render(); });
document.getElementById("sort").addEventListener("change", e => { state.sort = e.target.value; render(); });
document.querySelectorAll("#controls .chipbtn").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll("#controls .chipbtn").forEach(x => x.setAttribute("aria-pressed", x === btn));
  state.type = btn.dataset.type; render();
}));
document.querySelectorAll("#mode-controls .chipbtn").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll("#mode-controls .chipbtn").forEach(x => x.setAttribute("aria-pressed", x === btn));
  state.mode = btn.dataset.mode;
  renderCompare(); render();
}));
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
  document.getElementById("faq-min").textContent = fmtDT(min);
  document.getElementById("faq-min-stika").textContent = fmtDT(min * 6);
  document.getElementById("faq-winners").textContent = list;
})();

/* footer ----------------------------------------------------------------- */
document.getElementById("foot").innerHTML =
  `Prix indicatifs relevés le ${new Date(DATA.updated + "T12:00:00").toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"})}
   sur les boutiques en ligne — ils peuvent varier selon le magasin et la date. Sources :
   ${DATA.sources.map(s => `<a href="${s.url}" target="_blank" rel="noopener">${s.name}</a>`).join(" · ")}.
   Projet personnel — les visuels de bouteilles proviennent des catalogues des enseignes.`;
