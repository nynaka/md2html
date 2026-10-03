"""Tests for Mermaid diagram rendering."""

import os

from bs4 import BeautifulSoup

from md2html.converter import convert


def soup(html):
    return BeautifulSoup(html, "lxml")


def test_mermaid_block_becomes_pre_element():
    md = "```mermaid\nflowchart TD\n    A --> B\n```"
    html = convert(md)
    s = soup(html)
    pre = s.find("pre", class_="mermaid")
    assert pre is not None


def test_mermaid_pre_contains_diagram_source():
    md = "```mermaid\nflowchart TD\n    A --> B\n```"
    html = convert(md)
    s = soup(html)
    pre = s.find("pre", class_="mermaid")
    assert "flowchart TD" in pre.get_text()


def test_mermaid_script_tag_present():
    html = convert("```mermaid\nflowchart TD\n    A --> B\n```")
    s = soup(html)
    scripts = s.find_all("script")
    assert len(scripts) > 0


def test_mermaid_initialize_in_script():
    html = convert("```mermaid\nflowchart TD\n    A --> B\n```")
    assert "mermaid.initialize" in html
    assert "startOnLoad" in html


def test_mermaid_dark_theme_in_script():
    html = convert("```mermaid\nflowchart TD\n    A --> B\n```")
    assert "dark" in html


def test_mermaid_script_before_body_close():
    html = convert("```mermaid\nflowchart TD\n    A --> B\n```")
    script_pos = html.rfind("<script")
    body_close_pos = html.find("</body>")
    assert script_pos < body_close_pos


def test_no_mermaid_flag_renders_code_block():
    md = "```mermaid\nflowchart TD\n    A --> B\n```"
    html = convert(md, no_mermaid=True)
    s = soup(html)
    assert s.find("pre", class_="mermaid") is None
    # should fall back to a regular code block
    assert s.find("pre") is not None


def test_no_mermaid_flag_omits_script():
    html = convert("```mermaid\nflowchart TD\n    A --> B\n```", no_mermaid=True)
    assert "mermaid.initialize" not in html


def test_sequence_diagram():
    md = "```mermaid\nsequenceDiagram\n    Alice->>Bob: Hi\n```"
    html = convert(md)
    s = soup(html)
    assert s.find("pre", class_="mermaid") is not None
    assert "sequenceDiagram" in s.find("pre", class_="mermaid").get_text()


def test_gantt_chart():
    md = "```mermaid\ngantt\n    title Test\n    dateFormat YYYY-MM-DD\n```"
    html = convert(md)
    s = soup(html)
    assert s.find("pre", class_="mermaid") is not None


def test_fixture_mermaid():
    fixture = os.path.join(os.path.dirname(__file__), "fixtures", "mermaid.md")
    with open(fixture, encoding="utf-8") as fh:
        md = fh.read()
    html = convert(md)
    s = soup(html)
    mermaid_blocks = s.find_all("pre", class_="mermaid")
    assert len(mermaid_blocks) >= 3
