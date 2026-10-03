"""Tests for multi-file build and link-following feature in builder module."""

from bs4 import BeautifulSoup

from md2html.builder import build_site


def soup(html: str):
    return BeautifulSoup(html, "html.parser")


def test_single_markdown_to_dir(tmp_path):
    """Single markdown file should be converted to index.html/filename.html in output dir."""
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "dist"

    md_file = src / "README.md"
    md_file.write_text("# Hello World\nJust some content.", encoding="utf-8")

    built_files = build_site(str(md_file), str(out))

    assert (out / "README.html").exists()
    html = (out / "README.html").read_text(encoding="utf-8")
    s = soup(html)
    assert s.find("h1").text == "Hello World"
    assert str(out / "README.html") in built_files["html"]


def test_linked_markdown_converted(tmp_path):
    """Linked markdown files should be discovered and converted, with .md links updated to .html."""
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "dist"

    a_md = src / "a.md"
    b_md = src / "b.md"

    a_md.write_text("# Page A\nLink to [Page B](b.md#section-1).", encoding="utf-8")
    b_md.write_text("# Page B\nLink back to [Page A](a.md).", encoding="utf-8")

    build_site(str(a_md), str(out))

    assert (out / "a.html").exists()
    assert (out / "b.html").exists()

    a_html = (out / "a.html").read_text(encoding="utf-8")
    s_a = soup(a_html)
    link_to_b = s_a.find("a", href=True)
    assert link_to_b["href"] == "b.html#section-1"

    b_html = (out / "b.html").read_text(encoding="utf-8")
    s_b = soup(b_html)
    link_to_a = s_b.find("a", href=True)
    assert link_to_a["href"] == "a.html"


def test_subfolder_markdown_link(tmp_path):
    """Markdown in subdirectories should maintain relative directory structure."""
    src = tmp_path / "src"
    src.mkdir()
    sub = src / "docs"
    sub.mkdir()
    out = tmp_path / "dist"

    index_md = src / "index.md"
    spec_md = sub / "spec.md"

    index_md.write_text("# Top\nGo to [Spec](docs/spec.md).", encoding="utf-8")
    spec_md.write_text("# Spec\nBack to [Top](../index.md).", encoding="utf-8")

    build_site(str(index_md), str(out))

    assert (out / "index.html").exists()
    assert (out / "docs" / "spec.html").exists()

    top_html = (out / "index.html").read_text(encoding="utf-8")
    assert soup(top_html).find("a")["href"] == "docs/spec.html"

    spec_html = (out / "docs" / "spec.html").read_text(encoding="utf-8")
    assert soup(spec_html).find("a")["href"] == "../index.html"


def test_asset_file_copied_with_subdirectories(tmp_path):
    """Non-markdown files (images, PDFs, etc.) linked should be copied preserving path."""
    src = tmp_path / "src"
    src.mkdir()
    img_dir = src / "images"
    img_dir.mkdir()
    doc_dir = src / "assets"
    doc_dir.mkdir()
    out = tmp_path / "dist"

    img_file = img_dir / "diagram.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\nfake-png-data")

    pdf_file = doc_dir / "manual.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake-pdf-data")

    index_md = src / "index.md"
    index_md.write_text(
        "# Documents\n![Diagram](images/diagram.png)\nDownload [Manual](assets/manual.pdf).\n",
        encoding="utf-8",
    )

    built = build_site(str(index_md), str(out))

    assert (out / "index.html").exists()
    assert (out / "images" / "diagram.png").exists()
    assert (out / "images" / "diagram.png").read_bytes() == b"\x89PNG\r\n\x1a\nfake-png-data"

    assert (out / "assets" / "manual.pdf").exists()
    assert (out / "assets" / "manual.pdf").read_bytes() == b"%PDF-1.4 fake-pdf-data"

    # HTML image and link tags should preserve their relative paths
    html = (out / "index.html").read_text(encoding="utf-8")
    s = soup(html)
    assert s.find("img")["src"] == "images/diagram.png"
    assert s.find("a", href=True)["href"] == "assets/manual.pdf"

    assert str(out / "images" / "diagram.png") in built["assets"]
    assert str(out / "assets" / "manual.pdf") in built["assets"]


def test_external_and_anchor_links_untouched(tmp_path):
    """External URLs and same-page anchor links should not be rewritten or copied."""
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "dist"

    index_md = src / "index.md"
    index_md.write_text(
        "# Links\n"
        "[Google](https://google.com)\n"
        "[Doc](http://example.com/foo.md)\n"
        "[Section](#links)\n"
        "[Mail](mailto:test@example.com)\n",
        encoding="utf-8",
    )

    build_site(str(index_md), str(out))

    html = (out / "index.html").read_text(encoding="utf-8")
    s = soup(html)
    hrefs = [a["href"] for a in s.find_all("a", href=True)]

    assert "https://google.com" in hrefs
    assert "http://example.com/foo.md" in hrefs
    assert "#links" in hrefs
    assert "mailto:test@example.com" in hrefs


def test_circular_links(tmp_path):
    """Circular links should not cause infinite recursion."""
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "dist"

    f1 = src / "1.md"
    f2 = src / "2.md"
    f3 = src / "3.md"

    f1.write_text("[Go to 2](2.md)", encoding="utf-8")
    f2.write_text("[Go to 3](3.md)", encoding="utf-8")
    f3.write_text("[Go to 1](1.md)", encoding="utf-8")

    build_site(str(f1), str(out))

    assert (out / "1.html").exists()
    assert (out / "2.html").exists()
    assert (out / "3.html").exists()


def test_nested_subfolder_assets_and_title(tmp_path):
    """Deeply nested markdown referencing assets and custom title handling."""
    src = tmp_path / "src"
    src.mkdir()
    docs = src / "docs"
    docs.mkdir()
    img_dir = docs / "images"
    img_dir.mkdir()
    out = tmp_path / "dist"

    img = img_dir / "sub_img.png"
    img.write_bytes(b"image-content")

    main_md = src / "README.md"
    sub_md = docs / "guide.md"

    main_md.write_text("# Main\n[Guide](docs/guide.md)", encoding="utf-8")
    sub_md.write_text(
        "---\ntitle: Sub Guide\n---\n# Guide\n![Sub](images/sub_img.png)\n",
        encoding="utf-8",
    )

    build_site(str(main_md), str(out), title="Custom Main Title")

    assert (out / "README.html").exists()
    assert (out / "docs" / "guide.html").exists()
    assert (out / "docs" / "images" / "sub_img.png").exists()

    main_html = (out / "README.html").read_text(encoding="utf-8")
    assert soup(main_html).find("title").text == "Custom Main Title"

    sub_html = (out / "docs" / "guide.html").read_text(encoding="utf-8")
    assert soup(sub_html).find("title").text == "Sub Guide"
    assert soup(sub_html).find("img")["src"] == "images/sub_img.png"
