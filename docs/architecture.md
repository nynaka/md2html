# md2html 基本仕様

## 概要

MarkdownファイルをスタンドアロンなシングルファイルHTMLに変換するコマンドラインツール。  
CSS・JavaScript（Mermaid, シンタックスハイライト）はすべてHTMLに埋め込み、外部ファイルを参照しない。

---

## コマンドインターフェース

```bash
md2html [OPTIONS] INPUT [OUTPUT]
```

| 引数/オプション | 説明 |
|---|---|
| `INPUT` | 起点となる Markdown ファイルパス（`-` で標準入力） |
| `OUTPUT` | 出力先フォルダパス（デフォルト: `dist`。stdin 入力時は標準出力） |
| `--title TEXT` | `<title>` タグに使用するタイトル（起点ドキュメントに適用。省略時: ファイル名） |
| `--theme {github,gitlab,auto}` | CSSテーマ（デフォルト: `github`） |
| `--highlight-style TEXT` | シンタックスハイライトのカラースキーム（デフォルト: `default`） |
| `--no-highlight` | シンタックスハイライトを無効化 |
| `--mode {auto,light,dark}` | カラーモード（デフォルト: `auto`）。`light` でライト強制、`dark` でダーク強制、`auto` で OS 設定に追従 |
| `--no-mermaid` | Mermaid 描画を無効化 |
| `--no-minimap` (`--no-toc`) | ミニマップ (目次) サイドバーを無効化（非表示） |

### 使用例

```bash
# 出力先フォルダを指定して変換（リンクされた Markdown も連鎖変換 & 画像等のアセットもコピー）
md2html README.md dist/

# 出力先フォルダ省略時はデフォルトで dist/ に出力
md2html README.md

# タイトル指定
md2html --title "設計書ポータル" docs/index.md dist/

# GitLab テーマで変換
md2html --theme gitlab doc.md dist/

# ミニマップ（目次）を非表示
md2html --no-minimap doc.md dist/
```

---

## 機能仕様

### 1. Markdown 変換

標準的な CommonMark 仕様に準拠したMarkdownを変換する。

サポートする要素:

- 見出し（h1〜h6）
- 段落、改行
- 強調（bold, italic, strikethrough）
- リスト（順序あり・なし・ネスト）
- テーブル（GitHub Flavored Markdown 拡張、リスト内・引用内のインデント配置対応）
- リンク・画像
- インラインコード・コードブロック
- 引用（blockquote）
- 水平線
- HTML パススルー（Markdown 中の生 HTML タグをそのまま出力）
- Docusaurus / YAML Front Matter（`---` メタデータヘッダー）の自動除外および `title` 自動抽出

---

### 2. スタイル（CSS）

GitHub および GitLab のドキュメントスタイルを踏襲した CSS を HTML に直接埋め込む。

**基本方針:**

- `<style>` タグで `<head>` 内にインライン埋め込み
- 外部 CDN・外部ファイルへの参照なし
- カラーモード制御: `--mode` オプションで `light`（強制ライト）・`dark`（強制ダーク）・`auto`（OS 設定追従）を選択可能
  - `auto` 時: `prefers-color-scheme: dark` メディアクエリで自動切り替え
  - `light` / `dark` 時: メディアクエリを除去し、指定モードのスタイルを直接埋め込む
- 本文幅: 最大 `980px`、中央揃え（GitHub スタイル準拠）
- フォント: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`
- コードフォント: `SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace`

**テーマ:**

| テーマ名 | 説明 |
|---|---|
| `github` | GitHub の README 表示スタイル |
| `gitlab` | GitLab の Wiki/ドキュメントスタイル |
| `auto` | github CSS をベースにし、`prefers-color-scheme: dark` 時に gitlab の CSS 変数を上書き適用 |

---

### 3. シンタックスハイライト

コードブロック（` ```言語名 `）の言語識別子に基づきハイライトを適用する。

- ハイライト用CSSは `<style>` タグにインライン埋め込み
- デフォルトカラースキーム: `default`（Pygments 標準ライトスタイル）
- `--mode auto` 時: ライトスタイルをデフォルトとし、`github-dark` スタイルを `prefers-color-scheme: dark` メディアクエリで上書き適用
- `--mode light` 時: ライトスタイルのみ埋め込み（ダーク用メディアクエリなし）
- `--mode dark` 時: `github-dark` スタイルのみ埋め込み（メディアクエリなし）
- 言語指定がない場合はハイライトなし（プレーンテキスト扱い）
- サポート言語例: `python`, `javascript`, `typescript`, `bash`, `sh`, `sql`, `json`, `yaml`, `go`, `rust`, `java`, `c`, `cpp`, `html`, `css` など主要言語すべて

---

### 4. Mermaid 図の描画

コードブロックの言語識別子が `mermaid` のブロックを SVG 図として描画する。

**実装方針:**

- `<pre class="mermaid">` 要素に変換し、クライアントサイドでレンダリング
- `--mode auto` 時: `window.matchMedia('(prefers-color-scheme: dark)')` で Mermaid テーマを動的切り替え
- `--mode light` 時: Mermaid テーマを `'default'`（ライト）に固定
- `--mode dark` 時: Mermaid テーマを `'dark'` に固定
- Mermaid JS は `assets/mermaid.min.js` としてバンドル・インライン埋め込みが理想形。  
  未配置の場合は CDN（`cdn.jsdelivr.net`）からのロードにフォールバックする。

