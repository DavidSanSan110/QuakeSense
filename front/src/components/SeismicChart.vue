<template>
    <LineChart :data="chartData" :options="chartOptions" />
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import { Line } from 'vue-chartjs';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
  } from 'chart.js';
  import annotationPlugin from 'chartjs-plugin-annotation';
  
  ChartJS.register(
    Title,
    Tooltip,
    Legend,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    annotationPlugin
  );
  
  export default defineComponent({
    name: 'SeismicChart',
    components: {
      LineChart: Line,
    },
    props: {
      chartData: {
        type: Object,
        required: true,
      },
      chartOptions: {
        type: Object,
        required: true,
      },
    },
  });
  </script>
  