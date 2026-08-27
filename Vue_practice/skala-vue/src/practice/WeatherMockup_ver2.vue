<script setup>
import { ref, computed, watch, watchEffect } from 'vue'

/* 1. 반응형 상태 관리 (ref) */

// 지역별 날씨 데이터 (1일차와 동일)
const weatherList = ref([
  { id: 'city_01', name: '구미', temp: 28, status: '맑음' },
  { id: 'city_02', name: '대구', temp: 24, status: '비' },
  { id: 'city_03', name: '부산', temp: 26, status: '구름' },
  { id: 'city_04', name: '서울', temp: 22, status: '흐림' },
  { id: 'city_05', name: '제주', temp: 30, status: '맑음' },
])

// 검색어
const searchQuery = ref('')

// 선택된 도시 (카드 클릭 시 해당 도시 객체가 담긴다)
const selectedCityInfo = ref(null)

// 한글(IME) 조합 여부 — ver1
const isComposing = ref(false)

/* 5. 추가 상태 - 25도 이상인 도시만 보기 */
const hotOnly = ref(false)

/* 2. Computed — 검색어로 필터링한 목록 */

const filteredWeatherList = computed(() => {
  let list = weatherList.value

  /* 5. 추가 조건 - 더운 도시만 보기 */
  if (hotOnly.value) {
    list = list.filter((city) => city.temp >= 25)
  }

  // 검색어가 비어 있으면 원본 데이터를 그대로 반환한다
  const keyword = searchQuery.value.trim()
  if (keyword === '') return list

  return list.filter((city) => city.name.includes(keyword))
})

// 상태바에 표시할 문구
const statusMessage = computed(() =>
  selectedCityInfo.value
    ? `"${selectedCityInfo.value.name}"이 선택되었습니다.`
    : '카드를 클릭하거나 도시를 검색해 보세요.',
)

/* 5. 추가 Computed : 현재 화면에 보이는 도시들의 평균 기온 */
const averageTemp = computed(() => {
  const list = filteredWeatherList.value
  if (list.length === 0) return 0
  const sum = list.reduce((acc, city) => acc + city.temp, 0)
  return Math.round((sum / list.length) * 10) / 10
})

/* 3. 반응형 변수 변화 감시 (watch / watchEffect) */

// (1) watch — 선택된 도시가 바뀔 때마다 이전 값과 새 값을 함께 기록
watch(selectedCityInfo, (newCity, oldCity) => {
  const before = oldCity ? oldCity.name : '없음'
  const after = newCity ? newCity.name : '없음'
  console.log(`👁 [watch 감지] 상태 바 문구가 업데이트되었습니다. ${before} → ${after}`)
  console.log(`   └ 현재 문구: ${statusMessage.value}`)
})

// (2) watchEffect — 콜백 안에서 읽은 searchQuery 를 자동 추적
//     감시 대상을 따로 명시하지 않아도 되고, 최초 1회 즉시 실행
watchEffect(() => {
  console.log(
    `⚡ [watchEffect 자동 호출] 현재 검색어 '${searchQuery.value}'에 해당하는 데이터를 필터링합니다.`,
  )
})

// (3) 5. 추가 Watcher - 검색 결과 건수가 바뀔 때만 기록
watch(
  () => filteredWeatherList.value.length,
  (newCount, oldCount) => {
    console.log(`📊 [watch 감지] 검색 결과 ${oldCount}건 → ${newCount}건`)
  },
)

/* 4. 이벤트 핸들러 */

const handleInput = (event) => {
  if (isComposing.value) return // 한글 조합 중에는 갱신하지 않음
  searchQuery.value = event.target.value
}

const handleCompositionEnd = (event) => {
  isComposing.value = false
  searchQuery.value = event.target.value
}

const selectCity = (city) => {
  selectedCityInfo.value = city
}

const showDetail = (cityName, status) => {
  window.alert(`${cityName}의 현재 날씨는 [${status}] 상태입니다.`)
}
</script>

