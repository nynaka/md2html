"""CLI argument parsing for md2html."""

import argparse


def parse_args(argv=None):
    """Parse command-line arguments and return the namespace."""
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="Convert Markdown to a standalone HTML file.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help='Markdown file path, or "-" to read from stdin',
    )
    parser.add_argument(
        "output",
        metavar="OUTPUT",
        nargs="?",
        default=None,
        help="Output directory path (default: dist, or stdout if reading from stdin)",
    )
    parser.add_argument(
        "--title",
        metavar="TEXT",
        default=None,
        help="Title for the HTML <title> tag (default: input filename)",
    )
    parser.add_argument(
        "--theme",
        choices=["github", "gitlab", "auto"],
        default="github",
        help="CSS theme to use (default: github)",
    )
    parser.add_argument(
        "--highlight-style",
        metavar="TEXT",
        default="default",
        help="Pygments colour scheme for syntax highlighting (default: default)",
    )
    parser.add_argument(
        "--no-highlight",
        action="store_true",
        default=False,
        help="Disable syntax highlighting",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "light", "dark"],
        default="auto",
        help="Colour scheme: auto follows OS setting, light forces light, dark forces dark"
        " (default: auto)",
    )
    parser.add_argument(
        "--no-mermaid",
        action="store_true",
        default=False,
        help="Disable Mermaid diagram rendering",
    )
    parser.add_argument(
        "--no-minimap",
        "--no-toc",
        "--disable-minimap",
        action="store_true",
        default=False,
        dest="no_minimap",
        help="Disable minimap / table of contents sidebar",
    )
    return parser.parse_args(argv)


def main():
    """Entry-point for the md2html command."""
    import os
    import sys

    from .builder import build_site
    from .converter import convert

    args = parse_args()

    try:
        if args.input == "-":
            markdown_text = sys.stdin.read()
            title = args.title or "stdin"
            html = convert(
                markdown_text,
                title=title,
                theme=args.theme,
                highlight_style=args.highlight_style,
                no_highlight=args.no_highlight,
                no_mermaid=args.no_mermaid,
                mode=args.mode,
                no_minimap=args.no_minimap,
            )
            if args.output:
                os.makedirs(args.output, exist_ok=True)
                out_file = os.path.join(args.output, "index.html")
                with open(out_file, "w", encoding="utf-8") as fh:
                    fh.write(html)
            else:
                sys.stdout.write(html)
        else:
            output_dir = args.output or "dist"
            build_site(
                entry_md_path=args.input,
                output_dir=output_dir,
                title=args.title,
                theme=args.theme,
                highlight_style=args.highlight_style,
                no_highlight=args.no_highlight,
                no_mermaid=args.no_mermaid,
                mode=args.mode,
                no_minimap=args.no_minimap,
            )

    except FileNotFoundError as exc:
        print(f"md2html: error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"md2html: error: {exc}", file=sys.stderr)
        sys.exit(1)
