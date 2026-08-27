<script setup>
/* ==================================================================
 * WeatherHomeView.vue — 메인 날씨 대시보드 (ver3의 WeatherParent 대체)
 *
 * ver3와 달라진 점은 딱 하나.
 * 상세보기 버튼을 눌렀을 때 window.alert() 를 띄우는 대신
 * router.push() 로 상세 페이지로 이동한다. (Programmatic Navigation)
 * ================================================================== */
import { ref, computed, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver4/exercise_ver4/BaseDashboardCard.vue'
import SearchBar from '@/components_ver4/exercise_ver4/SearchBar.vue'
import WeatherCard from '@/components_ver4/exercise_ver4/WeatherCard.vue'
import StatusBar from '@/components_ver4/exercise_ver4/StatusBar.vue'

import { weatherList as mockWeatherList } from '@/data_ver4/weatherMock'

// 라우터 인스턴스 — 스크립트에서 페이지를 전환할 때 사용
const router = useRouter()

/* ------------------------------------------------------------------
 * 1. 반응형 상태 관리 (ref)
 * ------------------------------------------------------------------ */
const weatherList = ref(mockWeatherList)
const searchQuery = ref('')
const selectedCityInfo = ref(null)
const hotOnly = ref(false)

/* ------------------------------------------------------------------
 * 2. Computed
 * ------------------------------------------------------------------ */
const filteredWeatherList = computed(() => {
  let list = weatherList.value

  if (hotOnly.value) {
    list = list.filter((city) => city.temp >= 25)
  }

  // 검색어가 비어 있으면 원본 데이터를 그대로 반환한다
  const keyword = searchQuery.value.trim()
  if (keyword === '') return list

  return list.filter((city) => city.name.includes(keyword))
})

const statusMessage = computed(() =>
  selectedCityInfo.value
    ? `"${selectedCityInfo.value.name}"이 선택되었습니다.`
    : '카드를 클릭하거나 도시를 검색해 보세요.',
)

const averageTemp = computed(() => {
  const list = filteredWeatherList.value
  if (list.length === 0) return 0
  const sum = list.reduce((acc, city) => acc + city.temp, 0)
  return Math.round((sum / list.length) * 10) / 10
})

const listMeta = computed(
  () => `${filteredWeatherList.value.length}건 · 평균 ${averageTemp.value}°C`,
)

/* ------------------------------------------------------------------
 * 3. 반응형 변수 변화 감시 (watch / watchEffect)
 * ------------------------------------------------------------------ */
watch(selectedCityInfo, (newCity, oldCity) => {
  const before = oldCity ? oldCity.name : '없음'
  const after = newCity ? newCity.name : '없음'
  console.log(`👁 [watch 감지] 상태 바 문구가 업데이트되었습니다. ${before} → ${after}`)
  console.log(`   └ 현재 문구: ${statusMessage.value}`)
})

watchEffect(() => {
  console.log(
    `⚡ [watchEffect 자동 호출] 현재 검색어 '${searchQuery.value}'에 해당하는 데이터를 필터링합니다.`,
  )
})

watch(
  () => filteredWeatherList.value.length,
  (newCount, oldCount) => {
    console.log(`📊 [watch 감지] 검색 결과 ${oldCount}건 → ${newCount}건`)
  },
)

/* ------------------------------------------------------------------
 * 4. 자식 컴포넌트 이벤트 핸들러
 * ------------------------------------------------------------------ */
const handleUpdateQuery = (value) => {
  searchQuery.value = value
}

const handleSelectCard = (city) => {
  selectedCityInfo.value = city
}

// ver3 : window.alert(...)
// ver4 : Programmatic Navigation 으로 상세 페이지 이동
const handleClickDetail = (city) => {
  router.push(`/weather/${city.id}`)
}
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">날씨 현황</h1>
      <p class="view-sub">과제 4 · Vue Router</p>
    </div>

    <BaseDashboardCard title="도시 검색">
      <SearchBar :query="searchQuery" @update-query="handleUpdateQuery" />

      <!-- slot 내부이지만 부모 스코프이므로 hotOnly 와 v-model 직접 연결 가능 -->
      <label class="toggle">
        <input type="checkbox" v-model="hotOnly" />
        25도 이상만 보기
      </label>
    </BaseDashboardCard>

    <BaseDashboardCard title="지역별 날씨 현황" :meta="listMeta">
      <template v-if="filteredWeatherList.length > 0">
        <WeatherCard
          v-for="city in filteredWeatherList"
          :key="city.id"
          :city="city"
          @select-card="handleSelectCard"
          @click-detail="handleClickDetail"
        />
      </template>

      <p v-else class="empty">검색 결과와 일치하는 도시가 없습니다.</p>
    </BaseDashboardCard>

    <StatusBar :message="statusMessage" />
  </div>
</template>

<style scoped>
.toggle {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 12px;
  font-size: 12.5px;
  color: var(--muted);
  cursor: pointer;
  user-select: none;
}

.toggle input {
  width: 14px;
  height: 14px;
  accent-color: var(--red);
  cursor: pointer;
}

.empty {
  margin: 0;
  padding: 26px 16px;
  border: 1px dashed var(--line-2);
  border-radius: 10px;
  background: #131117;
  font-size: 13px;
  color: var(--muted);
  text-align: center;
}
</style>
