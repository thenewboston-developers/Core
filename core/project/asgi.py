import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from core.accounts.routing import websocket_urlpatterns
from core.core.authentication import SignatureAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.project.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': SignatureAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
