import json
from channels.consumer import SyncConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis


class BackgroundDeliveryConsumer(SyncConsumer):


    def __init__(self):
        self.chat_db = redis.Redis(db=0, decode_responses=True)
        self.chat_layer = get_channel_layer()
        super(SyncConsumer, self).__init__()


    def deliver_messages(self, message):
        print(f'running task_a with argument {message}')
        player_name = message['player_name']
        messages = self.chat_db.lrange('tosend', 0, -1)
        for message_id in reversed(messages):
            message = json.loads(self.chat_db.get(message_id))
            print(f'{message_id} : {message}')
            async_to_sync(self.chat_layer.group_send)(
                    'chat_1', {
                        'type': 'chat_message',
                        'message': message
                        })


