# Agent Guidelines

本リポジトリは、Markdown ファイルを外部依存のないスタンドアロンな単一 HTML ファイルへ変換する Python 製 CLI ツール「**md2html**」です。  
CSS、JavaScript（Mermaid、シンタックスハイライト、コードコピーボタン、ミニマップ/目次サイドバー）をすべて単一の HTML ファイル内にインライン埋め込みし、オフライン環境でも完全な表示を実現します。

AI エージェントがコード変更、新機能追加、リファクタリング、仕様書作成・更新を行う際は、以下の仕様・アーキテクチャ原則・制約・ワークフローに厳密に従ってください。

---

## 1. プロジェクト概要 & 技術スタック

| レイヤー / 領域 | 採用技術 | バージョン / 備考 |
| :--- | :--- | :--- |
| **言語** | Python | 3.11 以上（型ヒント徹底） |
| **Markdown パーサー** | mistune | 3.0.0 以上（CommonMark 準拠、プラグイン拡張） |
| **シンタックスハイライト** | Pygments | 2.17.0 以上（HTMLFormatter によるインライン CSS・クラス出力） |
| **ダイアグラム描画** | Mermaid.js | バンドル JS によるブラウザ側クライアントレンダリング |
| **CLI インターフェース** | argparse | 標準ライブラリによる堅牢な引数・オプション解析 |
| **テスト・カバレッジ** | pytest, pytest-cov, tox | カバレッジ計測、単体・結合テスト自動化 |
| **HTML 構造検証** | beautifulsoup4, lxml | テスト内でのパース結果 DOM 構造アサーション |
| **Linter / Formatter** | ruff, flake8 | 行長 100 文字、PEP 8 / pyproject.toml / setup.cfg 準拠 |
| **CI / CD** | GitLab CI (`.gitlab-ci.yml`) | `tox -e lint`, `tox -e py3` 自動実行 |

---

## 2. ディレクトリ構成と責務

関心の分離（SoC）および単一 HTML 生成パイプラインを意識した構成となっています。

```text
md2html/
├── src/
│   └── md2html/
│       ├── __init__.py         # パッケージ初期化
│       ├── __main__.py         # python -m md2html エントリポイント
│       ├── cli.py              # CLI 引数定義 (argparse)、入出力ストリーム制御、main 関数
│       ├── builder.py          # 複数ファイルクローラー & フォルダサイト構築 (リンク追従、アセットコピー)
│       ├── converter.py        # 変換パイプライン統括 (Frontmatter 除外, Admonition 処理, mistune 呼出, ミニマップ注入, HTML 構築)
│       ├── admonition.py       # MkDocs (!!!) / Docusaurus (:::) 記法 Admonition 正規表現プリプロセッサ
│       ├── highlighter.py      # Pygments 連携 mistune.HTMLRenderer サブクラス (コードブロックハイライト)
│       ├── mermaid.py          # Mermaid mistune.HTMLRenderer サブクラス & インライン <script> 生成
│       ├── minimap.py          # 見出し (h1〜h6) 解析、アンカー ID 自動付与、ミニマップ (TOC) HTML / スクリプト生成
│       └── assets/             # HTML へインライン埋め込みする静的リソース
│           ├── github.css      # GitHub 風ドキュメントスタイル CSS
│           ├── gitlab.css      # GitLab 風ドキュメントスタイル CSS
│           ├── admonition.css  # Admonitions スタイル定義 (タイプ別カラー・アイコン)
│           ├── copy-button.css # コードコピーボタン用スタイル
│           └── minimap.css     # ミニマップ (TOC) サイドバー用スタイル
├── tests/
│   ├── conftest.py             # pytest フィクスチャ設定
│   ├── fixtures/               # テスト用 Markdown サンプル (.md)
│   │   ├── basic.md            # 基本的な CommonMark 構文
│   │   ├── admonition_mkdocs.md     # MkDocs 形式 Admonition
│   │   ├── admonition_docusaurus.md # Docusaurus 形式 Admonition
│   │   ├── mermaid.md          # Mermaid ダイアグラムブロック
│   │   └── highlight.md        # シンタックスハイライト対象コードブロック
│   ├── test_builder.py         # リンク追従・再帰変換・アセットコピーのテスト
│   ├── test_cli.py             # CLI コマンド・引数・終了コード・入出力のテスト
│   ├── test_converter.py       # HTML 生成パイプライン・テーマ・モード切り替えの結合テスト
│   ├── test_admonition.py      # Admonition 前処理正規表現・ネスト・タイプ別テスト
│   ├── test_highlighter.py     # Pygments シンタックスハイライト・フォールバックテスト
│   ├── test_mermaid.py         # Mermaid ブロック変換・テーマ連動テスト
│   └── test_minimap.py         # 見出し抽出・ID付与・スラッグ重複回避・TOC 生成テスト
├── docs/                       # 仕様書・設計書
│   ├── requirements.md         # 要件定義書
│   ├── architecture.md         # 基本仕様・アーキテクチャ設計書
│   ├── functional_design.md    # 機能設計書 (モジュール詳細・API仕様)
│   └── coding_plan.md          # コーディング計画・パイプライン設計
├── .github/
│   └── copilot-instructions.md # Copilot / AI 向け設計・規約サマリ
├── .gitlab-ci.yml              # GitLab CI パイプライン設定
├── pyproject.toml              # パッケージビルド定義、ruff / pytest 設定
├── setup.cfg                   # flake8 設定
├── requirements.txt            # 実行時依存パッケージ
├── requirements-dev.txt        # 開発・テスト依存パッケージ
├── tox.ini                     # tox 自動化設定 (py3, lint)
├── README.md                   # ユーザー向け機能・オプション・利用ガイド
└── AGENT.md                    # 本エージェント開発ガイドライン
```

