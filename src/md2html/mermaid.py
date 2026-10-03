"""Mermaid diagram renderer for mistune."""

import os

import mistune


def mermaid_script_tag(mode: str = "auto") -> str:
    """Return an inline <script> tag with the bundled Mermaid JS."""
    if mode == "light":
        theme_expr = "'default'"
    elif mode == "dark":
        theme_expr = "'dark'"
    else:  # auto: follow OS preference at runtime
        theme_expr = (
            "window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'default'"
        )

    init = f"mermaid.initialize({{startOnLoad:true,theme: {theme_expr}}});"

    js_path = os.path.join(os.path.dirname(__file__), "assets", "mermaid.min.js")
    if os.path.exists(js_path):
        with open(js_path, encoding="utf-8") as fh:
            js_content = fh.read()
        return f"<script>\n{js_content}\n{init}\n</script>\n"
    else:
        # Fallback: load from CDN (only when mermaid.min.js is not bundled)
        return (
            '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>\n'
            f"<script>\n{init}\n</script>\n"
        )


class MermaidRenderer(mistune.HTMLRenderer):
    """mistune renderer that converts mermaid code blocks to <pre class="mermaid">."""

    def block_code(self, code: str, **attrs) -> str:
        info = attrs.get("info") or ""
        lang = info.strip().split()[0] if info.strip() else ""
        if lang == "mermaid":
            return f'<pre class="mermaid">{code}</pre>\n'
        return super().block_code(code, **attrs)
