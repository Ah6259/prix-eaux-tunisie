/* Composition minéralogique des eaux embouteillées tunisiennes (mg/L, sauf pH).
   Transcrit du tableau de l'Office du Thermalisme publié par le Dr Ing. Imed Houcine,
   « Composition des eaux minérales tunisiennes : bien choisir son eau », Babnet, 6 mai 2024.
   https://www.babnet.net/festivaldetail-287073.asp
   cat : 1 = eau minérale naturelle, 2 = eau de source, 3 = eau de table.
   Fichier statique entretenu à la main — n'est PAS regénéré par collect_prices.py. */
window.EAUX_COMPO = {
 "updated": "2024-05-06",
 "credit": {
  "name": "Office du Thermalisme / Dr Imed Houcine (Babnet, mai 2024)",
  "url": "https://www.babnet.net/festivaldetail-287073.asp"
 },
 "guide": { "tds": 500, "ca": 100, "mg": 50, "na": 200, "k": 12, "hco3": 420,
            "so4": 250, "cl": 250, "no3": 50, "f": 1.5, "ph": [6.5, 9] },
 "cats": { "1": "eau minérale naturelle", "2": "eau de source", "3": "eau de table" },
 "waters": {
  "hayet":      [{ "src": "Jelma (Sidi Bouzid)", "cat": 1, "tds": 238, "ca": 44.02, "mg": 15.36, "na": 13.71, "k": 1.68, "hco3": 160.02, "so4": 45.94, "cl": 20.36, "no3": 0.14, "f": 0.10, "ph": 7.7 }],
  "jannet":     [{ "src": "Haffouz (Kairouan)", "cat": 1, "tds": 272, "ca": 41.65, "mg": 23.30, "na": 28.75, "k": 1.45, "hco3": 235.85, "so4": 20.00, "cl": 26.90, "no3": 5.50, "f": 0.30, "ph": 7.7 }],
  "sabrine":    [{ "src": "Chébika (Kairouan)", "cat": 1, "tds": 303, "ca": 35.00, "mg": 17.00, "na": 56.45, "k": 2.80, "hco3": 244.00, "so4": 27.50, "cl": 27.00, "no3": 17.00, "f": 1.85, "ph": 7.7 }],
  "safia":      [{ "src": "Aïn Mizeb (Le Kef)", "cat": 1, "tds": 308, "ca": 69.00, "mg": 15.50, "na": 18.50, "k": 0.60, "hco3": 233.00, "so4": 18.00, "cl": 18.00, "no3": 15.00, "f": 0.18, "ph": 7.3 },
                 { "src": "Aïn Ksiba (Le Kef)", "cat": 1, "tds": 437, "ca": 83.00, "mg": 13.00, "na": 24.00, "k": 0.60, "hco3": 221.00, "so4": 10.00, "cl": 54.50, "no3": 27.00, "f": 0.15, "ph": 7.3 }],
  "tijen":      [{ "src": "Labiadh (Sidi Bouzid)", "cat": 1, "tds": 344, "ca": 60.00, "mg": 22.00, "na": 18.00, "k": 2.50, "hco3": 200, "so4": 71.00, "cl": 30, "no3": 2.50, "f": 0.35, "ph": 7.6 }],
  "primaqua":   [{ "src": "Koutine (Médenine)", "cat": 3, "tds": 349, "ca": 24.00, "mg": 16.12, "na": 63.66, "k": 1.18, "hco3": 42.7, "so4": 93.52, "cl": 77.66, "no3": 4.07, "f": 0.31, "ph": 7.4 }],
  "mira":       [{ "src": "Hajeb (Kairouan)", "cat": 2, "tds": 354, "ca": 63.35, "mg": 16.00, "na": 31.00, "k": 1.10, "hco3": 269.15, "so4": 24.40, "cl": 31.15, "no3": 13.30, "f": 0.60, "ph": 7.4 }],
  "bargou":     [{ "src": "Bargou (Siliana)", "cat": 2, "tds": 358, "ca": 89.00, "mg": 9.90, "na": 19.90, "k": 0.71, "hco3": 285.40, "so4": 13.50, "cl": 36.70, "no3": 1.70, "f": 0.10, "ph": 7.7 }],
  "jektiss":    [{ "src": "ex-Koutine (Médenine)", "cat": 3, "tds": 368, "ca": 24.00, "mg": 17.02, "na": 51.14, "k": 1.67, "hco3": 48.80, "so4": 91.94, "cl": 66.56, "no3": 6.70, "f": 0.37, "ph": 7.6 }],
  "fourat":     [{ "src": "Ouslatia (Kairouan)", "cat": 1, "tds": 370, "ca": 92.03, "mg": 14.43, "na": 21.60, "k": 2.50, "hco3": 274.05, "so4": 18.42, "cl": 32.24, "no3": 8.37, "f": 0.05, "ph": 7.5 }],
  "beya":       [{ "src": "Cherichira (Kairouan)", "cat": 2, "tds": 377, "ca": 55.30, "mg": 21.07, "na": 41.67, "k": 0.64, "hco3": 225.00, "so4": 21.01, "cl": 55.40, "no3": 7.40, "f": 0.68, "ph": 7.3 }],
  "marwa":      [{ "src": "Sidi Nsir (Bizerte)", "cat": 1, "tds": 378, "ca": 86.86, "mg": 8.21, "na": 36.37, "k": 1.79, "hco3": 254.66, "so4": 33.15, "cl": 72.78, "no3": 4.69, "f": 0.20, "ph": 7.6 }],
  "elixir":     [{ "src": "ex-Rayan, Nefza (Béja)", "cat": 2, "tds": 380, "ca": 77.21, "mg": 16.01, "na": 27.74, "k": 0.73, "hco3": 266.13, "so4": 21.31, "cl": 40.66, "no3": 3.15, "f": 0.24, "ph": 7.3 }],
  "dima":       [{ "src": "Tajerouine (Le Kef)", "cat": 1, "tds": 393, "ca": 82.88, "mg": 10.90, "na": 20.80, "k": 1.21, "hco3": 256.90, "so4": 40.60, "cl": 30.92, "no3": 17.30, "f": 0.23, "ph": 7.4 }],
  "melliti":    [{ "src": "Téboursouk (Béja)", "cat": 1, "tds": 422, "ca": 92.53, "mg": 7.30, "na": 30.24, "k": 0.82, "hco3": 260.77, "so4": 26.76, "cl": 53.96, "no3": 32.15, "f": 0.50, "ph": 7.0 }],
  "saha":       [{ "src": "El Fahs (Zaghouan)", "cat": 3, "tds": 430, "ca": 72.80, "mg": 6.81, "na": 43.55, "k": 0.90, "hco3": 135.42, "so4": 31.70, "cl": 86.20, "no3": 4.62, "f": 0.02, "ph": 7.2 }],
  "palma":      [{ "src": "Sidi Aïch (Gafsa)", "cat": 1, "tds": 438, "ca": 55.23, "mg": 32.40, "na": 30.77, "k": 1.24, "hco3": 205.26, "so4": 92.24, "cl": 18.86, "no3": 27.53, "f": 0.67, "ph": 7.4 }],
  "bulla-regia":[{ "src": "ex-Zullel (Jendouba)", "cat": 3, "tds": 441, "ca": 90.00, "mg": 10.53, "na": 28.00, "k": 1.17, "hco3": 122.00, "so4": 13.00, "cl": 130.00, "no3": 25.00, "f": 0.45, "ph": 7.2 }],
  "delice":     [{ "src": "Jelma (Sidi Bouzid)", "cat": 2, "tds": 491, "ca": 47.40, "mg": 28.45, "na": 92.23, "k": 5.15, "hco3": 237.30, "so4": 122.30, "cl": 58.65, "no3": 0.23, "f": 0.35, "ph": 7.4 }],
  "royal":      [{ "src": "ex-Cristal (Siliana)", "cat": 2, "tds": 491, "ca": 111.48, "mg": 18.38, "na": 27.46, "k": 0.69, "hco3": 330.95, "so4": 52.10, "cl": 38.41, "no3": 3.11, "f": 0.03, "ph": 7.2 }],
  "denya":      [{ "src": "Hajeb (Kairouan)", "cat": 2, "tds": 495, "ca": 51.92, "mg": 21.05, "na": 104.25, "k": 4.04, "hco3": 249.72, "so4": 85.16, "cl": 63.07, "no3": 6.75, "f": 0.59, "ph": 7.3 }],
  "melina":     [{ "src": "Bargou (Siliana)", "cat": 1, "tds": 508, "ca": 111.60, "mg": 16.90, "na": 30.05, "k": 0.87, "hco3": 344.28, "so4": 13.24, "cl": 61.40, "no3": 11.51, "f": 0.01, "ph": 7.4 }],
  "vivian":     [{ "src": "ex-Övia (Zaghouan)", "cat": 2, "tds": 558, "ca": 72.12, "mg": 19.10, "na": 100.16, "k": 1.44, "hco3": 254.00, "so4": 44.24, "cl": 126.81, "no3": 2.97, "f": 0.10, "ph": 7.3 }],
  "may":        [{ "src": "Le Krib (Siliana)", "cat": 2, "tds": 567, "ca": 102.76, "mg": 21.18, "na": 71.09, "k": 1.15, "hco3": 340.49, "so4": 84.88, "cl": 66.82, "no3": 8.40, "f": 0.16, "ph": 7.1 }],
  "tiba":       [{ "src": "Tlebt (Kasserine)", "cat": 2, "tds": 568, "ca": 78, "mg": 34, "na": 54, "k": 1.7, "hco3": 240, "so4": 113, "cl": 63, "no3": 23, "f": 0.6, "ph": 7.5 }],
  "aziz":       [{ "src": "Le Krib (Siliana)", "cat": 1, "tds": 580, "ca": 110, "mg": 15, "na": 56, "k": 1, "hco3": 358, "so4": 46, "cl": 60, "no3": 5.87, "f": 0.81, "ph": 7.3 }],
  "pristine":   [{ "src": "Henchir Kefia (Zaghouan)", "cat": 1, "tds": 581, "ca": 108.86, "mg": 24.72, "na": 31.78, "k": 0.69, "hco3": 221.70, "so4": 159.70, "cl": 41.63, "no3": 7.38, "f": 0.13, "ph": 7.3 }],
  "main":       [{ "src": "Tataouine nord", "cat": 1, "tds": 653, "ca": 65.15, "mg": 33.51, "na": 66.47, "k": 6.61, "hco3": 151.41, "so4": 184.85, "cl": 80.30, "no3": 23.63, "f": 0.62, "ph": 7.3 }],
  "cristaline": [{ "src": "Mogren (Zaghouan)", "cat": 1, "tds": 684, "ca": 112, "mg": 35, "na": 42, "k": 0.40, "hco3": 252, "so4": 189, "cl": 57, "no3": 5, "f": 0.15, "ph": 7.3 }],
  "aqualine":   [{ "src": "Mogren (Zaghouan)", "cat": 1, "tds": 752, "ca": 131.00, "mg": 35.00, "na": 39.00, "k": 0.60, "hco3": 235.00, "so4": 249.00, "cl": 50.00, "no3": 4.40, "f": 0.20, "ph": 7.2 }],
  "garci":      [{ "src": "Enfidha (Sousse)", "cat": 1, "tds": 1677, "ca": 169.00, "mg": 75.00, "na": 436.00, "k": 8.00, "hco3": 1119.00, "so4": 70.00, "cl": 328.0, "no3": 3.00, "f": 1.91, "ph": 6.3 }],
  "ain-oktor":  [{ "src": "Korbous (Nabeul)", "cat": 1, "tds": 1680, "ca": 160.00, "mg": 72.96, "na": 356.60, "k": 5.35, "hco3": 341.60, "so4": 144.30, "cl": 710.00, "no3": 11.70, "f": 0.50, "ph": 7.2 }]
 }
};
