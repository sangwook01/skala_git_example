<script setup>
/* ==================================================================
 * WeatherHomeView.vue — 메인 날씨 대시보드
 *
 * ver4에서 달라진 점
 *  - favoriteStore 를 구독해 즐겨찾기만 보기 필터를 추가
 *  - 기온 표시 단위는 WeatherCard 가 configStore 를 직접 읽어 처리하므로
 *    이 화면에서는 단위와 관련된 코드를 갖지 않는다.
 * ================================================================== */
import { ref, computed, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver5/exercise_ver5/BaseDashboardCard.vue'
import SearchBar from '@/components_ver5/exercise_ver5/SearchBar.vue'
import WeatherCard from '@/components_ver5/exercise_ver5/WeatherCard.vue'
import StatusBar from '@/components_ver5/exercise_ver5/StatusBar.vue'

import { weatherList as mockWeatherList } from '@/data_ver5/weatherMock'
import { useFavoriteStore } from '@/stores_ver5/favoriteStore'

const router = useRouter()
const favoriteStore = useFavoriteStore()

/* ------------------------------------------------------------------
 * 1. 반응형 상태 관리 (ref)
 * ------------------------------------------------------------------ */
const weatherList = ref(mockWeatherList)
const searchQuery = ref('')
const selectedCityInfo = ref(null)
const hotOnly = ref(false)
const favoriteOnly = ref(false)

/* ------------------------------------------------------------------
 * 2. Computed
 * ------------------------------------------------------------------ */
const filteredWeatherList = computed(() => {
  let list = weatherList.value

  if (hotOnly.value) {
    list = list.filter((city) => city.temp >= 25)
  }

  // 전역 Store 의 즐겨찾기 목록을 조건으로 사용
  if (favoriteOnly.value) {
    list = list.filter((city) => favoriteStore.isFavorite(city.id))
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
  () => `${filteredWeatherList.value.length}건 · 즐겨찾기 ${favoriteStore.favoriteCount}개`,
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

// Store 의 state 도 반응형이므로 그대로 감시할 수 있다
watch(
  () => favoriteStore.favoriteCount,
  (newCount, oldCount) => {
    console.log(`★ [watch 감지] 즐겨찾기 ${oldCount}개 → ${newCount}개`)
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

const handleClickDetail = (city) => {
  router.push(`/weather/${city.id}`)
}
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">날씨 현황</h1>
      <p class="view-sub">과제 5 · Pinia Store</p>
    </div>

    <BaseDashboardCard title="도시 검색">
      <SearchBar :query="searchQuery" @update-query="handleUpdateQuery" />

      <div class="filters">
        <label class="toggle">
          <input type="checkbox" v-model="hotOnly" />
          25도 이상만 보기
        </label>

        <label class="toggle">
          <input type="checkbox" v-model="favoriteOnly" />
          즐겨찾기만 보기
        </label>
      </div>
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
.filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.toggle {
  display: flex;
  align-items: center;
  gap: 7px;
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
