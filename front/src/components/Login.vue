<template>
  <div class="center">
    State your name
    <p>
      <input v-model="playerName" v-on:keyup.enter="login" v-bind:class="{error: nameError}"/>
    </p>
      <p v-if="nameError" class="error">
        Name length should be 1 to 11 chars and include only alphanumeric symbols
      </p>
    <button v-on:click="login" :disabled="nameError">Let's go</button>
  </div>
</template>

<script>


export default {
  components: {
  },
  data () {
    return {
      playerName: "playerOne",
      nameError: false
    }
  },
  methods: {
    login() {
      if (!this.nameError) {
        this.$emit('login', {'playerName': this.playerName})
      }
    },
  },
  computed: {

    },
  watch: {
    playerName: function (val) {
      if ((val.length > 12) | (!val.match(/^[0-9a-zA-Z]+$/))) { this.nameError = true }
      else { this.nameError = false }
    }
  },
}
</script>

<style>

.center {
}

.error {
  border-color: red;
  border: solid;
}

</style>

