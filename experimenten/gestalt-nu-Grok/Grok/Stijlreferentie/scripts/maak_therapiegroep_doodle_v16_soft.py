#!/usr/bin/env python3
"""v16 soft: Open Doodles-nabewerking zonder lijnen te verscherpen.
Bron: AI-raw → crème #F6EEDF + zachte teal ensō (stijlblad).
Gebaseerd op maak_therapiegroep_doodle_v10.py, maar zonder THICK/lijn-dikker."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
# Canonieke beelden: projectroot/afbeeldingen/ (niet meer alleen onder Grok/)
AFBEELDINGEN = Path(__file__).resolve().parents[4] / "afbeeldingen"
SRC = Path(
    r"C:\Users\jeroe\.cursor\projects\c-Users-jeroe-gestaltnu-layout-voorbeeld"
    r"\assets\therapiegroep-doodle-v16-soft-raw.jpg"
)
if not SRC.is_file():
    SRC = AFBEELDINGEN / "therapiegroep-doodle-v16-soft-raw.jpg"
OUT = AFBEELDINGEN / "therapiegroep-doodle-v16-opendoodles-soft.png"
OUT_COPY = AFBEELDINGEN / "therapiegroep-doodle-v16-opendoodles-soft.png"
PREV = AFBEELDINGEN / "therapiegroep-doodle-v16-opendoodles-soft-voorbeeld.jpg"

CREME = (246, 238, 223)  # #F6EEDF
TEAL = (0, 168, 165)  # #00A8A5
TEAL_D = (0, 112, 110)  # #00706E
W, H = 3200, 1800


def cream_canvas(w: int, h: int, seed: int = 16) -> Image.Image:
    rng = np.random.default_rng(seed)
    base = np.full((h, w, 3), CREME, dtype=np.float32)
    grain = rng.normal(0, 3.2, (h, w)).astype(np.float32)
    gspan = float(grain.max() - grain.min()) + 1e-6
    grain = np.asarray(
        Image.fromarray(((grain - grain.min()) / gspan * 255).astype("uint8")).filter(
            ImageFilter.GaussianBlur(1.2)
        )
    ).astype(np.float32)
    grain = (grain - 127.5) * 0.045
    for i in range(3):
        base[..., i] = np.clip(base[..., i] + grain, 0, 255)
    return Image.fromarray(base.astype("uint8"), "RGB").convert("RGBA")


def soft_enso(size: tuple[int, int]) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = w * 0.50, h * 0.58
    rx, ry = w * 0.42, h * 0.36
    # broken brush ring — soft, not sharp
    for i, col in enumerate((TEAL, TEAL_D, TEAL)):
        width = 22 - i * 4
        bbox = [cx - rx + i * 6, cy - ry + i * 4, cx + rx - i * 6, cy + ry - i * 4]
        start = 18 + i * 12
        end = 340 - i * 8
        draw.arc(bbox, start=start, end=end, fill=col + (118 - i * 18,), width=width)
    # slight dry-brush feel
    layer = layer.filter(ImageFilter.GaussianBlur(1.6))
    return layer


def near_white_mask(rgb: np.ndarray) -> np.ndarray:
    mn = rgb.min(axis=2)
    wb = np.abs(rgb[..., 0].astype(np.int16) - rgb[..., 2].astype(np.int16))
    return (mn >= 242) & (wb <= 12)


def main() -> None:
    src = Image.open(SRC).convert("RGB")
    # Fit into canvas while keeping soft look (LANCZOS, then light soften — no sharpen)
    src = src.resize((W, H), Image.LANCZOS)
    src = src.filter(ImageFilter.GaussianBlur(0.35))
    soft = ImageEnhance.Color(src).enhance(1.04)
    soft = ImageEnhance.Contrast(soft).enhance(0.97)
    a = np.asarray(soft).astype(np.float32)

    bg = near_white_mask(a.astype(np.uint8))
    # feather alpha: keep figures soft-edged
    alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
    alpha_img = Image.fromarray((alpha * 255).astype("uint8"), "L").filter(
        ImageFilter.GaussianBlur(1.8)
    )
    alpha = np.asarray(alpha_img).astype(np.float32) / 255.0

    # unpremultiply mild white fringe
    al = np.maximum(alpha, 1e-3)[..., None]
    col = np.clip((a - 255 * (1 - al)) / al, 0, 255)
    rgba = np.dstack([col, alpha * 255]).clip(0, 255).astype("uint8")
    fig = Image.fromarray(rgba, "RGBA")

    canvas = cream_canvas(W, H)
    canvas = Image.alpha_composite(canvas, soft_enso((W, H)))
    canvas = Image.alpha_composite(canvas, fig)
    out = canvas.convert("RGB")
    out.save(OUT, optimize=True)
    out.resize((1600, 900), Image.LANCZOS).save(PREV, quality=92)
    OUT_COPY.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_COPY, optimize=True)
    print("ok", OUT)
    print("copy", OUT_COPY)


if __name__ == "__main__":
    main()
