import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import apps.friends.routing as FriendsRouting
import apps.user.routing as UserRouting

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            FriendsRouting.websocket_urlpatterns + UserRouting.websocket_urlpatterns
        )
    ),
})
