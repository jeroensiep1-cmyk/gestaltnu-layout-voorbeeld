import sys; sys.path.insert(0,'/workspace/gestalt-nu/stijlvoorstel')
import numpy as np, math
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import gn_stijl as g
T='/workspace/gestalt-nu/test/'
hero=Image.open(T+'test-cirkel-vanaf-logo.png').convert('RGBA')
sec=Image.open(T+'poppetjes-sectie-gespiegeld-v29s.png').convert('RGB')
W,H=hero.size
cream=g.cream_canvas(W,2*H,seed=9).crop((0,0,W,H)).convert('RGBA')
A,LAM,PH=34,760,0.5
wy=lambda x:1736+A*math.sin(2*math.pi*x/LAM+PH)
X0=1268
shape=g.organic_box(X0-200,-50,W+300,1766,5,30,'b')
keep=g.svg_png(f'<path d="{g.dpath(shape)}" fill="#fff"/>',W,H).split()[3]
keep=keep.filter(ImageFilter.GaussianBlur(0.8))
# onder de golf: papier
cr=cream.copy(); cr=cr.crop((0,0,W,H))
sh=keep.filter(ImageFilter.GaussianBlur(14)); sh=ImageChops.offset(sh,8,14).point(lambda v:int(v*0.35))
dk=Image.new('RGBA',(W,H),(35,25,15,0)); dk.putalpha(sh); cr=Image.alpha_composite(cr,dk)
out=Image.composite(hero,cr,keep)
# alleen het fotogebied vervangen, linkerkant van de pagina blijft exact gelijk
left=Image.new('L',(W,H),0); ImageDraw.Draw(left).rectangle((0,0,X0-30,H),fill=255); left=left.filter(ImageFilter.GaussianBlur(14))
out=Image.composite(hero,out,left)
ha=np.asarray(hero.convert('RGB')).astype(float); lum=ha.mean(2)
kp=(lum>105)&(np.arange(W)[None,:]<1292)&(np.arange(W)[None,:]>=X0-40)&(np.arange(H)[:,None]>1700)
kp=Image.fromarray((kp*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1))
out=Image.composite(hero,out,kp)
pts=[(x,wy(x)-4) for x in range(X0-60,W+40,10)]
pass
out=out.convert('RGB')
out.paste(g.cream_canvas(W,H,seed=9).convert('RGB').crop((1292,1774,1312,1800)),(1292,1774))
fade=Image.new('L',(W,H),0); fd=ImageDraw.Draw(fade)
for k in range(70): fd.line((0,H-70+k,W,H-70+k),fill=int(255*(k/69)**1.5))
out=Image.composite(cream.convert('RGB'),out,fade)
pg=Image.new('RGB',(3200,3600)); pg.paste(out,(0,0)); pg.paste(sec,(0,1800))
pg.save(T+'website-voorpagina-met-poppetjes-v29.png')
pg.resize((1200,1350),Image.LANCZOS).save(T+'website-v29b.jpg',quality=92)
pg.crop((1000,1300,3200,2000)).save('/workspace/scratch/crop24.jpg')
