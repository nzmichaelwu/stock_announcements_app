<template>
  <v-app>
    <v-col cols="4">
      <div id="inputs">
        <v-row>
          <input type="text" v-model="ticker" placeholder="Enter stock ticker">
        </v-row>
        <v-row>
          <button @click="sendTicker"
              small
              text
              color="primary"
              class="ml-2 mb-2"
          >Store Ticker</button>
        </v-row>
      </div>
      <v-spacer></v-spacer>
      <div id="forecast">
        <v-row>
          <button v-on:click="doForecast"
              small
              text
              color="primary"
              class="ml-2 mb-2"
          >Run Forecast</button>
        </v-row>
      </div>
    </v-col>
    <v-col cols="8">
      <div id="chart">
        <time-series-chart v-if="ticker && forecastData" :forecastData="forecastData"></time-series-chart>
      </div>
    </v-col>
  </v-app>
</template>

<script>
  import axios from 'axios';
  import TimeSeriesChart from './TimeSeriesChart.vue';

  export default {
    components: {
      TimeSeriesChart
    },
    data() {
      return {
        ticker: '',
        forecastData: null,
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
        if (this.ticker) {
            console.log('Running Prophet forecast model...')
            // Get forecast output
            axios.get('/api/contents/forecast')
            .then(response => {
              this.forecastData = response.data;
              // console.log(response.data)
            })
            .catch(error => {
              console.error('Error fetching forecast data', error);
            });
          } else {
          console.log('No ticker code provided yet...')
        }
      }
    },
    updated() {
      this.doForecast();
    }
  }
</script>