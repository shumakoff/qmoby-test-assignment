<template>
  <div class="center">
    State your name
    <p>
      <input v-model="playerName" v-on:keyup.enter="login"/>
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
    }
  },
  methods: {
    login() {
      this.$emit('login', {'playerName': this.playerName});
    },
  },
  computed: {

    },
}
</script>

<style>

.center {
}

</style>

