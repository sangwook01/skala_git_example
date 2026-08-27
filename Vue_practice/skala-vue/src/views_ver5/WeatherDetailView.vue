<script setup>
/* ==================================================================
 * WeatherDetailView.vue — 지역별 상세 기상관측 페이지
 *
 * 경로 : /weather/:cityId   (동적 세그먼트)
 *
 * ver5에서 달라진 점
 *  - configStore 를 구독해 기온과 체감 온도를 현재 단위로 변환해 표시
 *  - favoriteStore 를 구독해 이 도시의 즐겨찾기 상태를 표시하고 토글
 * ================================================================== */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver5/exercise_ver5/BaseDashboardCard.vue'
import { findCityById, findDetailById } from '@/data_ver5/weatherMock'
import { useConfigStore } from '@/stores_ver5/configStore'
import { useFavoriteStore } from '@/stores_ver5/favoriteStore'

const route = useRoute()
const router = useRouter()

const configStore = useConfigStore()
const favoriteStore = useFavoriteStore()

const city = ref(null)
const detail = ref(null)

onMounted(() => {
  // 주소창의 :cityId 부분을 읽는다 — 예) /weather/city_01 → 'city_01'
  const cityId = route.params.cityId
  console.log(`🧭 [useRoute] 현재 경로: ${route.path} / cityId: ${cityId}`)

  city.value = findCityById(cityId)
  detail.value = findDetailById(cityId)

  if (!city.value) {
    console.warn(`⚠️ '${cityId}' 에 해당하는 도시 데이터가 없습니다.`)
  }
})

/*
 * 원본 데이터는 섭씨 숫자이므로 단위 설정에 맞춰 변환한다.
 * 이 화면에서는 기온과 체감 온도 두 곳에 필요하므로 함수로 한 번만 작성한다.
 * (여러 화면에서 반복되는 부분은 Composable 로 묶을 수 있으나 범위 제외)
 */
const toDisplayTemp = (rawTemp) => {
  if (configStore.unit === 'fahrenheit') {
    return Math.round((rawTemp * 9) / 5 + 32)
  }
  return rawTemp
}

const displayTemp = computed(() => (city.value ? toDisplayTemp(city.value.temp) : 0))
const displayFeelsLike = computed(() => (detail.value ? toDisplayTemp(detail.value.feelsLike) : 0))

const goHome = () => router.push('/')
const goBack = () => router.back()
</script>

<template>
  <div class="view">
    <!-- 도시 데이터를 찾은 경우 -->
    <template v-if="city">
      <div class="view-head">
        <p class="crumb">지역별 상세 기상관측</p>
        <h1 class="view-title">{{ city.name }}</h1>
        <p class="view-sub">
          {{ city.status }} · 현재 기온 {{ displayTemp }}{{ configStore.unitSymbol }}
        </p>
      </div>

      <BaseDashboardCard title="관측 정보" :meta="detail.observedAt">
        <dl class="spec">
          <div class="row">
            <dt>체감 온도</dt>
            <dd>{{ displayFeelsLike }}{{ configStore.unitSymbol }}</dd>
          </div>
          <div class="row">
            <dt>습도</dt>
            <dd>{{ detail.humidity }}%</dd>
          </div>
          <div class="row">
            <dt>풍속</dt>
            <dd>{{ detail.wind }} m/s</dd>
          </div>
          <div class="row">
            <dt>강수 확률</dt>
            <dd>{{ detail.rainChance }}%</dd>
          </div>
          <div class="row">
            <dt>미세먼지</dt>
            <dd>{{ detail.dust }}</dd>
          </div>
        </dl>
      </BaseDashboardCard>

      <BaseDashboardCard title="예보 코멘트">
        <p class="comment">{{ detail.comment }}</p>
      </BaseDashboardCard>

      <div class="actions">
        <button class="ghost" @click="favoriteStore.toggleFavorite(city.id)">
          {{ favoriteStore.isFavorite(city.id) ? '★ 즐겨찾기 해제' : '☆ 즐겨찾기' }}
        </button>
        <button class="ghost" @click="goBack">이전 페이지</button>
        <button class="primary" @click="goHome">대시보드</button>
      </div>
    </template>

    <!-- 정의되지 않은 도시 코드로 접근한 경우 -->
    <template v-else>
      <div class="view-head">
        <h1 class="view-title">도시를 찾을 수 없습니다</h1>
        <p class="view-sub">
          <code>{{ route.params.cityId }}</code> 에 해당하는 관측 데이터가 없습니다.
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

.comment {
  margin: 0;
  font-size: 13.5px;
  color: #bdb4c0;
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
