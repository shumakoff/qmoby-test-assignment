<template>
  <div>
    State your name
    <p>
      <input v-model="playerName">
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
      playerName: "",
    }
  },

  methods: {
    log(message) {
      console.log(message);
    },
    login() {
      console.log(this.playerName + " enters game");
    },
  },
  computed: {

    },
}
</script>

<style>
</style>

