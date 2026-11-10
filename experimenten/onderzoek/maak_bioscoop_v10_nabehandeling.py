# -*- coding: utf-8 -*-
"""
Nabehandeling zoals maak_therapiegroep_doodle_v10.py:
- achtergrond → alfa
- lijnen dikker (THICK=1.5), lijnkleur uit bron of #3A2F24
- crème canvas #F6EEDF met papierkorrel
Zonder ensō (bioscoopscène mag geen cirkel).
"""
from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

from io_veilig import force_utf8_stdio, wait_file_ready, wait_unlocked, write_bytes_atomic

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "bioscoop-doodle-raw.png"
OUT = ROOT / "bioscoop-doodle-final.png"
OUT_ALT = ROOT / "bioscoop-doodle-final-v2.png"
PREV = ROOT / "bioscoop-doodle-final-voorbeeld.jpg"
W, H = 3200, 1800
THICK = float(os.environ.get("V10_THICK", "1.5"))
CREME = (246, 238, 223)
FALLBACK_LINE = np.array([58.0, 47.0, 36.0])  # #3A2F24


def cream_canvas(w: int = W, h: int = H, seed: int = 9) -> Image.Image:
    """C-homepage-achtige crèmekorrel (lokaal, zonder gn_stijl)."""
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[:] = CREME
    grain = rng.normal(0, 3.4, (h, w)).astype(np.float32)
    grain = (
        np.asarray(
            Image.fromarray(np.clip(grain + 128, 0, 255).astype("uint8")).filter(
                ImageFilter.GaussianBlur(1.35)
            )
        ).astype(np.float32)
        - 128
    )
    # tweede, fijnere korrellaag
    fine = rng.normal(0, 1.6, (h, w)).astype(np.float32)
    fine = (
        np.asarray(
            Image.fromarray(np.clip(fine + 128, 0, 255).astype("uint8")).filter(
                ImageFilter.GaussianBlur(0.6)
            )
        ).astype(np.float32)
        - 128
    )
    out = np.clip(base + grain[..., None] * 0.38 + fine[..., None] * 0.18, 0, 255).astype("uint8")
    return Image.fromarray(out, "RGB").convert("RGBA")


def background_mask(a: np.ndarray) -> np.ndarray:
    mn = a.min(2)
    wb = a[..., 0].astype(np.int32) - a[..., 2].astype(np.int32)
    # crème of wit als achtergrond
    creme = np.abs(a.astype(np.int32) - np.array(CREME)[None, None, :]).sum(2) <= 28
    cand = ((mn >= 246) & (wb <= 6)) | creme
    lab, n = nd.label(cand)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(border))
    sizes = nd.sum(np.ones_like(lab), lab, range(1, n + 1))
    means = nd.mean(mn, lab, range(1, n + 1))
    for k in range(1, n + 1):
        if k in border:
            continue
        if sizes[k - 1] >= 400 and means[k - 1] >= 248.0:
            bg |= lab == k
    return bg


def thicken_v10(src: Image.Image) -> Image.Image:
    """Kern van maak_therapiegroep_doodle_v10: alfa + lijndikte, zonder opschaal/ensō."""
    a0 = np.asarray(src.convert("RGB")).astype(np.int32)
    bg0 = background_mask(a0)
    A = a0.astype(np.float32)
    bg = bg0
    mn = A.min(2)
    band = nd.binary_dilation(bg, iterations=3)
    F = nd.minimum_filter(np.where(band, 255, mn), size=7)
    alpha_mix = np.clip((255 - mn) / np.maximum(255 - F, 25), 0, 1)
    alpha = np.where(band, alpha_mix, 1.0)
    alpha = np.where(bg & (alpha < 0.04), 0, alpha)
    al = np.maximum(alpha, 1e-3)[..., None]
    col = np.clip((A - 255 * (1 - al)) / al, 0, 255)
    col = np.where(band[..., None], col, A)

    lum = (col * [0.3, 0.59, 0.11]).sum(2)
    dark = np.clip((120 - lum) / 60, 0, 1) * alpha
    core = dark > 0.5
    dist = nd.distance_transform_edt(~core)
    far = (dist > 4.5) & ~band
    _, (iy, ix) = nd.distance_transform_edt(~far, return_indices=True)
    ring = (dist > 0) & (dist <= 4.5) & ~band
    ref = col[iy, ix]
    col = np.where(ring[..., None], np.minimum(col, ref), col)
    grow = np.clip(THICK + 0.5 - dist, 0, 1)
    grow = (
        np.asarray(
            Image.fromarray((grow * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.45))
        ).astype(np.float32)
        / 255
    )
    grow = np.where(core, 1.0, grow)
    add = np.clip(grow - dark, 0, 1)
    # Alleen echt donkerbruine pixels als lijnkleur (geen teal/groen uit vullingen)
    brown = core & (alpha > 0.95) & (col[..., 0] > col[..., 1] - 5) & (col[..., 2] < 90) & (lum < 85)
    if brown.sum() >= 200:
        LC = np.median(col[brown], axis=0)
    else:
        LC = FALLBACK_LINE
    # Houd dicht bij #3A2F24
    if abs(LC[0] - 58) > 25 or LC[1] > 70:
        LC = FALLBACK_LINE
    print("lijnkleur", LC.round())
    newa = np.clip(alpha + add * (1 - alpha), 0, 1)
    w_old = alpha * (1 - add)
    w_new = add
    col2 = (col * w_old[..., None] + LC * w_new[..., None]) / np.maximum(w_old + w_new, 1e-6)[..., None]
    return Image.fromarray(np.dstack([col2, newa * 255]).clip(0, 255).astype("uint8"), "RGBA")


def main() -> int:
    force_utf8_stdio()
    try:
        wait_file_ready(SRC, min_bytes=5000, timeout_s=20.0)
        raw = Image.open(SRC).convert("RGB")
    except Exception as err:
        print(f"FOUT bron: {err}", file=sys.stderr)
        return 1

    if raw.size != (W, H):
        raw = raw.resize((W, H), Image.LANCZOS)

    try:
        fig = thicken_v10(raw)
        canvas = cream_canvas(W, H)
        # geen ensō
        canvas = Image.alpha_composite(canvas, fig)
        buf = BytesIO()
        canvas.convert("RGB").save(buf, format="PNG", optimize=True)
        data = buf.getvalue()
        target = OUT
        try:
            write_bytes_atomic(OUT, data)
        except PermissionError:
            target = OUT_ALT
            write_bytes_atomic(OUT_ALT, data)
            print(f"let op: {OUT.name} vergrendeld, geschreven naar {OUT_ALT.name}")
        try:
            canvas.convert("RGB").resize((1600, 900), Image.LANCZOS).save(PREV, quality=90)
        except OSError as err:
            print(f"waarschuwing preview: {err}")
    except Exception as err:
        print(f"FOUT nabehandeling: {type(err).__name__}: {err}", file=sys.stderr)
        return 3

    print(f"ok {target} {canvas.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
