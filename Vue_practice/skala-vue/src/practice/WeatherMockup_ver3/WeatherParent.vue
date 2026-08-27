<script setup>
/* ==================================================================
 * WeatherParent.vue — 모든 반응형 데이터를 보유하는 부모 컴포넌트
 *
 * ver2(WeatherComposition.vue)의 <script setup> 로직을 그대로 유지하고,
 * 화면만 4개의 자식 컴포넌트로 분리했다. (기능 변경 없음)
 * ================================================================== */
import { ref, computed, watch, watchEffect } from 'vue'

import BaseDashboardCard from './BaseDashboardCard.vue'
import SearchBar from './SearchBar.vue'
import WeatherCard from './WeatherCard.vue'
import StatusBar from './StatusBar.vue'

/* ------------------------------------------------------------------
 * 1. 반응형 상태 관리 (ref) — 모든 상태는 부모가 소유한다
 * ------------------------------------------------------------------ */
const weatherList = ref([
  { id: 'city_01', name: '구미', temp: 28, status: '맑음' },
  { id: 'city_02', name: '대구', temp: 24, status: '비' },
  { id: 'city_03', name: '부산', temp: 26, status: '구름' },
  { id: 'city_04', name: '서울', temp: 22, status: '흐림' },
  { id: 'city_05', name: '제주', temp: 30, status: '맑음' },
])

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
 * 4. 자식 컴포넌트가 emit 한 이벤트를 받아 상태를 변경하는 핸들러
 *    상태를 바꾸는 주체는 항상 부모다. (단방향 데이터 흐름)
 * ------------------------------------------------------------------ */

// SearchBar → update-query
const handleUpdateQuery = (value) => {
  searchQuery.value = value
}

// WeatherCard → select-card
const handleSelectCard = (city) => {
  selectedCityInfo.value = city
}

// WeatherCard → click-detail
const handleClickDetail = (city) => {
  window.alert(`${city.name}의 현재 날씨는 [${city.status}] 상태입니다.`)
}
</script>

<template>
  <div class="page">
    <div class="board">
      <header class="head">
        <div class="brand">SKALA</div>
        <h1 class="title">날씨 현황</h1>
        <p class="sub">과제 3 · Component 분리</p>
      </header>

      <!--
        BaseDashboardCard 는 패널 디자인만 담당하고 내용은 <slot> 으로 주입받는다.
        slot 으로 넘기는 내용은 "부모(WeatherParent)의 스코프에서 컴파일"되므로
        SearchBar 와 직접 props/emits 바인딩이 가능하다.
      -->
      <BaseDashboardCard title="도시 검색">
        <SearchBar :query="searchQuery" @update-query="handleUpdateQuery" />

        <!-- slot 내부이지만 부모 스코프이므로 hotOnly 와 v-model 직접 연결 가능 -->
        <label class="toggle">
          <input type="checkbox" v-model="hotOnly" />
          25도 이상만 보기
        </label>
      </BaseDashboardCard>

      <BaseDashboardCard title="지역별 날씨 현황" :meta="listMeta">
        <!-- 검색 결과가 있을 때 (검색어가 비면 원본 전체가 표시된다) -->
        <template v-if="filteredWeatherList.length > 0">
          <WeatherCard
            v-for="city in filteredWeatherList"
            :key="city.id"
            :city="city"
            @select-card="handleSelectCard"
            @click-detail="handleClickDetail"
          />
        </template>

        <!-- 검색 결과가 없을 때 -->
        <p v-else class="empty">검색 결과와 일치하는 도시가 없습니다.</p>
      </BaseDashboardCard>

      <StatusBar :message="statusMessage" />
    </div>
  </div>
</template>

<style scoped>
/* ------------------------------------------------------------------
 * CSS 변수는 .page 에 한 번만 선언한다.
 * scoped 스타일은 컴포넌트 밖으로 나가지 않지만, CSS 사용자 정의 속성은
 * DOM 상속을 따르므로 자식 컴포넌트 내부에서도 var(--red) 등을 그대로 쓸 수 있다.
 * ------------------------------------------------------------------ */
.page {
  --bg: #0b0a0c;
  --card: #17151a;
  --card-2: #1e1b21;
  --line: #2c272f;
  --line-2: #3a343e;
  --text: #f2eef0;
  --muted: #948d97;
  --red: #ff3b2f;
  --red-deep: #c8140c;
  --orange: #ff8a3d;
  --teal: #4fd1a5;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--bg);
  background-image:
    radial-gradient(58% 42% at 12% -6%, rgba(255, 59, 47, 0.2), transparent 62%),
    radial-gradient(50% 38% at 96% 8%, rgba(255, 138, 61, 0.13), transparent 60%),
    radial-gradient(70% 55% at 50% 108%, rgba(200, 20, 12, 0.16), transparent 66%);
  color: var(--text);
  font-family:
    -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR',
    sans-serif;
  line-height: 1.6;
}

.board {
  width: 100%;
  max-width: 460px;
}

/* ── 헤더 ── */
.head {
  text-align: center;
  margin-bottom: 28px;
}

.brand {
  display: inline-block;
  padding: 7px 20px 8px;
  margin-bottom: 18px;
  border: 1.5px solid var(--red);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(255, 59, 47, 0.1), rgba(200, 20, 12, 0.03));
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 2.5px;
  color: #fff;
  text-shadow: 0 0 14px rgba(255, 59, 47, 0.55);
  box-shadow:
    0 0 0 1px rgba(255, 59, 47, 0.18),
    0 0 22px rgba(255, 59, 47, 0.3),
    inset 0 0 18px rgba(255, 59, 47, 0.14);
}

.title {
  margin: 0 0 6px;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.8px;
  background: linear-gradient(92deg, #ffffff 12%, #ffb9a8 62%, var(--red) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

/* ------------------------------------------------------------------
 * 아래 두 클래스는 slot 으로 넘기는 요소에 적용된다.
 * slot 내용은 부모 스코프에서 컴파일되므로 부모의 scoped 스타일이 적용된다.
 * ------------------------------------------------------------------ */
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

<!-- 스캐폴딩 기본 스타일(#app 여백·그리드)이 화면을 좁히지 않도록 초기화 -->
<style>
body {
  margin: 0;
  background: #0b0a0c;
}
#app {
  max-width: none;
  padding: 0;
  margin: 0;
  display: block;
}
</style>
