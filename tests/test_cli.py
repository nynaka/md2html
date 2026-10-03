import pytest

from md2html.cli import parse_args


def test_input_only(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("# hello")
    args = parse_args([str(f)])
    assert args.input == str(f)
    assert args.output is None


def test_input_and_output(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("# hello")
    args = parse_args([str(f), "out.html"])
    assert args.input == str(f)
    assert args.output == "out.html"


def test_title_option(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--title", "My Doc", str(f)])
    assert args.title == "My Doc"


def test_title_defaults_to_none(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.title is None


def test_theme_github(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--theme", "github", str(f)])
    assert args.theme == "github"


def test_theme_gitlab(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--theme", "gitlab", str(f)])
    assert args.theme == "gitlab"


def test_theme_auto(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--theme", "auto", str(f)])
    assert args.theme == "auto"


def test_theme_default(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.theme == "github"


def test_theme_invalid(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    with pytest.raises(SystemExit):
        parse_args(["--theme", "invalid", str(f)])


def test_no_highlight_flag(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--no-highlight", str(f)])
    assert args.no_highlight is True


def test_no_highlight_default(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.no_highlight is False


def test_no_mermaid_flag(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--no-mermaid", str(f)])
    assert args.no_mermaid is True


def test_no_mermaid_default(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.no_mermaid is False


def test_highlight_style_option(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--highlight-style", "monokai", str(f)])
    assert args.highlight_style == "monokai"


def test_highlight_style_default(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.highlight_style == "default"


def test_mode_default(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args([str(f)])
    assert args.mode == "auto"


def test_mode_light_option(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--mode", "light", str(f)])
    assert args.mode == "light"


def test_mode_dark_option(tmp_path):
    f = tmp_path / "in.md"
    f.write_text("x")
    args = parse_args(["--mode", "dark", str(f)])
    assert args.mode == "dark"


def test_stdin_input():
    args = parse_args(["-"])
    assert args.input == "-"


def test_main_builds_directory(tmp_path, monkeypatch):
    import sys

    from md2html.cli import main

    in_file = tmp_path / "doc.md"
    in_file.write_text("# Test Title\nContent here", encoding="utf-8")
    out_dir = tmp_path / "build_output"

    monkeypatch.setattr(sys, "argv", ["md2html", str(in_file), str(out_dir)])
    main()

    assert (out_dir / "doc.html").exists()
    assert "# Test Title" not in (out_dir / "doc.html").read_text(encoding="utf-8")
    assert "<h1" in (out_dir / "doc.html").read_text(encoding="utf-8")


def test_main_stdin(tmp_path, monkeypatch, capsys):
    import io
    import sys

    from md2html.cli import main

    monkeypatch.setattr(sys, "stdin", io.StringIO("# Stdin Header\nBody"))
    monkeypatch.setattr(sys, "argv", ["md2html", "-"])
    main()

    captured = capsys.readouterr()
    assert "<h1" in captured.out
    assert "Stdin Header" in captured.out
