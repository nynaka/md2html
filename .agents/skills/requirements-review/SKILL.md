---
name: requirements-review
description: >-
  Use this skill when reviewing, validating, or updating `docs/requirements.md` to ensure
  functional/non-functional requirements coverage, scope boundaries, and consistency with project goals.
---

# Requirements Review Skill

[`docs/requirements.md`](file:///home/ynaka/gitlab/md2html/docs/requirements.md)（要件定義書）の内容が、プロジェクトの目的、ユースケース、技術制約、および関連設計書と整合しているかを監査・検証するためのガイドラインです。

## 1. レビューの主眼と目的

- **完全スタンドアロン要件の担保**: 外部通信を前提としない単一 HTML 出力というツールの根幹要件が揺らいでいないか。
- **機能要件の網羅性とテスト可能性**: 各要件（FR-1〜FR-7）が曖昧でなく、テストケース（`tests/`）として検証可能に定義されているか。
- **ドキュメント間の整合性**: アーキテクチャ設計書（[`docs/architecture.md`](file:///home/ynaka/gitlab/md2html/docs/architecture.md)）、ユーザー向け [`README.md`](file:///home/ynaka/gitlab/md2html/README.md)、および開発ガイドライン [`AGENT.md`](file:///home/ynaka/gitlab/md2html/AGENT.md) との間に矛盾がないか。

---

## 2. 要件定義レビュー・チェックリスト

### ① 背景・目的・スコープ
- [ ] **利用シーンの妥当性**: 閉域網での仕様書共有、CI/CD ビルド、ローカルプレビュー等の想定シナリオに即しているか。
- [ ] **スコープ境界**: In-Scope（Markdownパース、Admonitions、Mermaid、ミニマップ等）と Out-of-Scope（画像Base64化、HTTPサーバ機能等）の境界が明確か。

### ② 機能要件 (FR-1 〜 FR-7)
- [ ] **FR-1 (Markdown パース)**: CommonMark 準拠、GFM テーブル（リスト・引用内ネスト対応）、Front Matter 除去と title 抽出、生 HTML パススルー（`escape=False`）が明記されているか。
- [ ] **FR-2 (スタイリング & テーマ)**: `github`, `gitlab`, `auto` テーマの定義と、`auto`, `light`, `dark` モードの動作仕様（`prefers-color-scheme` 制御）が網羅されているか。
- [ ] **FR-3 (コードハイライト & コピー)**: Pygments による主要言語のハイライト、未指定言語の安全なフォールバック、クリップボードコピーボタン（Mermaid 除外含む）の仕様が定義されているか。
- [ ] **FR-4 (Mermaid ダイアグラム)**: クライアント側 SVG レンダリング、対応図種別、テーマ連動、および `--no-mermaid` 無効化仕様が網羅されているか。
- [ ] **FR-5 (Admonition 注意書き)**: MkDocs 形式 (`!!!`) と Docusaurus 形式 (`:::`) の両構文、サポートするタイプ一覧、4文字インデント、タイトル省略補完、アイコン表示が網羅されているか。
- [ ] **FR-6 (ミニマップ / TOC)**: 見出し（h1〜h6）抽出、アンカー ID 自動付与、日本語マルチバイト対応、重複スラッグの連番回避（`-1`, `-2`）、スクロール追従、および無効化（`--no-minimap`）仕様が網羅されているか。
- [ ] **FR-7 (CLI 仕様)**: 引数体系（`INPUT` / `OUTPUT`）、標準入出力（`-` 指定）、全 CLI オプション、および終了ステータス（成功 0 / 失敗 1）が網羅されているか。

### ③ 非機能要件 (NFR-1 〜 NFR-5)
- [ ] **NFR-1 (スタンドアロン性)**: 外部 CDN / リモート HTTP 参照のゼロ化（CSS/JS のインライン埋め込み）が最重要要件として定義されているか。
- [ ] **NFR-2 (動作環境)**: Python 3.11+、主要モダンブラウザ、レスポンシブ幅（1024px を境界とする 2 カラム/最適化配置）が明記されているか。
- [ ] **NFR-3 (パフォーマンス)**: 数千行規模の Markdown でも数秒以内で変換できる性能基準が示されているか。
- [ ] **NFR-4 (文字コード & 国際化)**: UTF-8 固定（`<meta charset="UTF-8">`）、日本語を含むスラッグ/アンカー ID 生成が明記されているか。
- [ ] **NFR-5 (品質・テスト)**: TDD、pytest、tox、BeautifulSoup による DOM 構造検証、ruff / flake8 静的解析基準が明記されているか。

### ④ 制約事項・トレーサビリティ
- [ ] **依存ライブラリの最小化**: 実行時依存が `mistune` と `pygments` のみに限定され、不要なサードパーティ製ライブラリが除外されているか。
- [ ] **実装との乖離**: 現在の `src/md2html/` の実装および `tests/` のテストケースと乖離していないか。

---

## 3. レビュー結果の提示フォーマット

要件定義書の監査を実施した際は、以下の形式で結果を報告してください：

```markdown
### 要件定義レビュー結果サマリ
- **判定**: [承認 (LGTM) / 要修正 (Action Required)]
- **対象ドキュメント**: `docs/requirements.md`

#### 指摘事項・改善提案
1. **[重要度: 高/中/低] 項目名**:
   - 現状の記述: ...
   - 課題・懸念点: ...
   - 推奨修正案: ...

#### ドキュメント整合性チェック
- [x] docs/architecture.md との整合
- [x] README.md との整合
- [x] 実装コード（src/md2html/）との整合
```
