// Prix signalés par les visiteurs (ou vus par Ahmed), VÉRIFIÉS puis ajoutés à la main.
// Reçus par email via le formulaire « Signaler un prix » (Formspree).
// Affichés sur la carte de la marque avec leur date, pendant 30 jours ;
// ils n'entrent PAS dans le calcul du moins cher / du gagnant du match.
//   id      : identifiant de la marque (comme dans data/eaux.json, ex. "safia")
//   litres  : format de la bouteille
//   prix    : prix d'UNE bouteille en DT (une stika signalée est divisée par 6, ou 12 si ≤ 0,75 L)
//   magasin : enseigne ou magasin ; lieu : ville / quartier (facultatif)
//   date    : jour où le prix a été vu (AAAA-MM-JJ)
window.EAUX_SIGNALES = [
  { id: "sabrine", litres: 1.5, type: "plate", prix: 0.680, magasin: "Monoprix", lieu: "boutique en ligne", date: "2026-09-30" },
];
