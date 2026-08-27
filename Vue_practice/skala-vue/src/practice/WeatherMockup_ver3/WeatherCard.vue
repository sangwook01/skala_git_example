<script setup>
/* ==================================================================
 * WeatherCard.vue — 날씨 카드 한 장
 *
 * props : 표시할 도시 객체를 부모로부터 전달받는다
 * emits : select-card  (카드 선택)
 *         click-detail (상세보기 버튼 클릭)
 *
 * 이 컴포넌트는 상태를 바꾸지 않고 "무슨 일이 일어났는지"만 부모에게 알린다.
 * ================================================================== */
defineProps({
  city: { type: Object, required: true },
})

const emit = defineEmits(['select-card', 'click-detail'])
</script>

<template>
  <div class="card" @click="emit('select-card', city)">
    <div class="card-head">
      <div>
        <p class="city">
          {{ city.name }} <span class="status">({{ city.status }})</span>
        </p>
        <p class="temp">현재 기온: {{ city.temp }}°C</p>
      </div>

      <!-- .stop 으로 부모 카드의 click 이벤트 전파 차단 -->
      <button class="btn" @click.stop="emit('click-detail', city)">상세보기</button>
    </div>

    <!-- 조건부 렌더링 (v-if / v-else) -->
    <span v-if="city.temp >= 25" class="badge badge--hot">🔥 더움 (25도 이상)</span>
    <span v-else class="badge badge--cool">❄️ 선선함 (25도 미만)</span>
  </div>
</template>

<style scoped>
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
</style>
