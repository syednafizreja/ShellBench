"""Smoke test: the shellbench package can be imported."""


def test_import_shellbench():
    """Import the package and check it exposes a version string."""
    import shellbench

    assert isinstance(shellbench.__version__, str)
