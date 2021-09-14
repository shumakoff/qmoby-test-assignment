<template>
  <div>
        <p>Chat</p>
        <p v-if="chatConn != null">
          Socket is {{ socketState }}
        </p>
        <p v-else>
          Socket disconnected
        </p>
        <input v-on:click="clearInput" v-model="chatInput">
        <button v-on:click="sendChatMessage">Send message</button>
        <table>
          <tr v-for="(msg, index) in messages" :key="index">
            <td><{{ msg['player_name'] }}></td>
            <td>{{ msg['message'] }}</td>
            <td v-if="msg['delivered_server']">&#x2611;</td>
            <td v-if="msg['delivered_player']">V</td>
            <!--td v-for="(key, index) in msg" :key="index">{{ key }}</td-->
          </tr>
        </table>
      </div>
    </div> 
  </div>
</template>

<script>


export default {
  components: {
  },
  props: ['playerName', 'roomNumber'],
  data () {
    return {
      socketState: null,
      chatConn: null,
      chatInput: "enter your message",
      messages: {},
      messageID: 0,
      networkDown: false,
    }
  },
  mounted () {
    this.startWebsocket()
  },
  methods: {
    clearInput() {
      this.chatInput = ""
    },
    startWebsocket() {
      this.chatConn = new WebSocket('ws://127.0.0.1:8000/ws/chat/'+this.roomNumber+'/')

      this.chatConn.onopen = (event) => {
        this.socketState = 'connected'
        // sending queued messages
        for (var [key, value] of Object.entries(this.messages)) {
          if (!value['delivered_server'] && value['player_name'] == this.playerName) {
            console.log('retrying delivery: ', key)
            this.chatConn.send(JSON.stringify(value))
          }
        }
        this.chatInput = ""
      }

      this.chatConn.onclose = (eventclose) => {
        this.socketState = 'closed'
        this.chatConn = null
        setTimeout(this.startWebsocket, 5000)
      },
      this.chatConn.onerror = (eventclose) => {
        this.socketState = 'error'
      }
      this.chatConn.onmessage = (event) => {
        var messageJsonData = JSON.parse(event.data)

        if (messageJsonData.hasOwnProperty('ack')) {
          // this is confirmation from the server that it has received message
          var ackInternalId = messageJsonData['ack']['internal_id']
          if (ackInternalId in this.messages) {
            var sentMessage = this.messages[ackInternalId]
            sentMessage['message_id'] = messageJsonData['ack']['message_id']
            sentMessage['delivered_server'] = true
            this.chatInput = ""
            this.chatInput = "enter your message"
          }
        } else if (messageJsonData.hasOwnProperty('message')) {
          // this is a regular user message
          if (messageJsonData['message']['player_name'] != this.playerName) {
            this.messages[messageJsonData['message']['internal_id']] = messageJsonData['message']
            // send confirmation
            this.chatConn.send(JSON.stringify(chatMessage))
            this.chatInput = ""
            this.chatInput = "enter your message"
          } 
        }
      }
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
</style>

