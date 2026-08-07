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
from bs4 import BeautifulSoup
from markupsafe import Markup

_SECTION_BOUNDARY_TAGS = {"h2", "h3"}


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


def _collapsible_h3(html: str) -> Markup:
    """Wrap each `<h3>` (and its content up to the next `<h2>`/`<h3>`) in a
    native `<details>` accordion, so long "problem/solution" write-ups can be
    collapsed. No JavaScript involved — `<details>` is expand/collapse and
    keyboard-operable by default.

    `<h2>` sections (e.g. "개요", "성과") are left untouched; only `<h3>`
    subsections are affected, since those are what long case-study pages use
    for individual problem entries.
    """
    soup = BeautifulSoup(html, "html.parser")
    for heading in soup.find_all("h3"):
        to_move = []
        node = heading.next_sibling
        while node is not None and getattr(node, "name", None) not in _SECTION_BOUNDARY_TAGS:
            to_move.append(node)
            node = node.next_sibling

        details = soup.new_tag("details")
        details["class"] = "collapsible"
        summary = soup.new_tag("summary")
        summary.string = heading.get_text(strip=True)
        details.append(summary)
        heading.replace_with(details)
        for element in to_move:
            details.append(element.extract())

    return Markup(str(soup))


def _lightbox_images(html: str) -> Markup:
    """Make every `<img>` in html open full-size on click.

    Pure CSS, no JavaScript: each image becomes a same-page anchor
    (`#lightbox-N`) to a fixed, full-screen overlay shown via the `:target`
    selector; the overlay is itself a link back to `#`, so clicking anywhere
    on the darkened backdrop (or the image) closes it. IDs are numbered in
    document order, scoped to a single render call, so they stay unique
    within one page even with multiple diagrams.
    """
    soup = BeautifulSoup(html, "html.parser")
    for index, img in enumerate(soup.find_all("img"), start=1):
        lightbox_id = f"lightbox-{index}"
        alt_value = img.get("alt")
        alt_text = alt_value if isinstance(alt_value, str) else ""
        src_value = img.get("src")
        src = src_value if isinstance(src_value, str) else ""

        trigger = soup.new_tag("a", href=f"#{lightbox_id}")
        trigger["class"] = "lightbox-trigger"
        img.replace_with(trigger)
        trigger.append(img)

        overlay = soup.new_tag("a", href="#")
        overlay["id"] = lightbox_id
        overlay["class"] = "lightbox-overlay"
        overlay["aria-label"] = "이미지 닫기"
        overlay.append(soup.new_tag("img", src=src, alt=alt_text))
        trigger.insert_after(overlay)

    return Markup(str(soup))


def _truncated(items: list[str], limit: int) -> dict[str, Any]:
    """Split a list into what a compact card shows up front and what's tucked
    behind a "+N개 더" expander.

    Used by project_card.html to keep the achievement/tag lists scannable
    when there are several projects on one page — `hidden` is rendered inside
    a native `<details>` the visitor can expand right there in the card
    (no JS), so the full list is never more than one click away.

    Returns {"visible": items[:limit], "hidden": items[limit:], "hidden_count": len(hidden)}.
    """
    visible = items[:limit]
    hidden = items[limit:]
    return {"visible": visible, "hidden": hidden, "hidden_count": len(hidden)}


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
    env.filters["collapsible_h3"] = _collapsible_h3
    env.filters["lightbox_images"] = _lightbox_images
    env.filters["truncated"] = _truncated
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
