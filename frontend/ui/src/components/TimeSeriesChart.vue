<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>

import { Line } from 'vue-chartjs';

export default {
  extends: Line,
  props: ['timeSeriesData'],
  mounted() {
    this.renderChart(
      {
        labels: this.timeSeriesData.labels,
        datasets: [
          {
            label: 'Time Series Data',
            data: this.timeSeriesData.values,
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
    );
  },
};
</script>
