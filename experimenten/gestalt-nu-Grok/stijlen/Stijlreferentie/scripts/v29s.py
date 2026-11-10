import sys; sys.path.insert(0,'/workspace/gestalt-nu/stijlvoorstel')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import gn_stijl as g
W,H=3200,1800
P=g.cream_canvas(W,2*H,seed=9); im=P.crop((0,H,W,2*H)).convert('RGBA')
# ---- paneel (spiegelbeeld van de foto): box in px, torn rechts en boven
x0,y0,x1,y1=-16,184,1936,1816
pw,ph=x1-x0,y1-y0
bgi=Image.open('/workspace/scratch/bg_leeg.jpg').convert('RGB')
bw=int(pw*1.0); bh=int(bgi.height*bw/bgi.width); bgi=bgi.resize((bw,bh),Image.LANCZOS); ox=(bw-pw)//2; bgi=bgi.crop((ox,0,ox+pw,bh)); bw=pw
_a=np.asarray(bgi).astype(float); _c=np.median(_a[0:6].reshape(-1,3),axis=0); _t=np.array([246,238,223.])
_w=np.clip(1-np.abs(_a-_c).sum(2)/70,0,1)[...,None]; bgi=Image.fromarray(np.clip(_a*(1-_w)+(_a*(_t/_c))*_w,0,255).astype(np.uint8))
top=np.asarray(bgi)[5:60,200:900].reshape(-1,3).mean(0)
row=np.median(np.asarray(bgi)[0:6].reshape(-1,3),axis=0).reshape(1,1,3)*np.ones((1,pw,1)); SH=230; fill=np.repeat(row,ph-bh-SH,axis=0).astype(np.uint8); brow=np.median(np.asarray(bgi)[-4:].reshape(-1,3),axis=0).reshape(1,1,3)*np.ones((1,pw,1)); bfill=np.repeat(brow,SH,axis=0).astype(np.uint8); panel=Image.fromarray(np.vstack([fill,np.asarray(bgi),bfill]))
panel=panel.convert('RGBA')
fg=Image.open('/workspace/scratch/figuren_v12.png'); tw=1700; th=int(fg.height*tw/fg.width)
fg=fg.resize((tw,th),Image.LANCZOS)
feet=ph-bh-SH+int(0.855*bh)
panel.alpha_composite(fg,((pw-tw)//2,feet-th))
full=Image.new('RGBA',(W,H),(0,0,0,0)); full.paste(panel,(x0,y0))
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rectangle((x0+60,y0+60,x1-70,y1-60),fill=255); m=m.filter(ImageFilter.GaussianBlur(45))
m=ImageChops.multiply(m,Image.new('L',(W,H),255))
sh=m.point(lambda v:0); dark=Image.new('RGBA',(W,H),(35,25,15,0)); dark.putalpha(sh)
im=Image.alpha_composite(im,dark)
full.putalpha(ImageChops.multiply(full.split()[3],m)); im=Image.alpha_composite(im,full)
# ---- tekst rechts (zelfde maten als de meiden-sectie, x gespiegeld)
dr=ImageDraw.Draw(im); INK=g.rgb(g.INK); TD=g.rgb(g.TEAL_D)
X=2080
def head(sz,w=430): 
    f=ImageFont.truetype(g.F_HEAD,sz); f.set_variation_by_axes([min(144,max(9,sz*0.9*0.5)),w,100,0]); return f
fH=g.head_font(160,430)
l1,l2='Hier mag je zijn','wie je bent'
print(dr.textlength(l1,font=fH),dr.textlength(l2,font=fH))
sz=160
while dr.textlength(l1,font=g.head_font(sz,430))>1000: sz-=4
fH=g.head_font(sz,430); print(sz)
dr.text((X,500),l1,font=fH,fill=INK); dr.text((X,680),l2,font=fH,fill=INK)
fh=g.hand_font(80)
dr.text((X+4,904),'in je pak, je tutu of je masker',font=fh,fill=TD)
fB=ImageFont.truetype(g.F_BODY,44)
for i,l in enumerate(['Coaching, ademwerk en een groep','in Rotterdam. Je hoeft het niet','alleen te doen. Alles mag er zijn.']):
    dr.text((X+2,1040+i*68),l,font=fB,fill=INK)
bx0,by0,bx1,by1=X,1320,X+540,1444
im=g.cuts_on(im,[(g.organic_box(bx0,by0,bx1,by1,seed=5,amp=5,sides='ltrb'),g.TEAL_D,1.0,None)],seed=2)
dr=ImageDraw.Draw(im); fBt=ImageFont.truetype(g.F_BODY_B,42)
dr.text(((bx0+bx1)/2,(by0+by1)/2),'Meld je aan',font=fBt,fill=g.rgb(g.CREAM),anchor='mm')
dr.text((X+590,1356),'Lees meer',font=fBt,fill=INK)
im,_=g.lines_on(im,g.underline(X+590,X+590+fBt.getlength('Lees meer'),1424,g.TERRA,8,seed=7)+g.underline(X+8,X+8+dr.textlength(l2,font=fH),880,g.TEAL,14,seed=4)),None
im=im.convert('RGB'); im.save('/workspace/gestalt-nu/test/poppetjes-sectie-gespiegeld-v29s.png')
h=Image.open('/workspace/gestalt-nu/test/test-cirkel-vanaf-logo.png').convert('RGB')
pg=Image.new('RGB',(3200,3600)); pg.paste(h,(0,0)); pg.paste(im,(0,1800))
pg.save('/workspace/gestalt-nu/test/website-voorpagina-met-poppetjes-v29s.png')
pg.resize((1200,1350),Image.LANCZOS).save('/workspace/gestalt-nu/test/website-voorpagina-met-poppetjes-v29s-voorbeeld.jpg',quality=92)
