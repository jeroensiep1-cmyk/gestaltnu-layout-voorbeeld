#!/usr/bin/env python3
"""TEST (intern) v10: v9-doodle (AI, Open Doodles-stijl) opgeschaald, lijnen ~30% dikker, witte achtergrond -> transparant,
op crème papier (C-homepage korrel) met de teal ensō uit gn_stijl achter de groep. 3200x1800."""
import sys, os
sys.dont_write_bytecode = True
os.environ.setdefault('GN_SCALE', '2')
sys.path.insert(0, '/workspace/gestalt-nu/stijlvoorstel'); sys.path.insert(0, '/workspace/gestalt-nu/test')
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd
from gn_stijl import enso, svg_png, TEAL
import maak_test_cirkel_c_homepage as CH          # cream_canvas_S (zelfde korrel als C), alleen gelezen

SRC = '/workspace/gestalt-nu/test/therapiegroep-doodle-v9.jpg'
OUT = '/workspace/gestalt-nu/test/therapiegroep-doodle-v10.png'
PREV = '/workspace/gestalt-nu/test/therapiegroep-doodle-v10-voorbeeld.jpg'
W, H = 3200, 1800
K = float(os.environ.get('V10_K', 1.93))          # schaal figuren
THICK = float(os.environ.get('V10_THICK', 1.5))  # extra lijndikte per kant (px op eindformaat)
ENSO_W = 17; MARGIN = 1.005

def background_mask(a):
    mn = a.min(2); wb = a[..., 0] - a[..., 2]
    cand = (mn >= 246) & (wb <= 6)
    lab, n = nd.label(cand)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(border))
    sizes = nd.sum(np.ones_like(lab), lab, range(1, n+1)); means = nd.mean(mn, lab, range(1, n+1))
    for k in range(1, n+1):     # ingesloten achtergrond-zakjes (bv. tussen arm en hoofd, handvat kettingzaag)
        if k in border: continue
        cx_k = nd.center_of_mass(lab == k)[1] if sizes[k-1] >= 150 else 0
        if (sizes[k-1] >= 400 and means[k-1] >= 251.0) or (sizes[k-1] >= 150 and means[k-1] >= 251.0 and cx_k > 300):
            bg |= lab == k          # (x>300: niet het witte overhemd van de vampier)
    # smalle witte spleetjes die aan de achtergrond grenzen (tussen tutu-veren en pak e.d.), losser criterium;
    # alleen kleine stukjes en niet in de mummie (die is zelf bijna wit en lekt anders weg)
    loose = (mn >= 238) & (wb <= 16)
    lab2, n2 = nd.label(loose)
    ids = np.unique(lab2[bg & loose]); ids = ids[ids > 0]
    add = np.isin(lab2, ids) & ~bg
    lab3, n3 = nd.label(add)
    for k in range(1, n3+1):
        ys, xs = np.where(lab3 == k)
        if len(ys) <= 400 and not (755 <= xs.mean() <= 950): bg[ys, xs] = True
    return bg