**対応する Mermaid 図種別:**

| 種別 | 記法例 |
|---|---|
| フローチャート | `flowchart TD` |
| シーケンス図 | `sequenceDiagram` |
| ガントチャート | `gantt` |
| クラス図 | `classDiagram` |
| 状態遷移図 | `stateDiagram-v2` |
| ER 図 | `erDiagram` |
| その他 Mermaid 公式サポート図 | — |

---

### 5. Admonitions（注意書きブロック）変換

#### 5.1 MkDocs 形式

```markdown
!!! note "タイトル"
    本文テキスト。
    複数行対応。

!!! warning
    タイトルなしも可。
```

**サポートタイプ:** `note`, `info`, `tip`, `success`, `warning`, `danger`, `failure`, `bug`, `example`, `quote`, `abstract`

出力HTML構造:
```html
<div class="admonition note">
  <p class="admonition-title">Note</p>
  <p>本文テキスト。</p>
</div>
```

#### 5.2 Docusaurus 形式

```markdown
:::note タイトル
本文テキスト。
:::

:::warning
タイトルなしも可。
:::
```

**サポートタイプ:** `note`, `tip`, `info`, `caution`, `danger`, `warning`

> `warning` は Docusaurus 公式仕様外だが、MkDocs との互換性のため追加サポート。

出力HTML構造:
```html
<div class="admonition note">
  <p class="admonition-title">Note</p>
  <p>本文テキスト。</p>
</div>
```

#### 5.3 Admonitions のスタイル

各タイプに対応した左ボーダーカラーとアイコンを CSS で定義する。

| タイプ | ボーダー色 | アイコン（絵文字） |
|---|---|---|
| `note` / `info` | 青 `#0969da` | 💡 |
| `tip` / `success` | 緑 `#1a7f37` | ✅ |
| `warning` / `caution` | 黄 `#9a6700` | ⚠️ |
| `danger` / `failure` | 赤 `#cf222e` | 🚨 |
| `bug` | 赤 `#cf222e` | 🐛 |
| `example` | 紫 `#8250df` | 📋 |
| `quote` / `abstract` | グレー `#6e7781` | 📝 |

---

### 6. コードコピーボタン

すべてのコードブロックにクリップボードコピーボタンを自動付与する。

**動作仕様:**

- コードブロック（`div.highlight` および `pre:not(.mermaid)`）にカーソルを乗せると右上にボタンが表示される
- クリックするとコードをクリップボードにコピーし、「✓ Copied」と表示（2 秒後に「Copy」に戻る）
- Mermaid 図ブロック（`pre.mermaid`）にはボタンを付与しない
- `navigator.clipboard` 未対応ブラウザでは `document.execCommand('copy')` にフォールバック

**実装方針:**

- スタイルは `assets/copy-button.css` にインライン埋め込み
- スクリプトは `<body>` 末尾に小さな即時実行関数（IIFE）として埋め込み
- 外部依存なし・オプションなし（常に有効）

---

### 7. ミニマップ（TOC / 目次サイドバー）

Markdown 内の `h1` 〜 `h6` 見出しから自動抽出し、画面右側上部に固定追従する目次サイドバーを生成する。

**機能仕様:**

- 見出しタグ（`<h1>`〜`<h6>`）に自動でアンカー ID を付与し、ミニマップからジャンプ可能にする
- ミニマップの表示位置: 本文（`.markdown-body`）の右側上部
- スクロール追従: CSS `position: sticky; top: 24px;` により、スクロール時も画面外にならず右側上部に常に留まる
- タイトル表示: 「ミニマップ」ヘッダータイトルは表示せず、目次リンク一覧をシンプルに表示
- アンカー＆スクロール連動ハイライト: URL のアンカー (`#hash`) やスクロール位置に合致する見出し項目をアクティブ表示 (`.active`)
- レスポンシブ対応: 画面幅 `1024px` 以下のモバイル・タブレット環境ではカード表示に最適化
- 無効化オプション: CLI `--no-minimap` (`--no-toc`) または API `no_minimap=True` で非表示化可能

---

## 出力HTMLの構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{タイトル}</title>
  <style>
    /* GitHub/GitLab スタイル CSS */
    /* Admonitions CSS */
    /* コピーボタン CSS */
    /* ミニマップ CSS */
    /* シンタックスハイライト CSS */
  </style>
</head>
<body>
  <div class="app-container">
    <div class="markdown-body">
      <!-- 変換されたHTML本文 -->
    </div>
    <aside class="minimap-wrapper" aria-label="ミニマップ">
      <nav class="minimap">
        <ul class="minimap-list">
          <!-- 見出しリンク一覧 -->
        </ul>
      </nav>
    </aside>
  </div>
  <script>/* コピーボタン IIFE */</script>
  <script>
    /* Mermaid JS（インライン埋め込み） */
    mermaid.initialize({ startOnLoad: true, theme: '...' });
  </script>
  <script>/* ミニマップ連動スクリプト IIFE */</script>
</body>
</html>
```

---

## 非機能要件

| 項目 | 要件 |
|---|---|
| 出力形式 | シングルファイルHTML（外部依存なし） |
| 文字コード | UTF-8 固定 |
| 標準入力 | `-` を INPUT に指定することで stdin から読み込み可 |
| エラー処理 | 変換エラー時は標準エラーにメッセージを出力し、終了コード 1 で終了 |
| 依存ライブラリ | Python 標準ライブラリ + 明示的に `requirements.txt` で管理 |
