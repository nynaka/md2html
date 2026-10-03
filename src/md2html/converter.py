"""Core Markdown → HTML conversion."""

import os
import re

import mistune
from mistune.plugins.table import table, table_in_list, table_in_quote
from pygments.formatters import HtmlFormatter

from .admonition import preprocess_admonitions
from .highlighter import HighlightRenderer
from .mermaid import MermaidRenderer, mermaid_script_tag
from .minimap import minimap_script_tag, process_headings_and_build_minimap

# Matches a top-level @media (prefers-color-scheme: dark) { ... } block,
# allowing one level of nesting (e.g. :root { } or .selector { }).
_DARK_MEDIA_RE = re.compile(
    r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{((?:[^{}]|\{[^{}]*\})*)\}",
    re.DOTALL,
)


def _load_asset(filename: str) -> str:
    """Read a bundled asset file and return its content as a string."""
    assets_path = os.path.join(os.path.dirname(__file__), "assets", filename)
    with open(assets_path, encoding="utf-8") as fh:
        return fh.read()


def _strip_dark_media(css: str) -> str:
    """Remove all @media (prefers-color-scheme: dark) blocks from CSS."""
    return _DARK_MEDIA_RE.sub("", css).strip()


def _unwrap_dark_media(css: str) -> str:
    """Strip @media dark wrappers so their inner rules apply unconditionally."""
    return _DARK_MEDIA_RE.sub(lambda m: m.group(1).strip(), css)


def _apply_mode(css: str, mode: str) -> str:
    """Adjust a CSS string based on the requested colour mode."""
    if mode == "light":
        return _strip_dark_media(css)
    if mode == "dark":
        return _unwrap_dark_media(css)
    return css  # auto: keep media queries as-is


def _build_css(theme: str, highlight_style: str, no_highlight: bool, mode: str = "auto") -> str:
    """Assemble all CSS into a single <style> block."""
    parts = []

    if theme == "github":
        parts.append(_apply_mode(_load_asset("github.css"), mode))
    elif theme == "gitlab":
        parts.append(_apply_mode(_load_asset("gitlab.css"), mode))
    else:  # auto: github base + gitlab dark via media query
        github_css = _load_asset("github.css")
        gitlab_css = _load_asset("gitlab.css")
        if mode == "auto":
            parts.append(github_css)
            parts.append("@media (prefers-color-scheme: dark) {\n" + gitlab_css + "\n}")
        elif mode == "light":
            parts.append(_strip_dark_media(github_css))
        else:  # dark
            parts.append(_unwrap_dark_media(github_css))

    parts.append(_apply_mode(_load_asset("admonition.css"), mode))
    parts.append(_load_asset("copy-button.css"))
    parts.append(_apply_mode(_load_asset("minimap.css"), mode))

    if not no_highlight:
        light_css = HtmlFormatter(style=highlight_style).get_style_defs(".highlight")
        dark_css = HtmlFormatter(style="github-dark").get_style_defs(".highlight")
        if mode == "light":
            parts.append(light_css)
        elif mode == "dark":
            parts.append(dark_css)
        else:  # auto
            parts.append(light_css)
            parts.append("@media (prefers-color-scheme: dark) {\n" + dark_css + "\n}")

    return "<style>\n" + "\n".join(parts) + "\n</style>"


def _copy_button_script_tag() -> str:
    """Return an inline <script> that appends copy buttons to all code blocks."""
    js = (
        "(function(){"
        "function addBtn(block,getText){"
        "var btn=document.createElement('button');"
        "btn.className='copy-btn';btn.textContent='Copy';"
        "block.appendChild(btn);"
        "btn.addEventListener('click',function(){"
        "var text=getText(block);"
        "var p=navigator.clipboard?navigator.clipboard.writeText(text):Promise.reject();"
        "p.catch(function(){"
        "var ta=document.createElement('textarea');"
        "ta.value=text;ta.style.cssText='position:fixed;top:0;left:0;opacity:0';"
        "document.body.appendChild(ta);ta.select();"
        "document.execCommand('copy');document.body.removeChild(ta);"
        "}).then(function(){"
        "btn.textContent='\u2713 Copied';"
        "setTimeout(function(){btn.textContent='Copy';},2000);"
        "});});"
        "}"
        "document.querySelectorAll('div.highlight').forEach(function(el){"
        "addBtn(el,function(b){return(b.querySelector('pre')||b).textContent;});"
        "});"
        "document.querySelectorAll('.markdown-body pre:not(.mermaid)').forEach(function(el){"
        "if(!el.closest('.highlight'))addBtn(el,function(b){return b.textContent;});"
        "});"
        "})();"
    )
    return f"<script>\n{js}\n</script>\n"


