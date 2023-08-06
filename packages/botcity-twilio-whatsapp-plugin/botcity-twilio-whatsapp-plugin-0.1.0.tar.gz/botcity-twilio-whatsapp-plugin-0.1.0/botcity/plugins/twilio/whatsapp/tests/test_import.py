def test_package_import():
    import botcity.plugins.twilio.whatsapp as plugin
    assert plugin.__file__ != ""
