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
      <div id="chart_container">
        <div id="chart_title">
          <h2>Forecast Chart</h2>
        </div>
        <hr>
        <div id="chart_content">
          <time-series-chart v-if="loaded" :chart-data="forecastData" :chart-labels="labels"></time-series-chart>
        </div>
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
        loaded: false,
        loading: false,
        forecastData: [],
        labels: [],
        rawData: '',
      };
    },
    mounted() {
      if (this.ticker != '') {
        this.doForecast()
      } else {
          console.log('No ticker code provided yet...')
      }
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
      resetState() {
        this.loaded = false
      },
      doForecast() {
        if (this.ticker === '') {
          this.loading = false
          return
        }
        console.log(this.loading)
        this.resetState()
        this.loading = true
        console.log(this.loading)
        console.log('Running Prophet forecast model...')
        // Get forecast output
        axios.get('/api/contents/forecast')
        .then(response => {
          console.log(response.data)
          this.rawData = response.data.items
          this.forecastData = response.data.items.map(item => item.value)
          this.labels = response.data.items.map(item => item.date)
          this.loaded = true
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching forecast data', error);
        });
      }
    },
  }
</script>