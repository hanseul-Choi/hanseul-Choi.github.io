"""Tests for sitebuilder.site_builder.pipeline.

Covers the full build orchestration plus the output-path guard documented in
src/sitebuilder/site_builder/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sitebuilder.site_builder.pipeline import BuildError, _ensure_output_dir_allowed, build_site
from tests.site_builder.conftest import SitePaths


class TestBuildSiteHappyPath:
    def test_builds_all_pages_and_copies_static(self, site_paths: SitePaths) -> None:
        result = build_site(
            content_dir=site_paths.content_dir,
            data_dir=site_paths.data_dir,
            templates_dir=site_paths.templates_dir,
            static_dir=site_paths.static_dir,
            output_dir=site_paths.output_dir,
            project_root=site_paths.project_root,
        )

        assert result.ok
        assert "index.html" in result.pages_written
        assert "projects/index.html" in result.pages_written
        assert (site_paths.output_dir / "index.html").is_file()
        assert (site_paths.output_dir / "projects" / "index.html").is_file()
        assert (site_paths.output_dir / "static" / "style.css").is_file()

    def test_rendered_project_appears_in_output(self, site_paths: SitePaths) -> None:
        result = build_site(
            content_dir=site_paths.content_dir,
            data_dir=site_paths.data_dir,
            templates_dir=site_paths.templates_dir,
            static_dir=site_paths.static_dir,
            output_dir=site_paths.output_dir,
            project_root=site_paths.project_root,
        )
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "Demo" in projects_html

    def test_empty_projects_list_builds_without_error(self, site_paths: SitePaths) -> None:
        (site_paths.data_dir / "projects.yaml").write_text("[]\n", encoding="utf-8")
        result = build_site(
            content_dir=site_paths.content_dir,
            data_dir=site_paths.data_dir,
            templates_dir=site_paths.templates_dir,
            static_dir=site_paths.static_dir,
            output_dir=site_paths.output_dir,
            project_root=site_paths.project_root,
        )
        assert result.ok


class TestBuildSiteFailures:
    def test_invalid_content_raises_build_error(self, site_paths: SitePaths) -> None:
        (site_paths.data_dir / "site.yaml").write_text("title: Only Title\n", encoding="utf-8")
        with pytest.raises(BuildError, match="Content loading failed"):
            build_site(
                content_dir=site_paths.content_dir,
                data_dir=site_paths.data_dir,
                templates_dir=site_paths.templates_dir,
                static_dir=site_paths.static_dir,
                output_dir=site_paths.output_dir,
                project_root=site_paths.project_root,
            )

    def test_missing_template_raises_build_error(self, site_paths: SitePaths) -> None:
        (site_paths.templates_dir / "page.html").unlink()
        with pytest.raises(BuildError, match="Rendering failed"):
            build_site(
                content_dir=site_paths.content_dir,
                data_dir=site_paths.data_dir,
                templates_dir=site_paths.templates_dir,
                static_dir=site_paths.static_dir,
                output_dir=site_paths.output_dir,
                project_root=site_paths.project_root,
            )

    def test_strict_mode_raises_on_link_issues(self, site_paths: SitePaths) -> None:
        (site_paths.content_dir / "broken.md").write_text(
            "---\ntitle: Broken\n---\n![](/missing.png)\n", encoding="utf-8"
        )
        with pytest.raises(BuildError, match="Link check failed"):
            build_site(
                content_dir=site_paths.content_dir,
                data_dir=site_paths.data_dir,
                templates_dir=site_paths.templates_dir,
                static_dir=site_paths.static_dir,
                output_dir=site_paths.output_dir,
                project_root=site_paths.project_root,
                strict=True,
            )

    def test_non_strict_mode_returns_issues_without_raising(self, site_paths: SitePaths) -> None:
        (site_paths.content_dir / "broken.md").write_text(
            "---\ntitle: Broken\n---\n![](/missing.png)\n", encoding="utf-8"
        )
        result = build_site(
            content_dir=site_paths.content_dir,
            data_dir=site_paths.data_dir,
            templates_dir=site_paths.templates_dir,
            static_dir=site_paths.static_dir,
            output_dir=site_paths.output_dir,
            project_root=site_paths.project_root,
            strict=False,
        )
        assert not result.ok
        assert len(result.link_issues) >= 1


class TestOutputDirGuard:
    def test_rejects_output_dir_outside_project_root(self, tmp_path: Path) -> None:
        project_root = tmp_path / "repo"
        project_root.mkdir()
        outside = tmp_path / "elsewhere"

        with pytest.raises(BuildError, match="outside the project root"):
            _ensure_output_dir_allowed(outside, project_root)

    def test_allows_output_dir_inside_project_root(self, tmp_path: Path) -> None:
        project_root = tmp_path / "repo"
        project_root.mkdir()
        inside = project_root / "dist"

        assert _ensure_output_dir_allowed(inside, project_root) == inside.resolve()

    def test_build_site_enforces_guard_end_to_end(
        self, site_paths: SitePaths, tmp_path: Path
    ) -> None:
        outside_output = tmp_path.parent / "outside-dist"
        with pytest.raises(BuildError, match="outside the project root"):
            build_site(
                content_dir=site_paths.content_dir,
                data_dir=site_paths.data_dir,
                templates_dir=site_paths.templates_dir,
                static_dir=site_paths.static_dir,
                output_dir=outside_output,
                project_root=site_paths.project_root,
            )
