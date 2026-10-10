/* Protection légère contre la copie — commune à toutes les pages (consigne d'Ahmed, 05/10/2026)
   - photos : pas de clic droit ni de glisser-déposer ;
   - contenus de valeur (prix, classements, compositions) : non sélectionnables (style.css) et, si on les copie
     quand même, « Source : <adresse> — © tous droits réservés » est ajouté au texte copié ;
   - restent utilisables : recherche, filtres, formulaires (signaler, vote, avis), liens et boutons WhatsApp/Telegram ;
   - pas d'affichage dans le cadre (iframe) d'un autre site.
   Limite : ce qu'un visiteur voit peut toujours être capturé ; la vraie protection = licence + © + preuves. */
(function () {
  var COPIABLE = "input, select, textarea, form, a, button";
  var PROTEGE = ".hero, #top-reponse, #compare, #grid, #histo-section, .card, .compo, table, .faq, .baisses";

  function element(n) { return n && (n.nodeType === 1 ? n : n.parentElement); }

  document.addEventListener("contextmenu", function (e) {
    var el = element(e.target);
    if (el && el.closest("img, picture, .ic-photo")) e.preventDefault();
  });
  document.addEventListener("dragstart", function (e) {
    var el = element(e.target);
    if (el && el.closest("img")) e.preventDefault();
  });
  document.addEventListener("copy", function (e) {
    var sel = window.getSelection && window.getSelection();
    if (!sel || sel.isCollapsed || !e.clipboardData) return;
    var n = element(sel.anchorNode);
    if (!n || n.closest(COPIABLE) || !n.closest(PROTEGE)) return;
    e.clipboardData.setData("text/plain", sel.toString() + "\n\nSource : " + location.href.split("?")[0].split("#")[0] +
      " — © tous droits réservés");
    e.preventDefault();
  });

  // anti-iframe : seulement depuis le même site (les tests locaux en fichier sont permis)
  if (window.top !== window.self && location.protocol !== "file:") {
    var memeSite = false;
    try { memeSite = window.top.location.hostname === location.hostname; } catch (err) { memeSite = false; }
    if (!memeSite) {
      try { window.top.location.href = location.href; }
      catch (err) { document.documentElement.style.display = "none"; }
    }
  }
})();

/* Boutons « Partager » existants (petit bouton de l'accueil, gros boutons des pages marques et guides), harmonisés
   avec les autres sites d'Ahmed (06/10/2026) : clic compté anonymement « partage/<page> » ; menu de partage du téléphone
   (navigator.share) s'il existe, sinon le lien WhatsApp (wa.me) s'ouvre normalement. Annulation = rien. */
document.addEventListener("click", function (e) {
  var el = e.target && (e.target.nodeType === 1 ? e.target : e.target.parentElement);
  var a = el && el.closest('a[href^="https://wa.me/?text="]');
  if (!a) return;
  try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: "partage" + location.pathname.replace(/^\/prix-eaux-tunisie\//, "/"), title: "Partage", event: true }); } catch (err) {}
  // lien vers la page vidéo + adresse du site (window.partagerLien, plus bas) ; le texte du bouton sert de titre
  var texte = "";
  try { texte = new URL(a.href).searchParams.get("text") || ""; } catch (err) { return; }
  var m = texte.match(/https?:\/\/\S+/);
  e.preventDefault();
  window.partagerLien(texte.replace(/https?:\/\/\S+/g, "").replace(/\s+[—:-]?\s*$/, "").trim() || null, m ? m[0] : null);
});

/* Bouton « Partager » de l'en-tête, sur TOUTES les pages (règle commune à tous les sites, oubli corrigé le 09/10/2026) :
   même icône que les autres sites ; le clic passe par [data-partager-video] (plus bas) → page vidéo + adresse du site. */
(function () {
  function ajouter() {
    var h = document.querySelector("header.site .site-inner");
    if (!h || h.querySelector(".partager")) return;
    var b = document.createElement("button");
    b.type = "button"; b.className = "partager"; b.setAttribute("data-partager-video", "");
    b.setAttribute("aria-label", "Partager ce site"); b.title = "Partager";
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>';
    h.appendChild(b);
  }
  ajouter(); // en-tête déjà là (script en bas de page) ; sinon à la fin du chargement — jamais de doublon
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ajouter);
})();

/* Installation sur le téléphone : service worker PRUDENT (sw.js : réseau d'abord pour les pages et les données).
   Seulement en https (jamais en file: pendant les tests locaux). */
/* Adresse du site (11/10/2026) : prix-eau.clicvia.com (racine « / ») ; l'ancienne adresse ah6259.github.io/prix-eaux-tunisie/
   redirige vers elle. BASE_SITE = dossier du site selon l'adresse ; GoatCounter garde le préfixe /prix-eaux-tunisie
   (même compteur pour tous les sites d'Ahmed, séparés par chemin). */
var BASE_SITE = /\.github\.io$/.test(location.hostname) ? "/prix-eaux-tunisie/" : "/";
window.goatcounter = window.goatcounter || {};
window.goatcounter.path = function (p) { return BASE_SITE === "/" ? "/prix-eaux-tunisie" + p : p; };
if ("serviceWorker" in navigator && location.protocol === "https:") {
  window.addEventListener("load", function () {
    try { navigator.serviceWorker.register(BASE_SITE + "sw.js", { scope: BASE_SITE })["catch"](function () {}); }
    catch (e) { /* rien : le site marche sans */ }
  });
}

