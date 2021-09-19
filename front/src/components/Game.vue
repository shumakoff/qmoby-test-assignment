<template>
  <div>

    <div class="row">

      <!-- player map -->
      <div class="column">
        <table>
          <tr v-for="mapRow, y_cor in playerMap">
            <td v-for="mapCell, x_cor in mapRow" v-bind:class="{'bg-ship': mapCell,
                                                                'bg-miss': mapCell==3,
                                                                'bg-hit': mapCell==2,
                                                                'bg-water': !mapCell}"></td>
          </tr>
        </table>
      </div>

      <!-- player shots -->
      <div class="column">
        <table>
          <tr v-for="mapRow, y_cor in playerShots">
            <td v-for="mapCell, x_cor in mapRow"
                v-bind:class="{'bg-miss': mapCell==3,
			       'bg-hit': mapCell==2&myturn,
			       'bg-water':
			       !mapCell&inprogress&myturn,
                               'bg-disabled': !inprogress|!myturn&mapCell!=2,
                               'bg-hit-disabled': !myturn&mapCell==2}"
                v-on:click="sendHit(y_cor, x_cor)"></td>
          </tr>
        </table>
      </div>

    </div>

    <h1 v-if="!inprogress">Waiting for other player to join</h1>
    <h1 v-if="!gameFinished&myturn">Your turn</h1>
    <h1 v-if="gameFinished">{{ winner }} have wonnered!!!11</h1>

  </div>
</template>

<script>


export default {
  components: {
  },
  props: ['playerName'],
  data () {
    return {
      playerMap: [],
      playerShots: [],
      inprogress: false,
      myturn: false,
      gameFinished: false,
      winner: ""
    }
  },
  mounted () {
    this.startWebsocket()
  },

  methods: {

    clearInput() {
      this.chatInput = ""
    },

    sendHit(y_cor, x_cor) {
      if (!this.inprogress | !this.myturn | this.gameFinished) {
        return
      }	
      console.log(y_cor+' '+x_cor)
      var chatMessage = {}
      chatMessage['message'] = {}
      chatMessage['player_name'] = this.playerName
      chatMessage['message_type'] = 'move'
      chatMessage['message']['y_cor'] = y_cor
      chatMessage['message']['x_cor'] = x_cor
      this.chatConn.send(JSON.stringify(chatMessage))
    },

    startWebsocket() {
      this.chatConn = new WebSocket('ws://'+window.location.hostname+':8000/ws/game/1/')

      this.chatConn.onopen = (event) => {
        this.sendJoinMessage()
      }

      this.chatConn.onclose = (eventclose) => {
        this.chatConn = null
        setTimeout(this.startWebsocket, 5000)
      },

      this.chatConn.onerror = (eventclose) => {
      }

      this.chatConn.onmessage = (event) => {
        var messageJsonData = JSON.parse(event.data)
        console.log(messageJsonData)

        if (messageJsonData['message_type'] == 'game_state') {
          console.log('we have received game state, updating')
          this.updateGameState(messageJsonData['message'])
	} 

	else if (messageJsonData['message_type'] == 'announce_start') {
          console.log('Starting the game')
          this.startGame(messageJsonData)
          this.switchTurns(messageJsonData)
        } 

	else if (messageJsonData['message_type'] == 'announce_nextmove') {
          console.log('Received next move data')
          this.switchTurns(messageJsonData)
        } 

	else if (messageJsonData['message_type'] == 'announce_hit') {
          console.log('Received hit data')
          this.processHit(messageJsonData)
        } 

	else if (messageJsonData['message_type'] == 'announce_victory') {
          console.log('Received victory event')
          this.victory(messageJsonData)
        } 
      }
    },

    processHit(message) {
      console.log(message)
      var playerName = message['message']['player_name']
      var y_cor = message['message']['y_cor']
      var x_cor = message['message']['x_cor']
      if (message['message']['hit']) {
          console.log('this is a hit')
          var hitMarker = 2
      } else { 
          console.log('this is a miss')
          var hitMarker = 3
      }
      if (playerName == this.playerName) {
        // fuck vue reactivity
        var map_row = this.playerShots[y_cor]
        map_row[x_cor] = hitMarker
        this.playerShots.splice(y_cor, 1, map_row)
      } else {
        var map_row = this.playerMap[y_cor]
        map_row[x_cor] = hitMarker
        this.playerMap.splice([y_cor], 1, map_row)
         }
    },

    victory(message) {
      this.winner = message['message']['player_name']
      this.gameFinished = true
    },

    startGame(message) {
      this.inprogress = true
    },

    switchTurns(message) {
      if (message['message']['move'] == this.playerName) {
        console.log('yay')
        this.myturn = true
      } else {
        console.log('nay')
        this.myturn = false
      }
    },

    updateGameState(state) {
      if (state.hasOwnProperty('player_map')) {
        this.playerMap = state['player_map']
      }
      this.playerShots = state['player_shots']
    },
    
    sendJoinMessage() {
      var chatMessage = new Object
      chatMessage['player_name'] = this.playerName
      chatMessage['message_type'] = 'join'
      this.chatConn.send(JSON.stringify(chatMessage))
    },

    sendChatMessage() {
      var chatMessage = new Object
      chatMessage['player_name'] = this.playerName
      chatMessage['internal_id'] = this.uuidv4()
      chatMessage['delivered_server'] = false
      chatMessage['delivered_player'] = false
      chatMessage['message'] = this.chatInput
      this.messages[chatMessage['internal_id']] = chatMessage
      this.chatConn.send(JSON.stringify(chatMessage))
      this.chatInput = ""
      this.chatInput = "enter your message"
    },

    uuidv4() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    }
 
  },
  watch: {
  },
  computed: {
  },
}
</script>

<style>
.row {
  display: flex;
}

.column {
  flex: 50%;
}

table {
  border: 1px solid black;
  border-collapse: collapse;
}

td, th {
  border: 1px solid black;
  border-collapse: collapse;
  width: 30px;
  height: 30px;
}

.bg-ship {
  background-color: gray;
}

.bg-hit {
  background-color: pink;
}

.bg-hit-disabled {
  background-color: darkgrey;
}

.bg-miss {
  background-color: lightblue;
  background-image:
    linear-gradient(to bottom right,  transparent calc(50% - 1px), red, transparent calc(50% + 1px)), 
    linear-gradient(to bottom left,  transparent calc(50% - 1px), red, transparent calc(50% + 1px)); 
}

.bg-water {
  background-color: lightblue;
}

.bg-disabled {
  background-color: lightgray;
}

</style>

