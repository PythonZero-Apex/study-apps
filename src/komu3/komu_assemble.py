# -*- coding: utf-8 -*-
"""公害防止管理者 大気関係第3種 — ビルドスクリプト
ka..ke.py(各30問)を読み込み→検証→正解テキストをインデックスへ変換→
index.html(テンプレートにデータ埋め込み)と問題バンクJSONを生成する。

使い方:  cd src/komu3 && python3 komu_assemble.py
出力:    ./index.html  ./komu-3-air-questions.json
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ka, kb, kc, kd, ke  # noqa: E402

MODULES = [ka, kb, kc, kd, ke]
CATEGORIES = ["公害総論", "大気概論", "大気特論", "ばいじん・粉じん特論", "大規模大気特論"]

VERSION = "2026-06-21a"


def build():
    questions = []
    errors = []
    qid = 0
    for mod in MODULES:
        for q in mod.QUESTIONS:
            qid += 1
            ctx = f"[{mod.AREA} #{qid}] {q.get('q','')[:30]}"
            opts = q.get("options", [])
            # --- 検証 ---
            if len(opts) != 5:
                errors.append(f"{ctx}: 選択肢が5個でない({len(opts)})")
            if len(set(opts)) != len(opts):
                errors.append(f"{ctx}: 選択肢に重複あり")
            qtype = q.get("type")
            if qtype not in ("single", "multi"):
                errors.append(f"{ctx}: type不正({qtype})")
            corr = q.get("correct", [])
            if not corr:
                errors.append(f"{ctx}: 正解が空")
            for c in corr:
                if c not in opts:
                    errors.append(f"{ctx}: 正解テキストが選択肢に無い: {c}")
            if qtype == "single" and len(corr) != 1:
                errors.append(f"{ctx}: single なのに正解数={len(corr)}")
            if qtype == "multi" and len(corr) < 2:
                errors.append(f"{ctx}: multi なのに正解数={len(corr)}")
            if not q.get("explanation"):
                errors.append(f"{ctx}: 解説が空")
            # --- 変換 ---
            answer = sorted(opts.index(c) for c in corr if c in opts)
            questions.append({
                "id": qid,
                "domain": q["area"],
                "sub": q.get("sub", ""),
                "type": qtype,
                "q": q["q"],
                "options": opts,
                "answer": answer,
                "explanation": q["explanation"],
            })

    if errors:
        print("‼ 検証エラー:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)

    multi = sum(1 for q in questions if q["type"] == "multi")
    by_cat = {c: sum(1 for q in questions if q["domain"] == c) for c in CATEGORIES}

    meta = {
        "exam": "公害防止管理者 大気関係第3種",
        "title": "公害防止管理者(大気3種) 問題バンク",
        "version": VERSION,
        "source": "公式出題範囲(産業環境管理協会)に基づく独自作成。公式・民間の過去問傾向を参照した本番難度・5肢択一・選択肢ランダム化・複数選択対応・詳細解説。",
        "format": "5肢択一(single/multi)。本番は各科目6割で合格。",
        "passing": "正答率60%目安",
        "count": len(questions),
        "multi_select": multi,
        "categories": CATEGORIES,
        "category_counts": by_cat,
        "live_app": "https://pythonzero-apex.github.io/study-apps/komu3/",
    }

    bank = {"meta": meta, "questions": questions}

    # JSON バンク出力(Obsidian / 検証用)
    bank_path = os.path.join(HERE, "komu-3-air-questions.json")
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)

    # index.html 生成
    tpl_path = os.path.join(HERE, "komu_template.html")
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()
    data_js = json.dumps(bank, ensure_ascii=False)
    out = re.sub(
        r"/\*__DATA__\*/.*?/\*__END__\*/",
        "/*__DATA__*/" + data_js.replace("\\", "\\\\") + "/*__END__*/",
        tpl, count=1, flags=re.S,
    )
    html_path = os.path.join(HERE, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(out)

    print("✅ ビルド完了")
    print(f"   問題数: {len(questions)}  (複数選択 {multi}問)")
    for c in CATEGORIES:
        print(f"     - {c}: {by_cat[c]}問")
    print(f"   出力: {html_path}")
    print(f"        {bank_path}")
    return bank


if __name__ == "__main__":
    build()
