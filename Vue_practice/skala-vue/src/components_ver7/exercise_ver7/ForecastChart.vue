<script setup>
/* ==================================================================
 * ForecastChart.vue — ECharts 로 그린 단기 예보 그래프
 *
 * ver6에서는 3시간 간격 예보를 목록으로 나열했지만,
 * 기온 변화는 추세를 보는 것이 목적이므로 꺾은선 그래프가 적절하다.
 *
 * Naive UI 에는 차트가 없으므로 vue-echarts 를 별도로 사용한다.
 * 필요한 모듈만 등록하면 번들 크기를 줄일 수 있다.
 * ================================================================== */
import { computed } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

import { useConfigStore } from '@/stores_ver7/configStore'
import { palette } from '@/theme_ver7/naiveTheme'

// 사용할 모듈만 등록 (전체 import 대신)
use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  // OpenWeatherMap forecast API 의 list 배열
  slots: { type: Array, default: () => [] },
})

const configStore = useConfigStore()

const toDisplayTemp = (rawTemp) =>
  configStore.unit === 'fahrenheit' ? Math.round((rawTemp * 9) / 5 + 32) : Math.round(rawTemp)

const option = computed(() => {
  const labels = props.slots.map((slot) => slot.dt_txt.slice(5, 13).replace('-', '/'))
  const temps = props.slots.map((slot) => toDisplayTemp(slot.main.temp))
  const pops = props.slots.map((slot) => Math.round(slot.pop * 100))

  return {
    backgroundColor: 'transparent',
    grid: { top: 24, right: 12, bottom: 24, left: 36 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: palette.card2,
      borderColor: palette.line2,
      textStyle: { color: palette.text, fontSize: 12 },
      formatter: (params) => {
        const time = params[0].axisValue
        const temp = params[0].data
        const pop = pops[params[0].dataIndex]
        return `${time}<br/>기온 ${temp}${configStore.unitSymbol}<br/>강수 ${pop}%`
      },
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: palette.line2 } },
      axisLabel: { color: palette.muted, fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        color: palette.muted,
        fontSize: 10,
        formatter: (value) => `${value}°`,
      },
      splitLine: { lineStyle: { color: palette.line } },
    },
    series: [
      {
        type: 'line',
        data: temps,
        smooth: true,
        symbolSize: 6,
        lineStyle: { color: palette.red, width: 2 },
        itemStyle: { color: palette.red },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 59, 47, 0.28)' },
              { offset: 1, color: 'rgba(255, 59, 47, 0)' },
            ],
          },
        },
      },
    ],
  }
})
</script>

<template>
  <VChart v-if="slots.length > 0" class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 200px;
}
</style>
