---
name: admonition-processing
description: >-
  Use this skill when adding, modifying, or fixing Admonition blocks (MkDocs `!!!` and Docusaurus `:::` syntax),
  handling indentation/nesting rules, or updating admonition styling and icons.
---

# Admonition Processing Skill

[`src/md2html/admonition.py`](file:///home/ynaka/gitlab/md2html/src/md2html/admonition.py) における注意書き（Admonitions）ブロックの解析と HTML 生成に関するガイドです。

## 1. サポートする構文仕様

### MkDocs 形式
- 記法: `!!! <type> ["タイトル"]` または `!!! <type>`
- 後続行は4文字以上のインデントで本文を記述。空行後もインデントが維持される限り同一ブロックとして扱う。
- サポートタイプ: `note`, `info`, `tip`, `success`, `warning`, `danger`, `failure`, `bug`, `example`, `quote`, `abstract`

```markdown
!!! note "カスタムタイトル"
    ここが本文です。
    複数行記述可能。

!!! warning
    タイトル省略時は自動的に "Warning" と補完されます。
```

### Docusaurus 形式
- 記法: `:::<type>[ タイトル]` 〜 `:::`
- サポートタイプ: `note`, `tip`, `info`, `caution`, `danger`, `warning`

```markdown
:::caution 注意事項
Docusaurus 形式では終了タグ `:::` までの行が本文となります。
:::
```

## 2. 処理アーキテクチャ

1. **プリプロセス実行**: Mistune のパース前に、入力テキスト全体に対して正規表現でマッチングを行い、対応する HTML 構造へ変換します。
2. **インデント保持**: 本文がリスト項目や引用ブロック内にネストされている場合、ベースインデントを保持して外側の構文が壊れないように配慮します。
3. **出力 HTML 構造**:
   ```html
   <div class="admonition <type>">
     <div class="admonition-title"><span class="admonition-icon">...</span>タイトル</div>
     <div class="admonition-content">
       本文テキスト
     </div>
   </div>
   ```

## 3. スタイルとの連動

タイプごとのボーダー色、背景色、および絵文字アイコンの定義は [`src/md2html/assets/admonition.css`](file:///home/ynaka/gitlab/md2html/src/md2html/assets/admonition.css) に集約されています。
新しいタイプを追加する場合は、`admonition.py` 内の Set 定義（`MKDOCS_TYPES` / `DOCUSAURUS_TYPES`）と `admonition.css` の双方にスタイルルールを追加してください。

## 4. テストと検証

```bash
# Admonition 関連テスト全件実行
pytest tests/test_admonition.py -v

# MkDocs / Docusaurus のサンプルフィクスチャを用いた検証
pytest tests/test_converter.py -k "admonition" -v
```