<template>
  <div class="page">
    <div class="board">
      <header class="head">
        <div class="brand">SKALA</div>
        <h1 class="title">날씨 현황</h1>
        <p class="sub">과제 2 · Composition API</p>
      </header>

      <!-- 도시 검색 -->
      <section class="panel">
        <h2 class="panel-title">도시 검색</h2>
        <input
          class="input"
          type="text"
          placeholder="검색할 도시 이름 입력"
          :value="searchQuery"
          @input="handleInput"
          @compositionstart="isComposing = true"
          @compositionend="handleCompositionEnd"
        />
        <p class="echo">
          검색 중인 도시: <b>{{ searchQuery }}</b>
        </p>

        <!-- 5. 추가 상태 - 더운 도시만 보기 -->
        <label class="toggle">
          <input type="checkbox" v-model="hotOnly" />
          25도 이상만 보기
        </label>
      </section>

      <!-- 지역별 날씨 현황 -->
      <section class="panel">
        <div class="panel-head">
          <h2 class="panel-title">지역별 날씨 현황</h2>
          <span class="meta"> {{ filteredWeatherList.length }}건 · 평균 {{ averageTemp }}°C </span>
        </div>

        <!-- 4. 검색 결과 표시 - 일치하는 데이터가 있을 때 -->
        <template v-if="filteredWeatherList.length > 0">
          <div
            v-for="city in filteredWeatherList"
            :key="city.id"
            class="card"
            @click="selectCity(city)"
          >
            <div class="card-head">
              <div>
                <p class="city">
                  {{ city.name }} <span class="status">({{ city.status }})</span>
                </p>
                <p class="temp">현재 기온: {{ city.temp }}°C</p>
              </div>

              <button class="btn" @click.stop="showDetail(city.name, city.status)">상세보기</button>
            </div>

            <span v-if="city.temp >= 25" class="badge badge--hot">🔥 더움 (25도 이상)</span>
            <span v-else class="badge badge--cool">❄️ 선선함 (25도 미만)</span>
          </div>
        </template>

        <!-- 4. 검색 결과 표시 - 일치하는 데이터가 없을 때 -->
        <p v-else class="empty">검색 결과와 일치하는 도시가 없습니다.</p>
      </section>

      <!-- 상태바 -->
      <p class="status-bar">{{ statusMessage }}</p>
    </div>
  </div>
</template>

<style scoped>
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

/* ── 패널 ── */
.panel {
  margin-bottom: 16px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.panel-title {
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  color: var(--muted);
  text-transform: uppercase;
}

.meta {
  font-size: 11.5px;
  color: var(--orange);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* ── 검색 ── */
.input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--line-2);
  border-radius: 8px;
  background: #131117;
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.input::placeholder {
  color: #6b636f;
}

.input:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px rgba(255, 59, 47, 0.14);
}

.echo {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--muted);
}

.echo b {
  color: var(--orange);
}

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

/* ── 날씨 카드 ── */
.card {
  padding: 14px 16px;
  margin-bottom: 10px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #131117;
  cursor: pointer;
  transition:
    border-color 0.15s,
    background 0.15s;
}

.card:last-child {
  margin-bottom: 0;
}

.card:hover {
  border-color: rgba(255, 59, 47, 0.42);
  background: #171319;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.city {
  margin: 0 0 3px;
  font-size: 15px;
  font-weight: 700;
}

.status {
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
}

.temp {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

.btn {
  flex-shrink: 0;
  padding: 7px 14px;
  border: 0;
  border-radius: 7px;
  background: linear-gradient(180deg, #ff4b3c, var(--red-deep));
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  box-shadow:
    0 0 14px rgba(255, 59, 47, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  transition: filter 0.15s;
}

.btn:hover {
  filter: brightness(1.14);
}

/* ── 조건부 라벨 ── */
.badge {
  display: inline-block;
  margin-top: 12px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}

.badge--hot {
  border: 1px solid rgba(255, 59, 47, 0.45);
  background: rgba(255, 59, 47, 0.12);
  color: #ff7a6e;
}

.badge--cool {
  border: 1px solid rgba(79, 209, 165, 0.38);
  background: rgba(79, 209, 165, 0.1);
  color: var(--teal);
}

/* ── 검색 결과 없음 ── */
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

/* ── 상태바 ── */
.status-bar {
  margin: 0;
  padding: 14px 18px;
  border: 1px solid var(--line);
  border-left: 3px solid var(--orange);
  border-radius: 10px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
  font-size: 13px;
  color: #bdb4c0;
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
