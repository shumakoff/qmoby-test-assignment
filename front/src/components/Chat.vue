<template>
  <div>
        <p>Chat</p>
        <input v-model="chatInput" v-on:keyup.enter="sendChatMessage" placeholder="enter your message">
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
      chatInput: "",
      chatError: false,
      messages: {},
      messageID: 0,
      networkDown: false,
    }
  },
  mounted () {
    this.startWebsocket()
  },
  methods: {
    startWebsocket() {
      this.chatConn = new WebSocket('ws://'+window.location.hostname+':8000/ws/chat/1/')

      this.chatConn.onopen = (event) => {
        this.joinChat()
        // sending queued messages
        for (var [key, value] of Object.entries(this.messages)) {
          if (!value['delivered_server'] && value['player_name'] == this.playerName) {
            console.log('retrying delivery: ', key)
            this.chatConn.send(JSON.stringify(value))
          }
        }
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
        if (messageJsonData['type'] == 'ack_message') {
          console.log('got delivery confirmation')
          var ackInternalId = messageJsonData['internal_id']
          if (ackInternalId in this.messages) {
            var sentMessage = this.messages[ackInternalId]
            sentMessage['message_id'] = messageJsonData['message_id']
            sentMessage['delivered_server'] = true
          }
          return

        // this is a regular user message
        } else if (messageJsonData['type'] == 'chat_message') {
          if (messageJsonData['message']['player_name'] != this.playerName) {
            console.log('this is regular message from '+messageJsonData['message']['player_name'])
            var internalId = messageJsonData['message']['internal_id']
            this.$set(this.messages, internalId, messageJsonData['message'])
            // send confirmation
            // no need to confirm for server anno
            if (messageJsonData['message']['player_name'] == 'Server Announcement') {
              return
            }
            var confirmationMessage = {}
            confirmationMessage['type'] = 'ack_message'
            confirmationMessage['internal_id'] = messageJsonData['message']['internal_id']
            confirmationMessage['message_id'] = messageJsonData['message']['message_id']
            console.log('sending delivery confirmation')
            console.log(confirmationMessage)
            this.chatConn.send(JSON.stringify(confirmationMessage))
          } 
        }
      }
    },

    joinChat() {
      this.chatConn.send(JSON.stringify({
        'type':'join_message',
        'player_name': this.playerName}))
    },
    
    sendChatMessage() {
      if (!this.chatInput) { return }
      if (this.chatEror) { return }
      var chatMessage = new Object
      chatMessage['type'] = 'chat_message'
      chatMessage['player_name'] = this.playerName
      chatMessage['internal_id'] = this.uuidv4()
      chatMessage['delivered_server'] = false
      chatMessage['delivered_player'] = false
      chatMessage['message'] = this.chatInput
      this.$set(this.messages, chatMessage['internal_id'], chatMessage)
      this.chatConn.send(JSON.stringify(chatMessage))
      this.chatInput = ""
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

