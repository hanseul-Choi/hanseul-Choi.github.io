"""Tests for sitebuilder.renderer.

Covers happy paths plus the XSS/autoescape scenario documented in
src/sitebuilder/renderer/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sitebuilder.renderer import RenderError, create_environment, render_page


@pytest.fixture
def templates_dir(tmp_path: Path) -> Path:
    (tmp_path / "greeting.html").write_text("Hello, {{ name }}!", encoding="utf-8")
    (tmp_path / "safe.html").write_text("{{ body | safe }}", encoding="utf-8")
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
