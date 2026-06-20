# -*- coding: utf-8 -*-
# PL-900 アプリアイコン生成（Power Platform風の4タイル・エンブレム + PL-900）
from PIL import Image, ImageDraw, ImageFont
import math

S = 512
img = Image.new("RGBA", (S, S), (0,0,0,0))
d = ImageDraw.Draw(img)

# --- 角丸の背景（縦方向グラデーション: ダークネイビー→パープル） ---
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
top = (16,18,32)      # #101220
bot = (40,22,64)      # #281640 紫寄り
bg = Image.new("RGB",(S,S))
bd = ImageDraw.Draw(bg)
for y in range(S):
    bd.line([(0,y),(S,y)], fill=lerp(top,bot,y/S))
# 角丸マスク
radius = 112
mask = Image.new("L",(S,S),0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,S-1,S-1], radius=radius, fill=255)
img.paste(bg,(0,0),mask)
d = ImageDraw.Draw(img)

# 内側のうっすらした枠線
d.rounded_rectangle([6,6,S-7,S-7], radius=radius-6, outline=(120,110,180,90), width=3)

# --- 4タイルのエンブレム（45度回転したダイヤ配置） ---
# Power Platform の各サービス色に寄せた配色
colors = [
    (162, 92, 246),  # 紫  (Power Apps系)
    (217, 70, 166),  # マゼンタ (アクセント)
    (79, 140, 255),  # 青  (Power Automate系)
    (45, 196, 170),  # ティール (Power Pages系)
]
cx, cy = S//2, int(S*0.42)
tile = 116      # タイル一辺
gap = 20
r = 26          # タイル角丸
# 2x2 を 45度回転させた見た目にするため、菱形配置
positions = [
    (cx, cy - (tile/2+gap/2)),   # 上
    (cx + (tile/2+gap/2), cy),   # 右
    (cx, cy + (tile/2+gap/2)),   # 下
    (cx - (tile/2+gap/2), cy),   # 左
]
# タイルを回転描画するため、各タイルを別レイヤーで作って45度回転
for (px,py),col in zip(positions, colors):
    layer = Image.new("RGBA",(tile,tile),(0,0,0,0))
    ld = ImageDraw.Draw(layer)
    # 軽いグラデーション風（上明るめ）
    ld.rounded_rectangle([0,0,tile-1,tile-1], radius=r, fill=col+(255,))
    hi = tuple(min(255,c+40) for c in col)
    ld.rounded_rectangle([0,0,tile-1,int(tile*0.5)], radius=r, fill=hi+(70,))
    layer = layer.rotate(45, expand=True, resample=Image.BICUBIC)
    lw,lh = layer.size
    img.alpha_composite(layer, (int(px-lw/2), int(py-lh/2)))

# 中央の小さな白い菱形（まとまり感）
center = Image.new("RGBA",(46,46),(0,0,0,0))
ImageDraw.Draw(center).rounded_rectangle([0,0,45,45], radius=12, fill=(255,255,255,235))
center = center.rotate(45, expand=True, resample=Image.BICUBIC)
cw,ch = center.size
img.alpha_composite(center,(int(cx-cw/2),int(cy-ch/2)))

# --- テキスト "PL-900" ---
def load_font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

f_big = load_font(126)
txt = "PL-900"
bbox = d.textbbox((0,0), txt, font=f_big)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
ty = int(S*0.70)
# 影
d.text(((S-tw)/2 - bbox[0]+3, ty+3), txt, font=f_big, fill=(0,0,0,120))
d.text(((S-tw)/2 - bbox[0], ty), txt, font=f_big, fill=(245,243,255,255))

img.save("pl900_icon.png")
# 念のため小サイズも確認用に
img.resize((180,180), Image.LANCZOS).save("pl900_icon_preview.png")
print("saved pl900_icon.png", img.size)
