from users.consumers import UserConsumer


def test_userconsumer():
    consumer = UserConsumer()
    assert consumer.user_message(None) is None
