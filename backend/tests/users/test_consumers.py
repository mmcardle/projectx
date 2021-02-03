from users.consumers import UserConsumer


def test_UserConsumer():
    consumer = UserConsumer()
    assert consumer.user_message(None) is None
