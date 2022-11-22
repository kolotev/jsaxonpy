def test_version():
    from jsaxonpy import __version__, version
    assert __version__ is not None
    assert version is not None
