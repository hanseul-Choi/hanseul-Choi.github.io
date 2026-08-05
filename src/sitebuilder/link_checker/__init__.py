"""Public API of the link_checker module.

Other modules must import only from here, never from
`sitebuilder.link_checker.checker` directly — enforced by import-linter.
"""

from sitebuilder.link_checker.checker import LinkCheckError, LinkIssue, check_internal_links

__all__ = ["LinkCheckError", "LinkIssue", "check_internal_links"]
