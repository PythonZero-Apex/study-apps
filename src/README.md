# src — 練習アプリのソース一式

`study-apps` で公開している各資格の練習アプリ（`../<cert>/index.html`）を生成するためのソースコードです。
**正本はこのフォルダ**です。問題を直したいときはここを編集し、ビルドして生成物をデプロイします。

対象資格: AI-900 / AZ-900 / PL-900 / DP-900 / SC-900（各 全120問・公式カテゴリ準拠・選択肢ランダム化・複数選択あり・本番難度）

## フォルダ構成

```
src/
├── README.md            … 本ファイル
├── ai900/               … AI-900 のソース
│   ├── aa.py … ae.py    … 問題定義（ドメイン別）
│   ├── ai_assemble.py   … 検証＋index.html生成
│   ├── ai_template.html … HTML雛形（__QUESTIONS__を置換）
│   └── make_icon_ai.py  … アイコン生成（出力: ai900_icon.png）
├── az900/  (qa.py..qc.py, assemble.py, template.html)   ※アイコンは既存流用
├── pl900/  (pa.py..pe.py, pl_assemble.py, pl_template.html, make_icon.py)
├── dp900/  (da.py..dd.py, dp_assemble.py, dp_template.html, make_icon_dp.py)
├── sc900/  (sa.py..sd.py, sc_assemble.py, sc_template.html, make_icon_sc.py)
└── tools/
    ├── verify.js        … 出力index.htmlのロジック検証（ランダム化/正誤判定）
    └── export_banks.py  … 5資格分の問題バンクJSONをdist/へ書き出し
```

## 問題データの形式（各 *.py 内）
1問 = dict。`assemble` が `correct`（正解の選択肢テキスト）を `answer`（インデックス配列）へ自動変換します。
```python
{"area":"大分類","sub":"公式サブカテゴリ","type":"single",  # or "multi"
 "q":"問題文","options":["選択肢A","選択肢B","選択肢C","選択肢D"],
 "correct":["選択肢B"],          # multiは2つ以上
 "explanation":"解説"}
```

## 前提ツール
- Python 3（標準ライブラリのみで assemble は動作）
- アイコン生成のみ Pillow（`pip install pillow`）
- 検証スクリプトに Node.js（`node`）

## ビルド手順（資格ごと）
各資格フォルダに `cd` して assemble を実行すると、その場に `index.html`（問題データ埋め込み済み）が生成されます。

```bash
# 例: AI-900
cd src/ai900
python3 ai_assemble.py            # → 集計表示・重複/整合チェック・index.html生成
node ../tools/verify.js           # → 選択肢ランダム化と正誤判定をロジック検証
python3 make_icon_ai.py           # → ai900_icon.png（任意・アイコン更新時のみ）
```

| 資格 | ビルドコマンド（フォルダ内） | テンプレート |
|------|------------------------------|--------------|
| AI-900 | `python3 ai_assemble.py` | ai_template.html |
| AZ-900 | `python3 assemble.py`    | template.html |
| PL-900 | `python3 pl_assemble.py` | pl_template.html |
| DP-900 | `python3 dp_assemble.py` | dp_template.html |
| SC-900 | `python3 sc_assemble.py` | sc_template.html |

## デプロイ
生成された `index.html`（必要なら `*_icon.png` を `icon.png` にリネーム）を、リポジトリの各資格フォルダ（`ai900/` `az900/` …）へ上書きアップロード→コミットすると、GitHub Pagesで同じURL・同じアイコンのまま中身が更新されます。

## 問題バンクJSONの再生成
```bash
cd src/tools
python3 export_banks.py   # → src/tools/dist/<cert>-questions.json（meta+questions）
```

## メモ
- 検証観点: 重複なし／正解整合（single=1・multi≥2）／選択肢ランダム化（正解位置がA〜Dに均等分散）／正誤判定が選択肢位置に依存しない。
- 学習ノートはObsidian（MyBrain）`30_Resources/Tech/Azure/` 側に資格別ナレッジとして整備済み。
