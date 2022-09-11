import Vue from 'vue'
import Vuetify from 'vuetify'
import App from './App.vue'

Vue.use(Vuetify)

Vue.config.productionTip = false

new Vue({
  el: '#app',
  vuetify: new Vuetify({}),
  render: h => h(App)
})
