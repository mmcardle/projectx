from django.conf.urls import url

from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from projectx.consumers import projectx_WebSocketConsumer

# Consumer Imports

application = ProtocolTypeRouter({

    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r"^ws/$", projectx_WebSocketConsumer),
        ])
    ),
    "channel": ChannelNameRouter({
        #"users": usersConsumer,
    })
})
