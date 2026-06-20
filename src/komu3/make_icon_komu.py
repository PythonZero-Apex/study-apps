# -*- coding: utf-8 -*-
"""公害大気3種アプリ用アイコン生成。出力: icon_komu.png (512x512)
依存: pillow  (pip install pillow --break-system-packages)
"""
from PIL import Image, ImageDraw, ImageFont
import os

S = 512
img = Image.new("RGB", (S, S), "#1f7a4d")
d = ImageDraw.Draw(img)

# 背景グラデーション（緑→濃緑）
for y in range(S):
    t = y / S
    r = int(0x2e + (0x16 - 0x2e) * t)
    g = int(0x9e + (0x5f - 0x9e) * t)
    b = int(0x66 + (0x3a - 0x66) * t)
    d.line([(0, y), (S, y)], fill=(r, g, b))

# 空（上部を淡く）
d.ellipse([S*0.62, S*0.12, S*0.84, S*0.34], fill=(255, 255, 255, 0), outline=None)
d.ellipse([int(S*0.66), int(S*0.14), int(S*0.82), int(S*0.30)], fill="#eaf6ef")  # お日さま風

# 工場（煙突2本＋建屋）白で
white = "#ffffff"
# 建屋
d.rectangle([S*0.18, S*0.60, S*0.82, S*0.80], fill=white)
# 屋根のギザギザ（ノコギリ屋根）
import math
xs = S*0.18
step = (S*0.82 - S*0.18) / 5
for i in range(5):
    x0 = xs + i*step
    d.polygon([(x0, S*0.60), (x0+step, S*0.60), (x0+step, S*0.55)], fill=white)
# 煙突
d.rectangle([S*0.30, S*0.40, S*0.40, S*0.60], fill=white)
d.rectangle([S*0.55, S*0.34, S*0.65, S*0.60], fill=white)
# 煙突の帯
d.rectangle([S*0.30, S*0.42, S*0.40, S*0.45], fill="#1f7a4d")
d.rectangle([S*0.55, S*0.36, S*0.65, S*0.39], fill="#1f7a4d")
# 煙（淡い円）
for (cx, cy, r) in [(0.355, 0.34, 0.045), (0.40, 0.30, 0.055), (0.60, 0.28, 0.05), (0.65, 0.23, 0.06)]:
    d.ellipse([S*(cx-r), S*(cy-r), S*(cx+r), S*(cy+r)], fill="#cfe9da")

# 下部ラベル帯
d.rectangle([0, int(S*0.80), S, S], fill="#15633d")

# テキスト「大気3種」
def font(sz):
    for p in ["/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
              "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

f = font(96)
txt = "大気3種"
try:
    bb = d.textbbox((0, 0), txt, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((S-tw)/2 - bb[0], S*0.80 + (S*0.20-th)/2 - bb[1]), txt, font=f, fill="#ffffff")
except Exception:
    d.text((S*0.2, S*0.85), txt, fill="#ffffff")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon_komu.png")
img.save(out)
print("saved:", out)
