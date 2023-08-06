def test_package_import():
    import botcity.plugins.twilio.sms as plugin
    assert plugin.__file__ != ""
