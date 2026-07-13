import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "live: hits real Grok Super (set OOPTDD_GROK_LIVE=1)")
