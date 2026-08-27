<script setup>
/* ==================================================================
 * WeatherDetailView.vue — 지역별 상세 기상관측 페이지
 *
 * 경로 : /weather/:cityId   (동적 세그먼트)
 * useRoute() 로 route.params.cityId 를 수신하고,
 * Mount 시점에 Mock Data 에서 해당 도시 객체를 선택한다.
 * ================================================================== */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver4/exercise_ver4/BaseDashboardCard.vue'
import { findCityById, findDetailById } from '@/data_ver4/weatherMock'

const route = useRoute() // 현재 활성화된 라우트 정보
const router = useRouter() // 페이지 전환용 라우터 인스턴스

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

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="view">
    <!-- 도시 데이터를 찾은 경우 -->
    <template v-if="city">
      <div class="view-head">
        <p class="crumb">지역별 상세 기상관측</p>
        <h1 class="view-title">{{ city.name }}</h1>
        <p class="view-sub">{{ city.status }} · 현재 기온 {{ city.temp }}°C</p>
      </div>

      <BaseDashboardCard title="관측 정보" :meta="detail.observedAt">
        <dl class="spec">
          <div class="row">
            <dt>체감 온도</dt>
            <dd>{{ detail.feelsLike }}°C</dd>
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
        <button class="ghost" @click="goBack">이전 페이지</button>
        <button class="primary" @click="goHome">대시보드로 돌아가기</button>
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
  padding: 12px 14px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
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
