"""Build pipeline: orchestrates content_loader -> renderer -> link_checker.

This is the only file in the repo allowed to import all four other
sitebuilder modules (AGENTS.md rule 25 — "App Shell"). See docs/POLICY.md
and docs/THREAT_MODEL.md in this directory for the output-path guard rules.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from sitebuilder.content_loader import (
    ContentLoadError,
    load_navigation,
    load_pages,
    load_projects,
    load_site_config,
)
from sitebuilder.link_checker import LinkIssue, check_internal_links
from sitebuilder.renderer import RenderError, create_environment, render_page


class BuildError(Exception):
    """Raised when the build pipeline cannot produce a valid site."""


@dataclass(frozen=True, slots=True)
class BuildResult:
    output_dir: Path
    pages_written: list[str] = field(default_factory=list)
    link_issues: list[LinkIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.link_issues


def _ensure_output_dir_allowed(output_dir: Path, project_root: Path) -> Path:
    """Refuse to build into a directory outside `project_root` (THREAT_MODEL.md #1)."""
    resolved_root = project_root.resolve()
    resolved_output = output_dir.resolve()
    if resolved_root not in resolved_output.parents and resolved_output != resolved_root:
        raise BuildError(
            f"Refusing to write build output to {output_dir} — it resolves "
            f"outside the project root {project_root}"
        )
    return resolved_output


def build_site(
    *,
    content_dir: Path,
    data_dir: Path,
    templates_dir: Path,
    static_dir: Path,
    output_dir: Path,
    project_root: Path,
    strict: bool = True,
) -> BuildResult:
    """Build the full static site.

    Raises BuildError if content fails validation, templates fail to render,
    or (when strict=True) the link checker finds any issue.
    """
    resolved_output = _ensure_output_dir_allowed(output_dir, project_root)

    try:
        site_config = load_site_config(data_dir)
        nav = load_navigation(data_dir)
        projects = load_projects(data_dir)
        pages = load_pages(content_dir)
    except ContentLoadError as exc:
        raise BuildError(f"Content loading failed: {exc}") from exc

    env = create_environment(templates_dir)
    resolved_output.mkdir(parents=True, exist_ok=True)
    pages_written: list[str] = []

    try:
        for page in pages:
            target = "index.html" if page.slug == "index" else f"{page.slug}/index.html"
            html = render_page(env, "page.html", site=site_config, nav=nav, page=page)
            _write(resolved_output / target, html)
            pages_written.append(target)

        projects_html = render_page(
            env, "projects.html", site=site_config, nav=nav, projects=projects
        )
        _write(resolved_output / "projects" / "index.html", projects_html)
        pages_written.append("projects/index.html")
    except RenderError as exc:
        raise BuildError(f"Rendering failed: {exc}") from exc

    if static_dir.is_dir():
        shutil.copytree(static_dir, resolved_output / "static", dirs_exist_ok=True)

    link_issues = check_internal_links(resolved_output)
    if strict and link_issues:
        details = "\n".join(str(issue) for issue in link_issues)
        raise BuildError(f"Link check failed with {len(link_issues)} issue(s):\n{details}")

    return BuildResult(
        output_dir=resolved_output, pages_written=pages_written, link_issues=link_issues
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
