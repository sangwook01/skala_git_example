<script setup>
/* ==================================================================
 * StateNotice.vue — n-skeleton / n-alert 로 교체한 상태 표시
 *
 * ver6에서는 스피너 하나로 로딩을 표현했지만,
 * 실제로 채워질 카드와 같은 모양의 뼈대를 보여주면
 * 화면이 갑자기 바뀌는 느낌이 줄어든다.
 * ================================================================== */
import { NSkeleton, NAlert, NButton, NEmpty } from 'naive-ui'

defineProps({
  // 'loading' | 'error' | 'empty'
  type: { type: String, default: 'empty' },
  message: { type: String, default: '' },
  // 로딩 시 보여줄 뼈대 개수
  count: { type: Number, default: 3 },
})

defineEmits(['retry'])
</script>

<template>
  <!-- 로딩 : 카드 모양 뼈대 -->
  <div v-if="type === 'loading'" class="skeletons">
    <div v-for="n in count" :key="n" class="skeleton-card">
      <NSkeleton height="16px" width="45%" :sharp="false" />
      <NSkeleton height="13px" width="60%" :sharp="false" style="margin-top: 8px" />
      <NSkeleton height="22px" width="35%" :sharp="false" style="margin-top: 12px" round />
    </div>
  </div>

  <!-- 에러 -->
  <NAlert v-else-if="type === 'error'" type="error" :bordered="true" :show-icon="true">
    {{ message }}
    <template #header>통신 오류</template>
    <div class="alert-action">
      <NButton size="tiny" type="error" ghost @click="$emit('retry')">다시 시도</NButton>
    </div>
  </NAlert>

  <!-- 결과 없음 -->
  <NEmpty v-else :description="message" size="small" class="empty" />
</template>

<style scoped>
.skeletons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-card {
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #131117;
}

.alert-action {
  margin-top: 10px;
}

.empty {
  padding: 24px 0;
}
</style>
