from projectx.wsgi import application


def test_wsgi():
    assert application is not None
