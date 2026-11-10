# -*- coding: utf-8 -*-
"""
Nabehandeling à la therapiegroep-doodle-v10, zonder gn_stijl/ensō:
- crème papier #F6EEDF + lichte korrel
- donkere lijnen dikker (~THICK 1.5), lijnkleur #3A2F24
In:  bioscoop-doodle-raw.png
Uit: bioscoop-doodle-final.png (3200x1800)
"""
from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from io_veilig import force_utf8_stdio, wait_file_ready, wait_unlocked, write_bytes_atomic

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "bioscoop-doodle-raw.png"
OUT = ROOT / "bioscoop-doodle-final.png"
CREME = (246, 238, 223)  # #F6EEDF
LINE = np.array([58.0, 47.0, 36.0])  # #3A2F24
W, H = 3200, 1800
THICK = 1.5


def cream_canvas(w: int, h: int, seed: int = 7) -> Image.Image:
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[:] = CREME
    grain = rng.normal(0, 3.2, (h, w, 1)).astype(np.float32)
    grain = (
        np.array(
            Image.fromarray(np.clip(grain[..., 0] + 128, 0, 255).astype("uint8")).filter(
                ImageFilter.GaussianBlur(1.2)
            )
        ).astype(np.float32)
        - 128
    )
    out = np.clip(base + grain[..., None] * 0.35, 0, 255).astype("uint8")
    return Image.fromarray(out, "RGB").convert("RGBA")


def thicken_dark(im: Image.Image, amount: float = THICK) -> Image.Image:
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3] / 255.0
    lum = (rgb * [0.3, 0.59, 0.11]).sum(2)
    dark = ((lum < 95) & (alpha > 0.35)).astype(np.uint8) * 255
    core = Image.fromarray(dark, "L")
    grown = core.filter(ImageFilter.MaxFilter(size=3))
    if amount >= 1.2:
        grown = grown.filter(ImageFilter.MaxFilter(size=3))
    if amount >= 1.45:
        grown = grown.filter(ImageFilter.MaxFilter(size=3))
    g = np.asarray(grown).astype(np.float32) / 255.0
    mix = np.clip(g[..., None], 0, 1)
    rgb2 = rgb * (1 - mix * 0.85) + LINE * (mix * 0.85)
    a2 = np.clip(alpha + g * (1 - alpha) * 0.9, 0, 1)
    return Image.fromarray(np.dstack([rgb2, a2 * 255]).clip(0, 255).astype("uint8"), "RGBA")


def knock_out_background(fig: Image.Image) -> Image.Image:
    a = np.asarray(fig).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    near = (np.abs(rgb - np.array(CREME)).sum(2) < 28) | (rgb.min(2) > 248)
    al = np.where(near, 0.0, al)
    return Image.fromarray(np.dstack([rgb, al]).astype("uint8"), "RGBA")


def save_png(path: Path, im: Image.Image) -> None:
    if path.exists() and not wait_unlocked(path, timeout_s=8.0):
        raise PermissionError(f"Kan niet schrijven, bestand vergrendeld: {path}")
    buf = BytesIO()
    im.convert("RGB").save(buf, format="PNG", optimize=True)
    write_bytes_atomic(path, buf.getvalue())


def main() -> int:
    force_utf8_stdio()
    try:
        wait_file_ready(SRC, min_bytes=5000, timeout_s=15.0)
    except FileNotFoundError as err:
        print(f"FOUT: {err}", file=sys.stderr)
        return 1

    try:
        raw = Image.open(SRC).convert("RGBA")
    except OSError as err:
        print(f"FOUT: kon raw niet openen: {err}", file=sys.stderr)
        return 1

    if raw.size != (W, H):
        raw = raw.resize((W, H), Image.LANCZOS)

    try:
        fig = thicken_dark(raw)
        fig = knock_out_background(fig)
        canvas = cream_canvas(W, H)
        # Geen ensō — expliciet voor bioscoopscène
        canvas = Image.alpha_composite(canvas, fig)
        save_png(OUT, canvas)
    except PermissionError as err:
        print(f"FOUT: {err}", file=sys.stderr)
        return 2
    except Exception as err:
        print(f"FOUT tijdens nabehandeling: {type(err).__name__}: {err}", file=sys.stderr)
        return 3

    print(f"ok {OUT} {canvas.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