---

## 3. 開発・実行コマンド体系

### 仮想環境セットアップ & 依存パッケージインストール

```bash
# 仮想環境作成と有効化
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 開発依存を含めた editable インストール
pip install -r requirements-dev.txt
pip install -e .
```

### CLI ツールの実行

```bash
# 基本実行 (出力先フォルダを指定。リンク先 Markdown 変換 & アセットコピー)
python -m md2html input.md dist/
# またはインストール済みコマンド
md2html input.md dist/

# 出力先フォルダ省略時はデフォルトで dist/ に出力
md2html input.md

# 標準入力から読み込み (標準出力またはフォルダ内 index.html に出力)
cat input.md | md2html -
cat input.md | md2html - dist/

# オプション指定例
md2html --title "ドキュメントタイトル" --theme gitlab --mode dark input.md dist/
md2html --no-mermaid --no-minimap input.md dist/
```

### テスト実行

```bash
# tox による全テスト + lint 一括実行
tox

# テスト (pytest + coverage) のみ実行
tox -e py3

# lint (ruff + flake8) のみ実行
tox -e lint

# 仮想環境内で pytest を直接実行する場合 (PYTHONPATH に src を含める)
pytest tests/

# 単一テストファイルの実行
pytest tests/test_converter.py -v

# 特定テストケースの実行
pytest tests/test_converter.py::test_full_featured_document -v

# カバレッジレポート出力
pytest tests/ --cov=src/md2html --cov-report=term-missing
```

### コードスタイル & 静的解析

```bash
# ruff によるフォーマットチェック
ruff format --check src/ tests/

# ruff による自動フォーマット適用
ruff format src/ tests/

# ruff による Linter チェック & 自動修正
ruff check src/ tests/
ruff check --fix src/ tests/

# flake8 による静的チェック (最大行長 100 文字)
flake8 src/ tests/
```

---

## 4. アーキテクチャ原則 & 実装ルール（最重要）

### ① 完全スタンドアロン（ゼロ外部依存）の厳守
- 生成される HTML ファイルは、**インターネット接続のないオフライン環境で完全に表示・動作**しなければなりません。
- 外部 CDN や外部ホストを参照する `<link rel="stylesheet" href="http...">` や `<script src="http...">` を出力してはなりません。
- CSS、JavaScript（Mermaid, コピーボタン, ミニマップスクリプト）はすべて `<style>` または `<script>` タグ内にインライン埋め込みしてください。

### ② アセットの読み込み規約
- CSS や JavaScript などの静的アセットは、`src/md2html/assets/` に配置し、実行時に `converter.py` 等から読み込みます。
- パス解決は必ず `os.path.join(os.path.dirname(__file__), "assets", filename)` を用い、カレント作業ディレクトリに依存しないようにしてください。

### ③ レンダラーの多重継承（MRO）とパイプライン設計
- `converter.py` では、必要に応じて動的な多重継承クラス（`CombinedRenderer`）を生成します。
  ```python
  class CombinedRenderer(MermaidRenderer, HighlightRenderer):
      pass
  ```
