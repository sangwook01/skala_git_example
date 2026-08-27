<script setup>
/* ==================================================================
 * UnitToggler.vue — n-switch 로 교체한 단위 변경 UI
 *
 * ver6까지는 [단위변경] 버튼이었지만, 두 상태를 오가는 설정이므로
 * 스위치가 현재 상태를 더 직관적으로 보여준다.
 * Store 를 직접 구독하는 구조는 ver5와 동일하다.
 * ================================================================== */
import { computed } from 'vue'
import { NSwitch } from 'naive-ui'

import { useConfigStore } from '@/stores_ver7/configStore'

const configStore = useConfigStore()

// n-switch 는 boolean 을 다루므로 Store 의 문자열 상태와 연결해 준다
const isFahrenheit = computed({
  get: () => configStore.unit === 'fahrenheit',
  set: () => configStore.toggleUnit(),
})
</script>

<template>
  <div class="toggler">
    <NSwitch v-model:value="isFahrenheit" size="small">
      <template #checked>°F</template>
      <template #unchecked>°C</template>
    </NSwitch>

    <span class="label">{{ configStore.unitLabel }}</span>
  </div>
</template>

<style scoped>
.toggler {
  display: flex;
  align-items: center;
  gap: 9px;
}

.label {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
}
</style>
