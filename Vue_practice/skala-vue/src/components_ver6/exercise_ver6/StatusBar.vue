<script setup>
/* ==================================================================
 * StatusBar.vue — 표시 전용 컴포넌트 (ver3에서 그대로 이어짐)
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
