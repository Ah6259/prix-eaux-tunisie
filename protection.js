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
  try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: "partage" + location.pathname.replace("/prix-eaux-tunisie/", "/"), title: "Partage", event: true }); } catch (err) {}
  if (!navigator.share) return;
  var texte = "";
  try { texte = new URL(a.href).searchParams.get("text") || ""; } catch (err) { return; }
  var m = texte.match(/https?:\/\/\S+/);
  var url = m ? m[0] : location.href.split("#")[0].split("?")[0];
  e.preventDefault();
  // vidéo de présentation + lien (texte du bouton), sinon lien seul (window.partagerVideo, plus bas)
  var v = window.VIDEO_PRESENTATION();
  window.partagerVideo(v.url, v.nom, texte.replace(url, "").replace(/\s+[—:-]?\s*$/, "").trim() || document.title.split(" | ")[0], url);
});

/* Installation sur le téléphone : service worker PRUDENT (sw.js : réseau d'abord pour les pages et les données).
   Seulement en https (jamais en file: pendant les tests locaux). */
if ("serviceWorker" in navigator && location.protocol === "https:") {
  window.addEventListener("load", function () {
    try { navigator.serviceWorker.register("/prix-eaux-tunisie/sw.js", { scope: "/prix-eaux-tunisie/" })["catch"](function () {}); }
    catch (e) { /* rien : le site marche sans */ }
  });
}

/* >>> vidéo de présentation (fabriquée par l'outil vidéos d'Ahmed) */
// Vidéo à partager : anglais par défaut sur le site des conférences (version française si la page est en français).
window.VIDEO_PRESENTATION = function () {
  var fr = false && document.documentElement.lang === "fr";
  return { url: "/prix-eaux-tunisie/assets/video/presentation" + (fr ? "-fr" : "") + ".mp4", nom: "prix-eaux-tunisie" + (fr ? "-fr" : "") + ".mp4" };
};
/* Partage de la vidéo de présentation (demande d'Ahmed, octobre 2026) : le bouton « Partager » envoie la VIDÉO + le lien
   (dans le texte) quand le téléphone sait partager un fichier (Instagram, Facebook, TikTok, WhatsApp…) ; sinon le lien
   seul (menu de partage du téléphone, sinon WhatsApp). « Préparation de la vidéo… » pendant le téléchargement ; si le
   téléphone refuse le partage après l'attente (geste trop ancien), la vidéo reste prête : un second toucher la partage. */
window.partagerVideo = (function () {
  var pret = null;                                   // { cle, fichier } : vidéo déjà téléchargée
  function langue() { return document.documentElement.lang || "fr"; }
  function M(fr, en, ar) { var l = langue(); return l === "ar" ? ar : l === "en" ? en : fr; }
  function message(texte) {
    var m = document.getElementById("partage-msg");
    if (!texte) { if (m) m.hidden = true; return; }
    if (!m) { m = document.createElement("div"); m.id = "partage-msg"; m.className = "partage-msg"; m.setAttribute("role", "status"); document.body.appendChild(m); }
    m.textContent = texte; m.hidden = false;
  }
  function lienSeul(titre, url) {
    if (navigator.share) {
      return navigator.share({ title: titre, text: titre, url: url }).then(function () { return "lien"; }, function (e) {
        if (e && e.name === "AbortError") return "annule";
        window.open("https://wa.me/?text=" + encodeURIComponent(titre + " " + url), "_blank", "noopener"); return "whatsapp";
      });
    }
    window.open("https://wa.me/?text=" + encodeURIComponent(titre + " " + url), "_blank", "noopener");
    return Promise.resolve("whatsapp");
  }
  return function (video, nomFichier, titre, url) {
    var possible = false;
    try { possible = !!(navigator.share && navigator.canShare && window.File && window.fetch && navigator.canShare({ files: [new File([""], nomFichier, { type: "video/mp4" })] })); } catch (e) {}
    if (!possible) return lienSeul(titre, url);
    var etape = (pret && pret.cle === video) ? Promise.resolve() : (function () {
      message(M("Préparation de la vidéo…", "Preparing the video…", "جارٍ تحضير الفيديو…"));
      return fetch(video).then(function (r) {
        if (!r.ok) throw new Error("vidéo absente");
        return r.blob();
      }).then(function (b) {
        var f = new File([b], nomFichier, { type: "video/mp4" });
        if (!navigator.canShare({ files: [f] })) throw new Error("fichier refusé");
        pret = { cle: video, fichier: f };
      });
    })();
    return etape.then(function () {
      return navigator.share({ files: [pret.fichier], title: titre, text: titre + " " + url });
    }).then(function () { message(""); return "video"; }, function (e) {
      if (e && e.name === "AbortError") { message(""); return "annule"; }
      if (e && e.name === "NotAllowedError" && pret && pret.cle === video) {
        message(M("Vidéo prête : touchez encore « Partager »", "Video ready: tap “Share” again", "الفيديو جاهز: المس « شارك » مرة أخرى"));
        setTimeout(function () { message(""); }, 6000); return "pret";
      }
      message(""); return lienSeul(titre, url);
    });
  };
})();
// Lien discret « Vidéo de présentation » en bas de l'accueil et de À propos (pour la regarder, la télécharger, la publier).
(function () {
  function poser() {
    var p = location.pathname.replace(/index\.html$/, "");
    if (p !== "/prix-eaux-tunisie/" && p !== "/prix-eaux-tunisie/a-propos/") return;
    var el = document.getElementById("lien-video");
    if (!el) {
      el = document.createElement("p"); el.id = "lien-video"; el.className = "lien-video";
      var a = document.createElement("a"); el.appendChild(a);
      var m = document.querySelector("main"); if (m) m.insertAdjacentElement("afterend", el); else document.body.appendChild(el);
    }
    var l = document.documentElement.lang, lien = el.firstChild;
    lien.href = window.VIDEO_PRESENTATION().url;
    lien.textContent = l === "ar" ? "الفيديو التقديمي" : l === "en" ? "Presentation video" : "Vidéo de présentation";
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setTimeout(poser, 0); }); else setTimeout(poser, 0);
  document.addEventListener("langue", function () { setTimeout(poser, 0); });
})();
/* <<< vidéo de présentation */
