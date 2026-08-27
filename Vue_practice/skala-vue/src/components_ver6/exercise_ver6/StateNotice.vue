<script setup>
/* ==================================================================
 * StateNotice.vue — 로딩 / 에러 / 비어 있음 상태를 표시하는 공용 Component
 *
 * ver6부터는 통신이 들어오면서 "데이터가 아직 없는 상태"가 생긴다.
 * 화면마다 같은 안내를 반복하지 않도록 표시 전용 Component 로 분리했다.
 * ================================================================== */
defineProps({
  // 'loading' | 'error' | 'empty'
  type: { type: String, default: 'empty' },
  message: { type: String, default: '' },
})

defineEmits(['retry'])
</script>

<template>
  <div class="notice" :class="`notice--${type}`">
    <p class="icon">
      <span v-if="type === 'loading'" class="spinner"></span>
      <span v-else-if="type === 'error'">⚠️</span>
      <span v-else>🔍</span>
    </p>

    <p class="text">{{ message }}</p>

    <button v-if="type === 'error'" class="retry" @click="$emit('retry')">다시 시도</button>
  </div>
</template>

<style scoped>
.notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 32px 16px;
  border: 1px dashed var(--line-2);
  border-radius: 10px;
  background: #131117;
  text-align: center;
}

.notice--error {
  border-style: solid;
  border-color: rgba(255, 59, 47, 0.4);
  background: rgba(255, 59, 47, 0.06);
}

.icon {
  margin: 0;
  font-size: 20px;
  line-height: 1;
}

.text {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

.notice--error .text {
  color: #ff9b91;
}

/* 로딩 스피너 */
.spinner {
  display: block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--line-2);
  border-top-color: var(--red);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation-duration: 2s;
  }
}

.retry {
  padding: 7px 16px;
  border: 1px solid rgba(255, 59, 47, 0.45);
  border-radius: 7px;
  background: transparent;
  color: var(--red);
  font-size: 12px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
}

.retry:hover {
  background: rgba(255, 59, 47, 0.12);
}
</style>
