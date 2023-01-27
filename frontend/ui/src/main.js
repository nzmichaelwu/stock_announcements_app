import Vue from 'vue'
import Vuetify from 'vuetify'
import App from './App.vue'
import router from './router'
import axios from './axios'

Vue.use(Vuetify)

Vue.config.productionTip = false

new Vue({
  el: '#app',
  vuetify: new Vuetify({}),
  axios,
  router,
  render: h => h(App)
})
