from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import pytest

DEFAULT_ALLOWED_HOSTS = "demowebshop.tricentis.com,localhost,127.0.0.1"


def is_allowed(url: str, allowed: set[str]) -> bool:
    host = urlparse(url).hostname or ""
    return host in allowed


def load_allowed_hosts(raw: str) -> set[str]:
    return {host.strip().lower() for host in raw.split(",") if host.strip()}


@pytest.fixture(autouse=True)
def _qa_sandbox(request: pytest.FixtureRequest) -> None:
    """Abort all outbound network requests except allowlisted hosts.

    Never instantiates a browser itself: only when the test actually
    uses the `page`/`context` fixtures.
    """
    if os.environ.get("QA_SANDBOX", "1") == "0":
        return

    needs_browser = "page" in request.fixturenames or "context" in request.fixturenames
    if not needs_browser:
        return

    allowed = load_allowed_hosts(
        os.environ.get("QA_SANDBOX_ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS)
    )
    context: Any = request.getfixturevalue("context")

    def _route(route: Any) -> None:
        if is_allowed(route.request.url, allowed):
            route.continue_()
        else:
            route.abort("blockedbyclient")

    context.route("**/*", _route)