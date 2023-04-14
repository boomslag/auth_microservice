import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import *
from apps.user_profile.models import *
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Case, When

class OnlineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        uuid_str = str(uuid.uuid4()) # generate a random UUID
        self.group_name = f"online_{uuid_str}_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print(f'User {self.user_id} connected to Online Status Websocket with group name: {self.group_name}')
        await self.accept()

    async def disconnect(self, close_code):
        await self.set_user_status(False)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except ValueError:
            # Reject message if it's not valid JSON
            return

        if "type" not in text_data_json:
            # Reject message if it doesn't have a "type" field
            return

        message_type = text_data_json["type"]
        if message_type == 'is_online':
            user_status = await self.set_user_status(True)
            await self.send_user_status(user_status)
        elif message_type == 'send_message':
            if "message" not in text_data_json:
                # Reject message if it doesn't have a "message" field
                return

            message = text_data_json["message"]
            event = {
                'type': 'send_message',
                'message': message
            }
            # send message to group
            await self.channel_layer.group_send(self.group_name, event)
        else:
            # Reject message if type is unknown
            return
        
    @database_sync_to_async
    def set_user_status(self, status):
        User.objects.filter(id=self.user_id).update(
            is_online=Case(
                When(is_online=True, then=status),
                When(is_online=False, then=status),
                output_field=models.BooleanField(),
            ),
        )
        return status
    
    async def send_user_status(self, data):
        message = {
            'type': 'user_status',
            'data': data
        }
        await self.send(text_data=json.dumps(message))

    async def send_message(self, event):
        message = event['message']
        # send message to websocket
        await self.send(text_data=json.dumps({'message':message}))