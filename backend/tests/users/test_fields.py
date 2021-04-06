from users.fields import LowercaseEmailField


def test_LowercaseEmailField():
    assert LowercaseEmailField().to_python(None) is None
    assert LowercaseEmailField().to_python("NONE@tempurl.com") == "none@tempurl.com"
