<script setup>
/* ==================================================================
 * WeatherDetailView.vue — 지역별 상세 기상관측 페이지
 *
 * 경로 : /weather/:cityId
 *
 * ver6에서 달라진 점 (요구사항 2 — API 추가로 기능 확장)
 *  - Air Pollution API 로 실제 대기오염 정보를 조회
 *  - 5 day / 3 hour Forecast API 로 단기 예보를 조회해 목록으로 표시
 *  - 두 API 는 서로 의존하지 않으므로 Promise.all 로 동시에 요청
 * ================================================================== */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver6/exercise_ver6/BaseDashboardCard.vue'
import StateNotice from '@/components_ver6/exercise_ver6/StateNotice.vue'

import { useWeatherStore } from '@/stores_ver6/weatherStore'
import { useConfigStore } from '@/stores_ver6/configStore'
import { useFavoriteStore } from '@/stores_ver6/favoriteStore'
import { fetchForecast, fetchAirPollution, toAirGrade } from '@/api_ver6/weatherApi'

const route = useRoute()
const router = useRouter()

const weatherStore = useWeatherStore()
const configStore = useConfigStore()
const favoriteStore = useFavoriteStore()

const city = ref(null)
const air = ref(null)
const forecast = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

/* ------------------------------------------------------------------
 * 단위 변환 — 원본은 섭씨로 두고 표시할 때만 변환한다
 * ------------------------------------------------------------------ */
const toDisplayTemp = (rawTemp) =>
  configStore.unit === 'fahrenheit' ? Math.round((rawTemp * 9) / 5 + 32) : rawTemp

const displayTemp = computed(() => (city.value ? toDisplayTemp(city.value.temp) : 0))
const displayFeelsLike = computed(() => (city.value ? toDisplayTemp(city.value.feelsLike) : 0))

/* ------------------------------------------------------------------
 * 상세 데이터 조회
 * ------------------------------------------------------------------ */
const loadDetail = async () => {
  const cityId = route.params.cityId
  const target = weatherStore.findCityById(cityId)

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
    // 3시간 간격 예보 중 앞의 6개(약 18시간)만 사용한다
    forecast.value = forecastData.list.slice(0, 6)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  // 상세 페이지로 새로고침 진입하면 Store 가 비어 있을 수 있으므로 먼저 목록을 채운다
  if (weatherStore.weatherList.length === 0) {
    await weatherStore.loadAllWeather()
  }
  await loadDetail()
})

/* ------------------------------------------------------------------
 * 예보 표시용 가공
 * ------------------------------------------------------------------ */
const formatTime = (dtText) => dtText.slice(5, 16).replace('-', '/')

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
        <dl class="spec">
          <div class="row">
            <dt>체감 온도</dt>
            <dd>{{ displayFeelsLike }}{{ configStore.unitSymbol }}</dd>
          </div>
          <div class="row">
            <dt>습도</dt>
            <dd>{{ city.humidity }}%</dd>
          </div>
          <div class="row">
            <dt>풍속</dt>
            <dd>{{ city.wind }} m/s</dd>
          </div>
        </dl>
      </BaseDashboardCard>

      <!-- 요구사항 2 : Air Pollution API -->
      <BaseDashboardCard title="대기오염 정보">
        <StateNotice v-if="isLoading" type="loading" message="대기 정보를 불러오는 중입니다" />
        <StateNotice
          v-else-if="errorMessage"
          type="error"
          :message="errorMessage"
          @retry="loadDetail"
        />

        <dl v-else-if="air" class="spec">
          <div class="row">
            <dt>대기질 지수</dt>
            <dd :class="`aqi aqi--${air.main.aqi}`">{{ toAirGrade(air.main.aqi) }}</dd>
          </div>
          <div class="row">
            <dt>미세먼지 (PM10)</dt>
            <dd>{{ Math.round(air.components.pm10) }} ㎍/㎥</dd>
          </div>
          <div class="row">
            <dt>초미세먼지 (PM2.5)</dt>
            <dd>{{ Math.round(air.components.pm2_5) }} ㎍/㎥</dd>
          </div>
        </dl>
      </BaseDashboardCard>

      <!-- 요구사항 2 : 5 day / 3 hour Forecast API -->
      <BaseDashboardCard title="단기 예보" meta="3시간 간격">
        <StateNotice v-if="isLoading" type="loading" message="예보를 불러오는 중입니다" />

        <ul v-else-if="forecast.length > 0" class="forecast">
          <li v-for="slot in forecast" :key="slot.dt" class="slot">
            <span class="time">{{ formatTime(slot.dt_txt) }}</span>
            <img
              class="slot-icon"
              :src="`https://openweathermap.org/img/wn/${slot.weather[0].icon}.png`"
              :alt="slot.weather[0].description"
            />
            <span class="desc">{{ slot.weather[0].description }}</span>
            <span class="pop">강수 {{ Math.round(slot.pop * 100) }}%</span>
            <span class="slot-temp">
              {{ toDisplayTemp(Math.round(slot.main.temp)) }}{{ configStore.unitSymbol }}
            </span>
          </li>
        </ul>
      </BaseDashboardCard>

      <div class="actions">
        <button class="ghost" @click="favoriteStore.toggleFavorite(city.id)">
          {{ favoriteStore.isFavorite(city.id) ? '★ 해제' : '☆ 즐겨찾기' }}
        </button>
        <button class="ghost" @click="goBack">이전</button>
        <button class="primary" @click="goHome">대시보드</button>
      </div>
    </template>

    <!-- 목록에 없는 도시 코드로 접근한 경우 -->
    <template v-else>
      <div class="view-head">
        <h1 class="view-title">도시를 찾을 수 없습니다</h1>
        <p class="view-sub">
          <code>{{ route.params.cityId }}</code> 에 해당하는 도시가 목록에 없습니다.
        </p>
      </div>

      <div class="actions">
        <button class="primary" @click="goHome">대시보드로 돌아가기</button>
      </div>
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

/* ── 관측 정보 ── */
.spec {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 0;
  border-bottom: 1px solid var(--line);
}

.row:last-child {
  border-bottom: 0;
}

dt {
  font-size: 13px;
  color: var(--muted);
}

dd {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}

.aqi--1,
.aqi--2 {
  color: var(--teal);
}

.aqi--3 {
  color: var(--orange);
}

.aqi--4,
.aqi--5 {
  color: #ff7a6e;
}

/* ── 예보 ── */
.forecast {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
}

.slot {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 0;
  border-bottom: 1px solid var(--line);
  font-size: 12.5px;
}

.slot:last-child {
  border-bottom: 0;
}

.time {
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.slot-icon {
  width: 26px;
  height: 26px;
  margin: -6px 0;
}

.desc {
  flex: 1;
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pop {
  color: var(--teal);
  white-space: nowrap;
}

.slot-temp {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

/* ── 버튼 ── */
.actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.actions button {
  flex: 1;
  padding: 12px 10px;
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition:
    filter 0.15s,
    border-color 0.15s,
    color 0.15s;
}

.primary {
  border: 0;
  background: linear-gradient(180deg, #ff4b3c, var(--red-deep));
  color: #fff;
  box-shadow:
    0 0 14px rgba(255, 59, 47, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

.primary:hover {
  filter: brightness(1.14);
}

.ghost {
  border: 1px solid var(--line-2);
  background: transparent;
  color: var(--muted);
}

.ghost:hover {
  border-color: rgba(255, 138, 61, 0.5);
  color: var(--orange);
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
