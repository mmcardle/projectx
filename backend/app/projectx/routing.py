from django.conf.urls import url

from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from projectx.consumers import UserWebSocketConsumer
from users.consumers import UserConsumer

# Consumer Imports

application = ProtocolTypeRouter({

    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r"^ws/$", UserWebSocketConsumer),
        ])
    ),
    "channel": ChannelNameRouter({
        "users": UserConsumer,
    })
})
