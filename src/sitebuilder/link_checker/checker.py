"""Offline checks over a built site's HTML output.

See docs/POLICY.md and docs/THREAT_MODEL.md in this directory: this module
never makes network requests by default, and every filesystem access stays
confined to the given output directory (path-traversal guard).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

_EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel"}
_SKIP_PREFIXES = ("#",)


@dataclass(frozen=True, slots=True)
class LinkIssue:
    """A single problem found while checking a built page."""

    source_file: Path
    kind: str  # "broken_link" | "missing_alt"
    detail: str

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"{self.source_file}: [{self.kind}] {self.detail}"


class LinkCheckError(Exception):
    """Raised for programmer errors (bad output_dir), not for found issues."""


def _attr_str(value: str | list[str] | None) -> str:
    """Normalize a bs4 tag attribute (str, multi-valued list, or absent) to a plain string.

    bs4 returns `list[str]` for attributes it treats as space-separated
    (e.g. `class`); `href`/`src`/`alt` are not among those, but the type
    stub covers the general case, so we narrow it explicitly here instead
    of silencing mypy.
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(value)
    return value


def _ensure_within_base(path: Path, base: Path) -> Path:
    resolved_base = base.resolve()
    resolved_path = path.resolve()
    if resolved_base not in resolved_path.parents and resolved_path != resolved_base:
        raise LinkCheckError(f"Refusing to inspect {path} — it resolves outside {base}")
    return resolved_path


def _resolve_internal_target(html_file: Path, output_dir: Path, href: str) -> Path | None:
    """Resolve an internal href/src to a filesystem path, or None if external/skippable."""
    if not href or href.startswith(_SKIP_PREFIXES):
        return None

    parsed = urlparse(href)
    if parsed.scheme in _EXTERNAL_SCHEMES:
        return None
    if parsed.netloc:  # protocol-relative or scheme-less external link
        return None

    path_part = parsed.path
    if not path_part:
        return None

    if path_part.startswith("/"):
        target = output_dir / path_part.lstrip("/")
    else:
        target = html_file.parent / path_part

    if target.suffix == "" or path_part.endswith("/"):
        target = target / "index.html"

    return target


def _check_internal_target(
    html_file: Path, output_dir: Path, raw_ref: str, *, attr: str
) -> list[LinkIssue]:
    """Resolve `raw_ref` (an href or src) and return any broken_link issue found."""
    target = _resolve_internal_target(html_file, output_dir, raw_ref)
    if target is None:
        return []

    resolved = target.resolve()
    resolved_output = output_dir.resolve()
    if resolved_output not in resolved.parents and resolved != resolved_output:
        return [LinkIssue(html_file, "broken_link", f"{attr}={raw_ref!r} escapes output dir")]
    if not resolved.is_file():
        return [LinkIssue(html_file, "broken_link", f"{attr}={raw_ref!r} -> {target}")]
    return []


def check_internal_links(output_dir: Path) -> list[LinkIssue]:
    """Scan every `*.html` file under `output_dir` for broken links and missing alt text."""
    if not output_dir.is_dir():
        raise LinkCheckError(f"Output directory does not exist: {output_dir}")

    issues: list[LinkIssue] = []
    for html_file in sorted(output_dir.rglob("*.html")):
        _ensure_within_base(html_file, output_dir)
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")

        for anchor in soup.find_all("a"):
            href = _attr_str(anchor.get("href"))
            issues.extend(_check_internal_target(html_file, output_dir, href, attr="href"))

        for image in soup.find_all("img"):
            src = _attr_str(image.get("src"))
            issues.extend(_check_internal_target(html_file, output_dir, src, attr="src"))
            if not _attr_str(image.get("alt")):
                issues.append(
                    LinkIssue(html_file, "missing_alt", f"img src={src!r} has no alt text")
                )

    return issues
