<template>
  <div>
        <p>Chat</p>
        <input v-on:click="clearInput" v-model="chatInput">
        <button v-on:click="sendChatMessage">Send message</button>
        <table class="regular">
          <tr v-for="(msg, index) in messages" :key="index" class="regular">
            <td class="regular"><{{ msg['player_name'] }}></td>
            <td class="regular">{{ msg['message'] }}</td>
            <td v-if="msg['delivered_server']" class="regular">&#x2611;</td>
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
  props: ['playerName'],
  data () {
    return {
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
      this.chatConn = new WebSocket('ws://192.168.1.39:8000/ws/chat/1/')

      this.chatConn.onopen = (event) => {
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
        this.chatConn = null
        setTimeout(this.startWebsocket, 5000)
      },
      this.chatConn.onerror = (eventclose) => {
      }
      this.chatConn.onmessage = (event) => {
        var messageJsonData = JSON.parse(event.data)
        console.log(messageJsonData)

        // this is confirmation from the server that it has received message
        if (messageJsonData.hasOwnProperty('ack')) {
          var ackInternalId = messageJsonData['ack']['internal_id']
          if (ackInternalId in this.messages) {
            var sentMessage = this.messages[ackInternalId]
            sentMessage['message_id'] = messageJsonData['ack']['message_id']
            sentMessage['delivered_server'] = true
            this.chatInput = ""
            this.chatInput = "enter your message"
          }

        // this is a regular user message
        } else if (messageJsonData.hasOwnProperty('message')) {
          console.log('this is regular message')
          if (messageJsonData['message']['player_name'] != this.playerName) {
            this.messages[messageJsonData['message']['internal_id']] = messageJsonData['message']
            // send confirmation
            //this.chatConn.send(JSON.stringify(chatMessage))
            this.chatInput = ""
            this.chatInput = "enter your message"
          } 
        }
      }
    },
    
    sendChatMessage(message) {
      var chatMessage = new Object
      chatMessage['player_name'] = this.playerName
      chatMessage['internal_id'] = this.uuidv4()
      chatMessage['delivered_server'] = false
      chatMessage['delivered_player'] = false
      chatMessage['message'] = this.chatInput
      if (message) {
        chatMessage['message'] = message
      }
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

.regular {
  border: none;
}
</style>

