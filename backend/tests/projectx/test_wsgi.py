from projectx.asgi import application


def test_asgi():
    assert application is not None
