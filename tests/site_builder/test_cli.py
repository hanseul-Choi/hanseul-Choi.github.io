"""Tests for sitebuilder.site_builder.cli.

Covers the `build` command wiring and the localhost-only guard for `serve`
documented in src/sitebuilder/site_builder/docs/THREAT_MODEL.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from sitebuilder.site_builder.cli import HostNotAllowedError, app, check_host_allowed
from tests.site_builder.conftest import SitePaths

runner = CliRunner()


def _build_args(site_paths: SitePaths, **overrides: str) -> list[str]:
    args = {
        "--content-dir": str(site_paths.content_dir),
        "--data-dir": str(site_paths.data_dir),
        "--templates-dir": str(site_paths.templates_dir),
        "--static-dir": str(site_paths.static_dir),
        "--output-dir": str(site_paths.output_dir),
        "--project-root": str(site_paths.project_root),
        **overrides,
    }
    return ["build", *[part for pair in args.items() for part in pair]]


class TestCheckHostAllowed:
    @pytest.mark.parametrize("host", ["127.0.0.1", "localhost"])
    def test_localhost_is_always_allowed(self, host: str) -> None:
        check_host_allowed(host, allow_public=False)  # must not raise

    def test_public_host_without_opt_in_is_rejected(self) -> None:
        with pytest.raises(HostNotAllowedError):
            check_host_allowed("0.0.0.0", allow_public=False)

    def test_public_host_with_opt_in_is_allowed(self) -> None:
        check_host_allowed("0.0.0.0", allow_public=True)  # must not raise


class TestBuildCommand:
    def test_succeeds_on_valid_site(self, site_paths: SitePaths) -> None:
        result = runner.invoke(app, _build_args(site_paths))
        assert result.exit_code == 0, result.output
        assert "Built" in result.output
        assert (site_paths.output_dir / "index.html").is_file()

    def test_exits_non_zero_on_build_error(self, site_paths: SitePaths) -> None:
        (site_paths.templates_dir / "page.html").unlink()
        result = runner.invoke(app, _build_args(site_paths))
        assert result.exit_code == 1
        assert "Build failed" in result.output

    def test_exits_non_zero_when_output_dir_escapes_project_root(
        self, site_paths: SitePaths, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        outside_dir = tmp_path_factory.mktemp("outside") / "dist"
        result = runner.invoke(app, _build_args(site_paths, **{"--output-dir": str(outside_dir)}))
        assert result.exit_code == 1
        assert "outside the project root" in result.output


class TestServeCommand:
    def test_refuses_public_host_without_flag(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["serve", "--output-dir", str(tmp_path), "--host", "0.0.0.0"])
        assert result.exit_code == 1
        assert "Refusing to bind" in result.output

    def test_refuses_when_output_dir_missing(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["serve", "--output-dir", str(tmp_path / "does-not-exist")])
        assert result.exit_code == 1
        assert "does not exist" in result.output
