import uuid
import time
from random import randint
from string import ascii_uppercase
import json
import redis
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
import channels.exceptions
from .utils import generate_map, generate_shots


class CoreConsumer(JsonWebsocketConsumer):


    def __init__(self):
        self.game_db = redis.Redis(db=1, decode_responses=True)
        super(JsonWebsocketConsumer, self).__init__()


    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_number']
        self.room_group_name = 'game_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        # try to cleanup after player that have "join" on the game
        player_name = self.game_db.get(self.channel_name)
        if player_name:
            print(f'{player_name} is leaving')
            self.game_db.delete(self.channel_name)
            if not self.game_db.get('inprogress'):
                self.game_db.lrem('players_list', count=0, value=player_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # Receive message from WebSocket
    def receive_json(self, text_data):
        """
        Main dispatcher
        """
        player_name = text_data['player_name']

        if text_data['message_type'] == 'join':
            self.join_player(player_name)
            self.start_game(player_name)

        elif text_data['message_type'] == 'move':
            move = text_data['message']
            self.move(player_name, move)


    def join_player(self, player_name):
        """
        Joins player to the game
        """
        if self.game_db.get('inprogress'):
            if player_name in self.game_db.lrange('players_list', 0, -1):
                self.announce_join(player_name)
                self.send_json({'message_type': 'game_state',
                                'message': {
                                    'player_map': json.loads(self.game_db.get(player_name+'_map')),
                                    'player_shots': json.loads(self.game_db.get(player_name+'_shots'))
                                    }
                                })
            else:
                self.send_json('go away')
        else:
            # joining new game
            # check if we still have open slots
            if len(self.game_db.lrange('players_list', 0, -1)) < 2:
                # check if player already joined
                if player_name in self.game_db.lrange('players_list', 0, -1):
                    self.send_json('You have already joined')
                    self.close()
                else:
                    self.announce_join(player_name)
                    # mark channels so we could clean up on disconnect
                    self.game_db.set(player_name, self.channel_name)
                    self.game_db.set(self.channel_name, player_name)
                    self.game_db.rpush('players_list', player_name)
                    # generate game data
                    player_map = generate_map()
                    player_shots = generate_shots()
                    self.game_db.set(player_name+'_map', json.dumps(player_map))
                    self.game_db.set(player_name+'_shots', json.dumps(player_shots))
                    self.send_json({'message_type': 'game_state',
                                    'message': {
                                        'player_map': player_map,
                                        'player_shots': player_shots
                                        }
                                    })
                    for row in player_map:
                        print(row)
            else:
                print('room capacity reached, players in the room',self.game_db.lrange('players_list', 0, -1),'joining player',player_name)
                self.send_json('We are at capacity, sir')
                self.close()


    def start_game(self, player_name):
        """
        Starts the game if everyone joined
        """
        if self.game_db.get('inprogress'):
            self.send_json('Game has already started')
        if len(self.game_db.lrange('players_list', 0, -1)) == 2:
            self.game_db.set('inprogress', 1)
            next_move = self.game_db.lrange('players_list', 1, 1)[0]
            self.game_db.set('next_move', next_move)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'announce_start',
                    'message': {'move': next_move},
                })
        else:
            # welp ig we have to wait some more
            self.send_json('Not enough players')


    def move(self, player_name, move):
        if self.game_db.get('inprogress'):
            if player_name in self.game_db.lrange('players_list', 0, -1):
                # check if that's person move time
                if player_name == self.game_db.get('next_move'):
                    # write down the move
                    y_cor = move['y_cor']
                    x_cor = move['x_cor']
                    # load data to check for hits
                    other_player = [x for x in self.game_db.lrange('players_list', 0, -1) if x != player_name][0]
                    player_shots = json.loads(self.game_db.get(player_name+'_shots'))
                    other_player_map = json.loads(self.game_db.get(other_player+'_map'))
                    # check if we hit something
                    if other_player_map[y_cor][x_cor] == 1:
                        other_player_map[y_cor][x_cor] = 2
                        player_shots[y_cor][x_cor] = 2
                        next_move = player_name
                        hit = True
                    else:
                        player_shots[y_cor][x_cor] = 3
                        next_move = other_player
                        hit = False
                    # save info about hit
                    self.game_db.set(player_name+'_shots', json.dumps(player_shots))
                    self.game_db.set(other_player+'_map', json.dumps(other_player_map))
                    self.game_db.set('next_move', next_move)
                    # notify the player about hit or miss
                    # TODO notify other player about game state
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'announce_move',
                            'message': {'player_name': player_name,
                                        'y_cor': y_cor,
                                        'x_cor': x_cor,
                                        'hit': hit},
                        })
                    """
                    self.send_json({'message_type': 'game_state',
                                    'message': {'player_shots': player_shots}
                                    })
                    """
                    # check if other player has any ships left
                    if not any(1 in map_row for map_row in other_player_map):
                        print('victory condition')
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type': 'announce_victory',
                                'message': {'player_name': player_name},
                            })
                        self.game_db.flushdb()
                    else:
                        self.game_db.set(next_move, other_player)
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type': 'announce_nextmove',
                                'message': {'move': next_move},
                            })
                else:
                    print('It\'s not your turn')
                    self.send_json('It\'s not you turn')


    def announce_move(self, event):
        print('this is an announce_hit method')
        message = event['message']

        self.send(text_data=json.dumps({
            'message_type': 'announce_hit',
            'message': message
        }))


    def announce_victory(self, event):
        print('this is an announce_victory methid')
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message_type': 'announce_victory',
            'message': message
        }))


    def announce_nextmove(self, event):
        print('this is an announce_nextmove methid')
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message_type': 'announce_nextmove',
            'message': message
        }))


    def announce_start(self, event):
        print(event)
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message_type': 'announce_start',
            'message': message
        }))


    def announce_join(self, player_name):
        """
        Announce join in chat
        """
        chat_layer = get_channel_layer()
        async_to_sync(chat_layer.group_send)(
                'chat_1',
                {'type': 'chat_message',
                 'message': {'message': f'{player_name} have joined',
                             'internal_id': str(uuid.uuid4()),
                             'player_name': 'Server Announcement'}
                })
