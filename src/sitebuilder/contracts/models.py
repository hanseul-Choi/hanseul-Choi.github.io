"""Shared data contracts used across every sitebuilder module.

This is the only module every other feature module is allowed to depend on
(see AGENTS.md rule 10 and docs/architecture/harness-overview.md). It defines
no I/O — pure data shapes and the errors raised when data does not conform
to them.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class ContractValidationError(ValueError):
    """Raised when raw content/data does not satisfy a contract's schema.

    Distinct from pydantic.ValidationError so callers outside this module can
    catch a single, stable exception type without depending on pydantic's
    exception shape.
    """


class NavItem(BaseModel):
    """A single entry in the site navigation menu."""

    model_config = ConfigDict(extra="forbid")

    title: str
    url: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("NavItem.title must not be blank")
        return value

    @field_validator("url")
    @classmethod
    def url_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("NavItem.url must not be blank")
        return value


class Project(BaseModel):
    """A single portfolio project entry."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    summary: str
    category: str
    tags: list[str] = []
    achievements: list[str] = []
    repo_url: str | None = None
    live_url: str | None = None
    image_url: str | None = None
    order: int = 0

    @field_validator("slug")
    @classmethod
    def slug_is_url_safe(cls, value: str) -> str:
        if not value:
            raise ValueError("Project.slug must not be blank")
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if not set(value).issubset(allowed):
            raise ValueError(
                f"Project.slug={value!r} must contain only lowercase letters, digits, and hyphens"
            )
        return value

    @field_validator("title", "summary", "category")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be blank")
        return value

    @field_validator("tags")
    @classmethod
    def tags_have_no_whitespace(cls, value: list[str]) -> list[str]:
        # The /projects/ tag filter matches tags via a CSS attribute selector
        # (`[data-tags~="..."]`) against a space-separated attribute value —
        # a tag containing whitespace would silently split into two tokens
        # there and never match as intended.
        for tag in value:
            if not tag or tag != tag.strip() or " " in tag:
                raise ValueError(
                    f"Project.tags entry {tag!r} must be a single non-blank token with no spaces"
                )
        return value


class PageContent(BaseModel):
    """A single Markdown-authored page (About, Contact, ...)."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    body_html: str


class SiteConfig(BaseModel):
    """Global site metadata."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    base_url: str
    author_name: str
    social_links: list[NavItem] = []
