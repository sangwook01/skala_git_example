<script setup>
/* ==================================================================
 * UnitToggler.vue — 날씨 단위 설정을 변경하는 UI
 *
 * 부모로부터 props 를 받지 않고 Store 를 직접 구독한다.
 * Navigation Bar 옆에 배치되지만 상태는 App 이 아니라 configStore 가 소유하므로,
 * 상위 컴포넌트를 거치지 않고도 대시보드·상세 화면과 같은 값을 공유한다.
 * ================================================================== */
import { useConfigStore } from '@/stores_ver6/configStore'

const configStore = useConfigStore()
</script>

<template>
  <div class="toggler">
    <span class="label">
      날씨단위: <b>{{ configStore.unitLabel }}</b>
    </span>

    <!-- action 을 직접 호출해 전역 상태를 변경한다 -->
    <button class="btn" @click="configStore.toggleUnit">단위변경</button>
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

.label b {
  color: var(--orange);
  font-weight: 700;
}

.btn {
  padding: 5px 12px;
  border: 1px solid var(--line-2);
  border-radius: 7px;
  background: #131117;
  color: var(--text);
  font-size: 12px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition:
    border-color 0.15s,
    color 0.15s;
}

.btn:hover {
  border-color: var(--red);
  color: var(--red);
}
</style>
