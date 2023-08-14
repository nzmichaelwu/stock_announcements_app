<template>
  <div id="time-series-chart">
    <Line :data="chartData"/>
  </div>
</template>


<script>

import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale)

// export default {
//   name: 'TimeSeriesChart',
//   components: { Line },
//   data: () => ({
//     loaded: false,
//     forecastData: null
//   }),
//   async mounted() {
//     this.loaded = false

//     try {
//       const { data } = await fetch('/api/contents/forecast')
//       this.forecastData = data

//       this.loaded = true
//     } catch (e) {
//       console.error(e)
//     }
//   }
// }

export default {
  name: 'TimeSeriesChart',
  components: { Line },
  props: ['forecastData'],
  data(){
    return {
      chartData: {
        labels: this.forecastData.map(items => items.date),
        datasets: [
          {
            label: 'Time Series Data',
            data: this.forecastData.map(items => items.value),
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 1,
          },
        ],
      }
    }
  },
  // async mounted() {
  //   console.log('at renderChart...')
  //   console.log(this.forecastData)
  //   this.renderChart(
  //     {
  //       labels: this.forecastData.map(items => items.date),
  //       datasets: [
  //         {
  //           label: 'Time Series Data',
  //           data: this.forecastData.map(items => items.value),
  //           borderColor: 'rgba(75, 192, 192, 1)',
  //           backgroundColor: 'rgba(75, 192, 192, 0.2)',
  //           borderWidth: 1,
  //         },
  //       ],
  //     },
  //     {
  //       responsive: true,
  //       maintainAspectRatio: false,
  //     }
  //   )
  // },
};
</script>
