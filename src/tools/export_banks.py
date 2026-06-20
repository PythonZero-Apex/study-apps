# -*- coding: utf-8 -*-
"""
全5資格の問題バンクを {meta, questions[]} 形式のJSONとして書き出す。
リポジトリ構成（src/ 配下に資格ごとのフォルダ）を前提に、相対パスで動作する。

使い方:
    cd src/tools
    python3 export_banks.py
  -> src/tools/dist/<cert>-questions.json を生成
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))   # src/tools
SRC  = os.path.dirname(HERE)                          # src
VER  = "2026-06-20a"
SRCNOTE = "Microsoft Learn 公式出題範囲に基づく独自作成（本番難度・選択肢ランダム化対応）"

# 各資格: (フォルダ, 表示名, タイトル, [(モジュール名, 変数名), ...])
CERTS = {
 "ai-900": ("ai900","AI-900","Azure AI Fundamentals 問題バンク",
            [("aa","AA"),("ab","AB"),("ac","AC"),("ad","AD"),("ae","AE")]),
 "az-900": ("az900","AZ-900","Azure Fundamentals 問題バンク",
            [("qa","QA"),("qb","QB"),("qc","QC")]),
 "pl-900": ("pl900","PL-900","Power Platform Fundamentals 問題バンク",
            [("pa","PA"),("pb","PB"),("pc","PC"),("pd","PD"),("pe","PE")]),
 "dp-900": ("dp900","DP-900","Azure Data Fundamentals 問題バンク",
            [("da","DA"),("db","DB"),("dc","DC"),("dd","DD")]),
 "sc-900": ("sc900","SC-900","Security, Compliance, and Identity Fundamentals 問題バンク",
            [("sa","SA"),("sb","SB"),("sc","SC"),("sd","SD")]),
}

def load_modules(folder, mods):
    d = os.path.join(SRC, folder)
    if d not in sys.path:
        sys.path.insert(0, d)
    out = []
    import importlib
    for name, var in mods:
        m = importlib.import_module(name)
        out.append(getattr(m, var))
    return out

def build(modlists):
    out=[]; i=0
    for lst in modlists:
        for q in lst:
            i+=1
            out.append({
                "id": i, "domain": q["area"], "sub": q["sub"], "type": q["type"],
                "q": q["q"], "options": q["options"],
                "answer": sorted(q["options"].index(c) for c in q["correct"]),
                "explanation": q["explanation"],
            })
    return out

def main():
    dist = os.path.join(HERE, "dist"); os.makedirs(dist, exist_ok=True)
    for key,(folder,exam,title,mods) in CERTS.items():
        qs = build(load_modules(folder, mods))
        multi = sum(1 for q in qs if q["type"]=="multi")
        doc = {"meta":{
            "exam":exam,"title":title,"version":VER,"source":SRCNOTE,
            "passing":"700/1000相当（このバンクでは正答率70%を目安）",
            "count":len(qs),"multi_select":multi,
            "live_app":f"https://pythonzero-apex.github.io/study-apps/{folder}/",
        },"questions":qs}
        with open(os.path.join(dist,f"{key}-questions.json"),"w",encoding="utf-8") as f:
            json.dump(doc,f,ensure_ascii=False,indent=1)
        print(f"{key}: {len(qs)}問 (multi {multi})")
    print("dist/ に書き出し完了")

if __name__ == "__main__":
    main()
