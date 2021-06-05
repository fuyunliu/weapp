from django.urls import path
from wechat import consumers

websocket_urlpatterns = [
    path('chat/', consumers.ChatConsumer)
]