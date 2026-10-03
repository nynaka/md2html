---
name: minimap-toc
description: >-
  Use this skill when working on the minimap (TOC sidebar), heading parsing (h1-h6),
  anchor ID and slug generation (including multi-byte Japanese characters), or scroll-spy JS/CSS.
---

# Minimap (TOC) & Heading Parsing Skill

[`src/md2html/minimap.py`](file:///home/ynaka/gitlab/md2html/src/md2html/minimap.py) は、HTML ドキュメント内の見出し（`<h1>`〜`<h6>`）を自動抽出し、右側固定の目次サイドバー（ミニマップ）およびスクロール連動スクリプトを生成します。

## 1. 処理フロー

```text
[変換済み body HTML]
       │
       ▼
1. 見出しタグ走査 (_HEADING_RE)
   - 既存の id 属性があればそれを採用
   - 無ければ見出しテキストから _slugify() で ID を生成
       │
       ▼
2. アンカー ID 自動注入
   - 重複 ID の回避 (例: slug, slug-1, slug-2)
   - 見出しタグに id="..." を付与して再構築
       │
       ▼
3. ミニマップ HTML 構築
   - <aside class="minimap"> ... </aside> を生成
   - 各見出しレベル (h1〜h6) に応じたインデントクラス (.level-1〜.level-6) を適用
       │
       ▼
4. スクロール連動スクリプト注入 (minimap_script_tag)
   - IntersectionObserver による閲覧中セクションのハイライト同期
```

## 2. スラッグ生成規則 (`_slugify`)

- 空白文字（半角スペース、タブ、改行）をハイフン `-` に置換。
- 日本語（ひらがな、カタカナ、漢字、全角記号）および英数字・アンダースコア・ハイフンを保持。
- 記号類（HTML 特殊文字、マークアップタグ）は事前に除去。
- 空白のみの見出しなどの場合はデフォルトで `"heading"` をフォールバック。
- 同一文書内に同じスラッグが複数回出現した場合は、自動的に `-1`, `-2` の連番サフィックスを付与して重複を解消。

## 3. ミニマップの無効化制御

CLI オプション `--no-minimap` または `--no-toc` が指定された場合：
- `converter.py` は `process_headings_and_build_minimap()` の呼び出しをスキップ、または `minimap_html` と `minimap_script_tag()` の注入を行いません。
- 生成される HTML の DOM に `<aside class="minimap">` や関連スクリプトが含まれないことを保証します。

## 4. テストと検証

```bash
# ミニマップ単体テスト
pytest tests/test_minimap.py -v

# 重複見出しや日本語見出しのアンカーテスト
pytest tests/test_minimap.py -k "slug or duplicate or japanese" -v
```
