# -*- coding: utf-8 -*-
"""AI-900 Azure AI Fundamentals — ビルドスクリプト
aa..ae.py(5分野・計120問)を読み込み→検証→正解テキストをインデックスへ変換→
index.html(テンプレートにデータ埋め込み)と問題バンクJSONを生成する。

特徴: Azure AI Foundry系の最新サービス名称に対応。選択肢は実在サービスで構成し
消去法が効きにくい本番難度。単一選択(4択)＋複数選択を含む。

使い方:  cd src/ai900 && python3 ai_assemble.py
出力:    ./index.html  ./ai-900-questions.json
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aa, ab, ac, ad, ae  # noqa: E402

MODULES = [aa, ab, ac, ad, ae]
CATEGORIES = [
    "AIワークロードと考慮事項",
    "機械学習の基本原則",
    "コンピュータービジョン",
    "自然言語処理（NLP）",
    "生成AI",
]
VERSION = "2026-06-21a"


def build():
    questions, errors, qid = [], [], 0
    for mod in MODULES:
        for q in mod.QUESTIONS:
            qid += 1
            ctx = f"[{mod.AREA} #{qid}] {q.get('q','')[:28]}"
            opts = q.get("options", [])
            if len(opts) < 4:
                errors.append(f"{ctx}: 選択肢が4未満({len(opts)})")
            if len(set(opts)) != len(opts):
                errors.append(f"{ctx}: 選択肢に重複")
            qtype = q.get("type")
            if qtype not in ("single", "multi"):
                errors.append(f"{ctx}: type不正({qtype})")
            corr = q.get("correct", [])
            if not corr:
                errors.append(f"{ctx}: 正解が空")
            for c in corr:
                if c not in opts:
                    errors.append(f"{ctx}: 正解が選択肢に無い: {c}")
            if qtype == "single" and len(corr) != 1:
                errors.append(f"{ctx}: single の正解数={len(corr)}")
            if qtype == "multi" and len(corr) < 2:
                errors.append(f"{ctx}: multi の正解数={len(corr)}")
            if len(q.get("explanation", "")) < 20:
                errors.append(f"{ctx}: 解説が短い/空")
            answer = sorted(opts.index(c) for c in corr if c in opts)
            questions.append({
                "id": qid, "domain": q["area"], "sub": q.get("sub", ""),
                "type": qtype, "q": q["q"], "options": opts,
                "answer": answer, "explanation": q["explanation"],
            })

    if errors:
        print("‼ 検証エラー:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)

    multi = sum(1 for q in questions if q["type"] == "multi")
    by_cat = {c: sum(1 for q in questions if q["domain"] == c) for c in CATEGORIES}

    meta = {
        "exam": "AI-900",
        "title": "Azure AI Fundamentals 問題バンク",
        "version": VERSION,
        "source": "Microsoft Learn 公式出題範囲(Skills measured)に基づく独自作成。Azure AI Foundry系の最新サービス名称に対応し、選択肢は実在サービスで構成（消去法が効きにくい本番難度）。詳細解説付き。",
        "passing": "700/1000相当（このバンクでは正答率70%を目安）",
        "naming": "Azure AI Foundry / Azure OpenAI in Foundry Models / Azure AI Vision・Language・Speech・Translator・Document Intelligence・Content Safety・Search 等の最新名称に統一",
        "count": len(questions),
        "multi_select": multi,
        "categories": CATEGORIES,
        "category_counts": by_cat,
        "live_app": "https://pythonzero-apex.github.io/study-apps/ai900/",
        "note": "AI-900は2026-06-30で終了→AI-901へ。内容はほぼ流用可。",
    }
    bank = {"meta": meta, "questions": questions}

    with open(os.path.join(HERE, "ai-900-questions.json"), "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)

    with open(os.path.join(HERE, "ai_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    data_js = json.dumps(bank, ensure_ascii=False)
    out = re.sub(r"/\*__DATA__\*/.*?/\*__END__\*/",
                 "/*__DATA__*/" + data_js.replace("\\", "\\\\") + "/*__END__*/",
                 tpl, count=1, flags=re.S)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)

    print("✅ ビルド完了")
    print(f"   問題数: {len(questions)}  (複数選択 {multi}問)")
    for c in CATEGORIES:
        print(f"     - {c}: {by_cat[c]}問")
    return bank


if __name__ == "__main__":
    build()
