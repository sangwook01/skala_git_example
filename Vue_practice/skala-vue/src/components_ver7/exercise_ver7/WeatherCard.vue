<script setup>
/* ==================================================================
 * WeatherCard.vue — n-tag / n-button 을 적용한 날씨 카드
 *
 * ver6의 직접 만든 배지와 버튼을 Naive UI 컴포넌트로 교체했다.
 * props / emits 구조와 단위 변환 로직은 ver5~ver6과 동일하다.
 * ================================================================== */
import { computed } from 'vue'
import { NTag, NButton, NIcon } from 'naive-ui'

import { useConfigStore } from '@/stores_ver7/configStore'
import { useFavoriteStore } from '@/stores_ver7/favoriteStore'

const props = defineProps({
  city: { type: Object, required: true },
})

const emit = defineEmits(['select-card', 'click-detail'])

const configStore = useConfigStore()
const favoriteStore = useFavoriteStore()

const displayTemp = computed(() => {
  const rawTemp = props.city.temp // API 에서 units=metric 으로 받은 섭씨 숫자
  if (configStore.unit === 'fahrenheit') {
    return Math.round((rawTemp * 9) / 5 + 32)
  }
  return rawTemp
})

const iconUrl = computed(() =>
  props.city.icon ? `https://openweathermap.org/img/wn/${props.city.icon}@2x.png` : '',
)

const isHot = computed(() => props.city.temp >= 25)
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
        <NButton
          quaternary
          circle
          size="small"
          :type="favoriteStore.isFavorite(city.id) ? 'warning' : 'default'"
          @click.stop="favoriteStore.toggleFavorite(city.id)"
        >
          <NIcon>{{ favoriteStore.isFavorite(city.id) ? '★' : '☆' }}</NIcon>
        </NButton>

        <!-- .stop 으로 부모 카드의 click 이벤트 전파 차단 -->
        <NButton type="primary" size="small" @click.stop="emit('click-detail', city)">
          상세보기
        </NButton>
      </div>
    </div>

    <!-- 조건부 렌더링 : ver1부터의 v-if / v-else 구조를 그대로 유지 -->
    <NTag v-if="isHot" size="small" type="error" :bordered="true" class="badge">
      🔥 더움 (25도 이상)
    </NTag>
    <NTag v-else size="small" type="success" :bordered="true" class="badge">
      ❄️ 선선함 (25도 미만)
    </NTag>
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

.badge {
  margin-top: 12px;
}
</style>
