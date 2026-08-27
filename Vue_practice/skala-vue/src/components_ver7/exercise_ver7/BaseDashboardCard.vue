<script setup>
/* ==================================================================
 * BaseDashboardCard.vue — 패널 디자인 공통화 (ver3에서 그대로 이어짐)
 *
 * 내용은 갖지 않고 껍데기만 담당하며, 실제 내용은 부모가 <slot> 으로 주입한다.
 * ================================================================== */
defineProps({
  title: { type: String, required: true },
  meta: { type: String, default: '' },
})
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <h2 class="panel-title">{{ title }}</h2>
      <span v-if="meta" class="meta">{{ meta }}</span>
    </div>

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