def main():
    src = Image.open(SRC).convert('RGB'); a0 = np.asarray(src).astype(np.int32)
    bg0 = background_mask(a0)
    fg0 = ~bg0; ys, xs = np.where(fg0)
    # ---- ellips rond de groep (bronpixels), aspect 1.8
    cx0 = (xs.min()+xs.max())/2; cy0 = (ys.min()+ys.max())/2 + 20; asp = 1.8
    ry0 = np.sqrt(((xs-cx0)/asp)**2 + (ys-cy0)**2).max()
    sw, sh = int(round(src.width*K)), int(round(src.height*K))
    ox = int(round(W/2 - cx0*K)); oy = int(round(H/2 + 5 - cy0*K))
    ecx, ecy = cx0*K + ox, cy0*K + oy; ery = ry0*K*MARGIN; erx = ery*asp
    print('figuren', sw, sh, 'op', ox, oy, '| ellips', round(ecx), round(ecy), round(erx), round(ery))
    # ---- opschalen + licht verscherpen
    up = src.resize((sw, sh), Image.LANCZOS)
    A = np.asarray(up).astype(np.float32)
    # ontringen: LANCZOS-overshoot (lichte randjes naast donkere lijnen) begrenzen tot het lokale bereik van bilineair
    Bl = np.asarray(src.resize((sw, sh), Image.BILINEAR)).astype(np.float32)
    fp = int(round(K))*2+1
    lo = np.stack([nd.minimum_filter(Bl[..., i], size=fp) for i in range(3)], -1)
    hi = np.stack([nd.maximum_filter(Bl[..., i], size=fp) for i in range(3)], -1)
    A = np.clip(A, lo, hi)
    bgm = np.asarray(Image.fromarray((bg0*255).astype('uint8')).resize((sw, sh), Image.BILINEAR)).astype(np.float32)/255
    bg = bgm > 0.5
    # ---- alfa: ontmengen met wit in een band rond de achtergrond (geen witte halo)
    mn = A.min(2)
    bw = int(round(2*K))
    band = nd.binary_dilation(bg, iterations=bw)                         # achtergrond + smalle anti-aliasrand
    F = nd.minimum_filter(np.where(band, 255, mn), size=2*bw+3)          # kleur van de 'vaste' voorgrond vlakbij
    alpha_mix = np.clip((255 - mn)/np.maximum(255 - F, 25), 0, 1)
    alpha = np.where(band, alpha_mix, 1.0)
    alpha = np.where(bg & (alpha < 0.04), 0, alpha)
    al = np.maximum(alpha, 1e-3)[..., None]
    col = np.clip((A - 255*(1-al))/al, 0, 255)
    col = np.where(band[..., None], col, A)
    # ---- lijnen dikker: donkere kern -> afstand -> zachte rand (fractioneel, anti-aliased)
    lum = (col*[0.3, 0.59, 0.11]).sum(2)
    dark = np.clip((120 - lum)/60, 0, 1)*alpha                          # 1 = volle lijn
    core = dark > 0.5
    dist = nd.distance_transform_edt(~core)
    # lichte JPEG-randjes naast de lijnen (binnenkant) weghalen: ring 1..4 px mag niet lichter zijn dan het vlak erachter
    far = (dist > 4.5) & ~band
    _, (iy, ix) = nd.distance_transform_edt(~far, return_indices=True)
    ring = (dist > 0) & (dist <= 4.5) & ~band
    ref = col[iy, ix]
    col = np.where(ring[..., None], np.minimum(col, ref), col)
    grow = np.clip(THICK + 0.5 - dist, 0, 1)
    grow = np.asarray(Image.fromarray((grow*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.45))).astype(np.float32)/255
    grow = np.where(core, 1.0, grow)
    add = np.clip(grow - dark, 0, 1)                                    # alleen waar het nog niet donker was
    LC = np.median(col[core & (alpha > 0.95)], axis=0)                  # lijnkleur (donkerbruin uit de bron)
    print('lijnkleur', LC.round())
    newa = np.clip(alpha + add*(1-alpha), 0, 1)
    w_old = alpha*(1-add); w_new = add
    col2 = (col*w_old[..., None] + LC*w_new[..., None])/np.maximum(w_old+w_new, 1e-6)[..., None]
    fig = np.dstack([col2, newa*255]).clip(0, 255).astype('uint8')
    figim = Image.fromarray(fig, 'RGBA')
    # ---- canvas: crème met korrel, ensō, figuren erover
    canvas = CH.cream_canvas_S()
    assert canvas.size == (W, H)
    body = enso(ecx, ecy, erx, w=ENSO_W, col=TEAL, seed=11, ry=ery, a0=112, a1=461, dry=0.65)
    L = svg_png(body, W, H); la = np.asarray(L).astype(np.float32)
    gr = np.random.default_rng(5).random((H, W), dtype=np.float32)
    gr = np.asarray(Image.fromarray((gr*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.4))).astype(np.float32)/255
    la[..., 3] *= (0.78 + 0.22*gr)
    canvas = Image.alpha_composite(canvas, Image.fromarray(la.clip(0, 255).astype('uint8')))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.paste(figim, (ox, oy))
    canvas = Image.alpha_composite(canvas, layer)
    canvas.convert('RGB').save(OUT, optimize=True)
    canvas.convert('RGB').resize((1600, 900), Image.LANCZOS).save(PREV, quality=90)
    # controle: voorgrond buiten de ellips?
    la2 = np.asarray(layer.split()[3]) > 128; yy, xx = np.where(la2)
    r = np.sqrt(((xx-ecx)/erx)**2 + ((yy-ecy)/ery)**2); print('max r figuren', r.max().round(3), 'pixels buiten', int((r > 1).sum()))
    print('ok', OUT)

if __name__ == '__main__': main()
