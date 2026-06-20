# -*- coding: utf-8 -*-
import json, sys, re, difflib
from sa import SA
from sb import SB
from sc import SC
from sd import SD

SUBS = {
 "SCIの概念":["セキュリティとコンプライアンスの概念","IDの概念"],
 "Microsoft Entraの機能":["Entra IDの機能とID種別","認証機能","アクセス管理機能","ID保護とガバナンス"],
 "Microsoftセキュリティソリューション":["Azureの中核インフラセキュリティ","Azureのセキュリティ管理","Microsoft Sentinel","Microsoft Defender XDR"],
 "Microsoftコンプライアンスソリューション":["Service Trust Portalとプライバシー","Purviewのコンプライアンス管理","情報保護とデータライフサイクル","インサイダーリスク・eDiscovery・監査"],
}

raw = SA + SB + SC + SD
errors = []; out = []
for i, q in enumerate(raw, start=1):
    qq = dict(q); qq["id"] = i
    if qq["area"] not in SUBS: errors.append(f"id{i}: area不正 {qq['area']}")
    elif qq["sub"] not in SUBS[qq["area"]]: errors.append(f"id{i}: sub不正 {qq['sub']} ({qq['area']})")
    opts = qq["options"]
    if len(set(opts)) != len(opts): errors.append(f"id{i}: 選択肢重複 {opts}")
    ans = []
    for c in qq["correct"]:
        if c not in opts: errors.append(f"id{i}: correct不在 '{c}' / {opts}")
        else: ans.append(opts.index(c))
    ans.sort(); qq["answer"] = ans
    if qq["type"]=="single" and len(ans)!=1: errors.append(f"id{i}: single正解{len(ans)}")
    if qq["type"]=="multi" and len(ans)<2: errors.append(f"id{i}: multi正解{len(ans)}")
    del qq["correct"]; out.append(qq)

def norm(t): return re.sub(r"\s+","",t)
seen={}
for q in out:
    n=norm(q["q"])
    if n in seen: errors.append(f"id{q['id']}: 完全重複 with id{seen[n]}")
    seen[n]=q["id"]
texts=[(q["id"],q["q"]) for q in out]
for a in range(len(texts)):
    for b in range(a+1,len(texts)):
        r=difflib.SequenceMatcher(None,texts[a][1],texts[b][1]).ratio()
        if r>0.90: errors.append(f"類似{r:.2f}: id{texts[a][0]}~id{texts[b][0]}")

from collections import Counter
area_ct=Counter(q["area"] for q in out); sub_ct=Counter(q["sub"] for q in out)
print("=== 集計 ===\n総問題数:",len(out))
for area,subs in SUBS.items():
    print(f"[{area}] = {area_ct[area]}問")
    for s in subs: print(f"    - {s}: {sub_ct[s]}問")
print("複数選択問題:",sum(1 for q in out if q["type"]=="multi"))
print("\n=== 検証 ===")
if errors:
    print("NG:",len(errors)); [print("  -",e) for e in errors]; sys.exit(1)
print("OK: エラーなし")
with open("sc_template.html",encoding="utf-8") as f: tpl=f.read()
html=tpl.replace("__QUESTIONS__",json.dumps(out,ensure_ascii=False))
with open("index.html","w",encoding="utf-8") as f: f.write(html)
print("\nindex.html サイズ:",len(html))
