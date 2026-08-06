"""Shared fixtures for site_builder tests: a minimal, valid site tree on disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True, slots=True)
class SitePaths:
    project_root: Path
    content_dir: Path
    project_content_dir: Path
    data_dir: Path
    templates_dir: Path
    static_dir: Path
    output_dir: Path


_NAV_YAML = "- title: Home\n  url: /\n- title: Projects\n  url: /projects/\n"
_SITE_YAML = (
    "title: Test Site\ndescription: A test site.\n"
    "base_url: https://example.com\nauthor_name: Tester\n"
)
_PROJECTS_YAML = (
    "- slug: demo\n"
    "  title: Demo\n"
    "  summary: A demo project.\n"
    "  achievements: ['Cut latency 50%']\n"
    "  order: 1\n"
)

_BASE_TEMPLATE = (
    "<!doctype html><html><head><title>{{ site.title }}</title>"
    # References asset_version like the real base.html, so StrictUndefined
    # catches any pipeline.py render_page() call site that forgets to pass
    # it (every template extends base.html, so it's a required kwarg
    # everywhere, not just where it's visibly used).
    '<link rel="stylesheet" href="/static/style.css?v={{ asset_version }}"></head>'
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
_HOME_TEMPLATE = (
    "{% extends 'base.html' %}{% block content %}"
    "<h1>{{ site.author_name | initials }}</h1>"
    "{% for project in featured_projects %}{% include 'components/project_card.html' %}{% endfor %}"
    "{% endblock %}"
)
_PROJECTS_TEMPLATE = (
    "{% extends 'base.html' %}{% block content %}"
    "{% for project in projects %}{% include 'components/project_card.html' %}{% endfor %}"
    "{% endblock %}"
)
_PROJECT_CARD_TEMPLATE = (
    "{% set detail = project_details.get(project.slug) if project_details is defined else none %}"
    "<article><h2>{{ project.title }}</h2><p>{{ project.summary }}</p>"
    "{% if project.achievements %}<ul class='ach'>"
    "{% for a in project.achievements %}<li>{{ a }}</li>{% endfor %}</ul>{% endif %}"
    "{% if detail %}"
    '<a class="detail-link" href="#project-modal-{{ project.slug }}">자세히 보기</a>{% endif %}'
    "</article>"
    "{% if detail %}"
    '<div id="project-modal-{{ project.slug }}" class="modal-overlay">'
    "<a href='#' class='modal-close'>x</a>{{ detail.body_html | collapsible_h3 }}"
    "<a href='/projects/{{ project.slug }}/' class='modal-full-link'>전체 페이지에서 보기</a>"
    "</div>{% endif %}"
)
_PROJECT_DETAIL_TEMPLATE = (
    "{% extends 'base.html' %}{% block content %}"
    "<h1>{{ project.title }}</h1>{{ detail.body_html | safe }}{% endblock %}"
)


@pytest.fixture
def site_paths(tmp_path: Path) -> SitePaths:
    project_root = tmp_path
    content_dir = project_root / "content"
    project_content_dir = project_root / "content-projects"
    data_dir = project_root / "data"
    templates_dir = project_root / "templates"
    static_dir = project_root / "static"
    output_dir = project_root / "dist"

    content_dir.mkdir()
    project_content_dir.mkdir()
    data_dir.mkdir()
    templates_dir.mkdir()
    (templates_dir / "components").mkdir()
    static_dir.mkdir()

    (content_dir / "index.md").write_text("---\ntitle: Home\n---\nWelcome.\n", encoding="utf-8")
    (content_dir / "about.md").write_text("---\ntitle: About\n---\nHi there.\n", encoding="utf-8")
    (project_content_dir / "demo.md").write_text(
        "---\ntitle: Demo\n---\n## Architecture\n\nHow it's built.\n", encoding="utf-8"
    )
    (data_dir / "navigation.yaml").write_text(_NAV_YAML, encoding="utf-8")
    (data_dir / "site.yaml").write_text(_SITE_YAML, encoding="utf-8")
    (data_dir / "projects.yaml").write_text(_PROJECTS_YAML, encoding="utf-8")
    (templates_dir / "base.html").write_text(_BASE_TEMPLATE, encoding="utf-8")
    (templates_dir / "home.html").write_text(_HOME_TEMPLATE, encoding="utf-8")
    (templates_dir / "page.html").write_text(_PAGE_TEMPLATE, encoding="utf-8")
    (templates_dir / "projects.html").write_text(_PROJECTS_TEMPLATE, encoding="utf-8")
    (templates_dir / "project_detail.html").write_text(_PROJECT_DETAIL_TEMPLATE, encoding="utf-8")
    (templates_dir / "components" / "nav.html").write_text(_NAV_TEMPLATE, encoding="utf-8")
    (templates_dir / "components" / "project_card.html").write_text(
        _PROJECT_CARD_TEMPLATE, encoding="utf-8"
    )
    (static_dir / "style.css").write_text("body { margin: 0; }", encoding="utf-8")

    return SitePaths(
        project_root=project_root,
        content_dir=content_dir,
        project_content_dir=project_content_dir,
        data_dir=data_dir,
        templates_dir=templates_dir,
        static_dir=static_dir,
        output_dir=output_dir,
    )
