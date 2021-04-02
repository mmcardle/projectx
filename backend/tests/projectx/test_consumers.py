import json
from unittest import mock

import pytest

from projectx.consumers import UserWebSocketConsumer


@pytest.fixture(name="websocket_consumer")
def create_websocket_consumer():
    websocket_con = UserWebSocketConsumer()
    websocket_con.scope = dict()
    websocket_con.channel_layer = mock.Mock()
    websocket_con.channel_name = "channel_name"
    websocket_con.base_send = mock.Mock()
    websocket_con.close = mock.Mock()
    return websocket_con


def test_web_socket_consumer_is_anonymous(mocker):

    mocker.patch("projectx.consumers.AsyncToSync")
    user = mock.Mock(is_anonymous=True)
    websocket_consumer = UserWebSocketConsumer()
    websocket_consumer.scope = dict(user=user)
    websocket_consumer.channel_name = "channel_name"
    websocket_consumer.base_send = mock.Mock()
    websocket_consumer.close = mock.Mock()
    websocket_consumer.accept = mock.Mock()

    websocket_consumer.connect()

    assert websocket_consumer.close.mock_calls == [mock.call()]
    assert websocket_consumer.accept.mock_calls == []
    assert websocket_consumer.joined_channels == []


def test_web_socket_consumer(mocker):

    AsyncToSync = mocker.patch("projectx.consumers.AsyncToSync")
    user = mock.Mock(is_anonymous=False, is_staff=False, unique_name=lambda: "user1")
    websocket_consumer = UserWebSocketConsumer()
    websocket_consumer.scope = dict(user=user)
    websocket_consumer.channel_name = "channel_name"
    websocket_consumer.base_send = mock.Mock()
    websocket_consumer.channel_layer = mock.Mock()
    websocket_consumer.close = mock.Mock()
    websocket_consumer.accept = mock.Mock()

    websocket_consumer.connect()

    assert websocket_consumer.close.mock_calls == []
    assert websocket_consumer.accept.mock_calls == [mock.call()]
    assert websocket_consumer.joined_channels == ["user1"]

    assert AsyncToSync.mock_calls == [
        mock.call(websocket_consumer.channel_layer.group_add),
        mock.call()("user1", "channel_name"),
    ]


def test_web_socket_consumer_user_message_no_data(websocket_consumer):
    websocket_consumer.send_json = mock.Mock()
    websocket_consumer.user_message("{}")
    assert websocket_consumer.send_json.mock_calls == []


def test_web_socket_consumer_user_message_with_data(websocket_consumer):
    message = {"key": "val"}
    websocket_consumer.send_json = mock.Mock()
    websocket_consumer.user_message({"data": json.dumps(message)})
    assert websocket_consumer.send_json.mock_calls == [mock.call(message)]


def test_web_socket_consumer_user_message_json_error(websocket_consumer):
    message = "bad_data"
    websocket_consumer.send_json = mock.Mock()
    websocket_consumer.user_message({"data": message})
    assert websocket_consumer.send_json.mock_calls == []


def test_web_socket_consumer_receive_json(websocket_consumer, mocker):
    logger = mocker.patch("projectx.consumers.logger")
    websocket_consumer.receive_json("msg")
    assert logger.mock_calls == [
        mock.call.debug("receive_json %s.", "msg"),
        mock.call.warning("Ignoring message %s.", "msg"),
    ]


def test_web_socket_consumer_disconnect(websocket_consumer, mocker):
    AsyncToSync = mocker.patch("projectx.consumers.AsyncToSync")
    logger = mocker.patch("projectx.consumers.logger")
    websocket_consumer.joined_channels = ["channel1", "channel2"]
    websocket_consumer.user = mock.Mock()
    websocket_consumer.disconnect("close_code")
    assert logger.mock_calls == [
        mock.call.debug(
            "Disconnect %s %s from channels %s", websocket_consumer.user, "channel_name", ["channel1", "channel2"]
        ),
    ]

    assert AsyncToSync.mock_calls == [
        mock.call(websocket_consumer.channel_layer.group_discard),
        mock.call()("channel1", "channel_name"),
        mock.call(websocket_consumer.channel_layer.group_discard),
        mock.call()("channel2", "channel_name"),
    ]
