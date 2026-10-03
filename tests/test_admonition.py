"""Tests for Admonitions: MkDocs and Docusaurus syntax."""

import os

import pytest
from bs4 import BeautifulSoup

from md2html.admonition import preprocess_admonitions
from md2html.converter import convert


def soup_admonition(html, admon_type):
    return BeautifulSoup(html, "lxml").find("div", class_=f"admonition {admon_type}")


# ---------------------------------------------------------------------------
# MkDocs  !!!  syntax
# ---------------------------------------------------------------------------


class TestMkDocs:
    def test_note_with_title(self):
        md = '!!! note "My Note"\n    Content here.\n'
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        div = s.find("div", class_="admonition note")
        assert div is not None
        assert s.find("p", class_="admonition-title").text == "My Note"

    def test_warning_without_title_uses_type_name(self):
        md = "!!! warning\n    Watch out.\n"
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_="admonition warning") is not None
        title = s.find("p", class_="admonition-title")
        assert title.text == "Warning"

    def test_multiline_body(self):
        md = '!!! info "Info"\n    Line one.\n    Line two.\n'
        html = preprocess_admonitions(md)
        assert "Line one" in html
        assert "Line two" in html

    @pytest.mark.parametrize(
        "admon_type",
        [
            "note",
            "info",
            "tip",
            "success",
            "warning",
            "danger",
            "failure",
            "bug",
            "example",
            "quote",
            "abstract",
        ],
    )
    def test_all_mkdocs_types(self, admon_type):
        md = f"!!! {admon_type}\n    body\n"
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_=f"admonition {admon_type}") is not None

    def test_admonition_css_in_output(self):
        html = convert('!!! note "Test"\n    body\n')
        assert "admonition" in html

    def test_admonition_css_border_classes_present(self):
        html = convert("!!! warning\n    body\n")
        # admonition.css should define the .admonition.warning rule
        assert ".admonition.warning" in html

    def test_fixture_mkdocs(self):
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "admonition_mkdocs.md")
        with open(fixture, encoding="utf-8") as fh:
            md = fh.read()
        html = convert(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_="admonition note") is not None
        assert s.find("div", class_="admonition warning") is not None


# ---------------------------------------------------------------------------
# Docusaurus  :::  syntax
# ---------------------------------------------------------------------------


class TestDocusaurus:
    def test_note_with_title(self):
        md = ":::note My Note\nContent here.\n:::"
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_="admonition note") is not None
        assert s.find("p", class_="admonition-title").text == "My Note"

    def test_warning_without_title_uses_type_name(self):
        md = ":::warning\nWatch out.\n:::"
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_="admonition warning") is not None
        title = s.find("p", class_="admonition-title")
        assert title.text == "Warning"

    def test_multiline_body(self):
        md = ":::info\nLine one.\nLine two.\n:::"
        html = preprocess_admonitions(md)
        assert "Line one" in html
        assert "Line two" in html

    @pytest.mark.parametrize("admon_type", ["note", "tip", "info", "caution", "danger"])
    def test_all_docusaurus_types(self, admon_type):
        md = f":::{admon_type}\nbody\n:::"
        html = preprocess_admonitions(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_=f"admonition {admon_type}") is not None

    def test_unknown_type_left_unchanged(self):
        md = ":::unknown\nbody\n:::"
        result = preprocess_admonitions(md)
        assert ":::unknown" in result

    def test_missing_closing_tag_graceful(self):
        """Unclosed ::: block should not raise an exception."""
        md = ":::note\nNo closing tag"
        try:
            preprocess_admonitions(md)
        except Exception as exc:
            pytest.fail(f"Raised exception on unclosed block: {exc}")

    def test_fixture_docusaurus(self):
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "admonition_docusaurus.md")
        with open(fixture, encoding="utf-8") as fh:
            md = fh.read()
        html = convert(md)
        s = BeautifulSoup(html, "lxml")
        assert s.find("div", class_="admonition note") is not None
        assert s.find("div", class_="admonition warning") is not None


# ---------------------------------------------------------------------------
# Mixed: both formats together
# ---------------------------------------------------------------------------


def test_mixed_formats_both_converted():
    md = (
        '!!! note "MkDocs Note"\n'
        "    mkdocs content\n"
        "\n"
        ":::tip Docusaurus Tip\n"
        "docusaurus content\n"
        ":::\n"
    )
    html = convert(md)
    s = BeautifulSoup(html, "lxml")
    assert s.find("div", class_="admonition note") is not None
    assert s.find("div", class_="admonition tip") is not None


# ---------------------------------------------------------------------------
# Indented admonitions (in lists, blockquotes, etc.)
# ---------------------------------------------------------------------------


def test_indented_mkdocs_in_list():
    md = '- item 1\n  !!! note "List Note"\n      Line 1\n      Line 2\n- item 2\n'
    html = convert(md)
    s = BeautifulSoup(html, "lxml")
    li = s.find("li")
    assert li is not None
    div = li.find("div", class_="admonition note")
    assert div is not None
    assert "Line 1" in div.text
    assert "Line 2" in div.text


def test_indented_docusaurus_in_list():
    md = "- item 1\n  :::tip Tip in List\n  Tip content\n  :::\n- item 2\n"
    html = convert(md)
    s = BeautifulSoup(html, "lxml")
    li = s.find("li")
    assert li is not None
    div = li.find("div", class_="admonition tip")
    assert div is not None
    assert "Tip content" in div.text


def test_indented_admonition_with_table():
    md = (
        "- item 1\n"
        '  !!! note "Table Note"\n'
        "      | H1 | H2 |\n"
        "      | --- | --- |\n"
        "      | V1 | V2 |\n"
    )
    html = convert(md)
    s = BeautifulSoup(html, "lxml")
    li = s.find("li")
    assert li is not None
    table = li.find("table")
    assert table is not None
    assert table.find("th").text == "H1"
