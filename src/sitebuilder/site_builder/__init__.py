"""Public API of the site_builder module (the App Shell).

This module (and only this module) is allowed to import every other
sitebuilder module — see AGENTS.md rule 25.
"""

from sitebuilder.site_builder.cli import app
from sitebuilder.site_builder.pipeline import BuildError, BuildResult, build_site

__all__ = ["BuildError", "BuildResult", "app", "build_site"]
