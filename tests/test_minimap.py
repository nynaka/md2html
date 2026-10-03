"""Tests for minimap (Table of Contents) sidebar feature."""

from bs4 import BeautifulSoup

from md2html.cli import parse_args
from md2html.converter import convert
from md2html.minimap import process_headings_and_build_minimap


def soup(html):
    return BeautifulSoup(html, "lxml")


def test_minimap_heading_id_generation():
    html_in = "<h1>Heading One</h1><h2>Heading Two</h2><h3>Heading Three</h3>"
    mod_html, minimap_html = process_headings_and_build_minimap(html_in)
    s_body = soup(mod_html)
    assert s_body.find("h1")["id"] == "Heading-One"
    assert s_body.find("h2")["id"] == "Heading-Two"
    assert s_body.find("h3")["id"] == "Heading-Three"

    s_map = soup(minimap_html)
    items = s_map.find_all("li", class_="minimap-item")
    assert len(items) == 3
    assert items[0]["class"] == ["minimap-item", "level-1"]
    assert items[1]["class"] == ["minimap-item", "level-2"]
    assert items[2]["class"] == ["minimap-item", "level-3"]


def test_minimap_duplicate_heading_ids():
    html_in = "<h1>Test</h1><h1>Test</h1>"
    mod_html, minimap_html = process_headings_and_build_minimap(html_in)
    s_body = soup(mod_html)
    h1s = s_body.find_all("h1")
    assert h1s[0]["id"] == "Test"
    assert h1s[1]["id"] == "Test-1"


def test_minimap_preserve_existing_id():
    html_in = '<h2 id="my-custom-id">Custom Header</h2>'
    mod_html, _ = process_headings_and_build_minimap(html_in)
    s_body = soup(mod_html)
    assert s_body.find("h2")["id"] == "my-custom-id"


def test_minimap_all_heading_levels_h1_to_h6():
    md = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n"
    html = convert(md)
    s = soup(html)
    minimap = s.find("aside", class_="minimap-wrapper")
    assert minimap is not None
    for level in range(1, 7):
        item = minimap.find("li", class_=f"minimap-item level-{level}")
        assert item is not None
        assert f"H{level}" in item.text


def test_convert_no_minimap_flag():
    md = "# Heading\nSome text."
    html_with = convert(md, no_minimap=False)
    html_without = convert(md, no_minimap=True)

    assert soup(html_with).find("aside", class_="minimap-wrapper") is not None
    assert soup(html_without).find("aside", class_="minimap-wrapper") is None


def test_no_headings_no_minimap_wrapper():
    md = "Just plain text without any headings."
    html = convert(md)
    s = soup(html)
    assert s.find("aside", class_="minimap-wrapper") is None


def test_cli_parse_no_minimap_flag():
    assert parse_args(["input.md", "--no-minimap"]).no_minimap is True
    assert parse_args(["input.md", "--no-toc"]).no_minimap is True
    assert parse_args(["input.md", "--disable-minimap"]).no_minimap is True


def test_minimap_has_no_title_header():
    md = "# Section Title\nSome content"
    html = convert(md)
    s = soup(html)
    minimap = s.find("aside", class_="minimap-wrapper")
    assert minimap is not None
    assert minimap.find("div", class_="minimap-title") is None


def test_docusaurus_frontmatter_stripped():
    md = (
        "---\n"
        "id: doc1\n"
        'title: "Docusaurus Title"\n'
        "sidebar_label: Label\n"
        "---\n\n"
        "# Actual Heading\n"
        "Body content here."
    )
    html = convert(md)
    s = soup(html)
    # Frontmatter text should not appear as raw HTML body text
    assert "sidebar_label" not in html
    assert "id: doc1" not in html

    # Page title tag should extract title from frontmatter
    assert s.find("title").text == "Docusaurus Title"

    # Minimap should only contain the actual heading
    minimap = s.find("aside", class_="minimap-wrapper")
    items = minimap.find_all("li", class_="minimap-item")
    assert len(items) == 1
    assert items[0].text == "Actual Heading"
