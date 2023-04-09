import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

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
