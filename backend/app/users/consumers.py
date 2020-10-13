import json
import logging
from json.decoder import JSONDecodeError

from channels.consumer import SyncConsumer

logger = logging.getLogger(__name__)


class UserConsumer(SyncConsumer):

    def user_message(self, message):
        pass