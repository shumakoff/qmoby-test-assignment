import Vue from 'vue'
import App from './App.vue'

var vm = new Vue({
  el: '#wrapper',
  render: h => h(App)
})

global.vm = vm;
