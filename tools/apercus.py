"""Image d'aperçu de CHAQUE rapport (18/10/2026, Ahmed : « quand je partage l'article sur Facebook, l'image est celle du site ;
je veux partager l'ARTICLE », appliqué à tous les sites). 1200 × 630, JPEG : titre de l'article, mois, chiffre clé, nom et adresse du site.
Pillow (pip install pillow) ; polices DejaVu copiées dans tools/polices/ (licence libre, Bitstream Vera / DejaVu).
Sans Pillow : None (la page garde l'image générale des rapports, rien ne casse)."""
import os

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
TERRE, ENCRE, SABLE, DOUX, OR, LIGNE = (14, 127, 168), (15, 43, 61), (244, 248, 250), (90, 116, 132), (242, 179, 61), (215, 228, 235)


def _police(nom, taille):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(ICI, "polices", nom), taille)


def _lignes(dessin, texte, police, largeur):
    mots, lignes, cur = texte.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if dessin.textlength(essai, font=police) <= largeur:
            cur = essai
        else:
            if cur:
                lignes.append(cur)
            cur = m
    return lignes + ([cur] if cur else [])


def fabriquer(chemin_sortie, titre, mois, chiffre, sous_titre=""):
    """Écrit l'image ; renvoie True, ou False si Pillow manque."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False
    im = Image.new("RGB", (1200, 630), SABLE)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 14], fill=TERRE)
    # ruban « Rapport du mois · octobre 2026 »
    f_ruban = _police("DejaVuSans-Bold.ttf", 30)
    ruban = f"RAPPORT DU MOIS · {mois.upper()}"
    w = d.textlength(ruban, font=f_ruban)
    d.rounded_rectangle([64, 60, 64 + w + 40, 60 + 56], radius=12, fill=TERRE)
    d.text((84, 70), ruban, font=f_ruban, fill=(255, 255, 255))
    # titre de l'article (2 à 3 lignes)
    taille = 66
    while True:
        f_titre = _police("DejaVuSerif-Bold.ttf", taille)
        lignes = _lignes(d, titre, f_titre, 1070)
        if len(lignes) <= 3 or taille <= 44:
            break
        taille -= 4
    y = 150
    for l in lignes[:3]:
        d.text((64, y), l, font=f_titre, fill=ENCRE)
        y += int(taille * 1.18)
    # chiffre clé
    if chiffre:
        f_ch = _police("DejaVuSans-Bold.ttf", 40)
        y += 14
        d.rounded_rectangle([64, y, 64 + d.textlength(chiffre, font=f_ch) + 44, y + 70], radius=14, fill=(255, 255, 255), outline=LIGNE, width=3)
        d.text((86, y + 12), chiffre, font=f_ch, fill=TERRE)
        y += 86
    if sous_titre:
        d.text((64, y + 6), sous_titre, font=_police("DejaVuSans.ttf", 28), fill=DOUX)
    # pied : logo + nom + adresse
    try:
        logo = Image.open(os.path.join(RACINE, "assets", "icons", "icon-192.png")).convert("RGBA").resize((70, 70))
        im.paste(logo, (64, 528), logo)
    except OSError:
        pass
    d.text((150, 536), "Prix des Eaux de Tunisie", font=_police("DejaVuSerif-Bold.ttf", 34), fill=ENCRE)
    d.text((150, 578), "prix-eau.clicvia.com", font=_police("DejaVuSans-Bold.ttf", 26), fill=TERRE)
    os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)
    im.save(chemin_sortie, "JPEG", quality=85, optimize=True)
    return True
