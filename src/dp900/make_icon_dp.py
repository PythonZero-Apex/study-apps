# -*- coding: utf-8 -*-
# DP-900 アプリアイコン生成（データベース・シリンダー + DP-900）
from PIL import Image, ImageDraw, ImageFont

S = 512
img = Image.new("RGBA", (S, S), (0,0,0,0))

# --- 角丸の背景（縦グラデ: ダークティール→ダークブルー） ---
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
top = (11,23,25)     # #0b1719
bot = (14,34,42)     # #0e222a
bg = Image.new("RGB",(S,S))
bd = ImageDraw.Draw(bg)
for y in range(S):
    bd.line([(0,y),(S,y)], fill=lerp(top,bot,y/S))
radius = 112
mask = Image.new("L",(S,S),0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,S-1,S-1], radius=radius, fill=255)
img.paste(bg,(0,0),mask)
d = ImageDraw.Draw(img)
d.rounded_rectangle([6,6,S-7,S-7], radius=radius-6, outline=(40,120,130,90), width=3)

# --- データベース・シリンダー（3段ディスク） ---
cx = S//2
cyl_w = 230
cyl_x0 = cx - cyl_w//2
cyl_x1 = cx + cyl_w//2
ell_h = 54           # 楕円の高さ
top_y = 120          # 一番上の楕円中心
seg = 78             # 各段の高さ
# 段ごとのティール→シアン→青のグラデ色
seg_colors = [
    (20, 184, 166),  # teal
    (14, 165, 233),  # cyan-blue
    (37, 99, 235),   # blue
]
def disc(cy, col, top_face=True):
    # 円柱の側面（上の楕円中心cyから下にseg）
    body_top = cy
    body_bot = cy + seg
    # 側面
    d.rectangle([cyl_x0, body_top, cyl_x1, body_bot], fill=col+(255,))
    # 下の楕円（底）
    d.ellipse([cyl_x0, body_bot-ell_h//2, cyl_x1, body_bot+ell_h//2], fill=col+(255,))
    # 上の楕円（面）明るめ
    if top_face:
        hi = tuple(min(255,c+45) for c in col)
        d.ellipse([cyl_x0, body_top-ell_h//2, cyl_x1, body_top+ell_h//2], fill=hi+(255,))

# 下から描く（重なり順）
disc(top_y + seg*2, seg_colors[2], top_face=False)
disc(top_y + seg*1, seg_colors[1], top_face=False)
disc(top_y + seg*0, seg_colors[0], top_face=True)
# 各段の区切り楕円（うっすら）
for k in range(1,3):
    yy = top_y + seg*k
    d.ellipse([cyl_x0, yy-ell_h//2, cyl_x1, yy+ell_h//2], outline=(255,255,255,60), width=2)
# 一番上の面のハイライト輪郭
d.ellipse([cyl_x0, top_y-ell_h//2, cyl_x1, top_y+ell_h//2], outline=(255,255,255,140), width=2)

# --- テキスト "DP-900" ---
def load_font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

f_big = load_font(118)
txt = "DP-900"
bbox = d.textbbox((0,0), txt, font=f_big)
tw = bbox[2]-bbox[0]
ty = int(S*0.74)
d.text(((S-tw)/2 - bbox[0]+3, ty+3), txt, font=f_big, fill=(0,0,0,120))
d.text(((S-tw)/2 - bbox[0], ty), txt, font=f_big, fill=(233,243,242,255))

img.save("dp900_icon.png")
print("saved dp900_icon.png", img.size)
