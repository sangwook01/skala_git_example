<script setup>
/* ==================================================================
 * BaseDashboardCard.vue — 검색박스와 리스트박스의 디자인을 공용화한 컴포넌트
 *
 * 내용은 갖지 않고 "패널 껍데기"만 담당한다.
 * 실제 내용(도시 검색 / 지역별 날씨 현황)은 부모가 <slot> 으로 주입한다.
 * ================================================================== */
defineProps({
  // 패널 제목
  title: { type: String, required: true },
  // 제목 우측에 표시할 부가 정보 (없으면 표시하지 않음)
  meta: { type: String, default: '' },
})
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <h2 class="panel-title">{{ title }}</h2>
      <span v-if="meta" class="meta">{{ meta }}</span>
    </div>

    <!-- 부모가 주입하는 내용이 들어오는 자리 -->
    <slot></slot>
  </section>
</template>

<style scoped>
.panel {
  margin-bottom: 16px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.panel-title {
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  color: var(--muted);
  text-transform: uppercase;
}

.meta {
  font-size: 11.5px;
  color: var(--orange);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
</style>
