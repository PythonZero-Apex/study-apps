# -*- coding: utf-8 -*-
import json, sys, re, difflib
from pa import PA
from pb import PB
from pc import PC
from pd import PD
from pe import PE

SUBS = {
 "Power Platformのビジネス価値":["サービスのビジネス価値","ソリューション拡張のビジネス価値"],
 "環境の管理":["Microsoft Dataverse","管理とガバナンス"],
 "Power Appsの機能":["Power Apps機能の識別","キャンバスアプリの構築","モデル駆動型アプリの構築"],
 "Power Automateの機能":["Power Automateコンポーネントの識別","フローの構築"],
 "Power Pagesの機能":["Power Pagesの機能","Power Pagesサイトの作成"],
}

raw = PA + PB + PC + PD + PE
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
            errors.append(f"類似度{r:.2f}: id{texts[a][0]} ~ id{texts[b][0]} / '{texts[a][1][:30]}' ~ '{texts[b][1][:30]}'")

from collections import Counter
area_ct = Counter(q["area"] for q in out)
sub_ct = Counter(q["sub"] for q in out)

print("=== 集計 ===")
print("総問題数:", len(out))
for area, subs in SUBS.items():
    print(f"[{area}] = {area_ct[area]}問")
    for s in subs:
        print(f"    - {s}: {sub_ct[s]}問")
mult = sum(1 for q in out if q["type"]=="multi")
print("複数選択問題:", mult)

print("\n=== 検証 ===")
if errors:
    print("NG:", len(errors), "件")
    for e in errors: print("  -", e)
    sys.exit(1)
print("OK: エラーなし")

with open("pl_template.html", encoding="utf-8") as f:
    tpl = f.read()
html = tpl.replace("__QUESTIONS__", json.dumps(out, ensure_ascii=False))
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\nindex.html を書き出しました。サイズ:", len(html), "bytes")

# ---- 問題バンクJSONも書き出す（verify/Obsidianスナップショット用） ----
meta = {
    "exam": "PL-900",
    "title": "Power Platform Fundamentals 問題バンク",
    "version": "2026-06-21-pl900a",
    "source": "Microsoft Learn 公式出題範囲(Skills measured 2025-06-20版)＋公式Practice Assessment実測(50問)に基づく独自作成。選択肢は実在の兄弟サービス/近接概念で構成し消去法が効きにくい本番難度。詳細解説付き。",
    "passing": "700/1000相当（このバンクでは正答率70%を目安）",
    "naming": "Copilot Studio(旧Power Virtual Agents)、Power PlatformのCopilot機能、プロセスマイニング等の最新要素に対応。Power BI/AI Builderは出題範囲外のため誤答選択肢としてのみ使用。",
    "count": len(out),
    "multi_select": mult,
    "categories": list(SUBS.keys()),
    "category_counts": {a: area_ct[a] for a in SUBS},
    "live_app": "https://pythonzero-apex.github.io/study-apps/pl900/",
}
bank = {"meta": meta, "questions": out}
with open("pl-900-questions.json", "w", encoding="utf-8") as f:
    json.dump(bank, f, ensure_ascii=False, indent=1)
print("pl-900-questions.json を書き出しました。問題数:", len(out), " 複数選択:", mult)
