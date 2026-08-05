"""Tests for sitebuilder.contracts data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sitebuilder.contracts import NavItem, PageContent, Project, SiteConfig


class TestNavItem:
    def test_valid_item_round_trips(self) -> None:
        item = NavItem(title="Home", url="/")
        assert item.title == "Home"
        assert item.url == "/"

    def test_blank_title_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NavItem(title="   ", url="/")

    def test_blank_url_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NavItem(title="Home", url="   ")

    def test_missing_required_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NavItem.model_validate({"title": "Home"})

    def test_unknown_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            NavItem.model_validate({"title": "Home", "url": "/", "icon": "house"})


class TestProject:
    def test_valid_project_has_defaults(self) -> None:
        project = Project(slug="my-project", title="My Project", summary="A thing I built.")
        assert project.tags == []
        assert project.order == 0
        assert project.repo_url is None
        assert project.live_url is None

    @pytest.mark.parametrize(
        "bad_slug",
        ["My Project", "my_project", "my project", "MY-PROJECT", "", "프로젝트"],
    )
    def test_invalid_slug_is_rejected(self, bad_slug: str) -> None:
        with pytest.raises(ValidationError):
            Project(slug=bad_slug, title="T", summary="S")

    def test_blank_title_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project(slug="ok", title="   ", summary="S")

    def test_blank_summary_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project(slug="ok", title="T", summary="   ")

    def test_unknown_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project.model_validate({"slug": "ok", "title": "T", "summary": "S", "featured": True})


class TestPageContent:
    def test_valid_page_round_trips(self) -> None:
        page = PageContent(slug="about", title="About", body_html="<p>hi</p>")
        assert page.slug == "about"
        assert page.body_html == "<p>hi</p>"


class TestSiteConfig:
    def test_valid_config_with_social_links(self) -> None:
        config = SiteConfig(
            title="My Site",
            description="A site.",
            base_url="https://example.com",
            author_name="Someone",
            social_links=[NavItem(title="GitHub", url="https://github.com/example")],
        )
        assert config.social_links[0].title == "GitHub"

    def test_social_links_default_to_empty_list(self) -> None:
        config = SiteConfig(
            title="My Site",
            description="A site.",
            base_url="https://example.com",
            author_name="Someone",
        )
        assert config.social_links == []

    def test_unknown_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SiteConfig.model_validate(
                {
                    "title": "My Site",
                    "description": "A site.",
                    "base_url": "https://example.com",
                    "author_name": "Someone",
                    "theme_color": "#fff",
                }
            )
