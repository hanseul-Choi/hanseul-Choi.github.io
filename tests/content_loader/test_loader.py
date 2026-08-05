"""Tests for sitebuilder.content_loader.

Covers happy paths plus the failure/threat scenarios documented in
src/sitebuilder/content_loader/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sitebuilder.content_loader import (
    ContentLoadError,
    load_navigation,
    load_pages,
    load_projects,
    load_site_config,
)


class TestLoadNavigation:
    def test_loads_valid_navigation(self, tmp_path: Path) -> None:
        (tmp_path / "navigation.yaml").write_text(
            "- title: Home\n  url: /\n- title: About\n  url: /about/\n", encoding="utf-8"
        )
        nav = load_navigation(tmp_path)
        assert [item.title for item in nav] == ["Home", "About"]

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ContentLoadError, match="Expected a YAML file"):
            load_navigation(tmp_path)

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "navigation.yaml").write_text("", encoding="utf-8")
        assert load_navigation(tmp_path) == []

    def test_non_list_content_raises(self, tmp_path: Path) -> None:
        (tmp_path / "navigation.yaml").write_text("title: Home\n", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="must contain a YAML list"):
            load_navigation(tmp_path)

    def test_invalid_item_raises(self, tmp_path: Path) -> None:
        (tmp_path / "navigation.yaml").write_text("- title: Home\n", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="Invalid nav item"):
            load_navigation(tmp_path)

    def test_rejects_unsafe_yaml_tags(self, tmp_path: Path) -> None:
        (tmp_path / "navigation.yaml").write_text(
            "- !!python/object/apply:builtins.list []\n", encoding="utf-8"
        )
        with pytest.raises(ContentLoadError, match="Invalid YAML"):
            load_navigation(tmp_path)

    def test_rejects_path_outside_base_dir(self, tmp_path: Path) -> None:
        # tmp_path/outside.yaml sits next to (not inside) data_dir, so
        # "../outside.yaml" resolves outside the allowed base directory.
        (tmp_path / "outside.yaml").write_text("- title: Home\n  url: /\n", encoding="utf-8")
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        with pytest.raises(ContentLoadError, match="outside the allowed base directory"):
            load_navigation(data_dir, filename="../outside.yaml")


class TestLoadProjects:
    def test_loads_and_sorts_by_order(self, tmp_path: Path) -> None:
        (tmp_path / "projects.yaml").write_text(
            "- slug: second\n  title: Second\n  summary: s\n  order: 2\n"
            "- slug: first\n  title: First\n  summary: s\n  order: 1\n",
            encoding="utf-8",
        )
        projects = load_projects(tmp_path)
        assert [p.slug for p in projects] == ["first", "second"]

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "projects.yaml").write_text("[]\n", encoding="utf-8")
        assert load_projects(tmp_path) == []

    def test_duplicate_slug_raises(self, tmp_path: Path) -> None:
        (tmp_path / "projects.yaml").write_text(
            "- slug: dup\n  title: A\n  summary: s\n- slug: dup\n  title: B\n  summary: s\n",
            encoding="utf-8",
        )
        with pytest.raises(ContentLoadError, match="Duplicate project slug"):
            load_projects(tmp_path)

    def test_invalid_entry_raises(self, tmp_path: Path) -> None:
        (tmp_path / "projects.yaml").write_text(
            "- slug: 'Not Valid'\n  title: A\n  summary: s\n", encoding="utf-8"
        )
        with pytest.raises(ContentLoadError, match="Invalid project entry"):
            load_projects(tmp_path)


class TestLoadSiteConfig:
    def test_loads_valid_config(self, tmp_path: Path) -> None:
        (tmp_path / "site.yaml").write_text(
            "title: My Site\ndescription: desc\nbase_url: https://example.com\nauthor_name: Me\n",
            encoding="utf-8",
        )
        config = load_site_config(tmp_path)
        assert config.title == "My Site"

    def test_non_mapping_raises(self, tmp_path: Path) -> None:
        (tmp_path / "site.yaml").write_text("- not\n- a\n- mapping\n", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="must contain a YAML mapping"):
            load_site_config(tmp_path)

    def test_missing_required_field_raises(self, tmp_path: Path) -> None:
        (tmp_path / "site.yaml").write_text("title: My Site\n", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="Invalid site config"):
            load_site_config(tmp_path)


class TestLoadPages:
    def test_loads_pages_sorted_by_filename(self, tmp_path: Path) -> None:
        (tmp_path / "a-about.md").write_text("---\ntitle: About\n---\n# Hi\n", encoding="utf-8")
        (tmp_path / "b-contact.md").write_text(
            "---\ntitle: Contact\n---\nEmail me.\n", encoding="utf-8"
        )
        pages = load_pages(tmp_path)
        assert [p.slug for p in pages] == ["a-about", "b-contact"]
        assert "<h1" in pages[0].body_html

    def test_missing_title_frontmatter_raises(self, tmp_path: Path) -> None:
        (tmp_path / "broken.md").write_text("# No frontmatter title\n", encoding="utf-8")
        with pytest.raises(ContentLoadError, match="missing required 'title'"):
            load_pages(tmp_path)

    def test_missing_content_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ContentLoadError, match="does not exist"):
            load_pages(tmp_path / "nope")

    def test_no_markdown_files_returns_empty_list(self, tmp_path: Path) -> None:
        assert load_pages(tmp_path) == []
