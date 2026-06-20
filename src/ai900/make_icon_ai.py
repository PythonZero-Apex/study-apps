# -*- coding: utf-8 -*-
# AI-900 アプリアイコン生成（ニューラルネットワーク + AI-900）
from PIL import Image, ImageDraw, ImageFont
import math

S = 512
img = Image.new("RGBA",(S,S),(0,0,0,0))

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
top=(13,15,31); bot=(23,18,57)   # indigo dark
bg=Image.new("RGB",(S,S)); bd=ImageDraw.Draw(bg)
for y in range(S): bd.line([(0,y),(S,y)],fill=lerp(top,bot,y/S))
radius=112
mask=Image.new("L",(S,S),0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,S-1,S-1],radius=radius,fill=255)
img.paste(bg,(0,0),mask)
d=ImageDraw.Draw(img,"RGBA")
d.rounded_rectangle([6,6,S-7,S-7],radius=radius-6,outline=(110,110,230,90),width=3)

INDIGO=(99,102,241); CYAN=(34,211,238)
def col_at(t): return lerp(INDIGO,CYAN,t)

# ニューラルネット: 3層 (3-4-3 ノード)
cx0=150; cx2=362; cx1=256
top_y=150; bot_y=320
def layer_nodes(x,n):
    ys=[top_y+(bot_y-top_y)*i/(n-1) for i in range(n)] if n>1 else [(top_y+bot_y)/2]
    return [(x,y) for y in ys]
L0=layer_nodes(cx0,3)
L1=layer_nodes(cx1,4)
L2=layer_nodes(cx2,3)

# 接続線（半透明）
def connect(A,B,t):
    c=col_at(t)
    for (ax,ay) in A:
        for (bx,by) in B:
            d.line([(ax,ay),(bx,by)],fill=c+(70,),width=2)
connect(L0,L1,0.3)
connect(L1,L2,0.7)

# ノード（グラデーション円＋外周グロー）
def node(x,y,t,r=15):
    c=col_at(t)
    d.ellipse([x-r-6,y-r-6,x+r+6,y+r+6],fill=c+(45,))     # glow
    d.ellipse([x-r,y-r,x+r,y+r],fill=c+(255,))
    d.ellipse([x-r,y-r,x+r,y+int(r*0.2)],fill=(255,255,255,60))
for p in L0: node(*p,0.15)
for p in L1: node(*p,0.5)
for p in L2: node(*p,0.85)

# テキスト "AI-900"
def load_font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(p,size)
        except: pass
    return ImageFont.load_default()
f=load_font(122)
txt="AI-900"
bb=d.textbbox((0,0),txt,font=f); tw=bb[2]-bb[0]
ty=int(S*0.70)
d.text(((S-tw)/2-bb[0]+3,ty+3),txt,font=f,fill=(0,0,0,120))
d.text(((S-tw)/2-bb[0],ty),txt,font=f,fill=(236,234,252,255))

img.save("ai900_icon.png")
print("saved ai900_icon.png",img.size)
