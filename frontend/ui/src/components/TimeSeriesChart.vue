<template>
  <div>
    <Line
      :chart-options="chartOptions"
      :chart-data="forecastData"
      :chart-id="chartId"
      :dataset-id-key="datasetIdKey"
      :css-classes="cssClasses"
      :styles="styles"
      :width="width"
      :height="height"
    />
  </div>
</template>

<script>

import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)


export default {
  extends: Line,
  props: ['forecastData'],
  mounted() {
    console.log('at renderChart...')
    this.renderChart(
      {
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
      },
      {
        responsive: true,
        maintainAspectRatio: false,
      }
    )
  },
};
</script>
