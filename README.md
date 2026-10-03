# md2html

Markdown ファイルを、外部依存のないスタンドアロンな HTML サイト（フォルダ）に変換するコマンドラインツールです。  
指定した Markdown からリンクされている別の Markdown ドキュメントも再帰的に連鎖変換し、画像や PDF などのアセットファイルも相対パスを維持したまま出力フォルダへ自動コピーします。

CSS・JavaScript（Mermaid, シンタックスハイライト, ミニマップ目次, コピーボタン）はすべて HTML 内にインライン埋め込みされるため、生成されたフォルダはオフライン環境でも完全な表示・ナビゲーションが可能です。

## 特徴

- **リンクドキュメントの連鎖変換** — リンクされている Markdown を自動探索して一括 HTML 化。`.md` リンクは自動的に `.html` へ書き換え（アンカーハッシュも保持）
- **アセット自動コピー** — 参照されている画像（PNG, SVG 等）や添付ファイル（PDF 等）の相対パス関係を維持して出力フォルダへ自動配置
- **GitHub / GitLab 風スタイル** — 選択可能なテーマとライト／ダーク／自動（OS追従）モード対応
- **シンタックスハイライト** — Pygments を使用した主要言語のコードハイライト
- **コードコピーボタン** — コードブロックにホバーするとクリップボードコピーボタンを表示
- **Mermaid 図** — フローチャート・シーケンス図・ガントチャートなどをブラウザ側で SVG レンダリング
- **ミニマップ (TOC)** — 見出し (h1〜h6) から自動抽出されたスクロール追従目次サイドバー
- **Admonitions** — MkDocs (`!!!`) および Docusaurus (`:::`) 形式の注意書きブロックに対応

## インストール

```bash
git clone <repo-url>
cd md2html

# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存インストール & パッケージを editable モードでインストール
pip install -e .
```

> `pip install -e .` によりソースを直接参照するため、コード変更後も再インストール不要で `md2html` コマンドが利用できます。

## 使い方

### 基本コマンド

起点となる Markdown ファイルと、出力先フォルダパスを指定して実行します。

```bash
# 出力先フォルダを指定して変換（推奨）
md2html README.md dist/

# 出力先フォルダを省略した場合はカレントの dist/ に出力されます
md2html README.md

# python -m 形式でも実行可能
python -m md2html README.md dist/
```

### 出力フォルダの構成例

起点ドキュメントからリンクされたファイル群が、相対パス関係を保ったまま出力フォルダ内に構成されます：

```text
# 変換元の構成例
project/
├── README.md              # [仕様書](docs/spec.md) および ![構成図](images/arch.png) へのリンクあり
├── docs/
│   └── spec.md            # [詳細](detail.md) へのリンクあり
│   └── detail.md
└── images/
    └── arch.png

# コマンド実行: md2html README.md dist/
# 出力先 (dist/) の構成
dist/
├── README.html            # リンク先は docs/spec.html に自動書き換え
├── docs/
│   ├── spec.html          # リンク先は detail.html に自動書き換え
│   └── detail.html
└── images/
    └── arch.png           # 画像が自動コピーされ、README.html からそのまま表示可能
```

### 主要オプションの使用例

```bash
# タイトルを指定（起点ファイルに適用）
md2html --title "仕様書ポータル" docs/index.md dist/

# GitLab 風テーマを使用
md2html --theme gitlab README.md dist/

# ライトモードを強制（OS がダークモードでも常に明るい表示）
md2html --mode light README.md dist/

# ダークモードを強制
md2html --mode dark README.md dist/

# OS テーマに自動追従（auto、デフォルト）
md2html --theme auto README.md dist/

# シンタックスハイライトのカラースキームを変更
md2html --highlight-style monokai README.md dist/

# Mermaid 描画を無効化
md2html --no-mermaid README.md dist/

# ミニマップ（目次サイドバー）を非表示
md2html --no-minimap README.md dist/

# 標準入力から読み込み（標準出力に出力、または出力フォルダの index.html に出力）
echo "# Hello" | md2html -
echo "# Hello" | md2html - dist/
```

### オプション一覧

| オプション | デフォルト | 説明 |
|---|---|---|
| `INPUT` | — | 起点となる Markdown ファイルパス、または `-`（stdin） |
| `OUTPUT` | `dist` | 出力先フォルダパス（stdin 入力時は stdout） |
| `--title TEXT` | ファイル名 | `<title>` タグの文字列（起点ドキュメントに適用） |
| `--theme {github,gitlab,auto}` | `github` | CSS テーマ |
| `--highlight-style TEXT` | `default` | Pygments カラースキーム |
| `--no-highlight` | — | シンタックスハイライトを無効化 |
| `--mode {auto,light,dark}` | `auto` | カラーモード: `light` でライト強制、`dark` でダーク強制、`auto` で OS 設定に追従 |
| `--no-mermaid` | — | Mermaid 描画を無効化 |
| `--no-minimap` (`--no-toc`) | — | ミニマップ (目次) サイドバーを無効化（非表示） |

## Admonitions 記法

### MkDocs 形式

```markdown
!!! note "タイトル"
    本文テキスト。

!!! warning
    タイトルなしも可。
```

サポートタイプ: `note` `info` `tip` `success` `warning` `danger` `failure` `bug` `example` `quote` `abstract`

### Docusaurus 形式

```markdown
:::note タイトル
本文テキスト。
:::

:::caution
タイトルなしも可。
:::
```

サポートタイプ: `note` `tip` `info` `caution` `danger` `warning`

## 開発環境セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# または
pip install -r requirements-dev.txt
pip install -e .
```

### テスト実行

```bash
# 全テスト + lint
tox

# テストのみ
tox -e py3

# lint のみ
tox -e lint

# 単一テスト
.venv/bin/pytest tests/test_converter.py::test_full_featured_document -v

# カバレッジ付き
.venv/bin/pytest tests/ --cov=src/md2html --cov-report=term-missing
```

### コードスタイル

```bash
# 自動フォーマット
.venv/bin/ruff format src/ tests/

# lint チェック
.venv/bin/ruff check src/ tests/
.venv/bin/flake8 src/ tests/
```

## ライセンス

MIT
