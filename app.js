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

function prodRow(p, b){
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
  const add = `<button type="button" class="addbtn" title="Ajouter à la commande"
      aria-label="Ajouter ${b.name} ${p.format} à la commande"
      data-bid="${b.id}" data-liters="${p.liters}" data-category="${p.category}" data-flavor="${p.flavor || ""}">+</button>`;
  return `<tr><td class="fmt">${label}</td><td><span class="offer-list">${offers}</span></td><td class="addc">${add}</td></tr>`;
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
    ${compoBlock(b)}
    <table class="prices">
      <tr><th>Format</th><th>Prix par enseigne</th><th></th></tr>
      ${b.products.slice().sort((a,z) =>
          (a.liters - z.liters) ||
          ((a.category === "gazeuse") - (z.category === "gazeuse")) ||
          (a.flavor || "").localeCompare(z.flavor || "")
        ).map(p => prodRow(p, b)).join("")}
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
  const key = { prix15: brand15, prixL: brandPerL, tds: brandTds }[state.sort];
  list = list.slice().sort(key
    ? (a,z) => (key(a) ?? 9999) - (key(z) ?? 9999)
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
  const p = b && b.products.find(x =>
    Math.abs(x.liters - liters) < .001 && x.category === category && (x.flavor || "") === (flavor || ""));
  return b && p ? {b, p} : null;
}

function addToCart(bid, liters, category, flavor){
  const found = findProduct(bid, liters, category, flavor);
  if (!found) return;
  const unit = (state.mode === "stika" && liters <= 2) ? "stika" : "bouteille";
  const key = [bid, liters, category, flavor || "", unit].join("|");
  const item = cart.find(x => x.key === key);
  if (item) item.qty += 1;
  else cart.push({ key, bid, liters, category, flavor: flavor || "", unit, qty: 1 });
  saveCart(); renderCartBar(); renderOrderItems();
}

function cartLines(){
  return cart.map(item => {
    const found = findProduct(item.bid, item.liters, item.category, item.flavor);
    if (!found) return null;
    const unitLabel = item.unit === "stika" ? "stika (6 bouteilles)" : "bouteille";
    return { ...item, nom: found.b.name, format: found.p.format,
             gaz: item.category === "gazeuse", unitLabel };
  }).filter(Boolean);
}

function renderCartBar(){
  const bar = document.getElementById("cartbar");
  const lines = cartLines();
  const n = lines.reduce((s, l) => s + l.qty, 0);
  bar.hidden = n === 0;
  document.body.classList.toggle("has-cart", n > 0);
  if (n) document.getElementById("cartbar-info").innerHTML =
    `${n} article${n > 1 ? "s" : ""} · prix et livraison confirmés sur WhatsApp`;
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
        <small>${l.unitLabel}</small></span>
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
  addToCart(btn.dataset.bid, parseFloat(btn.dataset.liters), btn.dataset.category, btn.dataset.flavor);
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