- **MRO（メソッド解決順序）の重要性**: `MermaidRenderer` が先に `block_code()` を評価し、言語が `mermaid` の場合は `<pre class="mermaid">` を出力します。それ以外の言語は `super().block_code()` 経由で `HighlightRenderer`（Pygments）へフォールバックします。この優先順位を崩さないでください。

### ④ `escape=False` の必須適用
- `mistune.HTMLRenderer` を継承するすべてのレンダラーで、`escape=False` を渡してください。
- これを怠ると、Markdown 内の生 HTML タグや、プリプロセスされた Admonition の `<div>` タグがエスケープされて画面にそのまま露出する原因になります。

### ⑤ プリプロセス方式による Admonition 変換
- MkDocs 形式（`!!! note "Title"`）および Docusaurus 形式（`:::note Title`）の Admonitions は、`admonition.py` において **mistune パース前に正規表現プリプロセス** で HTML (`<div class="admonition ...">`) へ置換します。
- インデントされた本文、リスト内・引用内での配置、タイトル省略時のデフォルトタイトル補完（`note` → `Note`）を正確に処理してください。

### ⑥ ミニマップ（TOC サイドバー）と見出しアンカー ID
- `minimap.py` は mistune による HTML レンダリング結果を走査し、`<h1>`〜`<h6>` タグを抽出して右側固定サイドバー（ミニマップ）を生成します。
- 見出しテキストからスラッグ（英数字 + 日本語マルチバイト対応）を生成し、一意な `id="..."` 属性を各見出しタグに自動付与します。重複する見出しテキストには `-1`, `-2` などのサフィックスを付与してアンカー衝突を防止してください。
- `--no-minimap` (`--no-toc`) が指定された場合は、ミニマップ HTML およびスクリプトを一切注入しないようにしてください。

### ⑦ カラーモード制御（`auto` / `light` / `dark`）
- **`auto`（デフォルト）**: CSS 内の `@media (prefers-color-scheme: dark)` を維持し、ブラウザ / OS の設定にリアルタイム追従させます。
- **`light`**: ダーク用メディアクエリブロックを CSS から除去（`_strip_dark_media`）し、ライトモードで固定します。
- **`dark`**: ダーク用メディアクエリをアンラップ（`_unwrap_dark_media`）して無条件適用し、ダークモードで固定します。

### ⑧ Front Matter（メタデータ）のハンドリング
- Markdown 先頭に存在する YAML / Docusaurus 形式の Front Matter（`---` で囲まれたブロック）は本文レンダリング対象から除外し、`title:` キーが存在する場合は `<title>` タグのデフォルト値として抽出・利用します。

### ⑨ テスト駆動開発（TDD: Test-Driven Development）の徹底
- 新機能の追加、仕様変更、および不具合修正時は、**必ずテスト駆動開発（Red → Green → Refactor）** で進めてください。
- **Red**: 実装前に `tests/` 配下に失敗するテストケース（または再現テスト）を作成します。
- **Green**: テストを通過させる最小限の実装を行います。
- **Refactor**: テストが全件 Green である状態を保ちながら、コードの可読性・設計・静的解析（`ruff`, `flake8`）を洗練させます。

---

## 5. エージェント向けスキル連携

本プロジェクトには、エージェントが専門タスクを遂行するための専用スキルが `.agents/skills/` に定義されています。必要に応じてこれらのスキルを参照・活用してください。

- **[requirements-review](.agents/skills/requirements-review/SKILL.md)**:  
  `docs/requirements.md` の要件定義書（FR-1〜FR-7、NFR-1〜NFR-5、スコープ、制約条件等）の網羅性・妥当性・テスト可能性を監査する際に使用します。
- **[architecture-review](.agents/skills/architecture-review/SKILL.md)**:  
  `docs/architecture.md` のパイプライン構造、レンダラー多重継承（MRO）、アセットバンドル、スタンドアロン性（外部CDN排除）、およびCLI設計の整合性を監査する際に使用します。
- **[converter-pipeline](.agents/skills/converter-pipeline/SKILL.md)**:  
  Markdown → HTML 変換パイプライン、Mistune レンダラー多重継承（MRO）、Frontmatter 抽出、スタンドアロン HTML 構築の仕様と実装手順。
