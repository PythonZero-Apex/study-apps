# -*- coding: utf-8 -*-
import json, sys, re, difflib
from da import DA
from db import DB
from dc import DC
from dd import DD

SUBS = {
 "コアデータの概念":["データの表現方法","データストレージの選択肢","一般的なデータワークロード","役割と責任"],
 "リレーショナルデータ":["リレーショナルの概念","リレーショナル系Azureサービス"],
 "非リレーショナルデータ":["Azureストレージ","Azure Cosmos DB"],
 "分析ワークロード":["大規模分析の要素","リアルタイム分析","Power BIによる可視化"],
}

raw = DA + DB + DC + DD
errors = []
out = []
for i, q in enumerate(raw, start=1):
    qq = dict(q)
    qq["id"] = i
    if qq["area"] not in SUBS:
        errors.append(f"id{i}: area不正 {qq['area']}")
    elif qq["sub"] not in SUBS[qq["area"]]:
        errors.append(f"id{i}: sub不正 {qq['sub']} (area {qq['area']})")
    opts = qq["options"]
    if len(set(opts)) != len(opts):
        errors.append(f"id{i}: 選択肢に重複テキスト {opts}")
    ans = []
    for c in qq["correct"]:
        if c not in opts:
            errors.append(f"id{i}: correctが選択肢にない '{c}' / opts={opts}")
        else:
            ans.append(opts.index(c))
    ans.sort()
    qq["answer"] = ans
    if qq["type"] == "single" and len(ans) != 1:
        errors.append(f"id{i}: singleなのに正解{len(ans)}個")
    if qq["type"] == "multi" and len(ans) < 2:
        errors.append(f"id{i}: multiなのに正解{len(ans)}個")
    del qq["correct"]
    out.append(qq)

def norm(t): return re.sub(r"\s+","", t)
seen = {}
for q in out:
    n = norm(q["q"])
    if n in seen: errors.append(f"id{q['id']}: 完全重複 with id{seen[n]}")
    seen[n] = q["id"]

texts = [(q["id"], q["q"]) for q in out]
for a in range(len(texts)):
    for b in range(a+1, len(texts)):
        r = difflib.SequenceMatcher(None, texts[a][1], texts[b][1]).ratio()
        if r > 0.90:
            errors.append(f"類似度{r:.2f}: id{texts[a][0]} ~ id{texts[b][0]} / '{texts[a][1][:28]}' ~ '{texts[b][1][:28]}'")

from collections import Counter
area_ct = Counter(q["area"] for q in out)
sub_ct = Counter(q["sub"] for q in out)

print("=== 集計 ===")
print("総問題数:", len(out))
for area, subs in SUBS.items():
    print(f"[{area}] = {area_ct[area]}問")
    for s in subs:
        print(f"    - {s}: {sub_ct[s]}問")
print("複数選択問題:", sum(1 for q in out if q["type"]=="multi"))

print("\n=== 検証 ===")
if errors:
    print("NG:", len(errors), "件")
    for e in errors: print("  -", e)
    sys.exit(1)
print("OK: エラーなし")

with open("dp_template.html", encoding="utf-8") as f:
    tpl = f.read()
html = tpl.replace("__QUESTIONS__", json.dumps(out, ensure_ascii=False))
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\nindex.html を書き出しました。サイズ:", len(html), "bytes")
