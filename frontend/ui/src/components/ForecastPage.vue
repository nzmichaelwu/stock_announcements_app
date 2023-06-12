<template>
  <v-app>
    <v-col cols="4">
      <div id="app">
        <v-row>
          <input type="text" v-model="ticker" placeholder="Enter stock ticker">
        </v-row>
        <v-row>
          <button @click="sendTicker">Store Ticker</button>
        </v-row>
        <v-row>
          <button @click="doForecast">Run Forecast</button>
        </v-row>
      </div>
    </v-col>
  </v-app>
</template>
<script>
  import axios from 'axios';

  export default {
    data() {
      return {
        ticker: '',
      };
    },
    methods: {
      sendTicker() {
        // Send ticker to backend
        axios.post('/api/contents/forecast', { ticker: this.ticker })
          .then(response => {
            // Handle the response from the backend
            if (response.status === 200) {
            // Process the response here if needed
              console.log('Ticker sent successfully');
            } else {
              console.error('Error sending ticker');
            }
          })
          .catch(error => {
            console.error('Error sending ticker', error);
          });
      },
      doForecast() {
        // Get forecast output
        axios.get('/api/contents/forecast')
          .then(response => (
          this.full_data = response.data.items,
          console.log(response.data.items)
        ))
      },
    },
  };
</script>