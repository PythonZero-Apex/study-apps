# -*- coding: utf-8 -*-
# SC-900 アプリアイコン生成（盾＋チェック + SC-900）
from PIL import Image, ImageDraw, ImageFont

S = 512
img = Image.new("RGBA",(S,S),(0,0,0,0))
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
top=(23,13,16); bot=(46,18,26)   # dark crimson
bg=Image.new("RGB",(S,S)); bd=ImageDraw.Draw(bg)
for y in range(S): bd.line([(0,y),(S,y)],fill=lerp(top,bot,y/S))
radius=112
mask=Image.new("L",(S,S),0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,S-1,S-1],radius=radius,fill=255)
img.paste(bg,(0,0),mask)
d=ImageDraw.Draw(img,"RGBA")
d.rounded_rectangle([6,6,S-7,S-7],radius=radius-6,outline=(230,120,90,90),width=3)

# --- 盾（shield）形 ---
cx=S//2; topY=118; w=150; h=210
# 盾のポリゴン（上が平ら、下がとがる）
shield=[
 (cx-w, topY+8),
 (cx-w, topY+90),
 (cx,   topY+h),
 (cx+w, topY+90),
 (cx+w, topY+8),
 (cx,   topY-14),
]
# グラデーション塗り（crimson→amber を縦方向に）：レイヤーを作ってマスク
shimg=Image.new("RGBA",(S,S),(0,0,0,0))
sd=ImageDraw.Draw(shimg)
for yy in range(topY-16, topY+h+2):
    t=(yy-(topY-16))/(h+18)
    col=lerp((225,29,72),(245,158,11),t)
    sd.line([(cx-w-4,yy),(cx+w+4,yy)],fill=col+(255,))
smask=Image.new("L",(S,S),0)
ImageDraw.Draw(smask).polygon(shield,fill=255)
img.paste(shimg,(0,0),smask)
d=ImageDraw.Draw(img,"RGBA")
# 盾の縁
d.polygon(shield,outline=(255,225,200,230))
# 内側の影で立体感
d.line([(cx,topY-14),(cx,topY+h)],fill=(255,255,255,40),width=2)

# --- チェックマーク（白） ---
d.line([(cx-58,topY+96),(cx-14,topY+140)],fill=(255,255,255,255),width=20,joint="curve")
d.line([(cx-14,topY+140),(cx+66,topY+50)],fill=(255,255,255,255),width=20,joint="curve")

# --- テキスト "SC-900" ---
def load_font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(p,size)
        except: pass
    return ImageFont.load_default()
f=load_font(118)
txt="SC-900"
bb=d.textbbox((0,0),txt,font=f); tw=bb[2]-bb[0]
ty=int(S*0.71)
d.text(((S-tw)/2-bb[0]+3,ty+3),txt,font=f,fill=(0,0,0,120))
d.text(((S-tw)/2-bb[0],ty),txt,font=f,fill=(246,233,236,255))

img.save("sc900_icon.png")
print("saved sc900_icon.png",img.size)
