# -*- coding: utf-8 -*-
"""
Bioscoopdoodle: Gestalt Nu-kleuren + losse hand-drawn doodle-esthetiek
(idee/compositie à la Grok kettingzaag-groep: imperfecte lijnen, korrel, geen clean vector).

Scène: zittend poppetje in bioscoop, eigen leven op het doek (maskers/triggers/muren),
grote open deur rechts met zon en vrijheid. Geen telefoon, geen ensō.
"""
from __future__ import annotations

import math
import random
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from io_veilig import force_utf8_stdio, write_bytes_atomic

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bioscoop-doodle-raw.png"
FINAL = ROOT / "bioscoop-doodle-final.png"
W, H = 3200, 1800

# Gestalt Nu-palet (zoals eerdere doodles / monnik / groep)
CREME = (246, 238, 223)
INK = (58, 47, 36)
TEAL = (15, 110, 110)
TEAL_L = (0, 148, 145)
TERRA = (196, 92, 62)
PEACH = (242, 184, 160)
SAGE = (126, 168, 106)
SAGE_L = (185, 200, 164)
YELLOW = (232, 184, 74)
SKIN = (240, 215, 194)
SCREEN = (42, 35, 28)
SHOE = (45, 40, 35)
FLOOR = (236, 226, 208)

RNG = random.Random(42)
SW = 16


def j(n: float, amt: float = 6.0) -> float:
    """Kleine wobble voor losse handtekening."""
    return n + RNG.uniform(-amt, amt)


def jpt(x: float, y: float, amt: float = 6.0) -> tuple[float, float]:
    return (j(x, amt), j(y, amt))


def wobble_poly(pts: list[tuple[float, float]], amt: float = 5.0, dens: int = 2) -> list[tuple[float, float]]:
    """Voeg tussenpunten + jitter toe zodat randen niet strak zijn."""
    out: list[tuple[float, float]] = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        out.append(jpt(x0, y0, amt))
        for k in range(1, dens):
            t = k / dens
            out.append(jpt(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, amt * 0.7))
    return out


