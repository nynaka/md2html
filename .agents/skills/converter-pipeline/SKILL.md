---
name: converter-pipeline
description: >-
  Use this skill when modifying, debugging, or extending the Markdown-to-HTML conversion pipeline,
  Mistune plugins, renderer composition (MRO), frontmatter parsing, or standalone HTML document assembly.
---

# Converter Pipeline Skill

`md2html` の中核である Markdown → HTML 変換パイプラインおよびスタンドアロン HTML 組み立ての設計・実装ガイドです。

## 1. 変換パイプラインの全体フロー

変換処理は [`src/md2html/converter.py`](file:///home/ynaka/gitlab/md2html/src/md2html/converter.py) の `convert()` 関数で統括されています。

```text
[入力 Markdown]
       │
       ▼
1. strip_frontmatter()        : YAML / Docusaurus Front Matter (---) の除去 & title 抽出
       │
       ▼
2. preprocess_admonitions()   : MkDocs / Docusaurus 形式の注意書きブロックを先行して HTML div 化
       │
       ▼
3. mistune レンダリング       : CombinedRenderer (Mermaid + Pygments) + 各種プラグインでパース
       │
       ▼
4. process_headings_and_build_minimap() : h1〜h6 の抽出、一意なアンカー ID 付与、ミニマップ HTML 生成
       │
       ▼
5. _build_html()              : CSS (テーマ・モード別)、インライン JS (Mermaid, コピー, ミニマップ) を埋め込み
       │
       ▼
[完全スタンドアロン HTML]
```

## 2. レンダラー多重継承（MRO）の設計

`converter.py` の `_make_renderer()` は、オプションに応じて動的に多重継承クラスを定義します。

```python
class CombinedRenderer(MermaidRenderer, HighlightRenderer):
    pass
```

- **MRO の優先順位**:
  1. `MermaidRenderer`: コードブロックの言語が `mermaid` の場合、`<pre class="mermaid">` を出力して処理完了。
  2. `HighlightRenderer`: 言語が `mermaid` 以外の場合、`super().block_code()` 経由で Pygments によるシンタックスハイライトを実行。
  3. `mistune.HTMLRenderer`: 指定言語に対応する Lexer が見つからない場合やプレーンコードの場合のフォールバック。

> [!IMPORTANT]
> すべての `mistune.HTMLRenderer` サブクラスには必ず `escape=False` を渡してください。これを怠ると、生 HTML やプリプロセス済み Admonition の `<div>` タグがエスケープされ、テキストとしてそのまま表示されてしまいます。

## 3. 組み込みプラグイン一覧

Mistune の初期化時に以下の標準プラグインを組み込んでいます：
- `strikethrough`: 取り消し線 (`~~text~~`)
- `table`: GFM テーブル
- `table_in_list`: リスト項目内にインデントされたテーブルのパース
- `table_in_quote`: 引用ブロック内に配置されたテーブルのパース
- `url`: 生 URL の自動リンク化

## 4. 変更・拡張時の作業手順

1. **仕様確認**: 変更が Markdown パーサー層、プリプロセス層、ポストプロセス層（ミニマップ等）のどこに属するかを特定します。
2. **テスト作成 (Red)**:
   - レンダリング結合テスト: [`tests/test_converter.py`](file:///home/ynaka/gitlab/md2html/tests/test_converter.py)
   - 必要に応じて `tests/fixtures/` にサンプル Markdown を追加。
3. **実装 (Green)**:
   - `converter.py` または関連モジュールを修正。
4. **検証**:
   ```bash
   pytest tests/test_converter.py -v
   ```
