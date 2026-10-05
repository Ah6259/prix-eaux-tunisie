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

/* Installation sur le téléphone : service worker PRUDENT (sw.js : réseau d'abord pour les pages et les données).
   Seulement en https (jamais en file: pendant les tests locaux). */
if ("serviceWorker" in navigator && location.protocol === "https:") {
  window.addEventListener("load", function () {
    try { navigator.serviceWorker.register("/prix-eaux-tunisie/sw.js", { scope: "/prix-eaux-tunisie/" })["catch"](function () {}); }
    catch (e) { /* rien : le site marche sans */ }
  });
}
