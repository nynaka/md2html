"""Syntax highlighting renderer for mistune using Pygments."""

import mistune
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound


class HighlightRenderer(mistune.HTMLRenderer):
    """mistune renderer that applies Pygments syntax highlighting to code blocks."""

    def __init__(self, highlight_style: str = "default", escape: bool = False, **kwargs):
        super().__init__(escape=escape, **kwargs)
        self._highlight_style = highlight_style

    def block_code(self, code: str, **attrs) -> str:
        info = attrs.get("info") or ""
        lang = info.strip().split()[0] if info.strip() else ""
        if not lang:
            escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return f"<pre><code>{escaped}</code></pre>\n"
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = TextLexer()
        formatter = HtmlFormatter(style=self._highlight_style, wrapcode=False)
        highlighted = highlight(code, lexer, formatter)
        return highlighted
