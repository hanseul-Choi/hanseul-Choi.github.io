"""Jinja2 rendering engine wrapper.

See docs/POLICY.md and docs/THREAT_MODEL.md in this directory: autoescape
must stay on, and the templates directory must never come from untrusted
input.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2


class RenderError(Exception):
    """Raised when a template cannot be found or fails to render."""


def create_environment(templates_dir: Path) -> jinja2.Environment:
    """Build a Jinja2 environment rooted at `templates_dir`.

    autoescape is always on (see THREAT_MODEL.md) — this is not
    configurable by callers on purpose.
    """
    if not templates_dir.is_dir():
        raise RenderError(f"Templates directory does not exist: {templates_dir}")

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        autoescape=jinja2.select_autoescape(enabled_extensions=("html",), default=True),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


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
