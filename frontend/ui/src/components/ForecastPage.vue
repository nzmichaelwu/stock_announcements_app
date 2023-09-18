<template>
<v-app>
  <v-col cols="4">
    <div id="inputs">
      <v-row>
        <input type="text" v-model="ticker" placeholder="Enter stock ticker">
      </v-row>
      <v-row>
        <button @click="sendTicker" small text color="primary" class="ml-2 mb-2">Store Ticker</button>
      </v-row>
    </div>
    <v-spacer></v-spacer>
    <div id="forecast">
      <v-row>
        <button v-on:click="doForecast" small text color="primary" class="ml-2 mb-2">Run Forecast</button>
      </v-row>
    </div>
  </v-col>
  <v-col cols="8">
    <div class="error-message" v-if="showError">
      {{ errorMessage }}
    </div>
    <hr>
    <div v-if="loading" class="loading">
      🔧 Building Charts ...
      <div class="sk-cube-grid">
        <div class="sk-cube sk-cube1"></div>
        <div class="sk-cube sk-cube2"></div>
        <div class="sk-cube sk-cube3"></div>
        <div class="sk-cube sk-cube4"></div>
        <div class="sk-cube sk-cube5"></div>
        <div class="sk-cube sk-cube6"></div>
        <div class="sk-cube sk-cube7"></div>
        <div class="sk-cube sk-cube8"></div>
        <div class="sk-cube sk-cube9"></div>
      </div>
    </div>

    <div id="chart_container" v-if="loaded">
      <div id="chart_title">
        <h2>Forecast Chart</h2>
      </div>
      <hr>
      <div id="chart_content">
        <TimeSeriesChart chart-id="time-series" v-if="loaded" :datasets="forecastData" :chart-labels="labels"></TimeSeriesChart>
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
      showError: false,
      errorMessage: 'Please enter a ticker code',
    };
  },
  mounted() {
    if (this.ticker != '' || this.ticker != null) {
      this.doForecast()
    }
  },
  methods: {
    sendTicker() {
      // Send ticker to backend
      axios.post('/api/contents/forecast', {
          ticker: this.ticker
        })
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
      this.showError = false
    },
    doForecast() {
      if (this.ticker === null || this.ticker === ''){
        this.showError = true
        this.loading = false
        return
      }
      console.log(this.loading)
      this.resetState()
      this.loading = true
      // console.log(this.loading)
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
          console.log(this.loaded)
        })
        .catch(error => {
          this.showError = true
          this.loading = false
          console.error('Error fetching forecast data', error);
        });
    }
  },
}
</script>
