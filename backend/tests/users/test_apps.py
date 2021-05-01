from users.app import UsersConfig


def test_app():
    assert UsersConfig.name == "users"
