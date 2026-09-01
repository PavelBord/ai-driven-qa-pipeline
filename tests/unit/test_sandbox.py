from __future__ import annotations

from pipeline.execution.sandbox import is_allowed, load_allowed_hosts


def test_load_allowed_hosts_strips_and_lowercases() -> None:
    hosts = load_allowed_hosts("Example.com, localhost, , 127.0.0.1")
    assert hosts == {"example.com", "localhost", "127.0.0.1"}


def test_is_allowed_accepts_allowlisted_host() -> None:
    allowed = {"demowebshop.tricentis.com"}
    assert is_allowed("https://demowebshop.tricentis.com/login", allowed) is True


def test_is_allowed_blocks_unknown_host() -> None:
    allowed = {"demowebshop.tricentis.com"}
    assert is_allowed("https://evil.invalid/payload", allowed) is False


def test_is_allowed_blocks_subdomain_not_listed() -> None:
    allowed = {"example.com"}
    assert is_allowed("https://sub.example.com/", allowed) is False