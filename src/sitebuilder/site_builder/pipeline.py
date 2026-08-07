"""Build pipeline: orchestrates content_loader -> renderer -> link_checker.

This is the only file in the repo allowed to import all four other
sitebuilder modules (AGENTS.md rule 25 — "App Shell"). See docs/POLICY.md
and docs/THREAT_MODEL.md in this directory for the output-path guard rules.
"""

from __future__ import annotations

import hashlib
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
from sitebuilder.contracts import Project
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


def _compute_asset_version(static_dir: Path) -> str:
    """A short, deterministic hash of every file under `static_dir`.

    Used as a `?v=...` cache-busting query string on the CSS/JS tags in
    base.html — not a security boundary, purely so a deploy is never masked
    by a visitor's or the CDN's cached copy of an old stylesheet/script (see
    docs/HISTORY.md for the incident that prompted this). Changes whenever
    any static asset's bytes change; returns a stable placeholder if
    `static_dir` doesn't exist so callers never need a special case.
    """
    if not static_dir.is_dir():
        return "no-static"

    digest = hashlib.sha256()
    for path in sorted(static_dir.rglob("*")):
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


def _group_projects_by_category(projects: list[Project]) -> list[tuple[str, list[Project]]]:
    """Group projects by `category`, preserving each category's first-
    appearance order.

    `projects` is expected to already be sorted by `Project.order` (as
    `load_projects` returns it) — grouping then walks that list in order and
    buckets by category using a dict, whose iteration order in Python is
    insertion order. So the category containing the lowest-`order` project
    is shown first, with no separate "category order" field to keep in sync.
    """
    groups: dict[str, list[Project]] = {}
    for project in projects:
        groups.setdefault(project.category, []).append(project)
    return list(groups.items())


def _collect_tags(projects: list[Project]) -> list[str]:
    """Every distinct tag across `projects`, in first-appearance order.

    Feeds the /projects/ tag filter's chip list (see templates/projects.html)
    — first-appearance order keeps it deterministic without imposing an
    unrelated alphabetical/frequency sort on top of the author's existing
    manual `order` field.
    """
    seen: dict[str, None] = {}
    for project in projects:
        for tag in project.tags:
            seen.setdefault(tag, None)
    return list(seen)


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
    project_content_dir: Path,
    strict: bool = True,
) -> BuildResult:
    """Build the full static site.

    `project_content_dir` holds one optional long-form Markdown write-up per
    project (matched by filename stem == Project.slug, e.g.
    `content/projects/my-app.md`) — architecture notes, diagrams, etc. A
    project without a matching file simply gets no detail page or "자세히
    보기" link; this directory may exist and be empty.

    Raises BuildError if content fails validation, templates fail to render,
    or (when strict=True) the link checker finds any issue.
    """
    resolved_output = _ensure_output_dir_allowed(output_dir, project_root)

    try:
        site_config = load_site_config(data_dir)
        nav = load_navigation(data_dir)
        projects = load_projects(data_dir)
        pages = load_pages(content_dir)
        project_details = {detail.slug: detail for detail in load_pages(project_content_dir)}
    except ContentLoadError as exc:
        raise BuildError(f"Content loading failed: {exc}") from exc

    detail_slugs = set(project_details)
    asset_version = _compute_asset_version(static_dir)

    env = create_environment(templates_dir)
    resolved_output.mkdir(parents=True, exist_ok=True)
    pages_written: list[str] = []

    try:
        for page in pages:
            is_home = page.slug == "index"
            target = "index.html" if is_home else f"{page.slug}/index.html"
            current_path = "/" if is_home else f"/{page.slug}/"
            template_name = "home.html" if is_home else "page.html"
            template_kwargs = (
                {
                    "featured_projects": projects[:3],
                    "detail_slugs": detail_slugs,
                    "project_details": project_details,
                }
                if is_home
                else {}
            )

            html = render_page(
                env,
                template_name,
                site=site_config,
                nav=nav,
                page=page,
                current_path=current_path,
                asset_version=asset_version,
                **template_kwargs,
            )
            _write(resolved_output / target, html)
            pages_written.append(target)

        projects_html = render_page(
            env,
            "projects.html",
            site=site_config,
            nav=nav,
            projects=projects,
            project_groups=_group_projects_by_category(projects),
            all_tags=_collect_tags(projects),
            current_path="/projects/",
            detail_slugs=detail_slugs,
            project_details=project_details,
            asset_version=asset_version,
        )
        _write(resolved_output / "projects" / "index.html", projects_html)
        pages_written.append("projects/index.html")

        for project in projects:
            detail = project_details.get(project.slug)
            if detail is None:
                continue
            detail_html = render_page(
                env,
                "project_detail.html",
                site=site_config,
                nav=nav,
                project=project,
                detail=detail,
                current_path="/projects/",
                asset_version=asset_version,
            )
            target = f"projects/{project.slug}/index.html"
            _write(resolved_output / target, detail_html)
            pages_written.append(target)
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
