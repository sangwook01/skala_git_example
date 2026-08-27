<script setup>
/* ==================================================================
 * WeatherCard.vue — 날씨 카드 한 장
 *
 * ver6 추가분
 *  - OpenWeatherMap 이 제공하는 날씨 아이콘을 함께 표시
 *  - 나머지 구조(props / emits / 단위 변환 / 즐겨찾기)는 ver5와 동일
 *
 * API 응답을 toCityItem() 에서 기존 도시 객체 형태로 맞춰 두었기 때문에
 * 이 Component 는 데이터가 Mock 인지 실제 API 인지 알 필요가 없다.
 * ================================================================== */
import { computed } from 'vue'
import { useConfigStore } from '@/stores_ver6/configStore'
import { useFavoriteStore } from '@/stores_ver6/favoriteStore'

const props = defineProps({
  city: { type: Object, required: true },
})

const emit = defineEmits(['select-card', 'click-detail'])

const configStore = useConfigStore()
const favoriteStore = useFavoriteStore()

// 단위 설정에 맞춰 표시할 기온을 계산한다
const displayTemp = computed(() => {
  const rawTemp = props.city.temp // API 에서 units=metric 으로 받은 섭씨 숫자
  if (configStore.unit === 'fahrenheit') {
    return Math.round((rawTemp * 9) / 5 + 32)
  }
  return rawTemp
})

// OpenWeatherMap 아이콘 주소
const iconUrl = computed(() =>
  props.city.icon ? `https://openweathermap.org/img/wn/${props.city.icon}@2x.png` : '',
)
</script>

<template>
  <div class="card" @click="emit('select-card', city)">
    <div class="card-head">
      <div class="info">
        <img v-if="iconUrl" class="icon" :src="iconUrl" :alt="city.status" />

        <div>
          <p class="city">
            {{ city.name }} <span class="status">({{ city.status }})</span>
          </p>
          <p class="temp">현재 기온: {{ displayTemp }}{{ configStore.unitSymbol }}</p>
        </div>
      </div>

      <div class="card-actions">
        <button
          class="star"
          :class="{ 'star--on': favoriteStore.isFavorite(city.id) }"
          @click.stop="favoriteStore.toggleFavorite(city.id)"
        >
          {{ favoriteStore.isFavorite(city.id) ? '★' : '☆' }}
        </button>

        <!-- .stop 으로 부모 카드의 click 이벤트 전파 차단 -->
        <button class="btn" @click.stop="emit('click-detail', city)">상세보기</button>
      </div>
    </div>

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

.info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  margin: -6px 0;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
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
  font-variant-numeric: tabular-nums;
}

/* ── 즐겨찾기 ── */
.star {
  padding: 4px 7px;
  border: 1px solid var(--line-2);
  border-radius: 7px;
  background: transparent;
  color: var(--muted);
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition:
    color 0.15s,
    border-color 0.15s;
}

.star:hover,
.star--on {
  border-color: rgba(255, 138, 61, 0.6);
  color: var(--orange);
}

.btn {
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
