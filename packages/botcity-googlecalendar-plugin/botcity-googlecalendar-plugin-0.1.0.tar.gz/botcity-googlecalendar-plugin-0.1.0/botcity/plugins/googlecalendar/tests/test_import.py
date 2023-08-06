def test_package_import():
    import botcity.plugins.googlecalendar as plugin
    assert plugin.__file__ != ""
