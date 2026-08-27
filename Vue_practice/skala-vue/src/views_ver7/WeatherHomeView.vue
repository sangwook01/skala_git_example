<script setup>
/* ==================================================================
 * WeatherHomeView.vue — 메인 날씨 대시보드
 *
 * ver7에서 달라진 점
 *  - SearchBar 가 자동완성이 되면서 [추가] 버튼 분기가 사라짐
 *  - 결과 안내를 화면 안 문구가 아니라 n-message 토스트로 표시
 *  - 필터 체크박스를 n-checkbox 로 교체
 * ================================================================== */
import { ref, computed, watch, watchEffect, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCheckbox, NSpace, NButton, useMessage } from 'naive-ui'

import BaseDashboardCard from '@/components_ver7/exercise_ver7/BaseDashboardCard.vue'
import SearchBar from '@/components_ver7/exercise_ver7/SearchBar.vue'
import WeatherCard from '@/components_ver7/exercise_ver7/WeatherCard.vue'
import StatusBar from '@/components_ver7/exercise_ver7/StatusBar.vue'
import StateNotice from '@/components_ver7/exercise_ver7/StateNotice.vue'

import { useWeatherStore } from '@/stores_ver7/weatherStore'
import { useFavoriteStore } from '@/stores_ver7/favoriteStore'

const router = useRouter()
const weatherStore = useWeatherStore()
const favoriteStore = useFavoriteStore()

// n-message-provider 하위에서만 사용할 수 있다 (App_ver7 에서 감쌈)
const message = useMessage()

/* ------------------------------------------------------------------
 * 1. 화면 단위 상태
 * ------------------------------------------------------------------ */
const searchQuery = ref('')
const selectedCityInfo = ref(null)
const hotOnly = ref(false)
const favoriteOnly = ref(false)

/* ------------------------------------------------------------------
 * 2. Computed
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

// 통신 에러는 화면 대신 토스트로 알린다
watch(
  () => weatherStore.errorMessage,
  (msg) => {
    if (msg) message.error(msg)
  },
)

/* ------------------------------------------------------------------
 * 4. Mount 시점에 통신 시작
 * ------------------------------------------------------------------ */
onMounted(() => {
  if (weatherStore.weatherList.length === 0) {
    weatherStore.loadAllWeather()
  }
})

/* ------------------------------------------------------------------
 * 5. 이벤트 핸들러
 * ------------------------------------------------------------------ */
const handleUpdateQuery = (value) => {
  searchQuery.value = value ?? ''
}

const handleSelectCard = (city) => {
  selectedCityInfo.value = city
}

const handleClickDetail = (city) => {
  router.push(`/weather/${city.id}`)
}

// 자동완성에서 도시를 고르면 좌표를 그대로 넘겨 추가한다
const handleSelectPlace = async (place) => {
  try {
    const added = await weatherStore.addCityByPlace(place)
    message.success(`'${added}' 을(를) 목록에 추가했습니다.`)
    searchQuery.value = ''
  } catch (error) {
    message.warning(error.message)
  }
}

const handleRefresh = async () => {
  await weatherStore.loadAllWeather()
  if (!weatherStore.hasError) message.success('날씨 정보를 새로 불러왔습니다.')
}
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">날씨 현황</h1>
      <p class="view-sub">과제 7 · Naive UI + ECharts</p>
    </div>

    <BaseDashboardCard title="도시 검색">
      <SearchBar
        :query="searchQuery"
        @update-query="handleUpdateQuery"
        @select-place="handleSelectPlace"
      />

      <NSpace class="filters" :size="14">
        <NCheckbox v-model:checked="hotOnly">25도 이상만 보기</NCheckbox>
        <NCheckbox v-model:checked="favoriteOnly">즐겨찾기만 보기</NCheckbox>
      </NSpace>
    </BaseDashboardCard>

    <BaseDashboardCard title="지역별 날씨 현황" :meta="listMeta">
      <StateNotice v-if="weatherStore.isLoading" type="loading" :count="4" />

      <StateNotice
        v-else-if="weatherStore.hasError"
        type="error"
        :message="weatherStore.errorMessage"
        @retry="weatherStore.loadAllWeather"
      />

      <template v-else-if="filteredWeatherList.length > 0">
        <WeatherCard
          v-for="city in filteredWeatherList"
          :key="city.id"
          :city="city"
          @select-card="handleSelectCard"
          @click-detail="handleClickDetail"
        />
      </template>

      <StateNotice
        v-else
        type="empty"
        message="검색 결과가 없습니다. 목록에서 도시를 골라 추가해 보세요."
      />
    </BaseDashboardCard>

    <div class="foot">
      <StatusBar :message="statusMessage" />
      <NButton :loading="weatherStore.isLoading" secondary @click="handleRefresh">
        새로고침
      </NButton>
    </div>
  </div>
</template>

<style scoped>
.filters {
  margin-top: 14px;
}

.foot {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.foot > :first-child {
  flex: 1;
}
</style>
