import Vue from 'vue'
import App from './App.vue'

let app = new Vue({
  el: '#wrapper',
  render: h => h(App)
})

global.vm = app;
