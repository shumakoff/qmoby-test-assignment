<template>
  <div v-if="playerName == ''">
    <login v-on:login="enterRoom($event)"/>
  </div>
  <div v-else>
    <room v-bind:player-name="playerName" v-bind:room-number="roomNumber"></room>
  </div>
</template>

<script>

import Login from '../components/Login.vue'
import Room from '../components/Room.vue'

export default {
  components: {
    'login': Login,
    'room': Room
  },
  data () {
    return {
      playerName: "",
      roomNumber: "",
    }
  },
  mounted() {
  },
  methods: {
    log(message) {
      console.log(message);
    },
    enterRoom(loginData) {
      this.playerName = loginData['playerName']
      this.roomNumber = loginData['roomNumber']
    }
  },
  computed: {
  },
}
</script>

<style>
</style>

