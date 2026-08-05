"""Typer CLI for the sitebuilder App Shell: `build` and `serve`.

See docs/POLICY.md and docs/THREAT_MODEL.md in this directory for the
default-deny rules this CLI enforces (output path, serve host binding).
"""

from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path

import typer

from sitebuilder.site_builder.pipeline import BuildError, build_site

app = typer.Typer(help="Build and preview the portfolio site.")

REPO_ROOT = Path(__file__).resolve().parents[3]


class HostNotAllowedError(ValueError):
    """Raised when `serve` is asked to bind a public interface without opt-in."""


def check_host_allowed(host: str, allow_public: bool) -> None:
    """Refuse to bind anything but localhost unless `allow_public` is set.

    Kept as a standalone function so it is unit-testable without actually
    starting a blocking TCP server (see docs/HISTORY.md).
    """
    if host not in {"127.0.0.1", "localhost"} and not allow_public:
        raise HostNotAllowedError(
            f"Refusing to bind host={host!r} without --allow-public "
            "(defaults to localhost-only; see docs/THREAT_MODEL.md)"
        )


@app.command()
def build(
    content_dir: Path = typer.Option(REPO_ROOT / "content" / "pages", help="Markdown pages dir"),
    data_dir: Path = typer.Option(REPO_ROOT / "data", help="YAML data dir"),
    templates_dir: Path = typer.Option(REPO_ROOT / "templates", help="Jinja2 templates dir"),
    static_dir: Path = typer.Option(REPO_ROOT / "static", help="Static assets dir"),
    output_dir: Path = typer.Option(REPO_ROOT / "dist", help="Build output dir"),
    project_root: Path = typer.Option(
        REPO_ROOT, help="Directory output_dir must resolve inside of (see THREAT_MODEL.md)"
    ),
    strict: bool = typer.Option(True, help="Fail the build on any link-check issue"),
) -> None:
    """Build the static site into `output_dir`."""
    try:
        result = build_site(
            content_dir=content_dir,
            data_dir=data_dir,
            templates_dir=templates_dir,
            static_dir=static_dir,
            output_dir=output_dir,
            project_root=project_root,
            strict=strict,
        )
    except BuildError as exc:
        typer.secho(f"Build failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.secho(
        f"Built {len(result.pages_written)} page(s) into {result.output_dir} "
        f"({len(result.link_issues)} link issue(s))",
        fg=typer.colors.GREEN,
    )


@app.command()
def serve(
    output_dir: Path = typer.Option(REPO_ROOT / "dist", help="Directory to serve"),
    host: str = typer.Option("127.0.0.1", help="Bind host (localhost-only by default)"),
    port: int = typer.Option(8000, help="Bind port"),
    allow_public: bool = typer.Option(False, help="Allow binding a non-localhost host"),
) -> None:
    """Serve a previously built site for local preview."""
    try:
        check_host_allowed(host, allow_public)
    except HostNotAllowedError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if not output_dir.is_dir():
        typer.secho(
            f"{output_dir} does not exist yet — run `sitebuilder build` first",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(output_dir))
    with socketserver.TCPServer((host, port), handler) as httpd:
        typer.echo(f"Serving {output_dir} at http://{host}:{port} (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    app()
