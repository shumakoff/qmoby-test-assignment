<template>
  <div v-if="playerName == ''" class="container">
    <login v-on:login="enterRoom($event)"/>
  </div>
  <div v-else>
    <room v-bind:player-name="playerName"></room>
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
    }
  },
  computed: {
  },
}
</script>


<style>

.container {
  display: flex;
  justify-content: center;
  align-items: center;
}

</style>

