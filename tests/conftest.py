"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def fixtures_dir(request):
    """Return path to tests/fixtures directory."""
    return request.fspath.dirpath("fixtures")
