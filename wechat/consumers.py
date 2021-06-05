import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user_id = self.scope['session']['_auth_user_id']
        self.group_name = f'{user_id}'

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Receive message from WebSocket
        text_data = json.loads(text_data)

        # Send message to room group
        message = {'type': 'recieve_group_message', 'message': text_data['message']}
        await self.channel_layer.group_send(self.group_name, message)

    async def recieve_group_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}))
