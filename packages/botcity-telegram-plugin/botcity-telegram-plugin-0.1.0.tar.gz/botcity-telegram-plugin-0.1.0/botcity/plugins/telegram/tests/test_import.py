def test_package_import():
    import botcity.plugins.telegram as plugin
    assert plugin.__file__ != ""
