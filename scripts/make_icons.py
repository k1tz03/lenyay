"""Génère les icônes PWA de Lenyay — un « L » blanc sur vert-de-gris profond.

Dessiné en formes pures (pas de police : le rendu est identique partout).
Usage : python scripts/make_icons.py   (nécessite Pillow, dev uniquement —
les PNG générés sont commités, personne d'autre n'a besoin de Pillow).
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "coordinator" / "static" / "icons"
DEEP = (36, 82, 71)      # --verd-deep
VERD = (63, 140, 121)    # --verd
WHITE = (255, 255, 255)


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = 0 if maskable else size // 5
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=DEEP)
    # léger dégradé : bande diagonale plus claire, discrète
    d.polygon([(0, 0), (size, 0), (0, size)], fill=VERD + (40,))

    # Le « L » : deux rectangles, centré dans la zone sûre.
    # Zone sûre maskable = 80 % du canevas.
    safe = 0.62 if maskable else 0.52
    h = size * safe                 # hauteur du L
    stem = h * 0.30                 # épaisseur du trait
    w = h * 0.72                    # largeur du pied
    x0 = (size - w) / 2
    y0 = (size - h) / 2
    d.rectangle([x0, y0, x0 + stem, y0 + h], fill=WHITE)          # jambe
    d.rectangle([x0, y0 + h - stem, x0 + w, y0 + h], fill=WHITE)  # pied
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    draw_icon(192).save(OUT / "icon-192.png")
    draw_icon(512).save(OUT / "icon-512.png")
    draw_icon(512, maskable=True).save(OUT / "icon-maskable-512.png")
    print(f"3 icônes écrites dans {OUT}")


if __name__ == "__main__":
    sys.exit(main())
