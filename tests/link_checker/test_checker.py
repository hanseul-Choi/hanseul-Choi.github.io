"""Tests for sitebuilder.link_checker.

Covers happy paths plus the path-traversal scenario documented in
src/sitebuilder/link_checker/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sitebuilder.link_checker import LinkCheckError, check_internal_links


def _write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


class TestCheckInternalLinks:
    def test_missing_output_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(LinkCheckError, match="does not exist"):
            check_internal_links(tmp_path / "nope")

    def test_valid_internal_links_produce_no_issues(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<a href="/about/">About</a><img src="/x.png" alt="x">')
        _write(tmp_path / "about" / "index.html", "<p>About</p>")
        _write(tmp_path / "x.png", "not really an image, just needs to exist")
        assert check_internal_links(tmp_path) == []

    def test_broken_internal_link_is_flagged(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<a href="/missing/">Missing</a>')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"

    def test_missing_alt_text_is_flagged(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<img src="/x.png">')
        _write(tmp_path / "x.png", "data")
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "missing_alt"

    def test_empty_alt_text_counts_as_missing(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<img src="/x.png" alt="">')
        _write(tmp_path / "x.png", "data")
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "missing_alt"

    @pytest.mark.parametrize(
        "href",
        [
            "https://example.com",
            "http://example.com/page",
            "mailto:me@example.com",
            "tel:+123",
            "#section",
            "blob:https://example.com/9a1b2c3d",
        ],
    )
    def test_external_and_anchor_links_are_skipped(self, tmp_path: Path, href: str) -> None:
        _write(tmp_path / "index.html", f'<a href="{href}">link</a>')
        assert check_internal_links(tmp_path) == []

    def test_data_uri_image_is_skipped_not_crashed_on(self, tmp_path: Path) -> None:
        # Regression test: any URI scheme (not just an http/https/mailto/tel
        # allowlist) must be treated as external. A `data:` URI previously
        # fell through the old allowlist check and got stat()'d as if it
        # were a filesystem path, crashing with OSError("File name too long").
        data_uri = "data:image/svg+xml;base64," + "A" * 500
        _write(tmp_path / "index.html", f'<img src="{data_uri}" alt="diagram">')
        assert check_internal_links(tmp_path) == []

    def test_relative_link_to_existing_sibling_page_is_ok(self, tmp_path: Path) -> None:
        _write(tmp_path / "blog" / "index.html", '<a href="../about/">About</a>')
        _write(tmp_path / "about" / "index.html", "<p>About</p>")
        assert check_internal_links(tmp_path) == []

    def test_flags_link_escaping_output_dir(self, tmp_path: Path) -> None:
        _write(tmp_path / "a" / "b" / "index.html", '<a href="../../../../outside.html">out</a>')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"
        assert "escapes output dir" in issues[0].detail

    def test_scans_nested_directories(self, tmp_path: Path) -> None:
        _write(tmp_path / "blog" / "post-1" / "index.html", '<img src="/missing.png" alt="ok">')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"
        assert issues[0].source_file == tmp_path / "blog" / "post-1" / "index.html"

    def test_broken_image_src_is_flagged(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<img src="/missing.png" alt="ok">')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"

    def test_broken_script_src_is_flagged(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<script src="/static/js/missing.js"></script>')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"

    def test_valid_script_src_produces_no_issue(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<script src="/static/js/app.js"></script>')
        _write(tmp_path / "static" / "js" / "app.js", "console.log(1);")
        assert check_internal_links(tmp_path) == []

    def test_inline_script_without_src_is_ignored(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", "<script>console.log(1);</script>")
        assert check_internal_links(tmp_path) == []

    def test_broken_stylesheet_link_is_flagged(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<link rel="stylesheet" href="/static/css/missing.css">')
        issues = check_internal_links(tmp_path)
        assert len(issues) == 1
        assert issues[0].kind == "broken_link"

    def test_valid_stylesheet_link_produces_no_issue(self, tmp_path: Path) -> None:
        _write(tmp_path / "index.html", '<link rel="stylesheet" href="/static/css/main.css">')
        _write(tmp_path / "static" / "css" / "main.css", "body { margin: 0; }")
        assert check_internal_links(tmp_path) == []
