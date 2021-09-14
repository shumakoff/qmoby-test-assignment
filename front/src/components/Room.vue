<template>
  <div>
    <p>
      Welcome to the game, {{ playerName }}
    </p>
    <div class="row">
      <div class="column">
        <chat v-bind:player-name="playerName" v-bind:room-number="roomNumber"/>
      </div>
      <div class="column">
        <game v-bind:player-name="playerName" v-bind:room-number="roomNumber"/>
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
  props: ['playerName', 'roomNumber'],
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
  flex: 50%;
}
</style>