/* >>> vidéo de présentation : page video/ partagée par le bouton « Partager » (outil vidéos d'Ahmed) */
window.VIDEO_SITE = {"base": BASE_SITE, "defaut": "fr", "nom": {"fr": "Prix des Eaux de Tunisie", "ar": "أسعار الماء المعدني في تونس"}};
/* Bouton « Partager » (demande d'Ahmed, octobre 2026) : partage un LIEN vers la page vidéo du site (qui montre la vidéo
   de présentation, avec un gros bouton « Ouvrir le site ») + l'adresse du site dans le texte. WhatsApp et Facebook
   affichent l'aperçu de la page vidéo (grande image, vidéo lisible sur Facebook). Menu de partage du téléphone, sinon WhatsApp.
   Espace professionnels des annuaires : page « video-pro/ ». Réglages : window.VIDEO_SITE (juste au-dessus). */
(function () {
  var S = window.VIDEO_SITE, ORIGINE = S.base === "/" ? "https://prix-eau.clicvia.com" : "https://ah6259.github.io";
  function langue() { return document.documentElement.lang || S.defaut; }
  function M(o) { return o[langue()] || o[S.defaut] || o.fr; }
  // page vidéo à partager (et page du site correspondante) selon la page où l'on est
  window.pageVideo = function () {
    var chemin = location.pathname, pro = false;
    for (var i = 0; i < (S.pro || []).length; i++) if (chemin.indexOf(S.base + S.pro[i]) === 0) pro = true;
    var l = langue(), q = l !== S.defaut ? "?lang=" + l : "";
    return { page: ORIGINE + S.base + (pro ? "video-pro/" : "video/") + q, site: ORIGINE + S.base + (pro ? S.site_pro : "") + q + (pro ? (S.ancre_pro || "") : ""),
             titre: M(pro ? S.titre_pro : S.nom) };
  };
  window.partagerLien = function (titre, site) {
    var v = window.pageVideo(), t = titre || v.titre;
    if (site) v.site = site;
    var texte = t + "\n" + M({ fr: "Le site : ", ar: "الموقع: ", en: "The website: " }) + v.site + "\n" + M({ fr: "Regardez la vidéo :", ar: "شاهد الفيديو:", en: "Watch the video:" });
    function whatsapp() { window.open("https://wa.me/?text=" + encodeURIComponent(texte + " " + v.page), "_blank", "noopener"); return "whatsapp"; }
    if (navigator.share) {
      return navigator.share({ title: t, text: texte, url: v.page }).then(function () { return "lien"; }, function (e) {
        return e && e.name === "AbortError" ? "annule" : whatsapp();
      });
    }
    return Promise.resolve(whatsapp());
  };
  // page vidéo : textes dans la langue de la page (data-vfr / data-var / data-ven), vidéo de la langue (data-src-fr…)
  function traduire() {
    var l = langue();
    var el = document.querySelectorAll("[data-vfr]");
    for (var i = 0; i < el.length; i++) { var t = el[i].getAttribute("data-v" + l) || el[i].getAttribute("data-v" + S.defaut); if (t && el[i].textContent !== t) el[i].textContent = t; }
    var v = document.querySelector(".video-lecteur");
    if (v) {
      var s = v.getAttribute("data-src-" + l) || v.getAttribute("data-src-defaut") || v.getAttribute("src");
      if (!v.getAttribute("data-src-defaut")) v.setAttribute("data-src-defaut", v.getAttribute("src"));
      if (v.getAttribute("src") !== s) v.setAttribute("src", s);
      if (!v.getAttribute("data-poster-defaut")) v.setAttribute("data-poster-defaut", v.getAttribute("poster"));
      var po = v.getAttribute("data-poster-" + l) || v.getAttribute("data-poster-defaut");
      if (v.getAttribute("poster") !== po) v.setAttribute("poster", po);
    }
    // lien discret « Vidéo de présentation » en bas de l'accueil et de À propos -> la page vidéo
    var p = location.pathname.replace(/index\.html$/, "");
    if (p === S.base || p === S.base + "a-propos/") {
      var b = document.getElementById("lien-video");
      if (!b) {
        b = document.createElement("p"); b.id = "lien-video"; b.className = "lien-video"; b.appendChild(document.createElement("a"));
        var m = document.querySelector("main"); if (m) m.insertAdjacentElement("afterend", b); else document.body.appendChild(b);
      }
      b.firstChild.href = S.base + "video/" + (l !== S.defaut ? "?lang=" + l : "");
      b.firstChild.textContent = M({ fr: "Vidéo de présentation", ar: "الفيديو التقديمي", en: "Presentation video" });
    }
  }
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest && e.target.closest("[data-partager-video]");
    if (!b) return;
    e.preventDefault();
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: "partage" + location.pathname.replace(S.base, "/"), title: "Partage", event: true }); } catch (x) {}
    window.partagerLien();
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setTimeout(traduire, 0); }); else setTimeout(traduire, 0);
  document.addEventListener("langue", function () { setTimeout(traduire, 0); });
  try { new MutationObserver(function () { setTimeout(traduire, 0); }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] }); } catch (x) {}
})();
/* <<< vidéo de présentation */
