"""Admonitions pre-processor: supports MkDocs and Docusaurus syntax."""

import re

# MkDocs admonition types
MKDOCS_TYPES = {
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
}

# Docusaurus admonition types
DOCUSAURUS_TYPES = {"note", "tip", "info", "caution", "danger", "warning"}


def _make_admonition_html(admon_type: str, title: str, body: str, indent: str = "") -> str:
    """Build the HTML for an admonition block."""
    display_title = title if title else admon_type.capitalize()
    body_content = body.strip()
    lines = [
        f'{indent}<div class="admonition {admon_type}">',
        f'{indent}<p class="admonition-title">{display_title}</p>',
        "",
    ]
    if body_content:
        for line in body_content.splitlines():
            if line.strip():
                lines.append(f"{indent}{line}")
            else:
                lines.append("")
        lines.append("")
    lines.append(f"{indent}</div>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# MkDocs  !!!  syntax
# ---------------------------------------------------------------------------

_MKDOCS_START = re.compile(
    r'^(?P<indent>[ \t]*)!!![ \t]+(?P<type>\w+)(?:[ \t]+"(?P<title>[^"]*)")?[ \t]*$',
    re.MULTILINE,
)


def _parse_mkdocs(text: str) -> str:
    """Replace MkDocs admonition blocks with HTML."""
    lines = text.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line_no_nl = lines[i].rstrip("\r\n")
        m = _MKDOCS_START.match(line_no_nl)
        if m:
            admon_type = m.group("type").lower()
            if admon_type in MKDOCS_TYPES:
                indent = m.group("indent")
                title = m.group("title") or ""
                i += 1
                body_lines = []
                while i < len(lines):
                    curr_line = lines[i]
                    curr_no_nl = curr_line.rstrip("\r\n")
                    if not curr_no_nl.strip():
                        body_lines.append("")
                        i += 1
                        continue

                    if curr_no_nl.startswith(indent + "    "):
                        body_lines.append(curr_no_nl[len(indent) + 4 :])
                        i += 1
                    elif curr_no_nl.startswith(indent + "\t"):
                        body_lines.append(curr_no_nl[len(indent) + 1 :])
                        i += 1
                    elif len(curr_no_nl) - len(curr_no_nl.lstrip()) > len(indent):
                        curr_indent = len(curr_no_nl) - len(curr_no_nl.lstrip())
                        extra_indent_len = min(4, curr_indent - len(indent))
                        body_lines.append(curr_no_nl[len(indent) + extra_indent_len :])
                        i += 1
                    else:
                        break

                while body_lines and not body_lines[-1].strip():
                    body_lines.pop()

                body = "\n".join(body_lines)
                result.append(_make_admonition_html(admon_type, title, body, indent=indent))
                continue
        result.append(lines[i])
        i += 1
    return "".join(result)


# ---------------------------------------------------------------------------
# Docusaurus  :::  syntax
# ---------------------------------------------------------------------------

_DOCUSAURUS_START = re.compile(
    r"^(?P<indent>[ \t]*):::(?P<type>\w+)(?:[ \t]+(?P<title>[^\n]+))?$",
    re.MULTILINE,
)


def _parse_docusaurus(text: str) -> str:
    """Replace Docusaurus admonition blocks with HTML."""
    lines = text.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line_no_nl = lines[i].rstrip("\r\n")
        m = _DOCUSAURUS_START.match(line_no_nl)
        if m:
            admon_type = m.group("type").lower()
            if admon_type in DOCUSAURUS_TYPES:
                indent = m.group("indent")
                title = (m.group("title") or "").strip()
                start_i = i
                i += 1
                body_lines = []
                closed = False
                while i < len(lines):
                    curr_line = lines[i]
                    curr_no_nl = curr_line.rstrip("\r\n")
                    if curr_no_nl.strip() == ":::":
                        closed = True
                        i += 1
                        break
                    if curr_no_nl.startswith(indent):
                        body_lines.append(curr_no_nl[len(indent) :])
                    else:
                        body_lines.append(curr_no_nl)
                    i += 1

                if closed:
                    while body_lines and not body_lines[-1].strip():
                        body_lines.pop()
                    body = "\n".join(body_lines)
                    result.append(_make_admonition_html(admon_type, title, body, indent=indent))
                    continue
                else:
                    result.extend(lines[start_i:i])
                    continue

        result.append(lines[i])
        i += 1
    return "".join(result)


def preprocess_admonitions(text: str) -> str:
    """Apply MkDocs and Docusaurus admonition preprocessing to Markdown text."""
    text = _parse_docusaurus(text)
    text = _parse_mkdocs(text)
    return text
