from django.urls import re_path

from .consumers import BlockConsumer

websocket_urlpatterns = [
    re_path(r'ws/blocks/(?P<account_number>[a-f0-9]{64})$', BlockConsumer.as_asgi()),
]
