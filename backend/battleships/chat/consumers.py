import json
import redis
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
import channels.exceptions


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_number']
        self.room_group_name = 'chat_%s' % self.room_name
        print(self.room_group_name)
        self.chat_db = redis.Redis(db=0, decode_responses=True)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        # try to cleanup after player that have "join" on the chat
        player_name = self.chat_db.get(self.channel_name)
        if player_name:
            print(f'{player_name} is leaving')
            self.chat_db.delete(self.channel_name)
            self.chat_db.delete(player_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive_json(self, text_data):
        print('data received:',text_data)
        if text_data['type'] == 'join_message':
            player_name = text_data['player_name']
            self.chat_db.set(player_name, self.channel_name)
            self.chat_db.set(self.channel_name, player_name)
            bg_channel = get_channel_layer()
            async_to_sync(bg_channel.send)(
                    'message-delivery', {
                        'type': 'deliver_messages',
                        'player_name': player_name
                        })
            return

        internal_id = text_data['internal_id']

        # received confirmation of delivery from client
        if text_data['type'] == 'ack_message':
            # message_id could be spoofed
            # good enough for test assignment purposes
            # otherwise we could store message_id - client link
            # somemewhere and do additional check
            print('we have received confirmation from client')
            print(text_data)
            # proceed to remove message from db
            self.chat_db.delete(text_data['message_id'])
            self.chat_db.lrem('tosend', 0, text_data['message_id'])
            return

        # confirm message received
        message_id = self.chat_db.incr('lastval')
        ack_message = {'type': 'ack_message',
                       'internal_id': internal_id,
                       'messsage_id': message_id}
        self.send_json(ack_message)

        # send message to room group
        text_data['message_id'] = message_id
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data
            }
        )

        # store message in database for 
        # sending it later in case client disappers
        print(f'storing message {internal_id}')
        self.chat_db.set(message_id, json.dumps(text_data))
        self.chat_db.lpush('tosend', message_id)



    # Receive message from room group
    def chat_message(self, event):

        # Send message to WebSocket
        self.send_json(event)


    def retry_delivery(self, event):
        print(f'i have been called from bg worker with this data {event}')
        self.send_json(event)
