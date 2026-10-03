"""Tests for core Markdown→HTML conversion."""

import os

import pytest
from bs4 import BeautifulSoup

from md2html.converter import convert


def soup(html):
    return BeautifulSoup(html, "lxml")


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_output_starts_with_doctype():
    html = convert("# Hello")
    assert html.strip().startswith("<!DOCTYPE html>")


def test_output_has_markdown_body_wrapper():
    html = convert("# Hello")
    s = soup(html)
    assert s.find("div", class_="markdown-body") is not None


def test_title_from_argument():
    html = convert("# Hello", title="My Page")
    s = soup(html)
    assert s.find("title").text == "My Page"


def test_title_default_when_omitted():
    html = convert("# Hello")
    s = soup(html)
    # title should exist even if content is empty string or "Untitled"
    assert s.find("title") is not None


def test_charset_utf8():
    html = convert("こんにちは")
    s = soup(html)
    meta = s.find("meta", {"charset": True})
    assert meta is not None
    assert meta["charset"].lower() == "utf-8"


def test_viewport_meta():
    html = convert("x")
    s = soup(html)
    assert s.find("meta", {"name": "viewport"}) is not None


# ---------------------------------------------------------------------------
# Markdown elements
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("level", range(1, 7))
def test_headings(level):
    md = "#" * level + " Heading"
    html = convert(md)
    s = soup(html)
    assert s.find(f"h{level}") is not None


def test_paragraph():
    html = convert("Simple paragraph.")
    s = soup(html)
    assert s.find("p") is not None


def test_bold():
    html = convert("**bold text**")
    s = soup(html)
    assert s.find("strong") is not None


def test_italic():
    html = convert("*italic text*")
    s = soup(html)
    assert s.find("em") is not None


def test_strikethrough():
    html = convert("~~strike~~")
    s = soup(html)
    assert s.find("del") is not None


def test_unordered_list():
    html = convert("- a\n- b\n- c")
    s = soup(html)
    assert s.find("ul") is not None
    assert len(s.find("ul").find_all("li")) == 3


def test_ordered_list():
    html = convert("1. first\n2. second")
    s = soup(html)
    assert s.find("ol") is not None


def test_nested_list():
    md = "- a\n  - b\n  - c"
    html = convert(md)
    s = soup(html)
    assert len(s.find_all("ul")) >= 2


def test_table_gfm():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    html = convert(md)
    s = soup(html)
    assert s.find("table") is not None
    assert s.find("th") is not None
    assert s.find("td") is not None


def test_link():
    html = convert("[click](https://example.com)")
    s = soup(html)
    a = s.find("a")
    assert a is not None
    assert a["href"] == "https://example.com"


def test_image():
    html = convert("![alt](https://example.com/img.png)")
    s = soup(html)
    img = s.find("img")
    assert img is not None
    assert img["src"] == "https://example.com/img.png"


def test_inline_code():
    html = convert("Use `print()` function")
    s = soup(html)
    assert s.find("code") is not None


def test_blockquote():
    html = convert("> A quote")
    s = soup(html)
    assert s.find("blockquote") is not None


def test_horizontal_rule():
    html = convert("---")
    s = soup(html)
    assert s.find("hr") is not None


def test_html_passthrough():
    html = convert('<div class="raw">content</div>')
    assert 'class="raw"' in html


# ---------------------------------------------------------------------------
# CSS embedding
# ---------------------------------------------------------------------------


def test_style_tag_in_head():
    html = convert("x")
    s = soup(html)
    head = s.find("head")
    assert head.find("style") is not None


def test_fixture_basic_md(tmp_path):
    """Integration: convert the basic fixture without errors."""
    fixture = os.path.join(os.path.dirname(__file__), "fixtures", "basic.md")
    with open(fixture, encoding="utf-8") as fh:
        md = fh.read()
    html = convert(md, title="Basic")
    s = soup(html)
    assert s.find("h1") is not None
    assert s.find("table") is not None


# ---------------------------------------------------------------------------
# CSS theme (Phase 3)
# ---------------------------------------------------------------------------


def test_theme_github_css_in_style():
    html = convert("x", theme="github")
    assert "markdown-body" in html
    assert "--color-canvas-default" in html  # github CSS variable


def test_theme_gitlab_css_in_style():
    html = convert("x", theme="gitlab")
    assert "--gl-color-canvas-default" in html  # gitlab CSS variable


def test_theme_auto_contains_both_themes():
    html = convert("x", theme="auto")
    assert "--color-canvas-default" in html
    assert "--gl-color-canvas-default" in html


def test_style_tag_in_head_github():
    html = convert("x", theme="github")
    s = soup(html)
    assert s.head.find("style") is not None


def test_admonition_css_always_included():
    """admonition.css should be present regardless of theme."""
    for theme in ("github", "gitlab", "auto"):
        html = convert("x", theme=theme)
        assert "admonition" in html, f"missing admonition css for theme={theme}"


def test_copy_button_css_present():
    html = convert("```python\nx=1\n```")
    assert "copy-btn" in html


def test_copy_button_script_present():
    html = convert("```python\nx=1\n```")
    assert "Copy" in html
    assert "clipboard" in html


def test_copy_button_plain_pre():
    """Plain code blocks (no lang) should also get a copy button."""
    html = convert("```\nplain\n```")
    assert "copy-btn" in html


