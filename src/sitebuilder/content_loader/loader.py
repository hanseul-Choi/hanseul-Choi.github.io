"""Load and validate site content from disk into contract objects.

See docs/POLICY.md and docs/THREAT_MODEL.md in this directory before editing:
all file access here must stay confined to the caller-provided base
directory, and YAML must only ever be parsed with `yaml.safe_load`.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import markdown
import yaml
from pydantic import ValidationError

from sitebuilder.contracts import NavItem, PageContent, Project, SiteConfig

_MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "toc"]


class ContentLoadError(Exception):
    """Raised whenever content on disk cannot be turned into a valid contract."""


def _ensure_within_base(path: Path, base: Path) -> Path:
    """Resolve `path` and guarantee it is inside `base`.

    Raises ContentLoadError otherwise. This is the path-traversal guard
    required by docs/THREAT_MODEL.md.
    """
    resolved_base = base.resolve()
    resolved_path = path.resolve()
    if resolved_base not in resolved_path.parents and resolved_path != resolved_base:
        raise ContentLoadError(
            f"Refusing to read {path} — it resolves outside the allowed base directory {base}"
        )
    return resolved_path


def _read_yaml(path: Path, base: Path) -> object:
    safe_path = _ensure_within_base(path, base)
    if not safe_path.is_file():
        raise ContentLoadError(f"Expected a YAML file at {path}, found none")
    raw = safe_path.read_text(encoding="utf-8")
    try:
        return yaml.safe_load(raw)  # never yaml.load: see THREAT_MODEL.md
    except yaml.YAMLError as exc:
        raise ContentLoadError(f"Invalid YAML in {path}: {exc}") from exc


def load_navigation(data_dir: Path, filename: str = "navigation.yaml") -> list[NavItem]:
    """Load the site navigation menu from `data_dir/filename`."""
    raw = _read_yaml(data_dir / filename, data_dir)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ContentLoadError(
            f"{filename} must contain a YAML list of nav items, got {type(raw).__name__}"
        )
    try:
        return [NavItem.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise ContentLoadError(f"Invalid nav item in {filename}: {exc}") from exc


def load_projects(data_dir: Path, filename: str = "projects.yaml") -> list[Project]:
    """Load the project list from `data_dir/filename`, sorted by `order`."""
    raw = _read_yaml(data_dir / filename, data_dir)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ContentLoadError(
            f"{filename} must contain a YAML list of projects, got {type(raw).__name__}"
        )
    try:
        projects = [Project.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise ContentLoadError(f"Invalid project entry in {filename}: {exc}") from exc

    slugs = [project.slug for project in projects]
    duplicates = {slug for slug in slugs if slugs.count(slug) > 1}
    if duplicates:
        raise ContentLoadError(f"Duplicate project slug(s) in {filename}: {sorted(duplicates)}")

    return sorted(projects, key=lambda project: project.order)


def load_site_config(data_dir: Path, filename: str = "site.yaml") -> SiteConfig:
    """Load global site metadata from `data_dir/filename`."""
    raw = _read_yaml(data_dir / filename, data_dir)
    if not isinstance(raw, dict):
        raise ContentLoadError(f"{filename} must contain a YAML mapping, got {type(raw).__name__}")
    try:
        return SiteConfig.model_validate(raw)
    except ValidationError as exc:
        raise ContentLoadError(f"Invalid site config in {filename}: {exc}") from exc


def load_pages(content_dir: Path) -> list[PageContent]:
    """Load every Markdown page under `content_dir` (non-recursive)."""
    if not content_dir.is_dir():
        raise ContentLoadError(f"Content directory does not exist: {content_dir}")

    pages: list[PageContent] = []
    for md_path in sorted(content_dir.glob("*.md")):
        _ensure_within_base(md_path, content_dir)
        post = frontmatter.loads(md_path.read_text(encoding="utf-8"))
        title = post.metadata.get("title")
        if not title:
            raise ContentLoadError(f"{md_path} is missing required 'title' frontmatter")
        body_html = markdown.markdown(post.content, extensions=_MARKDOWN_EXTENSIONS)
        try:
            pages.append(PageContent(slug=md_path.stem, title=str(title), body_html=body_html))
        except ValidationError as exc:
            raise ContentLoadError(f"Invalid page content in {md_path}: {exc}") from exc

    return pages
