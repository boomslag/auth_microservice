import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from channels.routing import ProtocolTypeRouter, URLRouter

from middleware.authmiddleware import JWTAuthMiddlewareStack

import apps.friends.routing as FriendsRouting
import apps.user.routing as UserRouting

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(
            FriendsRouting.websocket_urlpatterns + UserRouting.websocket_urlpatterns
        )
    ),
})
