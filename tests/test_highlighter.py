"""Tests for syntax highlighting (Pygments integration)."""

import os

import pytest
from bs4 import BeautifulSoup

from md2html.converter import convert


def soup(html):
    return BeautifulSoup(html, "lxml")


@pytest.mark.parametrize(
    "lang",
    [
        "python",
        "javascript",
        "typescript",
        "bash",
        "sh",
        "sql",
        "json",
        "yaml",
        "go",
        "rust",
        "java",
        "c",
        "cpp",
        "html",
        "css",
    ],
)
def test_major_languages_highlighted(lang):
    md = f"```{lang}\ncode here\n```"
    html = convert(md)
    s = soup(html)
    assert s.find("div", class_="highlight") is not None, f"No highlight for {lang}"


def test_no_language_no_highlight():
    html = convert("```\nplain\n```")
    s = soup(html)
    assert s.find("div", class_="highlight") is None


def test_unknown_language_falls_back_gracefully():
    """Unknown language should not raise, falls back to plain text."""
    html = convert("```unknownlang\nsome code\n```")
    s = soup(html)
    assert s.find("pre") is not None


def test_highlight_css_in_style_block():
    html = convert("```python\nx=1\n```")
    s = soup(html)
    style = s.find("style")
    assert style is not None
    assert ".highlight" in style.string


def test_dark_mode_highlight_css_present():
    html = convert("```python\nx=1\n```")
    assert "prefers-color-scheme: dark" in html
    assert "github-dark" in html or ".highlight" in html


def test_no_highlight_skips_pygments_css():
    html = convert("```python\nx=1\n```", no_highlight=True)
    s = soup(html)
    assert s.find("div", class_="highlight") is None


def test_custom_highlight_style():
    html = convert("```python\nx=1\n```", highlight_style="monokai")
    s = soup(html)
    assert s.find("div", class_="highlight") is not None


def test_fixture_highlight(tmp_path):
    fixture = os.path.join(os.path.dirname(__file__), "fixtures", "highlight.md")
    with open(fixture, encoding="utf-8") as fh:
        md = fh.read()
    html = convert(md)
    s = soup(html)
    highlights = s.find_all("div", class_="highlight")
    assert len(highlights) >= 4  # python, javascript, bash, sql
