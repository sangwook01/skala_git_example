<script setup>
/* ==================================================================
 * WeatherDetailView.vue — 지역별 상세 기상관측 페이지
 *
 * ver7에서 달라진 점
 *  - 관측 정보를 n-descriptions 로 표시
 *  - 3시간 예보 목록을 ForecastChart(ECharts 꺾은선)로 교체
 *  - 대기질 등급을 n-tag 로 표시하고 버튼을 n-button 으로 교체
 * ================================================================== */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDescriptions, NDescriptionsItem, NTag, NButton, NSpace, useMessage } from 'naive-ui'

import BaseDashboardCard from '@/components_ver7/exercise_ver7/BaseDashboardCard.vue'
import StateNotice from '@/components_ver7/exercise_ver7/StateNotice.vue'
import ForecastChart from '@/components_ver7/exercise_ver7/ForecastChart.vue'

import { useWeatherStore } from '@/stores_ver7/weatherStore'
import { useConfigStore } from '@/stores_ver7/configStore'
import { useFavoriteStore } from '@/stores_ver7/favoriteStore'
import { fetchForecast, fetchAirPollution, toAirGrade } from '@/api_ver7/weatherApi'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const weatherStore = useWeatherStore()
const configStore = useConfigStore()
const favoriteStore = useFavoriteStore()

const city = ref(null)
const air = ref(null)
const forecast = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const toDisplayTemp = (rawTemp) =>
  configStore.unit === 'fahrenheit' ? Math.round((rawTemp * 9) / 5 + 32) : rawTemp

const displayTemp = computed(() => (city.value ? toDisplayTemp(city.value.temp) : 0))
const displayFeelsLike = computed(() => (city.value ? toDisplayTemp(city.value.feelsLike) : 0))

// 대기질 등급에 맞는 n-tag 색상
const airTagType = computed(() => {
  const aqi = air.value?.main.aqi
  if (aqi <= 2) return 'success'
  if (aqi === 3) return 'warning'
  return 'error'
})

const loadDetail = async () => {
  const target = weatherStore.findCityById(route.params.cityId)

  if (!target) {
    city.value = null
    return
  }

  city.value = target
  isLoading.value = true
  errorMessage.value = ''

  try {
    const coord = { lat: target.lat, lon: target.lon }

    // 두 요청은 서로 결과를 필요로 하지 않으므로 동시에 보낸다
    const [airData, forecastData] = await Promise.all([
      fetchAirPollution(coord),
      fetchForecast(coord),
    ])

    air.value = airData.list[0]
    forecast.value = forecastData.list.slice(0, 8) // 약 24시간
  } catch (error) {
    errorMessage.value = error.message
    message.error(error.message)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (weatherStore.weatherList.length === 0) {
    await weatherStore.loadAllWeather()
  }
  await loadDetail()
})

const handleToggleFavorite = () => {
  favoriteStore.toggleFavorite(city.value.id)
  message.info(
    favoriteStore.isFavorite(city.value.id)
      ? '즐겨찾기에 추가했습니다.'
      : '즐겨찾기를 해제했습니다.',
  )
}

const goHome = () => router.push('/')
const goBack = () => router.back()
</script>

<template>
  <div class="view">
    <template v-if="city">
      <div class="view-head">
        <p class="crumb">지역별 상세 기상관측</p>
        <h1 class="view-title">{{ city.name }}</h1>
        <p class="view-sub">
          {{ city.status }} · 현재 기온 {{ displayTemp }}{{ configStore.unitSymbol }}
        </p>
      </div>

      <BaseDashboardCard title="관측 정보" :meta="city.observedAt">
        <NDescriptions :column="3" label-placement="top" size="small">
          <NDescriptionsItem label="체감 온도">
            {{ displayFeelsLike }}{{ configStore.unitSymbol }}
          </NDescriptionsItem>
          <NDescriptionsItem label="습도">{{ city.humidity }}%</NDescriptionsItem>
          <NDescriptionsItem label="풍속">{{ city.wind }} m/s</NDescriptionsItem>
        </NDescriptions>
      </BaseDashboardCard>

      <!-- ECharts 예보 그래프 -->
      <BaseDashboardCard title="기온 추이" meta="3시간 간격 · 24시간">
        <StateNotice v-if="isLoading" type="loading" :count="1" />
        <StateNotice
          v-else-if="errorMessage"
          type="error"
          :message="errorMessage"
          @retry="loadDetail"
        />
        <ForecastChart v-else :slots="forecast" />
      </BaseDashboardCard>

      <BaseDashboardCard title="대기오염 정보">
        <StateNotice v-if="isLoading" type="loading" :count="1" />

        <NDescriptions v-else-if="air" :column="3" label-placement="top" size="small">
          <NDescriptionsItem label="대기질">
            <NTag size="small" :type="airTagType" :bordered="false">
              {{ toAirGrade(air.main.aqi) }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="PM10">
            {{ Math.round(air.components.pm10) }} ㎍/㎥
          </NDescriptionsItem>
          <NDescriptionsItem label="PM2.5">
            {{ Math.round(air.components.pm2_5) }} ㎍/㎥
          </NDescriptionsItem>
        </NDescriptions>
      </BaseDashboardCard>

      <NSpace justify="space-between" class="actions">
        <NButton
          :type="favoriteStore.isFavorite(city.id) ? 'warning' : 'default'"
          secondary
          @click="handleToggleFavorite"
        >
          {{ favoriteStore.isFavorite(city.id) ? '★ 해제' : '☆ 즐겨찾기' }}
        </NButton>

        <NSpace :size="8">
          <NButton quaternary @click="goBack">이전</NButton>
          <NButton type="primary" @click="goHome">대시보드</NButton>
        </NSpace>
      </NSpace>
    </template>

    <template v-else>
      <div class="view-head">
        <h1 class="view-title">도시를 찾을 수 없습니다</h1>
        <p class="view-sub">
          <code>{{ route.params.cityId }}</code> 에 해당하는 도시가 목록에 없습니다.
        </p>
      </div>

      <NButton type="primary" block @click="goHome">대시보드로 돌아가기</NButton>
    </template>
  </div>
</template>

<style scoped>
.crumb {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--orange);
}

.actions {
  width: 100%;
  margin-top: 4px;
}

code {
  padding: 1px 6px;
  border-radius: 4px;
  background: #131117;
  border: 1px solid var(--line);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  color: var(--orange);
}
</style>
