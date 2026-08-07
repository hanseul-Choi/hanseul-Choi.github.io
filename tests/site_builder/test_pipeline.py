"""Tests for sitebuilder.site_builder.pipeline.

Covers the full build orchestration plus the output-path guard documented in
src/sitebuilder/site_builder/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from sitebuilder.contracts import Project
from sitebuilder.site_builder.pipeline import (
    BuildError,
    BuildResult,
    _collect_tags,
    _ensure_output_dir_allowed,
    _group_projects_by_category,
    build_site,
)
from tests.site_builder.conftest import SitePaths


def _build(site_paths: SitePaths, **overrides: Any) -> BuildResult:
    kwargs: dict[str, Any] = {
        "content_dir": site_paths.content_dir,
        "project_content_dir": site_paths.project_content_dir,
        "data_dir": site_paths.data_dir,
        "templates_dir": site_paths.templates_dir,
        "static_dir": site_paths.static_dir,
        "output_dir": site_paths.output_dir,
        "project_root": site_paths.project_root,
        **overrides,
    }
    return build_site(**kwargs)


class TestBuildSiteHappyPath:
    def test_builds_all_pages_and_copies_static(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)

        assert result.ok
        assert "index.html" in result.pages_written
        assert "projects/index.html" in result.pages_written
        assert (site_paths.output_dir / "index.html").is_file()
        assert (site_paths.output_dir / "projects" / "index.html").is_file()
        assert (site_paths.output_dir / "static" / "style.css").is_file()

    def test_rendered_project_appears_in_output(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "Demo" in projects_html

    def test_empty_projects_list_builds_without_error(self, site_paths: SitePaths) -> None:
        (site_paths.data_dir / "projects.yaml").write_text("[]\n", encoding="utf-8")
        result = _build(site_paths)
        assert result.ok


class TestAssetCacheBusting:
    """Every static asset link carries a `?v=<hash>` so a deploy is never
    masked by a stale browser/CDN cache of the old CSS/JS (see
    docs/HISTORY.md — this is exactly what bit us in production)."""

    def test_same_version_query_string_appears_on_every_page(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        home_html = (result.output_dir / "index.html").read_text(encoding="utf-8")
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")

        home_version = re.search(r"style\.css\?v=([a-f0-9]+)", home_html)
        projects_version = re.search(r"style\.css\?v=([a-f0-9]+)", projects_html)
        assert home_version is not None
        assert projects_version is not None
        assert home_version.group(1) == projects_version.group(1)

    def test_version_changes_when_static_content_changes(self, site_paths: SitePaths) -> None:
        first = _build(site_paths)
        first_html = (first.output_dir / "index.html").read_text(encoding="utf-8")
        first_match = re.search(r"style\.css\?v=([a-f0-9]+)", first_html)
        assert first_match is not None

        (site_paths.static_dir / "style.css").write_text("body { margin: 1px; }", encoding="utf-8")
        second = _build(site_paths)
        second_html = (second.output_dir / "index.html").read_text(encoding="utf-8")
        second_match = re.search(r"style\.css\?v=([a-f0-9]+)", second_html)
        assert second_match is not None

        assert first_match.group(1) != second_match.group(1)


class TestProjectDetailPages:
    def test_generates_detail_page_when_markdown_exists(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)

        assert "projects/demo/index.html" in result.pages_written
        detail_html = (result.output_dir / "projects" / "demo" / "index.html").read_text(
            encoding="utf-8"
        )
        assert "Architecture" in detail_html

    def test_card_links_to_modal_when_detail_exists(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert 'href="#project-modal-demo"' in projects_html
        assert "자세히 보기" in projects_html

    def test_modal_contains_full_detail_body_and_link_to_real_page(
        self, site_paths: SitePaths
    ) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")

        assert 'id="project-modal-demo"' in projects_html
        assert "Architecture" in projects_html  # detail.body_html rendered inline
        assert (
            "/projects/demo/" in projects_html
        )  # "전체 페이지에서 보기" link back to the real page

    def test_modal_also_appears_on_home_for_featured_projects(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        home_html = (result.output_dir / "index.html").read_text(encoding="utf-8")
        assert 'id="project-modal-demo"' in home_html

    def test_no_detail_page_link_or_modal_when_markdown_is_missing(
        self, site_paths: SitePaths
    ) -> None:
        (site_paths.project_content_dir / "demo.md").unlink()
        result = _build(site_paths)

        assert "projects/demo/index.html" not in result.pages_written
        assert not (site_paths.output_dir / "projects" / "demo").exists()
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "자세히 보기" not in projects_html
        assert "project-modal-demo" not in projects_html

    def test_project_without_matching_slug_gets_no_detail_page(self, site_paths: SitePaths) -> None:
        # The detail file's stem ("demo") must match a project's slug exactly;
        # a mismatched slug should be silently ignored, not crash the build.
        (site_paths.project_content_dir / "demo.md").rename(
            site_paths.project_content_dir / "unrelated-slug.md"
        )
        result = _build(site_paths)
        assert result.ok
        assert not any("unrelated-slug" in p for p in result.pages_written)

    def test_achievements_render_on_the_card(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "Cut latency 50%" in projects_html


def _project(slug: str, category: str, order: int, tags: list[str] | None = None) -> Project:
    return Project(
        slug=slug,
        title=slug,
        summary="s",
        category=category,
        order=order,
        tags=tags or [],
    )


class TestGroupProjectsByCategory:
    def test_groups_preserve_first_appearance_order(self) -> None:
        # "b" comes first in the (already order-sorted) input, so its
        # category leads even though "Infra" projects exist too.
        projects = [
            _project("b", "Infra", order=1),
            _project("a", "Platform", order=2),
            _project("c", "Infra", order=3),
        ]
        groups = _group_projects_by_category(projects)
        assert [category for category, _ in groups] == ["Infra", "Platform"]

    def test_projects_within_a_category_keep_their_relative_order(self) -> None:
        projects = [
            _project("first", "Infra", order=1),
            _project("second", "Infra", order=2),
        ]
        groups = _group_projects_by_category(projects)
        assert [p.slug for p in dict(groups)["Infra"]] == ["first", "second"]

    def test_empty_project_list_returns_empty_groups(self) -> None:
        assert _group_projects_by_category([]) == []


class TestCollectTags:
    def test_collects_unique_tags_in_first_appearance_order(self) -> None:
        projects = [
            _project("a", "Infra", order=1, tags=["Python", "AWS"]),
            _project("b", "Infra", order=2, tags=["AWS", "Kubernetes"]),
        ]
        assert _collect_tags(projects) == ["Python", "AWS", "Kubernetes"]

    def test_no_tags_returns_empty_list(self) -> None:
        assert _collect_tags([_project("a", "Infra", order=1)]) == []

    def test_empty_project_list_returns_empty_list(self) -> None:
        assert _collect_tags([]) == []


class TestProjectsPageCategoryAndTagWiring:
    """End-to-end check that build_site() threads project_groups/all_tags
    into the real projects.html render call (see conftest._PROJECTS_TEMPLATE,
    which stands in for the real template)."""

    def test_category_heading_appears_on_projects_page(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "Demo Category" in projects_html

    def test_tag_appears_in_all_tags_list_on_projects_page(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert "<li>Python</li>" in projects_html

    def test_card_carries_full_tag_list_for_css_filtering(self, site_paths: SitePaths) -> None:
        result = _build(site_paths)
        projects_html = (result.output_dir / "projects" / "index.html").read_text(encoding="utf-8")
        assert 'data-tags="Python"' in projects_html


class TestBuildSiteFailures:
    def test_invalid_content_raises_build_error(self, site_paths: SitePaths) -> None:
        (site_paths.data_dir / "site.yaml").write_text("title: Only Title\n", encoding="utf-8")
        with pytest.raises(BuildError, match="Content loading failed"):
            _build(site_paths)

    def test_missing_project_content_dir_raises_build_error(self, site_paths: SitePaths) -> None:
        with pytest.raises(BuildError, match="Content loading failed"):
            _build(site_paths, project_content_dir=site_paths.project_content_dir / "nope")

    def test_missing_template_raises_build_error(self, site_paths: SitePaths) -> None:
        (site_paths.templates_dir / "page.html").unlink()
        with pytest.raises(BuildError, match="Rendering failed"):
            _build(site_paths)

    def test_strict_mode_raises_on_link_issues(self, site_paths: SitePaths) -> None:
        (site_paths.content_dir / "broken.md").write_text(
            "---\ntitle: Broken\n---\n![](/missing.png)\n", encoding="utf-8"
        )
        with pytest.raises(BuildError, match="Link check failed"):
            _build(site_paths, strict=True)

    def test_non_strict_mode_returns_issues_without_raising(self, site_paths: SitePaths) -> None:
        (site_paths.content_dir / "broken.md").write_text(
            "---\ntitle: Broken\n---\n![](/missing.png)\n", encoding="utf-8"
        )
        result = _build(site_paths, strict=False)
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
            _build(site_paths, output_dir=outside_output)
