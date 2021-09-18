"""
ASGI config for battleships project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import chat.routing
import core.routing
from delivery.consumers import BackgroundDeliveryConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'battleships.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "channel": ChannelNameRouter({
        "message-delivery": BackgroundDeliveryConsumer.as_asgi(),
    }),
    "websocket": AuthMiddlewareStack(
          URLRouter(
              chat.routing.websocket_urlpatterns+core.routing.websocket_urlpatterns
              )
      ),
})