def _build_html(
    body_html: str,
    title: str,
    theme: str,
    highlight_style: str,
    no_highlight: bool,
    no_mermaid: bool,
    mode: str = "auto",
    minimap_html: str = "",
    no_minimap: bool = False,
) -> str:
    """Wrap converted body HTML into a full standalone HTML document."""
    css_block = _build_css(theme, highlight_style, no_highlight, mode)

    mermaid_tag = "" if no_mermaid else mermaid_script_tag(mode)
    copy_tag = _copy_button_script_tag()
    minimap_tag = "" if no_minimap or not minimap_html else minimap_script_tag()

    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"<title>{title}</title>\n"
        f"{css_block}\n"
        "</head>\n"
        "<body>\n"
        '<div class="app-container">\n'
        '<div class="markdown-body">\n'
        f"{body_html}\n"
        "</div>\n"
        f"{minimap_html}\n"
        "</div>\n"
        f"{copy_tag}"
        f"{mermaid_tag}"
        f"{minimap_tag}"
        "</body>\n"
        "</html>\n"
    )


def _make_renderer(no_highlight: bool, no_mermaid: bool, highlight_style: str):
    """Return a mistune renderer with optional highlighting and mermaid support."""
    if not no_mermaid and not no_highlight:

        class CombinedRenderer(MermaidRenderer, HighlightRenderer):
            pass

        renderer = CombinedRenderer(escape=False, highlight_style=highlight_style)
    elif not no_mermaid:
        renderer = MermaidRenderer(escape=False)
    elif not no_highlight:
        renderer = HighlightRenderer(escape=False, highlight_style=highlight_style)
    else:
        renderer = mistune.HTMLRenderer(escape=False)
    return renderer


_FRONTMATTER_RE = re.compile(
    r"^\s*---\r?\n(?P<yaml>[\s\S]*?)\r?\n---\r?\n?",
)


def strip_frontmatter(text: str) -> tuple[str, str | None]:
    """Remove Docusaurus / YAML frontmatter headers from markdown text."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return text, None

    yaml_content = m.group("yaml")
    cleaned_text = text[m.end() :]

    title_match = re.search(
        r'^\s*title:\s*["\']?(?P<title>[^"\'\n]+)["\']?\s*$',
        yaml_content,
        re.MULTILINE,
    )
    extracted_title = title_match.group("title").strip() if title_match else None

    return cleaned_text, extracted_title


def convert(
    markdown_text: str,
    title: str = "",
    theme: str = "github",
    highlight_style: str = "default",
    no_highlight: bool = False,
    no_mermaid: bool = False,
    mode: str = "auto",
    no_minimap: bool = False,
) -> str:
    """Convert Markdown text to a full standalone HTML document string."""
    # Strip Docusaurus / YAML frontmatter header
    markdown_text, fm_title = strip_frontmatter(markdown_text)

    # Pre-process admonitions before Markdown parsing
    preprocessed = preprocess_admonitions(markdown_text)

    renderer = _make_renderer(no_highlight, no_mermaid, highlight_style)
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=["strikethrough", table, table_in_list, table_in_quote, "url"],
    )
    body_html = md(preprocessed)

    if not no_minimap:
        body_html, minimap_html = process_headings_and_build_minimap(body_html)
    else:
        minimap_html = ""

    return _build_html(
        body_html,
        title=title or fm_title or "Untitled",
        theme=theme,
        highlight_style=highlight_style,
        no_highlight=no_highlight,
        no_mermaid=no_mermaid,
        mode=mode,
        minimap_html=minimap_html,
        no_minimap=no_minimap,
    )
