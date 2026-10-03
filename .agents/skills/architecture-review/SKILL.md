---
name: architecture-review
description: >-
  Use this skill when reviewing, validating, or updating `docs/architecture.md` (or system architecture)
  to ensure pipeline design, renderer MRO, asset bundling, standalone HTML structure, and CLI interfaces align with requirements.
---

# Architecture Review Skill

[`docs/architecture.md`](file:///home/ynaka/gitlab/md2html/docs/architecture.md)（アーキテクチャ設計書・基本仕様書）およびシステム全体の構造設計が、要件定義書（[`docs/requirements.md`](file:///home/ynaka/gitlab/md2html/docs/requirements.md)）を忠実に満たし、堅牢で保守性の高い設計になっているかを監査・検証するためのガイドラインです。

## 1. レビューの主眼と目的

- **要件定義とのトレーサビリティ**: `docs/requirements.md` に定義された機能要件 (FR) / 非機能要件 (NFR) が、過不足なくアーキテクチャ・モジュール構造にマッピングされているか。
- **完全スタンドアロンの構造的保証**: HTML 構築パイプラインにおいて外部 CDN やリモート参照が混入する経路が排除されているか。
- **関心の分離（SoC）とパイプライン設計の健全性**: 各モジュール（`cli.py`, `converter.py`, `admonition.py`, `highlighter.py`, `mermaid.py`, `minimap.py`, `assets/`）の責務分担が適切か。

---

## 2. アーキテクチャレビュー・チェックリスト

### ① 変換パイプライン & レンダラー設計
- [ ] **パイプラインの順序妥当性**:
  - `strip_frontmatter()`（文頭 YAML 除外）
  - → `preprocess_admonitions()`（正規表現による先行 HTML 置換）
  - → `mistune` パース（CombinedRenderer + GFM テーブル・リンクプラグイン）
  - → `process_headings_and_build_minimap()`（見出し走査・アンカー注入・TOC 生成）
  - → `_build_html()`（CSS/JS 結合・スタンドアロン HTML 構築）
  という順序が論理的に正しく設計されているか。
- [ ] **MRO (メソッド解決順序) の厳密性**:
  - `class CombinedRenderer(MermaidRenderer, HighlightRenderer)` において、`MermaidRenderer` が優先され、非 Mermaid 言語が `HighlightRenderer`（Pygments）へ安全に委譲される設計になっているか。
- [ ] **`escape=False` 原則**:
  - 生 HTML や前処理済み Admonition の `<div>` が二重エスケープされないよう、全レンダラーで `escape=False` が指定されているか。

### ② アセット設計 & スタンドアロン保証
- [ ] **ゼロ外部依存の保証**:
  - すべての CSS（テーマ、Admonition、コピーボタン、ミニマップ、Pygments）が `<style>` タグ内に直接展開される設計か。
  - すべての JS（Mermaid、コピーボタン IIFE、ミニマップ IIFE）が `<script>` タグ内に直接展開される設計か。
- [ ] **アセット配置と読み込み規約**:
  - 静的ファイルが `src/md2html/assets/` に集約され、カレントディレクトリに依存しない `os.path.join(os.path.dirname(__file__), ...)` で読み込まれているか。
- [ ] **カラーモード制御アルゴリズム**:
  - `auto`: CSS 内の `@media (prefers-color-scheme: dark)` を維持。
  - `light`: `_strip_dark_media()` でダーク用ブロックを完全除去。
  - `dark`: `_unwrap_dark_media()` でダーク用ブロックを無条件展開。
  このロジックが破綻なく記述されているか。

### ③ 見出し解析 & ミニマップ（TOC）設計
- [ ] **アンカー ID 生成アルゴリズム**:
  - 日本語（漢字・ひらがな・カタカナ）を含むマルチバイト文字が破壊されず、安全なスラッグとして生成されるか。
  - 同一見出しが複数存在する場合の重複回避連番（`-1`, `-2`）の設計が明記されているか。
- [ ] **DOM 構造**:
  - `<div class="app-container">` 内に `.markdown-body` と `<aside class="minimap-wrapper">` が正しく配置され、CSS Sticky による追従設計がなされているか。
- [ ] **無効化（`--no-minimap`）時の整合性**:
  - ミニマップ無効化時に不要な DOM やスクリプトが残存しない設計になっているか。

### ④ CLI インターフェース & エラーハンドリング
- [ ] **入出力ストリーム設計**:
  - ファイルパス指定と標準入出力（`-` 指定）の切り替えが明快に設計されているか。
- [ ] **エラーハンドリング**:
  - ファイル未存在、パース例外発生時に適切な終了コード（`1`）と標準エラー出力を返す設計か。

---

## 3. レビュー結果の提示フォーマット

アーキテクチャレビューを実施した際は、以下の形式で結果を報告してください：

```markdown
### アーキテクチャレビュー結果サマリ
- **判定**: [承認 (LGTM) / 要修正 (Action Required)]
- **対象ドキュメント**: `docs/architecture.md` / `src/md2html/`

#### アーキテクチャ観点での評価
1. **[重要度: 高/中/低] 項目名**:
   - 設計上の課題・リスク: ...
   - 技術的影響（保守性・パフォーマンス・互換性）: ...
   - 推奨修正案 / 改善コード例: ...

#### パイプライン・アセット検証
- [x] レンダラー MRO 優先順位の妥当性
- [x] スタンドアロン性（外部 CDN 参照の完全排除）
- [x] escape=False 規約の遵守
- [x] docs/requirements.md とのトレーサビリティ
```
