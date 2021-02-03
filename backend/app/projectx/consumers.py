import json
import logging
from json.decoder import JSONDecodeError

from asgiref.sync import AsyncToSync
from channels.generic.websocket import JsonWebsocketConsumer

logger = logging.getLogger(__name__)


class BaseWebSocketConsumer(JsonWebsocketConsumer):

    user = None
    joined_channels = []

    def check_anonymous(self):
        if self.user.is_anonymous:
            logger.debug("Rejecting Connection: %s (%s)", self.channel_name, self.user)
            # Reject the connection
            self.close()
            return True
        return False

    def user_message(self, message):
        # logger.info("BaseWebSocketConsumer user_message: %s" % message)
        if "data" in message:
            try:
                self.send_json(json.loads(message["data"]))
            except JSONDecodeError:
                logger.exception("Could not send message %s", message)
        else:
            logger.exception("No data in message %s", message)

    def receive_json(self, content, **kwargs):
        logger.debug("receive_json %s.", content)
        logger.warning("Ignoring message %s.", content)

    def disconnect(self, code):
        # pylint: disable=unused-argument
        for channel in self.joined_channels:
            AsyncToSync(self.channel_layer.group_discard)(
                channel, self.channel_name
            )
        logger.debug(
            "Disconnect %s %s from channels %s",
            self.user, self.channel_name, self.joined_channels
        )


class UserWebSocketConsumer(BaseWebSocketConsumer):

    def connect(self):
        self.user = self.scope["user"]
        self.joined_channels = []

        if self.check_anonymous():
            return

        self.accept()
        logger.debug("New User Connection: %s (%s)", self.channel_name, self.user)

        user_channel_name = self.user.unique_name()
        AsyncToSync(self.channel_layer.group_add)(user_channel_name, self.channel_name)

        self.joined_channels = [user_channel_name]
        logger.info(
            "New User Connection %s joined %s (%s)",
            self.user, self.joined_channels, self.channel_name
        )
