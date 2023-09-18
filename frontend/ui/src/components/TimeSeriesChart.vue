<template>
  <Line :chart-data="chartData" />
</template>

<script>
import {
  Line
} from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale)

export default {
  name: 'TimeSeriesChart',
  components: { Line },
  props: {
    datasets: {
      type: [Array, Object],
      required: true
    },
    chartLabels: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      chartData: {
        labels: this.chartLabels,
        datasets: [
          {
            label: 'time_series',
            borderColor: '#249EBF',
            pointBackgroundColor: 'rgba(0,0,0,0)',
            pointBorderColor: 'rgba(0,0,0,0)',
            pointHoverBorderColor: '#249EBF',
            pointHoverBackgroundColor: '#fff',
            pointHoverRadius: 4,
            pointHitRadius: 10,
            pointHoverBorderWidth: 1,
            borderWidth: 1,
            // backgroundColor: this.gradient,
            data: this.datasets
          }
        ]
      },
      gradient: null,
      options: {
        showScale: true,
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: false,
              // callback: (value, index, values) => {
              //   return this.formatNumber(value)
              // }
            },
            gridLines: {
              display: true,
              color: '#EEF0F4',
              borderDash: [5, 15]
            }
          }],
          xAxes: [{
            gridLines: {
              display: true,
              color: '#EEF0F4',
              borderDash: [5, 15]
            }
          }]
        },
        tooltips: {
          backgroundColor: '#4F5565',
          titleFontStyle: 'normal',
          titleFontSize: 18,
          bodyFontFamily: "'Proxima Nova', sans-serif",
          cornerRadius: 3,
          bodyFontColor: '#20C4C8',
          bodyFontSize: 14,
          xPadding: 14,
          yPadding: 14,
          displayColors: false,
          mode: 'index',
          intersect: false,
          // callbacks: {
          //   title: tooltipItem => {
          //     return `🗓 ${tooltipItem[0].xLabel}`
          //   },
          //   label: (tooltipItem, data) => {
          //     let dataset = data.datasets[tooltipItem.datasetIndex]
          //     let currentValue = dataset.data[tooltipItem.index]
          //     return `📦 ${currentValue.toLocaleString()}`
          //   }
          // }
        },
        legend: {
          display: false
        },
        responsive: true,
        maintainAspectRatio: false
      }
    }
  },
  mounted() {
    // this.renderChart({
    //   labels: this.chartLabels,
    //   datasets: [{
    //     label: 'time_series',
    //     borderColor: '#249EBF',
    //     pointBackgroundColor: 'rgba(0,0,0,0)',
    //     pointBorderColor: 'rgba(0,0,0,0)',
    //     pointHoverBorderColor: '#249EBF',
    //     pointHoverBackgroundColor: '#fff',
    //     pointHoverRadius: 4,
    //     pointHitRadius: 10,
    //     pointHoverBorderWidth: 1,
    //     borderWidth: 1,
    //     // backgroundColor: this.gradient,
    //     data: this.chartData
    //   }]
    // }, this.options)
    console.log(this.datasetsf)
  }
}
</script>
