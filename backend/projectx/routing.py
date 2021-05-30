from django.urls import re_path

from projectx.consumers import UserWebSocketConsumer

websocket_urlpatterns = [
    re_path(r"^ws/$", UserWebSocketConsumer.as_asgi()),
]
