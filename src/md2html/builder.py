"""Multi-file crawler and directory site builder for md2html."""

import os
import shutil
import urllib.parse
from collections import deque

from bs4 import BeautifulSoup

from .converter import convert

MD_EXTENSIONS = {".md", ".markdown"}


def _is_local_relative(url_path: str) -> bool:
    """Check if a URL path is a local relative file path (not external or absolute)."""
    if not url_path:
        return False
    parsed = urllib.parse.urlsplit(url_path)
    if parsed.scheme or parsed.netloc or url_path.startswith("//"):
        return False
    path = parsed.path
    if not path or path.startswith("/"):
        return False
    return True


def _rewrite_links_and_collect(
    html: str,
    current_md_path: str,
    html_out_path: str,
) -> tuple[str, list[str], list[tuple[str, str]]]:
    """Parse HTML, rewrite .md links to .html, and collect linked .md files and assets to copy.

    Returns:
        (rewritten_html, linked_md_abs_paths, assets_to_copy)
        assets_to_copy is a list of (src_abs_path, dst_abs_path)
    """
    soup = BeautifulSoup(html, "html.parser")
    linked_md_paths = []
    assets_to_copy = []

    current_dir = os.path.dirname(os.path.abspath(current_md_path))
    current_out_dir = os.path.dirname(os.path.abspath(html_out_path))

    # Process <a> tags
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not _is_local_relative(href):
            continue

        parsed = urllib.parse.urlsplit(href)
        raw_path = urllib.parse.unquote(parsed.path)
        target_abs = os.path.normpath(os.path.join(current_dir, raw_path))

        ext = os.path.splitext(raw_path)[1].lower()
        if ext in MD_EXTENSIONS:
            if os.path.isfile(target_abs):
                linked_md_paths.append(target_abs)
                new_path = os.path.splitext(raw_path)[0] + ".html"
                new_href = urllib.parse.urlunsplit(
                    (parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment)
                )
                a["href"] = new_href
        else:
            # Non-markdown file (e.g. PDF, zip, image linked via <a>)
            if os.path.isfile(target_abs):
                dst_abs = os.path.normpath(os.path.join(current_out_dir, raw_path))
                assets_to_copy.append((target_abs, dst_abs))

    # Process embedded media tags (<img>, <source>, <video>, <audio>)
    for tag in soup.find_all(["img", "source", "video", "audio"], src=True):
        src = tag["src"]
        if not _is_local_relative(src):
            continue

        parsed = urllib.parse.urlsplit(src)
        raw_path = urllib.parse.unquote(parsed.path)
        target_abs = os.path.normpath(os.path.join(current_dir, raw_path))

        if os.path.isfile(target_abs):
            dst_abs = os.path.normpath(os.path.join(current_out_dir, raw_path))
            assets_to_copy.append((target_abs, dst_abs))

    return str(soup), linked_md_paths, assets_to_copy


def build_site(
    entry_md_path: str,
    output_dir: str,
    title: str | None = None,
    theme: str = "github",
    highlight_style: str = "default",
    no_highlight: bool = False,
    no_mermaid: bool = False,
    mode: str = "auto",
    no_minimap: bool = False,
) -> dict[str, list[str]]:
    """Recursively convert entry Markdown and all linked Markdowns to HTML.

    Copy any linked non-markdown files to output_dir preserving relative paths.

    Returns:
        {"html": [list of generated html file paths], "assets": [list of copied asset paths]}
    """
    entry_abs = os.path.abspath(entry_md_path)
    if not os.path.isfile(entry_abs):
        raise FileNotFoundError(f"Entry markdown file not found: {entry_md_path}")

    out_dir_abs = os.path.abspath(output_dir)
    os.makedirs(out_dir_abs, exist_ok=True)

    # 1. Discover all reachable markdown files to establish common root
    all_md_files: set[str] = set()
    queue = deque([entry_abs])
    all_md_files.add(entry_abs)

    while queue:
        curr_md = queue.popleft()
        try:
            with open(curr_md, encoding="utf-8") as fh:
                content = fh.read()
        except OSError:
            continue

        curr_dir = os.path.dirname(curr_md)
        # Fast extraction of markdown links using BeautifulSoup on initial conversion
        # or scanning markdown link patterns
        # Using convert() to ensure accurate links parsed
        temp_html = convert(
            content,
            theme=theme,
            highlight_style=highlight_style,
            no_highlight=no_highlight,
            no_mermaid=no_mermaid,
            mode=mode,
            no_minimap=no_minimap,
        )
        soup = BeautifulSoup(temp_html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not _is_local_relative(href):
                continue
            parsed = urllib.parse.urlsplit(href)
            raw_path = urllib.parse.unquote(parsed.path)
            ext = os.path.splitext(raw_path)[1].lower()
            if ext in MD_EXTENSIONS:
                target_abs = os.path.normpath(os.path.join(curr_dir, raw_path))
                if os.path.isfile(target_abs) and target_abs not in all_md_files:
                    all_md_files.add(target_abs)
                    queue.append(target_abs)

    # Determine common root for mapping to output directory
    entry_dir = os.path.dirname(entry_abs)
    # If all md files are within entry_dir, use entry_dir as root so entry is at top level
    is_sub = all(
        os.path.abspath(f).startswith(entry_dir + os.sep) or f == entry_abs for f in all_md_files
    )
    if is_sub:
        common_root = entry_dir
    else:
        common_root = os.path.commonpath(list(all_md_files))

    generated_html_files = []
    copied_asset_files = set()

    # 2. Convert each Markdown and copy assets
    for md_abs in all_md_files:
        rel_from_root = os.path.relpath(md_abs, common_root)
        html_rel = os.path.splitext(rel_from_root)[0] + ".html"
        html_out_path = os.path.normpath(os.path.join(out_dir_abs, html_rel))

        os.makedirs(os.path.dirname(html_out_path), exist_ok=True)

        with open(md_abs, encoding="utf-8") as fh:
            md_text = fh.read()

        doc_title = title if (md_abs == entry_abs and title) else None

        raw_html = convert(
            md_text,
            title=doc_title or "",
            theme=theme,
            highlight_style=highlight_style,
            no_highlight=no_highlight,
            no_mermaid=no_mermaid,
            mode=mode,
            no_minimap=no_minimap,
        )

        final_html, _, assets_to_copy = _rewrite_links_and_collect(
            raw_html,
            current_md_path=md_abs,
            html_out_path=html_out_path,
        )

        with open(html_out_path, "w", encoding="utf-8") as fh:
            fh.write(final_html)

        generated_html_files.append(html_out_path)

        # Copy assets
        for src_path, dst_path in assets_to_copy:
            if dst_path not in copied_asset_files:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                copied_asset_files.add(dst_path)

    return {
        "html": generated_html_files,
        "assets": sorted(copied_asset_files),
    }
