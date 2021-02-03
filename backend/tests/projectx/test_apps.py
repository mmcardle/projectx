from projectx.apps import ProjectXConfig


def test_apps():
    assert ProjectXConfig.name == "projectx"
