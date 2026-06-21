# -*- coding: utf-8 -*-
import json, sys, re, difflib
from qa import QA
from qb import QB
from qc import QC

SUBS = {
 "クラウドの概念":["クラウドコンピューティング","クラウドサービスの利点","クラウドサービスの種類"],
 "Azureのアーキテクチャとサービス":["コアアーキテクチャコンポーネント","コンピューティングとネットワーク","ストレージ","ID・アクセス・セキュリティ"],
 "Azureの管理とガバナンス":["コスト管理","ガバナンスとコンプライアンス","リソースの管理とデプロイ","監視ツール"],
}
VALID_SUBS = {s for subs in SUBS.values() for s in subs}

raw = QA + QB + QC
errors = []
out = []
for i, q in enumerate(raw, start=1):
    qq = dict(q)
    qq["id"] = i
    # validate area/sub
    if qq["area"] not in SUBS:
        errors.append(f"id{i}: area不正 {qq['area']}")
    elif qq["sub"] not in SUBS[qq["area"]]:
        errors.append(f"id{i}: sub不正 {qq['sub']} (area {qq['area']})")
    # build answer indices from 'correct' option texts
    opts = qq["options"]
    if len(set(opts)) != len(opts):
        errors.append(f"id{i}: 選択肢に重複テキスト {opts}")
    ans = []
    for c in qq["correct"]:
        if c not in opts:
            errors.append(f"id{i}: correctが選択肢にない {c}")
        else:
            ans.append(opts.index(c))
    ans.sort()
    qq["answer"] = ans
    # multi/single consistency
    if qq["type"] == "single" and len(ans) != 1:
        errors.append(f"id{i}: singleなのに正解{len(ans)}個")
    if qq["type"] == "multi" and len(ans) < 2:
        errors.append(f"id{i}: multiなのに正解{len(ans)}個")
    # answer must NOT be trivially all index0 across the bank (check later)
    del qq["correct"]
    out.append(qq)

# duplicate / near-duplicate question detection
def norm(t):
    return re.sub(r"\s+","", t)
seen = {}
for q in out:
    n = norm(q["q"])
    if n in seen:
        errors.append(f"id{q['id']}: 完全重複 with id{seen[n]}")
    seen[n] = q["id"]

# near-duplicate (ratio>0.92)
texts = [(q["id"], q["q"]) for q in out]
for a in range(len(texts)):
    for b in range(a+1, len(texts)):
        r = difflib.SequenceMatcher(None, texts[a][1], texts[b][1]).ratio()
        if r > 0.90:
            errors.append(f"類似度{r:.2f}: id{texts[a][0]} ~ id{texts[b][0]}")

# distribution report
from collections import Counter, OrderedDict
area_ct = Counter(q["area"] for q in out)
sub_ct = Counter(q["sub"] for q in out)
ans0 = sum(1 for q in out if q["answer"]==[0])

print("=== 集計 ===")
print("総問題数:", len(out))
for area, subs in SUBS.items():
    print(f"[{area}] = {area_ct[area]}問")
    for s in subs:
        print(f"    - {s}: {sub_ct[s]}問")
print("answer==[0] の数(=データ上1番目が正解):", ans0, "（実行時シャッフルで表示順はランダム化）")
mult = sum(1 for q in out if q["type"]=="multi")
print("複数選択問題:", mult)

print("\n=== 検証 ===")
if errors:
    print("NG:", len(errors), "件")
    for e in errors:
        print("  -", e)
    sys.exit(1)
else:
    print("OK: エラーなし")

# inject into template
with open("template.html", encoding="utf-8") as f:
    tpl = f.read()
qjson = json.dumps(out, ensure_ascii=False)
html = tpl.replace("__QUESTIONS__", qjson)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\nindex.html を書き出しました。サイズ:", len(html), "bytes")

# ---- 問題バンクJSONも書き出す（verify/Obsidian用） ----
meta = {
    "exam":"AZ-900","title":"Azure Fundamentals 問題バンク","version":"2026-06-az900a",
    "source":"Microsoft Learn 公式出題範囲(Skills measured 2026-01-14版)＋公式Practice Assessment実測(50問)に基づく独自作成。選択肢は実在Azureサービスで構成し消去法が効きにくい本番難度。Microsoft Entra ID等の最新名称に対応。",
    "passing":"700/1000相当（このバンクでは正答率70%を目安）",
    "count":len(out),"multi_select":mult,"categories":list(SUBS.keys()),
    "category_counts":{a:area_ct[a] for a in SUBS},
    "live_app":"https://pythonzero-apex.github.io/study-apps/az900/",
}
with open("az-900-questions.json","w",encoding="utf-8") as f:
    json.dump({"meta":meta,"questions":out}, f, ensure_ascii=False, indent=1)
print("az-900-questions.json を書き出しました。問題数:", len(out), " 複数選択:", mult)
