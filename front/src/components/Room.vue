<template>
  <div>
    <p>
      Welcome to the game, {{ playerName }}
    </p>
    <div class="row">
      <div class="column-chat">
        <chat v-bind:player-name="playerName"/>
      </div>
      <div class="column">
        <game v-bind:player-name="playerName"/>
      </div>
    </div> 
  </div>
</template>

<script>

import Chat from '../components/Chat.vue'
import Game from '../components/Game.vue'

export default {
  components: {
    'chat': Chat,
    'game': Game
  },
  props: ['playerName'],
  data () {
    return {
    }
  },
  mounted () {
  },
  methods: {
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
  flex: 70%;
}

.column-chat {
  flex: 30%;
}
</style>