def test_mode_auto_has_dark_media_query():
    html = convert("x", mode="auto")
    assert "prefers-color-scheme: dark" in html


def test_mode_light_no_dark_media_query():
    html = convert("x", mode="light")
    assert "prefers-color-scheme: dark" not in html


def test_mode_light_keeps_light_css_vars():
    html = convert("x", theme="github", mode="light")
    assert "--color-canvas-default" in html


def test_mode_dark_no_media_query():
    html = convert("x", mode="dark")
    assert "prefers-color-scheme: dark" not in html


def test_mode_dark_applies_dark_vars():
    html = convert("x", theme="github", mode="dark")
    # Dark-mode canvas colour should appear outside a media query
    assert "#0d1117" in html


# ---------------------------------------------------------------------------
# Syntax highlighting (Phase 4)
# ---------------------------------------------------------------------------


def test_highlight_css_included_by_default():
    html = convert("```python\nprint('hi')\n```")
    assert "highlight" in html


def test_highlight_python_block():
    html = convert("```python\ndef foo(): pass\n```")
    s = soup(html)
    assert s.find("div", class_="highlight") is not None


def test_highlight_javascript_block():
    html = convert("```javascript\nconst x = 1;\n```")
    s = soup(html)
    assert s.find("div", class_="highlight") is not None


def test_highlight_no_lang_plain():
    """Code block without language should not get highlight wrapper."""
    html = convert("```\nplain text\n```")
    s = soup(html)
    assert s.find("div", class_="highlight") is None
    assert s.find("pre") is not None


def test_highlight_css_absent_when_disabled():
    html = convert("```python\nprint('hi')\n```", no_highlight=True)
    s = soup(html)
    assert s.find("div", class_="highlight") is None


def test_highlight_xss_escape():
    """< > & in code must be escaped."""
    html = convert("```\n<script>alert(1)</script>\n```", no_highlight=True, no_mermaid=True)
    # The mermaid script tag is absent; any <script> would be unescaped user content
    pre = BeautifulSoup(html, "lxml").find("pre")
    assert "<script>" not in pre.decode_contents()
    assert "&lt;script&gt;" in pre.decode_contents()


def test_highlight_custom_style():
    html = convert("```python\nx=1\n```", highlight_style="monokai")
    assert "highlight" in html


# ---------------------------------------------------------------------------
# Integration tests (Phase 8)
# ---------------------------------------------------------------------------


def test_full_featured_document():
    """All features combined: headings, table, code, mermaid, admonitions."""
    md = (
        "# Title\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        "```python\nprint('hello')\n```\n\n"
        "```mermaid\nflowchart TD\n  A-->B\n```\n\n"
        '!!! note "Note"\n    body\n\n'
        ":::tip\ncontent\n:::\n"
    )
    html = convert(md, title="Full Test")
    s = soup(html)
    assert s.find("h1") is not None
    assert s.find("table") is not None
    assert s.find("div", class_="highlight") is not None
    assert s.find("pre", class_="mermaid") is not None
    assert s.find("div", class_="admonition note") is not None
    assert s.find("div", class_="admonition tip") is not None


def test_output_is_valid_utf8():
    html = convert("こんにちは世界 🎉")
    html.encode("utf-8")  # raises if not valid UTF-8


def test_output_file_written(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path

    src_root = str(Path(__file__).parent.parent / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src_root

    out_dir = tmp_path / "out_dir"
    md_file = tmp_path / "in.md"
    md_file.write_text("# Hello", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "md2html", str(md_file), str(out_dir)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert out_dir.exists()
    out_file = out_dir / "in.html"
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_nonexistent_file_exits_with_1(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path

    src_root = str(Path(__file__).parent.parent / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src_root

    result = subprocess.run(
        [sys.executable, "-m", "md2html", "/no/such/file.md"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 1
    assert "error" in result.stderr.lower()


def test_stdin_input(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path

    src_root = str(Path(__file__).parent.parent / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src_root

    result = subprocess.run(
        [sys.executable, "-m", "md2html", "-"],
        input="# From stdin",
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "<!DOCTYPE html>" in result.stdout
    assert "From stdin" in result.stdout


def test_table_in_list_conversion():
    md = "- item 1\n  | h1 | h2 |\n  | --- | --- |\n  | v1 | v2 |\n"
    html = convert(md)
    s = soup(html)
    li = s.find("li")
    assert li is not None
    assert li.find("table") is not None
    assert li.find("th").text == "h1"


def test_table_in_quote_conversion():
    md = "> | h1 | h2 |\n> | --- | --- |\n> | v1 | v2 |\n"
    html = convert(md)
    s = soup(html)
    blockquote = s.find("blockquote")
    assert blockquote is not None
    assert blockquote.find("table") is not None
    assert blockquote.find("th").text == "h1"


def test_complex_indented_list_admonition_table():
    md = (
        "1. List item 1\n"
        '   !!! note "Nested Note"\n'
        "       Inside note paragraph.\n\n"
        "       | Col A | Col B |\n"
        "       | --- | --- |\n"
        "       | Val A | Val B |\n"
    )
    html = convert(md)
    s = soup(html)
    ol = s.find("ol")
    assert ol is not None
    div = ol.find("div", class_="admonition note")
    assert div is not None
    assert "Inside note paragraph." in div.text
    table = div.find("table")
    assert table is not None
    assert table.find("th").text == "Col A"
