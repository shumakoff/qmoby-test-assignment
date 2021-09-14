import json
import redis
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import channels.exceptions


class CoreConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_number']
        self.room_group_name = 'chat_%s' % self.room_name
        self.chat_db = redis.Redis(db=self.room_name, decode_responses=True)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        # confirm message received
        self.message_id = self.chat_db.incr('lastval')
        internal_id = text_data_json['internal_id']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_ack',
                'message': {'internal_id': internal_id,
                            'message_id': self.message_id}
            }
        )

        # send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json
            }
        )

    # Confirm delivery 
    def chat_ack(self, event):
        print(event)
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'ack': message
        }))


    # Receive message from room group
    def chat_message(self, event):
        print(event)
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
