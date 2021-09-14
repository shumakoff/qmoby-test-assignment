<template>
  <div>
    State your name
    <p>
      <input v-model="playerName"/>
    </p>
    Enter room number
    <p>
      <input v-model="roomNumber">
    </p>
    <button v-on:click="login">Let's go</button>
  </div>
</template>

<script>


export default {
  components: {
  },
  data () {
    return {
      playerName: "playerOne",
      roomNumber: 1,
    }
  },
  methods: {
    login() {
      this.$emit('login', {'playerName': this.playerName, 'roomNumber': this.roomNumber});
    },
  },
  computed: {

    },
}
</script>

<style>
</style>

