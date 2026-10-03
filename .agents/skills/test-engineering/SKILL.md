---
name: test-engineering
description: >-
  Use this skill when designing, writing, or running tests (pytest, tox, coverage),
  creating Markdown fixtures, asserting HTML DOM structures with BeautifulSoup, or running linter/formatters.
---

# Test Engineering Skill

`md2html` のテスト設計、DOM 構造検証、自動化（tox）、カバレッジ計測、および品質チェックに関するガイドです。

## 1. テスト環境とツール

- **テストフレームワーク**: `pytest` (>= 8.0.0)
- **テスト自動化 / 多環境テスト**: `tox` (>= 4.0.0)
- **HTML DOM 検証**: `beautifulsoup4` (>= 4.12.0) + `lxml`
- **カバレッジ計測**: `pytest-cov` (>= 5.0.0)
- **Linter / Formatter**: `ruff` (>= 0.4.0), `flake8` (>= 7.0.0)

## 2. HTML DOM アサーションの定石パターン

文字列の部分一致（`in html`）だけでなく、`BeautifulSoup` を使用して階層構造や属性を厳密に検証します。

```python
from bs4 import BeautifulSoup
from md2html.converter import convert

def test_example_heading():
    md = "# 見出し 1"
    html = convert(md)
    soup = BeautifulSoup(html, "html.parser")
    
    # 見出し要素の検証
    h1 = soup.find("h1")
    assert h1 is not None
    assert h1.text == "見出し 1"
    assert h1.get("id") == "見出し-1"
    
    # ミニマップ内のリンク検証
    minimap_link = soup.select_one("aside.minimap a[href='#見出し-1']")
    assert minimap_link is not None
```

## 3. テストフィクスチャの活用

`tests/fixtures/` 配下の Markdown ファイルを利用して、包括的な変換テストを実施します。
- `basic.md`: CommonMark 標準要素
- `admonition_mkdocs.md`: MkDocs 形式
- `admonition_docusaurus.md`: Docusaurus 形式
- `mermaid.md`: 各種 Mermaid ダイアグラム
- `highlight.md`: 各種プログラミング言語のコードブロック

```python
def test_fixture_conversion(read_fixture):
    text = read_fixture("basic.md")
    html = convert(text)
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("table") is not None
```

## 4. TDD ワークフロー

1. **Red**: 要求仕様またはバグ再現条件を反映したテスト関数を `tests/test_*.py` に追加し、失敗することを確認。
2. **Green**: `src/md2html/` 配下のコードを実装し、テストを全件パスさせる。
3. **Refactor & Lint**:
   ```bash
   # 自動フォーマット
   ruff format src/ tests/

   # Lint チェック
   ruff check src/ tests/
   flake8 src/ tests/

   # tox による最終検証
   tox
   ```
