<script setup>
/* ==================================================================
 * StatusBar.vue — 요구사항 7에 따라 추가로 분리한 컴포넌트
 *
 * 부모의 statusMessage(computed)를 props 로 전달받아 표시만 담당한다.
 * 상태도 이벤트도 없는 순수 표시(Presentational) 컴포넌트.
 * ================================================================== */
defineProps({
  message: { type: String, default: '' },
})
</script>

<template>
  <p class="status-bar">{{ message }}</p>
</template>

<style scoped>
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
