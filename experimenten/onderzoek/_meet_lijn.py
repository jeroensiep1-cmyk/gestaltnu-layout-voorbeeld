# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
from scipy import ndimage as nd

p = r"C:\Users\jeroe\gestaltnu-layout-voorbeeld\gestalt-nu-Grok\Grok\Stijlreferentie\therapiegroep-doodle-v13-huisstijlcreme.png"
a = np.asarray(Image.open(p).convert("RGB"))
lum = (a * [0.3, 0.59, 0.11]).sum(2)
ink = (lum < 90) & (a[..., 0] < 100) & (a[..., 2] < 80)
crop = ink[600:1200, 300:900]
dist = nd.distance_transform_edt(crop)
core = dist[crop]
print("ink radius median/p90/max", float(np.median(core)), float(np.percentile(core, 90)), float(core.max()))
print("approx stroke width px", float(np.percentile(core, 90) * 2))
