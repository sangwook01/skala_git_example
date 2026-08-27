<script setup>
import { ref } from 'vue'

/* 1. 배열 렌더링용 데이터 */
const weatherList = ref([
  { id: 'city_01', name: '구미', temp: 28, status: '맑음' },
  { id: 'city_02', name: '대구', temp: 24, status: '비' },
  { id: 'city_03', name: '부산', temp: 26, status: '구름' },
  { id: 'city_04', name: '서울', temp: 22, status: '흐림' },
  { id: 'city_05', name: '제주', temp: 30, status: '맑음' },
])

/* 3. 양방향 바인딩 (:value / @input) + 한글 처리 */
const searchText = ref('')
const isComposing = ref(false)

const handleInput = (event) => {
  if (isComposing.value) return // 한글 조합 중에는 갱신하지 않음
  searchText.value = event.target.value
}

const handleCompositionEnd = (event) => {
  isComposing.value = false
  searchText.value = event.target.value
}

/* 4. 이벤트 및 수식어 */
const selectedMessage = ref('')

const selectCity = (cityName) => {
  selectedMessage.value = `"${cityName}"이 선택되었습니다.`
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
      </header>

      <!-- 3. 도시 검색 -->
      <section class="panel">
        <h2 class="panel-title">도시 검색</h2>
        <input
          class="input"
          type="text"
          placeholder="검색할 도시 이름 입력"
          :value="searchText"
          @input="handleInput"
          @compositionstart="isComposing = true"
          @compositionend="handleCompositionEnd"
        />
        <p class="echo">
          검색 중인 도시: <b>{{ searchText }}</b>
        </p>
      </section>

      <!-- 1. 배열 렌더링 (v-for + :key) -->
      <section class="panel">
        <h2 class="panel-title">지역별 날씨 현황</h2>

        <div v-for="city in weatherList" :key="city.id" class="card" @click="selectCity(city.name)">
          <div class="card-head">
            <div>
              <p class="city">
                {{ city.name }} <span class="status">({{ city.status }})</span>
              </p>
              <p class="temp">현재 기온: {{ city.temp }}°C</p>
            </div>

            <!-- 4. .stop 으로 부모 카드의 click 이벤트 전파 차단 -->
            <button class="btn" @click.stop="showDetail(city.name, city.status)">상세보기</button>
          </div>

          <!-- 2. 조건부 렌더링 (v-if / v-else) -->
          <span v-if="city.temp >= 25" class="badge badge--hot">🔥 더움 (25도 이상)</span>
          <span v-else class="badge badge--cool">❄️ 선선함 (25도 미만)</span>
          <!--<span v-if="city.temp < 25" class="badge badge--cool">❄️ 선선함 (25도 미만)</span>-->
        </div>
      </section>

      <!-- 4. 상태바 -->
      <p class="status-bar">
        {{ selectedMessage || '카드를 클릭하거나 도시를 검색해 보세요.' }}
      </p>
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
  margin: 0 0 8px;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.8px;
  background: linear-gradient(92deg, #ffffff 12%, #ffb9a8 62%, var(--red) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* ── 패널 ── */
.panel {
  margin-bottom: 16px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
}

.panel-title {
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  color: var(--muted);
  text-transform: uppercase;
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
