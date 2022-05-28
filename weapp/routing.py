from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from wechat import routing as wechat_routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(wechat_routing.websocket_urlpatterns))
})
