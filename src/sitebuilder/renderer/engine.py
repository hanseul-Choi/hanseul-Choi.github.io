"""Jinja2 rendering engine wrapper.

See docs/POLICY.md and docs/THREAT_MODEL.md in this directory: autoescape
must stay on, and the templates directory must never come from untrusted
input.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jinja2


class RenderError(Exception):
    """Raised when a template cannot be found or fails to render."""


def _initials(name: str) -> str:
    """Reduce a display name to 1-2 characters for the hero avatar placeholder.

    "Hanseul Choi" -> "HC" (first + last token initial).

    A single token is ambiguous: for a space-separated Latin name typed as
    one word it means "just an initial" ("cher" -> "C"), but for a Korean
    full name written surname+given-name with no space, the surname alone
    ("최") reads as a stranger's business card, not a personal avatar — the
    given name is what's recognizable. So a single non-ASCII token uses its
    last 1-2 characters instead: "최한슬" -> "한슬".
    """
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        token = parts[0]
        if not token.isascii() and len(token) >= 2:
            return token[-2:]
        return token[0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def create_environment(templates_dir: Path) -> jinja2.Environment:
    """Build a Jinja2 environment rooted at `templates_dir`.

    autoescape is always on (see THREAT_MODEL.md) — this is not
    configurable by callers on purpose.
    """
    if not templates_dir.is_dir():
        raise RenderError(f"Templates directory does not exist: {templates_dir}")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        autoescape=jinja2.select_autoescape(enabled_extensions=("html",), default=True),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["initials"] = _initials
    # A callable global (not a fixed value) so long-running processes (e.g.
    # `serve` across a year boundary) never render a stale build-time year.
    env.globals["build_year"] = lambda: datetime.now(UTC).year
    return env


def render_page(env: jinja2.Environment, template_name: str, **context: Any) -> str:
    """Render `template_name` with `context`, returning the resulting HTML."""
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound as exc:
        raise RenderError(f"Template not found: {template_name}") from exc

    try:
        return template.render(**context)
    except jinja2.UndefinedError as exc:
        raise RenderError(f"Missing context value while rendering {template_name}: {exc}") from exc
    except jinja2.TemplateError as exc:
        raise RenderError(f"Failed to render {template_name}: {exc}") from exc
