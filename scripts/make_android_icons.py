"""Icônes de lanceur Android — même « L » que la PWA, toutes densités.

Usage : python scripts/make_android_icons.py  (Pillow, dev uniquement ;
les PNG sont commités).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_icons import draw_icon  # noqa: E402

RES = Path(__file__).resolve().parent.parent / "android" / "app" / "src" / "main" / "res"
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def main() -> None:
    for density, size in DENSITIES.items():
        out = RES / f"mipmap-{density}"
        out.mkdir(parents=True, exist_ok=True)
        draw_icon(size).save(out / "ic_launcher.png")
    print(f"{len(DENSITIES)} icônes de lanceur écrites sous {RES}")


if __name__ == "__main__":
    main()