def fat_polyline(draw: ImageDraw.ImageDraw, pts, width: float = SW, fill=INK, wobble: float = 3.0):
    if len(pts) < 2:
        return
    soft = [jpt(x, y, wobble) for x, y in pts]
    # licht variërende dikte: twee lagen
    draw.line(soft, fill=fill, width=int(width + RNG.uniform(-2, 3)), joint="curve")
    draw.line(soft, fill=fill, width=max(8, int(width * 0.55)), joint="curve")
    r = int(width // 2)
    for x, y in (soft[0], soft[-1]):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def blob(draw, cx, cy, rx, ry, fill, outline=INK, ow=SW, wobble: float = 8.0):
    """Onregelmatige ovaal i.p.v. perfecte ellipse."""
    pts = []
    steps = 18
    for i in range(steps):
        a = (i / steps) * math.tau
        rr = 1.0 + RNG.uniform(-0.08, 0.08)
        pts.append((cx + math.cos(a) * rx * rr + RNG.uniform(-wobble, wobble) * 0.3,
                    cy + math.sin(a) * ry * rr + RNG.uniform(-wobble, wobble) * 0.3))
    poly = wobble_poly(pts, amt=wobble * 0.4, dens=1)
    draw.polygon(poly, fill=fill, outline=outline)
    fat_polyline(draw, poly + [poly[0]], width=ow, wobble=2.0)


def capsule(draw, x0, y0, x1, y1, radius, fill, outline=INK, ow=SW):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    # licht gebogen midden (niet kaarsrecht)
    mx, my = (x0 + x1) / 2 + RNG.uniform(-8, 8), (y0 + y1) / 2 + RNG.uniform(-8, 8)
    side_a = []
    side_b = []
    for t, bx, by in ((0, x0, y0), (0.5, mx, my), (1, x1, y1)):
        rad = radius * (1.0 + RNG.uniform(-0.08, 0.08))
        side_a.append((bx + px * rad, by + py * rad))
        side_b.append((bx - px * rad, by - py * rad))
    pts = side_a + list(reversed(side_b))
    poly = wobble_poly(pts, amt=4.0, dens=2)
    draw.polygon(poly, fill=fill, outline=outline)
    fat_polyline(draw, poly + [poly[0]], width=ow, wobble=2.0)
    blob(draw, x0, y0, radius * 0.95, radius * 0.95, fill, outline, max(10, ow - 2), wobble=3)
    blob(draw, x1, y1, radius * 0.95, radius * 0.95, fill, outline, max(10, ow - 2), wobble=3)


def hand(draw, cx, cy, scale=1.0, angle_deg=0):
    r = 38 * scale
    blob(draw, cx, cy, r, r * 0.9, SKIN, ow=max(11, int(SW * 0.8)), wobble=5)
    rad = math.radians(angle_deg)
    for off in (-28, -10, 8, 26):
        fx = cx + math.cos(rad) * (r + 16) + math.sin(rad) * off * scale
        fy = cy + math.sin(rad) * (r + 16) - math.cos(rad) * off * scale
        blob(draw, fx, fy, 11 * scale, 12 * scale, SKIN, ow=9, wobble=3)


def cinema_seat(draw, x, y, w, h, fill, ow=14):
    # rug — iets scheef
    blob(draw, x + w * 0.5 + RNG.uniform(-6, 6), y + h * 0.32, w * 0.38, h * 0.34, fill, ow=ow, wobble=7)
    # zitting
    seat_col = tuple(max(0, c - 18) for c in fill)
    blob(draw, x + w * 0.5, y + h * 0.62, w * 0.46, h * 0.22, seat_col, ow=ow, wobble=6)
    capsule(draw, x + 22, y + h * 0.55, x + 18, y + h * 0.84, 14, fill, ow=ow)
    capsule(draw, x + w - 22, y + h * 0.55, x + w - 16, y + h * 0.84, 14, fill, ow=ow)
    fat_polyline(draw, [(x + w * 0.22, y + h * 0.86), (x + w * 0.17, y + h + 28)], width=ow)
    fat_polyline(draw, [(x + w * 0.78, y + h * 0.86), (x + w * 0.84, y + h + 28)], width=ow)


def draw_screen(draw):
    # schermkader: wobbly afgeronde rechthoek
    frame = [
        (390, 200), (1840, 175), (1870, 850), (370, 870),
    ]
    poly = wobble_poly(frame, amt=12, dens=3)
    draw.polygon(poly, fill=SCREEN, outline=INK)
    fat_polyline(draw, poly + [poly[0]], width=SW + 2, wobble=4)

    inner = wobble_poly([(430, 240), (1800, 225), (1825, 800), (415, 815)], amt=8, dens=2)
    draw.polygon(inner, fill=(30, 24, 20), outline=INK)
    fat_polyline(draw, inner + [inner[0]], width=12, wobble=3)

    # eigen leven: maskers, triggers, belemmeringen — los getekend
    blob(draw, 760, 480, 120, 145, PEACH, ow=SW, wobble=10)
    blob(draw, 720, 450, 12, 14, INK, ow=1, wobble=1)
    blob(draw, 800, 448, 12, 14, INK, ow=1, wobble=1)
    fat_polyline(draw, [(690, 540), (730, 575), (800, 578), (845, 535)], width=12, wobble=4)
    # haarpluk op masker
    fat_polyline(draw, [(680, 360), (740, 310), (820, 315), (870, 365)], width=14, wobble=5)

    blob(draw, 1080, 510, 100, 125, TEAL_L, ow=SW, wobble=9)
    blob(draw, 1045, 480, 14, 16, CREME, ow=1, wobble=1)
    blob(draw, 1120, 478, 14, 16, CREME, ow=1, wobble=1)
    fat_polyline(draw, [(1030, 560), (1085, 585), (1140, 555)], width=11, wobble=3)

    # bliksem-triggers
    bolt = [(1280, 290), (1210, 455), (1285, 455), (1195, 690), (1425, 455), (1335, 455)]
    bolt = wobble_poly(bolt, amt=7, dens=1)
    draw.polygon(bolt, fill=YELLOW, outline=INK)
    fat_polyline(draw, bolt + [bolt[0]], width=SW, wobble=3)

    bolt2 = [(1525, 370), (1465, 475), (1525, 475), (1415, 615), (1605, 475), (1550, 475)]
    bolt2 = wobble_poly(bolt2, amt=6, dens=1)
    draw.polygon(bolt2, fill=TERRA, outline=INK)
    fat_polyline(draw, bolt2 + [bolt2[0]], width=14, wobble=3)

    # muur / belemmering
    wall = wobble_poly([(1645, 310), (1855, 295), (1870, 640), (1635, 650)], amt=8, dens=2)
    draw.polygon(wall, fill=(216, 200, 168), outline=INK)
    fat_polyline(draw, wall + [wall[0]], width=SW, wobble=3)
    fat_polyline(draw, [(1650, 415), (1860, 405)], width=12, wobble=3)
    fat_polyline(draw, [(1655, 515), (1855, 525)], width=12, wobble=3)
    fat_polyline(draw, [(1755, 305), (1765, 645)], width=12, wobble=3)
    for i, cy in enumerate((375, 455, 535, 605)):
        ox = 1890 + (i % 2) * 40
        blob(draw, ox + 25, cy + 20, 28, 22, None if False else CREME, ow=13, wobble=4)
        # ring-look: alleen outline-achtig — vul crème, herteken dikke rand
        blob(draw, ox + 25, cy + 20, 22, 16, SCREEN, ow=1, wobble=2)


def draw_door(draw):
    # deuropening — iets scheef
    opening = wobble_poly([(2270, 150), (3040, 130), (3080, 1620), (2250, 1635)], amt=10, dens=3)
    draw.polygon(opening, fill=CREME, outline=INK)
    fat_polyline(draw, opening + [opening[0]], width=SW + 2, wobble=4)

    sky = wobble_poly([(2310, 190), (3000, 175), (3020, 710), (2295, 720)], amt=8, dens=2)
    draw.polygon(sky, fill=(232, 240, 216), outline=INK)
    fat_polyline(draw, sky + [sky[0]], width=11, wobble=3)

    hills = wobble_poly(
        [(2300, 700), (2520, 530), (2720, 610), (2920, 500), (3020, 680), (3020, 1600), (2300, 1600)],
        amt=12,
        dens=2,
    )
    draw.polygon(hills, fill=SAGE, outline=INK)
    fat_polyline(draw, hills + [hills[0]], width=SW, wobble=4)

    hills2 = wobble_poly(
        [(2300, 900), (2580, 730), (2800, 820), (3000, 710), (3020, 880), (3020, 1600), (2300, 1600)],
        amt=10,
        dens=2,
    )
    draw.polygon(hills2, fill=SAGE_L, outline=INK)
    fat_polyline(draw, hills2 + [hills2[0]], width=14, wobble=3)

    # zon — imperfecte cirkel + stralen
    blob(draw, 2780, 360, 115, 115, YELLOW, ow=SW, wobble=8)
    for ang in range(0, 360, 40):
        a = math.radians(ang + RNG.uniform(-8, 8))
        r0, r1 = 125 + RNG.uniform(-5, 5), 175 + RNG.uniform(-10, 15)
        fat_polyline(
            draw,
            [
                (2780 + math.cos(a) * r0, 360 + math.sin(a) * r0),
                (2780 + math.cos(a) * r1, 360 + math.sin(a) * r1),
            ],
            width=13,
            wobble=2,
        )

    # boom
    capsule(draw, 2460, 1200, 2475, 980, 13, (90, 70, 50), ow=13)
    blob(draw, 2470, 920, 130, 120, SAGE, ow=SW, wobble=10)
    for fx, fy, col in ((2680, 1180, TERRA), (2810, 1290, YELLOW), (2930, 1160, PEACH)):
        blob(draw, fx, fy, 18, 18, col, ow=8, wobble=3)

    # open deurblad — scheef
    door = wobble_poly([(2960, 175), (3140, 290), (3135, 1545), (2955, 1605)], amt=8, dens=2)
    draw.polygon(door, fill=TEAL, outline=INK)
    fat_polyline(draw, door + [door[0]], width=SW, wobble=3)
    blob(draw, 3065, 880, 22, 22, YELLOW, ow=10, wobble=3)


def draw_sitter(draw):
    cinema_seat(draw, 980, 1050, 560, 420, TEAL_L, ow=SW)

    # torso — onregelmatig
    torso = wobble_poly(
        [(1145, 1170), (1225, 1110), (1365, 1105), (1445, 1175), (1415, 1445), (1165, 1440)],
        amt=7,
        dens=2,
    )
    draw.polygon(torso, fill=TERRA, outline=INK)
    fat_polyline(draw, torso + [torso[0]], width=SW, wobble=3)

    capsule(draw, 1295, 1125, 1290, 1180, 17, SKIN, ow=13)
    blob(draw, 1290, 1055, 115, 115, SKIN, ow=SW, wobble=8)
    # haar
    fat_polyline(draw, [(1200, 1005), (1245, 915), (1330, 900), (1405, 980)], width=SW, wobble=5)
    blob(draw, 1175, 1085, 18, 28, SKIN, ow=11, wobble=3)
    blob(draw, 1405, 1085, 18, 28, SKIN, ow=11, wobble=3)
    # stipogen
    blob(draw, 1255, 1055, 14, 14, INK, ow=1, wobble=1)
    blob(draw, 1335, 1052, 14, 14, INK, ow=1, wobble=1)
    fat_polyline(draw, [(1260, 1118), (1295, 1138), (1340, 1115)], width=11, wobble=2)

    # armen
    capsule(draw, 1185, 1230, 1045, 1350, 27, SKIN, ow=SW)
    capsule(draw, 1045, 1350, 1065, 1470, 25, SKIN, ow=SW)
    hand(draw, 1075, 1490, scale=1.3, angle_deg=95)

    capsule(draw, 1405, 1230, 1590, 1185, 27, SKIN, ow=SW)
    capsule(draw, 1590, 1185, 1830, 1105, 25, SKIN, ow=SW)
    hand(draw, 1870, 1090, scale=1.35, angle_deg=-18)

    # zittende benen
    capsule(draw, 1205, 1440, 1085, 1530, 33, TEAL, ow=SW)
    capsule(draw, 1385, 1440, 1530, 1530, 33, TEAL, ow=SW)
    capsule(draw, 1085, 1530, 1005, 1650, 29, TEAL, ow=SW)
    capsule(draw, 1530, 1530, 1610, 1650, 29, TEAL, ow=SW)
    blob(draw, 1005, 1650, 70, 38, SHOE, ow=13, wobble=5)
    blob(draw, 1615, 1650, 70, 38, SHOE, ow=13, wobble=5)


def paper_grain(img: Image.Image, n: int = 220000, seed: int = 11) -> Image.Image:
    rng = random.Random(seed)
    pix = img.load()
    for _ in range(n):
        x, y = rng.randrange(W), rng.randrange(H)
        r, g, b = pix[x, y]
        d = rng.randint(-6, 6)
        pix[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return img


def main():
    force_utf8_stdio()
    global RNG
    RNG = random.Random(42)

    img = Image.new("RGB", (W, H), CREME)
    draw = ImageDraw.Draw(img)

    # zachte vloer — wobbly
    floor = wobble_poly([(150, 910), (2150, 850), (2240, 1730), (130, 1730)], amt=14, dens=3)
    draw.polygon(floor, fill=FLOOR, outline=INK)
    fat_polyline(draw, floor + [floor[0]], width=11, wobble=4)

    # kleine doodle-hartjes / bloemetjes (à la kettingzaag-groep, in GN-kleuren)
    blob(draw, 220, 220, 28, 24, TEAL_L, ow=10, wobble=4)
    blob(draw, 255, 220, 28, 24, TEAL_L, ow=10, wobble=4)
    blob(draw, 238, 245, 22, 26, TEAL_L, ow=10, wobble=3)
    blob(draw, 2100, 260, 32, 28, TERRA, ow=11, wobble=4)
    for fx, fy, col in ((480, 1680, PEACH), (620, 1710, YELLOW), (780, 1675, SAGE)):
        blob(draw, fx, fy, 14, 14, col, ow=7, wobble=2)

    draw_screen(draw)

    for sx, sy, sw, sh, col in (
        (340, 880, 250, 160, TEAL_L),
        (640, 880, 250, 160, TERRA),
        (940, 880, 250, 160, SAGE),
        (1240, 880, 250, 160, TEAL),
        (280, 1020, 290, 180, SAGE_L),
        (640, 1020, 290, 180, TEAL_L),
        (1020, 1020, 290, 180, TERRA),
    ):
        cinema_seat(draw, sx + RNG.uniform(-8, 8), sy + RNG.uniform(-6, 6), sw, sh, col, ow=14)

    draw_sitter(draw)
    draw_door(draw)

    img = paper_grain(img)
    # lichte blur op vulvlakken + unsharp op lijnen = minder "vector-strak"
    soft = img.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.blend(soft, img, 0.72)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=90, threshold=4))

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    write_bytes_atomic(OUT, buf.getvalue())
    print(f"ok raw {OUT} {img.size}")

    # ook final schrijven (zelfde output; nabehandeling optioneel apart)
    write_bytes_atomic(FINAL, buf.getvalue())
    print(f"ok final {FINAL}")


if __name__ == "__main__":
    main()
