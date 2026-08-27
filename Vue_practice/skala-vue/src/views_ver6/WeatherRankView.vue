<script setup>
/* ==================================================================
 * WeatherRankView.vue — 본인 추가 View (요구사항 6)
 *
 * 경로 : /rank
 * 전체 도시를 기온 내림차순으로 정렬해 순위로 보여준다.
 * 항목을 누르면 해당 도시의 상세 페이지로 이동한다.
 * ================================================================== */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver6/exercise_ver6/BaseDashboardCard.vue'
import { useConfigStore } from '@/stores_ver6/configStore'
import { useWeatherStore } from '@/stores_ver6/weatherStore'

const router = useRouter()
const configStore = useConfigStore()
const weatherStore = useWeatherStore()

// 원본은 섭씨이므로 단위 설정에 맞춰 변환한다
const toDisplayTemp = (rawTemp) =>
  configStore.unit === 'fahrenheit' ? Math.round((rawTemp * 9) / 5 + 32) : rawTemp

// 원본 배열을 정렬하면 다른 화면에도 영향을 주므로 복사본을 만들어 정렬한다
const rankedList = computed(() => [...weatherStore.weatherList].sort((a, b) => b.temp - a.temp))

const hottest = computed(() => rankedList.value[0] ?? null)
const coldest = computed(() => rankedList.value[rankedList.value.length - 1] ?? null)

onMounted(() => {
  // 순위 페이지로 바로 진입한 경우에도 데이터를 채운다
  if (weatherStore.weatherList.length === 0) {
    weatherStore.loadAllWeather()
  }
})

const goDetail = (cityId) => {
  router.push(`/weather/${cityId}`)
}
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">기온 순위</h1>
      <p class="view-sub">관측된 도시를 기온이 높은 순으로 정렬했습니다</p>
    </div>

    <BaseDashboardCard title="요약">
      <div v-if="hottest && coldest" class="summary">
        <div class="stat">
          <span class="stat-label">가장 더운 곳</span>
          <span class="stat-value hot"
            >{{ hottest.name }} {{ toDisplayTemp(hottest.temp) }}{{ configStore.unitSymbol }}</span
          >
        </div>
        <div class="stat">
          <span class="stat-label">가장 선선한 곳</span>
          <span class="stat-value cool"
            >{{ coldest.name }} {{ toDisplayTemp(coldest.temp) }}{{ configStore.unitSymbol }}</span
          >
        </div>
      </div>
    </BaseDashboardCard>

    <BaseDashboardCard title="전체 순위" :meta="`${rankedList.length}개 도시`">
      <ol class="rank">
        <li
          v-for="(city, index) in rankedList"
          :key="city.id"
          class="rank-row"
          @click="goDetail(city.id)"
        >
          <span class="no">{{ index + 1 }}</span>
          <span class="name">{{ city.name }}</span>
          <span class="status">{{ city.status }}</span>
          <span class="temp">{{ toDisplayTemp(city.temp) }}{{ configStore.unitSymbol }}</span>
        </li>
      </ol>
    </BaseDashboardCard>
  </div>
</template>

<style scoped>
.summary {
  display: flex;
  gap: 12px;
}

.stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.stat-label {
  font-size: 11px;
  letter-spacing: 0.6px;
  color: var(--muted);
}

.stat-value {
  font-size: 15px;
  font-weight: 800;
}

.stat-value.hot {
  color: #ff7a6e;
}

.stat-value.cool {
  color: var(--teal);
}

/* ── 순위 목록 ── */
.rank {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
}

.rank-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 8px;
  border-bottom: 1px solid var(--line);
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}

.rank-row:last-child {
  border-bottom: 0;
}

.rank-row:hover {
  background: #171319;
}

.no {
  width: 20px;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 800;
  color: var(--orange);
  font-variant-numeric: tabular-nums;
}

.name {
  font-size: 14px;
  font-weight: 700;
}

.status {
  flex: 1;
  font-size: 12.5px;
  color: var(--muted);
}

.temp {
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
</style>