- **[admonition-processing](.agents/skills/admonition-processing/SKILL.md)**:  
  MkDocs 形式 (`!!!`) および Docusaurus 形式 (`:::`) の Admonition 正規表現プリプロセス、インデント保持、ネスト処理、アイコン/スタイル連動。
- **[minimap-toc](.agents/skills/minimap-toc/SKILL.md)**:  
  見出し（h1〜h6）解析、日本語マルチバイト対応スラッグ生成、重複 ID 連番回避、ミニマップ (TOC) サイドバーおよびスクロール連動スクリプトの生成。
- **[theme-styling](.agents/skills/theme-styling/SKILL.md)**:  
  GitHub / GitLab テーマ、カラーモード（auto / light / dark）による CSS 変換、Pygments シンタックスハイライト、インラインアセットの管理。
- **[test-engineering](.agents/skills/test-engineering/SKILL.md)**:  
  pytest / tox によるテスト自動化、BeautifulSoup による HTML DOM 構造検証、Markdown フィクスチャの活用、カバレッジ計測、品質チェック。

---

## 6. ドキュメント整合性の維持

コードの追加・変更・仕様変更を行った際は、**必ず関連ドキュメントも同時に確認・更新**してください。

- **[README.md](README.md)**: ユーザー向けの利用方法、オプション一覧、Admonition 記法例、インストール手順。
- **[docs/requirements.md](docs/requirements.md)**: 要件定義書（背景・スコープ・機能/非機能要件）。
- **[docs/architecture.md](docs/architecture.md)**: 基本仕様・アーキテクチャ設計書（HTML 構造、CSS / JS 埋め込み仕様）。
- **[docs/functional_design.md](docs/functional_design.md)**: 機能設計書（各モジュールの詳細仕様・インターフェース・アルゴリズム）。
- **[docs/coding_plan.md](docs/coding_plan.md)**: モジュール設計、パイプラインの流れ、テスト方針。
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: エージェント・Copilot 向けの基本規約と構成サマリ。

---

## 7. 禁止事項（Constraints）

- **外部リソース（CDN・リモートURL）へのリンク埋め込み禁止**: スタンドアロン性を破壊する外部 CSS / JS 参照を追加してはなりません。
- **テスト不在での機能・ロジック実装禁止（TDD違反）**: テストコードなしでのコード改変や、テストが通っていない状態での完了報告は禁止です。
- **既存テストの安易な削除・スキップ禁止**: 挙動変更が必要な正当な理由がない限り、既存テストケースを削除したり `@pytest.mark.skip` を設定して逃げてはなりません。
- **`escape=False` の未指定禁止**: mistune レンダラーで `escape=False` を外して HTML パススルーや Admonition を破壊してはなりません。
- **独断での重量パッケージ依存追加の禁止**: `requirements.txt` に新しいサードパーティライブラリを追加する際は、必ず事前にユーザーへ相談し承認を得てください。
- **行長制限（100文字）違反および Lint / Format エラーの放置禁止**: コミット前に必ず `ruff` / `flake8` を通過させてください。

---

## 8. タスク進行・自律実行ルール

エージェントが機能追加や修正タスクを行う際は、以下の進め方を原則とします。

### ① タスク開始時の整理
- 作業の目的、受け入れ条件、変更予定ファイル（モジュール、テスト、ドキュメント）を明確にし、必要に応じてユーザーに共有します。

### ② 自律実行可能な作業範囲
以下の範囲については、確認済みのタスク目的に沿っている限り、エージェントが自律的に実行して構いません。
- `src/md2html/` および `tests/` 配下のコード作成・修正
- TDD サイクルに基づくテスト実行（`pytest`, `tox`）およびエラー解消
- コードスタイル修正（`ruff format`, `ruff check --fix`）
- 変更内容に応じた関連ドキュメント（`README.md`, `docs/base_spec.md` 等）の整合性維持更新

### ③ 事前確認・承認が必要な事項（都度相談必須）
以下の事項が発生する場合は、自律実行せず**必ず事前に理由を説明しユーザーの承認**を得てください。
- `requirements.txt` や `pyproject.toml` への新規外部依存ライブラリの追加
- CLI オプションの破壊的変更（既存オプションの削除・意味の変更）
- 生成 HTML の基本構造や互換性を損なう大規模なアーキテクチャ変更
- ネットワーク通信を伴う外部リソースの取得やコマンド実行
