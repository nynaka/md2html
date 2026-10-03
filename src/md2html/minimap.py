"""Minimap (Table of Contents) sidebar generator and helper functions."""

import re

_HEADING_RE = re.compile(
    r"<h(?P<level>[1-6])(?P<attrs>[^>]*)>(?P<content>.*?)</h\1>",
    re.IGNORECASE | re.DOTALL,
)
_ID_ATTR_RE = re.compile(r'id=["\'](?P<id>[^"\']+)["\']', re.IGNORECASE)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")


def _slugify(text: str, used_ids: set) -> str:
    """Generate a clean URL anchor ID from heading text."""
    plain_text = _TAG_STRIP_RE.sub("", text).strip()
    slug = re.sub(r"[\s\t\n]+", "-", plain_text)
    slug = re.sub(r"[^\w\u3000-\u30fe\u4e00-\u9fa5\uFF00-\uFFEF-]", "", slug)
    if not slug:
        slug = "heading"

    base_slug = slug
    counter = 1
    while slug in used_ids:
        slug = f"{base_slug}-{counter}"
        counter += 1
    used_ids.add(slug)
    return slug


def process_headings_and_build_minimap(body_html: str) -> tuple[str, str]:
    """Find h1~h6 tags, add missing IDs, and build minimap sidebar HTML."""
    used_ids = set()
    items = []

    def _repl(match):
        level = int(match.group("level"))
        attrs = match.group("attrs")
        content = match.group("content")

        plain_text = _TAG_STRIP_RE.sub("", content).strip()

        id_match = _ID_ATTR_RE.search(attrs)
        if id_match:
            heading_id = id_match.group("id")
            used_ids.add(heading_id)
            new_attrs = attrs
        else:
            heading_id = _slugify(plain_text, used_ids)
            new_attrs = f' id="{heading_id}"{attrs}'

        items.append(
            {
                "level": level,
                "id": heading_id,
                "text": plain_text or f"Heading {level}",
            }
        )

        return f"<h{level}{new_attrs}>{content}</h{level}>"

    modified_html = _HEADING_RE.sub(_repl, body_html)
    minimap_html = _generate_minimap_html(items)
    return modified_html, minimap_html


def _generate_minimap_html(items: list) -> str:
    """Generate the HTML string for the minimap sidebar."""
    if not items:
        return ""

    lines = [
        '<aside class="minimap-wrapper" aria-label="ミニマップ">',
        '  <nav class="minimap">',
        '    <ul class="minimap-list">',
    ]

    for item in items:
        level = item["level"]
        hid = item["id"]
        text = item["text"]
        safe_text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        lines.append(
            f'      <li class="minimap-item level-{level}">'
            f'<a href="#{hid}" title="{safe_text}">{safe_text}</a>'
            f"</li>"
        )

    lines.extend(
        [
            "    </ul>",
            "  </nav>",
            "</aside>",
        ]
    )
    return "\n".join(lines)


def minimap_script_tag() -> str:
    """Return an inline <script> tag for anchor-based and scroll-based highlighting."""
    js = (
        "(function(){\n"
        "function initMinimap(){\n"
        "var list=document.querySelector('.minimap-list');\n"
        "if(!list)return;\n"
        "var links=Array.from(list.querySelectorAll('a'));\n"
        "if(!links.length)return;\n"
        "var targets=[];\n"
        "links.forEach(function(l){\n"
        "var href=l.getAttribute('href');\n"
        "if(href&&href.startsWith('#')){\n"
        "var id=decodeURIComponent(href.slice(1));\n"
        "var el=document.getElementById(id);\n"
        "if(el)targets.push({link:l,el:el,id:id});\n"
        "}\n"
        "});\n"
        "if(!targets.length)return;\n"
        "function updateActive(){\n"
        "var hash=window.location.hash;\n"
        "var currentHash=hash?decodeURIComponent(hash.slice(1)):'';\n"
        "var activeIndex=-1;\n"
        "if(currentHash){\n"
        "for(var j=0;j<targets.length;j++){\n"
        "if(targets[j].id===currentHash){\n"
        "activeIndex=j;\n"
        "break;\n"
        "}\n"
        "}\n"
        "}\n"
        "if(activeIndex===-1){\n"
        "var pos=window.scrollY||document.documentElement.scrollTop;\n"
        "if(pos>=50){\n"
        "for(var i=0;i<targets.length;i++){\n"
        "var top=targets[i].el.getBoundingClientRect().top+pos;\n"
        "if(pos>=top-120)activeIndex=i;\n"
        "else break;\n"
        "}\n"
        "}\n"
        "}\n"
        "links.forEach(function(l){l.classList.remove('active');});\n"
        "if(activeIndex>=0&&targets[activeIndex]){\n"
        "var activeLink=targets[activeIndex].link;\n"
        "activeLink.classList.add('active');\n"
        "var nav=activeLink.closest('.minimap');\n"
        "if(nav){\n"
        "var t=activeLink.offsetTop;\n"
        "var h=nav.clientHeight;\n"
        "if(t<nav.scrollTop||t>nav.scrollTop+h-40){\n"
        "nav.scrollTop=t-h/2;\n"
        "}\n"
        "}\n"
        "}\n"
        "}\n"
        "var ticking=false;\n"
        "window.addEventListener('scroll',function(){\n"
        "if(!ticking){\n"
        "window.requestAnimationFrame(function(){updateActive();ticking=false;});\n"
        "ticking=true;\n"
        "}\n"
        "},{passive:true});\n"
        "window.addEventListener('hashchange',updateActive);\n"
        "links.forEach(function(l){\n"
        "l.addEventListener('click',function(){\n"
        "setTimeout(updateActive,10);\n"
        "});\n"
        "});\n"
        "updateActive();\n"
        "if(document.readyState==='loading')\n"
        "document.addEventListener('DOMContentLoaded',initMinimap);\n"
        "else initMinimap();\n"
        "})();\n"
    )
    return f"<script>\n{js}\n</script>\n"
