"""Tests for sitebuilder.renderer.

Covers happy paths plus the XSS/autoescape scenario documented in
src/sitebuilder/renderer/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from sitebuilder.renderer import RenderError, create_environment, render_page


@pytest.fixture
def templates_dir(tmp_path: Path) -> Path:
    (tmp_path / "greeting.html").write_text("Hello, {{ name }}!", encoding="utf-8")
    (tmp_path / "safe.html").write_text("{{ body | safe }}", encoding="utf-8")
    (tmp_path / "initials.html").write_text("{{ name | initials }}", encoding="utf-8")
    (tmp_path / "year.html").write_text("{{ build_year() }}", encoding="utf-8")
    (tmp_path / "broken_include.html").write_text('{% include "missing.html" %}', encoding="utf-8")
    (tmp_path / "collapsible.html").write_text("{{ body | collapsible_h3 }}", encoding="utf-8")
    (tmp_path / "lightbox.html").write_text("{{ body | lightbox_images }}", encoding="utf-8")
    (tmp_path / "truncated.html").write_text(
        "{% set t = items | truncated(limit) %}"
        "visible={{ t.visible | join(',') }};"
        "hidden_items={{ t.hidden | join(',') }};"
        "hidden_count={{ t.hidden_count }}",
        encoding="utf-8",
    )
    return tmp_path


class TestCreateEnvironment:
    def test_missing_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(RenderError, match="does not exist"):
            create_environment(tmp_path / "nope")

    def test_valid_dir_returns_environment(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        assert env.loader is not None


class TestRenderPage:
    def test_renders_with_context(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        assert render_page(env, "greeting.html", name="World") == "Hello, World!"

    def test_missing_template_raises(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        with pytest.raises(RenderError, match="Template not found"):
            render_page(env, "missing.html", name="World")

    def test_missing_context_value_raises(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        with pytest.raises(RenderError, match="Missing context value"):
            render_page(env, "greeting.html")

    def test_autoescapes_html_in_context(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "greeting.html", name="<script>alert(1)</script>")
        assert "<script>" not in output
        assert "&lt;script&gt;" in output

    def test_safe_filter_still_allows_trusted_html(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "safe.html", body="<p>trusted</p>")
        assert output == "<p>trusted</p>"

    def test_broken_nested_include_raises_render_error(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        with pytest.raises(RenderError, match="Failed to render"):
            render_page(env, "broken_include.html")


class TestInitialsFilter:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("Hanseul Choi", "HC"),
            ("최한슬", "한슬"),  # single-token Korean name -> last 2 chars (given name)
            ("최", "최"),  # single-character token -> itself, no crash
            ("cher", "C"),  # single-token ASCII name -> first letter only
            ("  ", "?"),
            ("", "?"),
            ("  Han  Seul  Choi  ", "HC"),
        ],
    )
    def test_initials_filter(self, templates_dir: Path, name: str, expected: str) -> None:
        env = create_environment(templates_dir)
        assert render_page(env, "initials.html", name=name) == expected


class TestBuildYearGlobal:
    def test_returns_current_utc_year(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        assert render_page(env, "year.html") == str(datetime.now(UTC).year)


class TestCollapsibleH3Filter:
    def test_wraps_single_h3_and_its_content(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = "<h2>문제 및 해결</h2><h3>1. 문제</h3><p>내용</p>"
        output = render_page(env, "collapsible.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        details = soup.find_all("details", class_="collapsible")
        assert len(details) == 1
        assert details[0].summary.get_text(strip=True) == "1. 문제"
        assert details[0].p.get_text(strip=True) == "내용"
        assert soup.find("h3") is None  # replaced, not just wrapped alongside

    def test_stops_at_next_h3_not_leaking_into_next_section(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = "<h3>1. 문제 A</h3><p>A 내용</p><h3>2. 문제 B</h3><p>B 내용</p>"
        output = render_page(env, "collapsible.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        details = soup.find_all("details", class_="collapsible")
        assert len(details) == 2
        assert details[0].summary.get_text(strip=True) == "1. 문제 A"
        assert "A 내용" in details[0].get_text()
        assert "B 내용" not in details[0].get_text()
        assert details[1].summary.get_text(strip=True) == "2. 문제 B"
        assert "B 내용" in details[1].get_text()

    def test_stops_at_following_h2(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = "<h3>1. 문제</h3><p>문제 내용</p><h2>성과</h2><p>성과 내용</p>"
        output = render_page(env, "collapsible.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        details = soup.find("details", class_="collapsible")
        assert "문제 내용" in details.get_text()
        assert "성과 내용" not in details.get_text()
        # the h2 section survives outside the accordion, untouched
        assert soup.find("h2").get_text(strip=True) == "성과"

    def test_html_without_h3_is_left_effectively_unchanged(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = "<h2>개요</h2><p>그냥 내용</p>"
        output = render_page(env, "collapsible.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        assert soup.find("details") is None
        assert "그냥 내용" in output

    def test_preserves_rich_content_like_lists_and_code_blocks(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = "<h3>1. 문제</h3><ul><li>항목</li></ul><pre><code>code here</code></pre>"
        output = render_page(env, "collapsible.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        details = soup.find("details", class_="collapsible")
        assert details.find("li").get_text(strip=True) == "항목"
        assert details.find("code").get_text(strip=True) == "code here"


class TestLightboxImagesFilter:
    def test_wraps_image_in_trigger_and_overlay(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = '<img src="/static/x.png" alt="다이어그램">'
        output = render_page(env, "lightbox.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        trigger = soup.find("a", class_="lightbox-trigger")
        assert trigger is not None
        assert trigger.img["src"] == "/static/x.png"
        assert trigger.img["alt"] == "다이어그램"

        overlay_id = trigger["href"].lstrip("#")
        overlay = soup.find("a", id=overlay_id)
        assert "lightbox-overlay" in overlay["class"]
        assert overlay["href"] == "#"
        assert overlay.img["src"] == "/static/x.png"
        assert overlay.img["alt"] == "다이어그램"

    def test_multiple_images_get_distinct_ids(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        html = '<img src="/a.png" alt="A"><p>text</p><img src="/b.png" alt="B">'
        output = render_page(env, "lightbox.html", body=html)
        soup = BeautifulSoup(output, "html.parser")

        triggers = soup.find_all("a", class_="lightbox-trigger")
        hrefs = [t["href"] for t in triggers]
        assert len(hrefs) == len(set(hrefs)) == 2

        for trigger in triggers:
            overlay = soup.find("a", id=trigger["href"].lstrip("#"))
            assert overlay.img["src"] == trigger.img["src"]

    def test_image_without_alt_does_not_crash(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "lightbox.html", body='<img src="/x.png">')
        soup = BeautifulSoup(output, "html.parser")

        assert soup.find("a", class_="lightbox-trigger").img["src"] == "/x.png"

    def test_html_without_images_is_left_unchanged(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "lightbox.html", body="<p>그냥 텍스트</p>")
        soup = BeautifulSoup(output, "html.parser")

        assert soup.find("a", class_="lightbox-trigger") is None
        assert "그냥 텍스트" in output


class TestTruncatedFilter:
    def test_fewer_items_than_limit_are_all_visible(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "truncated.html", items=["a", "b"], limit=5)
        assert output == "visible=a,b;hidden_items=;hidden_count=0"

    def test_exactly_limit_items_are_all_visible(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "truncated.html", items=["a", "b"], limit=2)
        assert output == "visible=a,b;hidden_items=;hidden_count=0"

    def test_more_items_than_limit_are_truncated_with_a_count(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "truncated.html", items=["a", "b", "c", "d"], limit=2)
        assert output == "visible=a,b;hidden_items=c,d;hidden_count=2"

    def test_empty_list_is_untouched(self, templates_dir: Path) -> None:
        env = create_environment(templates_dir)
        output = render_page(env, "truncated.html", items=[], limit=2)
        assert output == "visible=;hidden_items=;hidden_count=0"
