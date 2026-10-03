---
name: theme-styling
description: >-
  Use this skill when modifying themes (GitHub, GitLab), color modes (auto, light, dark),
  Pygments syntax highlighting styles, code copy buttons, or bundled assets.
---

# Theme & Styling Skill

`md2html` のデザイン、テーマ（GitHub / GitLab）、カラーモード制御、およびアセットバンドルに関するガイドです。

## 1. 完全スタンドアロン（ゼロ外部依存）の原則

すべての HTML 出力は、外部 CDN や別ファイルへの HTTP 参照を含まない「スタンドアロンな単一 HTML」である必要があります。
- **CSS**: すべて `<style>` タグ内にインライン展開。
- **JavaScript**: Mermaid.js、コードコピーボタン用 JS、ミニマップ用 JS もすべて `<script>` タグ内にインライン展開。
- 静的アセットファイルはすべて [`src/md2html/assets/`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/) に配置し、実行時に `_load_asset()` で読み込みます。

## 2. アセット構成

- [`github.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/github.css): GitHub の Markdown スタイルを踏襲した CSS 変数ベースのスタイル。
- [`gitlab.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/gitlab.css): GitLab の Wiki/ドキュメントスタイル。
- [`admonition.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/admonition.css): 注意書きブロックのスタイルとアイコン。
- [`copy-button.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/copy-button.css): コードブロック右上のホバー時コピーボタンのスタイル。
- [`minimap.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/minimap.css): 目次サイドバーのレイアウトとアクティブ行表示。

## 3. カラーモード制御（`--mode`）

[`src/md2html/converter.py`](file:///home/ynaka/gitlab/md2html/src/md2html/converter.py) の `_apply_mode()` による CSS 変換ルール：

| モード | 動作仕様 | CSS 処理 |
| :--- | :--- | :--- |
| **`auto`** (デフォルト) | OS / ブラウザの配色設定に動的追従 | CSS 内の `@media (prefers-color-scheme: dark)` ブロックをそのまま維持 |
| **`light`** | 常に明るいテーマで固定 | `_strip_dark_media()` により `@media ... dark` ブロックを完全に除去 |
| **`dark`** | 常に暗いテーマで固定 | `_unwrap_dark_media()` によりダーク用ルールをメディアクエリから出して無条件適用 |

## 4. シンタックスハイライト CSS

Pygments の `HtmlFormatter` を使用して動的にスタイル定義を取得します：
- ライトスタイル: `--highlight-style` で指定されたスタイル（デフォルト: `default`）
- ダークスタイル: `github-dark`
- `auto` モード時は、ダークスタイルを `@media (prefers-color-scheme: dark) { ... }` で囲んでライトスタイルを上書きします。

## 5. テストと検証

```bash
# テーマ・カラーモード関連のテスト
pytest tests/test_converter.py -k "theme or mode or css" -v

# シンタックスハイライトのテスト
pytest tests/test_highlighter.py -v
```
