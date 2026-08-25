<template>
  <div ref="chartRef" style="height: 420px; width: 100%"></div>
</template>

<script setup>
import * as echarts from 'echarts'
import { onMounted, ref, watch } from 'vue'
const props = defineProps({ chart: { type: Object, default: () => ({ x_axis: [], series: [] }) } })
const chartRef = ref(null)
let instance
function render() {
  if (!instance && chartRef.value) instance = echarts.init(chartRef.value)
  if (!instance) return
  instance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll' },
    xAxis: { type: 'category', name: '应变', data: props.chart.x_axis || [] },
    yAxis: { type: 'value', name: '应力 MPa' },
    series: (props.chart.series || []).map(item => ({ ...item, type: 'line', smooth: true }))
  })
}
onMounted(render)
watch(() => props.chart, render, { deep: true })
</script>
