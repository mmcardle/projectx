from users.apps import UsersConfig


def test_apps():
    assert UsersConfig.name == "users"
