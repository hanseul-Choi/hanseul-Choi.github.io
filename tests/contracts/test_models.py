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
        project = Project(
            slug="my-project", title="My Project", summary="A thing I built.", category="Infra"
        )
        assert project.tags == []
        assert project.order == 0
        assert project.repo_url is None
        assert project.live_url is None
        assert project.image_url is None
        assert project.achievements == []

    def test_image_url_is_optional_and_settable(self) -> None:
        project = Project(
            slug="my-project",
            title="My Project",
            summary="A thing I built.",
            category="Infra",
            image_url="/static/images/my-project.png",
        )
        assert project.image_url == "/static/images/my-project.png"

    def test_achievements_is_optional_and_settable(self) -> None:
        project = Project(
            slug="my-project",
            title="My Project",
            summary="A thing I built.",
            category="Infra",
            achievements=["응답속도 200ms → 80ms 단축", "DAU 30% 증가"],
        )
        assert project.achievements == ["응답속도 200ms → 80ms 단축", "DAU 30% 증가"]

    @pytest.mark.parametrize(
        "bad_slug",
        ["My Project", "my_project", "my project", "MY-PROJECT", "", "프로젝트"],
    )
    def test_invalid_slug_is_rejected(self, bad_slug: str) -> None:
        with pytest.raises(ValidationError):
            Project(slug=bad_slug, title="T", summary="S", category="Infra")

    def test_blank_title_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project(slug="ok", title="   ", summary="S", category="Infra")

    def test_blank_summary_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project(slug="ok", title="T", summary="   ", category="Infra")

    def test_missing_category_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project.model_validate({"slug": "ok", "title": "T", "summary": "S"})

    def test_blank_category_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project(slug="ok", title="T", summary="S", category="   ")

    @pytest.mark.parametrize("bad_tag", ["has space", " leading", "trailing ", ""])
    def test_tag_with_whitespace_is_rejected(self, bad_tag: str) -> None:
        # The /projects/ tag filter matches tags via a CSS attribute
        # selector against a space-separated list — a tag containing a
        # space would silently split into two unmatchable tokens.
        with pytest.raises(ValidationError):
            Project(slug="ok", title="T", summary="S", category="Infra", tags=[bad_tag])

    def test_unknown_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Project.model_validate(
                {
                    "slug": "ok",
                    "title": "T",
                    "summary": "S",
                    "category": "Infra",
                    "featured": True,
                }
            )


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
