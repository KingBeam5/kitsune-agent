"""Kitsune Agent reports its host OS as Kitsune Linux (display text only)."""
from hermes_constants import os_display_name


def test_linux_reports_kitsune_linux():
    assert os_display_name("Linux") == "Kitsune Linux"


def test_other_systems_unchanged():
    assert os_display_name("Darwin") == "Darwin"
    assert os_display_name("Windows") == "Windows"


def test_dump_os_line(monkeypatch):
    import platform
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    import hermes_cli.dump as dump
    src = open(dump.__file__, encoding="utf-8").read()
    assert "os_display_name()" in src


def test_host_hint_names_kitsune_linux(monkeypatch):
    import sys, platform
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr("agent.prompt_builder.is_wsl", lambda: False)
    from agent.prompt_builder import _local_host_hints
    assert _local_host_hints()[0].startswith("Host: Kitsune Linux (")
