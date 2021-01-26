from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import re_path

from projectx.consumers import UserWebSocketConsumer
from users.consumers import UserConsumer

from .consumers import UserWebSocketConsumer

# Consumer Imports


websocket_urlpatterns = [
    re_path(r"^ws/$", UserWebSocketConsumer.as_asgi()),
]
