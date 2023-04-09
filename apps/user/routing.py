from django.urls import re_path

from .consumer import OnlineConsumer

websocket_urlpatterns = [
    re_path(r'ws/online/$', OnlineConsumer.as_asgi()),
]