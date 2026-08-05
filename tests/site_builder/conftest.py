"""Shared fixtures for site_builder tests: a minimal, valid site tree on disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True, slots=True)
class SitePaths:
    project_root: Path
    content_dir: Path
    data_dir: Path
    templates_dir: Path
    static_dir: Path
    output_dir: Path


_NAV_YAML = "- title: Home\n  url: /\n- title: Projects\n  url: /projects/\n"
_SITE_YAML = (
    "title: Test Site\ndescription: A test site.\n"
    "base_url: https://example.com\nauthor_name: Tester\n"
)
_PROJECTS_YAML = "- slug: demo\n  title: Demo\n  summary: A demo project.\n  order: 1\n"

_BASE_TEMPLATE = (
    "<!doctype html><html><head><title>{{ site.title }}</title></head>"
    "<body>{% include 'components/nav.html' %}"
    "{% block content %}{% endblock %}</body></html>"
)
_NAV_TEMPLATE = (
    '<nav>{% for item in nav %}<a href="{{ item.url }}">{{ item.title }}</a>{% endfor %}</nav>'
)
_PAGE_TEMPLATE = (
    "{% extends 'base.html' %}{% block content %}"
    "<h1>{{ page.title }}</h1>{{ page.body_html | safe }}{% endblock %}"
)
_PROJECTS_TEMPLATE = (
    "{% extends 'base.html' %}{% block content %}"
    "{% for project in projects %}{% include 'components/project_card.html' %}{% endfor %}"
    "{% endblock %}"
)
_PROJECT_CARD_TEMPLATE = (
    "<article><h2>{{ project.title }}</h2><p>{{ project.summary }}</p></article>"
)


@pytest.fixture
def site_paths(tmp_path: Path) -> SitePaths:
    project_root = tmp_path
    content_dir = project_root / "content"
    data_dir = project_root / "data"
    templates_dir = project_root / "templates"
    static_dir = project_root / "static"
    output_dir = project_root / "dist"

    content_dir.mkdir()
    data_dir.mkdir()
    templates_dir.mkdir()
    (templates_dir / "components").mkdir()
    static_dir.mkdir()

    (content_dir / "index.md").write_text("---\ntitle: Home\n---\nWelcome.\n", encoding="utf-8")
    (data_dir / "navigation.yaml").write_text(_NAV_YAML, encoding="utf-8")
    (data_dir / "site.yaml").write_text(_SITE_YAML, encoding="utf-8")
    (data_dir / "projects.yaml").write_text(_PROJECTS_YAML, encoding="utf-8")
    (templates_dir / "base.html").write_text(_BASE_TEMPLATE, encoding="utf-8")
    (templates_dir / "page.html").write_text(_PAGE_TEMPLATE, encoding="utf-8")
    (templates_dir / "projects.html").write_text(_PROJECTS_TEMPLATE, encoding="utf-8")
    (templates_dir / "components" / "nav.html").write_text(_NAV_TEMPLATE, encoding="utf-8")
    (templates_dir / "components" / "project_card.html").write_text(
        _PROJECT_CARD_TEMPLATE, encoding="utf-8"
    )
    (static_dir / "style.css").write_text("body { margin: 0; }", encoding="utf-8")

    return SitePaths(
        project_root=project_root,
        content_dir=content_dir,
        data_dir=data_dir,
        templates_dir=templates_dir,
        static_dir=static_dir,
        output_dir=output_dir,
    )
