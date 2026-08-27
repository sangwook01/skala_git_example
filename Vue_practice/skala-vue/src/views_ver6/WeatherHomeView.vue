<script setup>
/* ==================================================================
 * WeatherHomeView.vue — 메인 날씨 대시보드
 *
 * ver6에서 달라진 점
 *  - Mock Data 대신 weatherStore 가 OpenWeatherMap 에서 받아온 실제 데이터를 사용
 *  - onMounted 시점에 통신을 시작하고 로딩·에러 상태를 화면에 표시
 *  - 검색 결과가 없을 때 외부 지오코딩 API 로 도시를 추가하는 기능 제공
 * ================================================================== */
import { ref, computed, watch, watchEffect, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import BaseDashboardCard from '@/components_ver6/exercise_ver6/BaseDashboardCard.vue'
import SearchBar from '@/components_ver6/exercise_ver6/SearchBar.vue'
import WeatherCard from '@/components_ver6/exercise_ver6/WeatherCard.vue'
import StatusBar from '@/components_ver6/exercise_ver6/StatusBar.vue'
import StateNotice from '@/components_ver6/exercise_ver6/StateNotice.vue'

import { useWeatherStore } from '@/stores_ver6/weatherStore'
import { useFavoriteStore } from '@/stores_ver6/favoriteStore'

const router = useRouter()
const weatherStore = useWeatherStore()
const favoriteStore = useFavoriteStore()

/* ------------------------------------------------------------------
 * 1. 화면 단위 상태 (ref)
 * ------------------------------------------------------------------ */
const searchQuery = ref('')
const selectedCityInfo = ref(null)
const hotOnly = ref(false)
const favoriteOnly = ref(false)

/* ------------------------------------------------------------------
 * 2. Computed — 필터링 대상이 Store 의 목록으로 바뀌었을 뿐 로직은 ver5와 동일
 * ------------------------------------------------------------------ */
const filteredWeatherList = computed(() => {
  let list = weatherStore.weatherList

  if (hotOnly.value) {
    list = list.filter((city) => city.temp >= 25)
  }

  if (favoriteOnly.value) {
    list = list.filter((city) => favoriteStore.isFavorite(city.id))
  }

  const keyword = searchQuery.value.trim()
  if (keyword === '') return list

  return list.filter((city) => city.name.includes(keyword))
})

const statusMessage = computed(() =>
  selectedCityInfo.value
    ? `"${selectedCityInfo.value.name}"이 선택되었습니다.`
    : '카드를 클릭하거나 도시를 검색해 보세요.',
)

const listMeta = computed(() =>
  weatherStore.lastUpdated ? `${weatherStore.lastUpdated} 기준` : '',
)

// 검색어가 있는데 결과가 없으면 새 도시로 추가할 수 있는지 안내한다
const canAddCity = computed(
  () => searchQuery.value.trim() !== '' && filteredWeatherList.value.length === 0,
)

/* ------------------------------------------------------------------
 * 3. 감시
 * ------------------------------------------------------------------ */
watch(selectedCityInfo, (newCity, oldCity) => {
  const before = oldCity ? oldCity.name : '없음'
  const after = newCity ? newCity.name : '없음'
  console.log(`👁 [watch 감지] 상태 바 문구가 업데이트되었습니다. ${before} → ${after}`)
})

watchEffect(() => {
  console.log(
    `⚡ [watchEffect 자동 호출] 현재 검색어 '${searchQuery.value}'에 해당하는 데이터를 필터링합니다.`,
  )
})

/* ------------------------------------------------------------------
 * 4. Mount 시점에 통신 시작
 * ------------------------------------------------------------------ */
onMounted(() => {
  // 이미 불러온 데이터가 있으면 화면을 이동해 돌아왔을 때 다시 요청하지 않는다
  if (weatherStore.weatherList.length === 0) {
    weatherStore.loadAllWeather()
  }
})

/* ------------------------------------------------------------------
 * 5. 이벤트 핸들러
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

const handleAddCity = async () => {
  await weatherStore.addCityByName(searchQuery.value)
  if (!weatherStore.hasError) {
    searchQuery.value = '' // 추가에 성공하면 검색어를 비워 전체 목록을 보여준다
  }
}
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">날씨 현황</h1>
      <p class="view-sub">과제 6 · Axios + OpenWeatherMap</p>
    </div>

    <BaseDashboardCard title="도시 검색">
      <SearchBar :query="searchQuery" @update-query="handleUpdateQuery" />

      <!-- 검색 결과가 없을 때만 외부 API 로 도시를 추가할 수 있게 안내 -->
      <button v-if="canAddCity" class="add-btn" @click="handleAddCity">
        + '{{ searchQuery }}' 을(를) 새 도시로 추가
      </button>

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
      <!-- 통신 중 -->
      <StateNotice
        v-if="weatherStore.isLoading"
        type="loading"
        message="날씨 정보를 불러오는 중입니다"
      />

      <!-- 통신 실패 -->
      <StateNotice
        v-else-if="weatherStore.hasError"
        type="error"
        :message="weatherStore.errorMessage"
        @retry="weatherStore.loadAllWeather"
      />

      <!-- 정상 -->
      <template v-else-if="filteredWeatherList.length > 0">
        <WeatherCard
          v-for="city in filteredWeatherList"
          :key="city.id"
          :city="city"
          @select-card="handleSelectCard"
          @click-detail="handleClickDetail"
        />
      </template>

      <StateNotice v-else type="empty" message="검색 결과와 일치하는 도시가 없습니다." />
    </BaseDashboardCard>

    <div class="foot">
      <StatusBar :message="statusMessage" />
      <button
        class="refresh"
        :disabled="weatherStore.isLoading"
        @click="weatherStore.loadAllWeather"
      >
        새로고침
      </button>
    </div>
  </div>
</template>

<style scoped>
.add-btn {
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(255, 138, 61, 0.5);
  border-radius: 8px;
  background: rgba(255, 138, 61, 0.08);
  color: var(--orange);
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
}

.add-btn:hover {
  background: rgba(255, 138, 61, 0.16);
}

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

.foot {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.foot > :first-child {
  flex: 1;
}

.refresh {
  flex-shrink: 0;
  padding: 0 16px;
  border: 1px solid var(--line-2);
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition:
    border-color 0.15s,
    color 0.15s;
}

.refresh:hover:not(:disabled) {
  border-color: rgba(255, 138, 61, 0.5);
  color: var(--orange);
}

.refresh:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
