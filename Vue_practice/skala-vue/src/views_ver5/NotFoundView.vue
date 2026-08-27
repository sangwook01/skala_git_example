<script setup>
/* ==================================================================
 * NotFoundView.vue — 정의되지 않은 경로 접근 시 (Catch-all Route)
 *
 * Catch-all 이 없으면 매칭되는 컴포넌트를 찾지 못해
 * <RouterView /> 영역이 비어 화면이 하얗게 보인다.
 * ================================================================== */
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="view">
    <div class="notfound">
      <p class="code">404</p>
      <h1 class="view-title">페이지를 찾을 수 없습니다</h1>
      <p class="view-sub">
        요청하신 경로 <code>{{ route.fullPath }}</code> 는 등록되지 않았습니다.
      </p>

      <button class="primary" @click="goHome">대시보드로 돌아가기</button>
    </div>
  </div>
</template>

<style scoped>
.notfound {
  margin-top: 40px;
  padding: 44px 24px;
  border: 1px dashed var(--line-2);
  border-radius: 14px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
  text-align: center;
}

.code {
  margin: 0 0 10px;
  font-size: 46px;
  font-weight: 800;
  letter-spacing: 2px;
  color: var(--red);
  text-shadow: 0 0 24px rgba(255, 59, 47, 0.45);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.view-sub {
  margin-bottom: 22px;
}

code {
  padding: 1px 6px;
  border-radius: 4px;
  background: #131117;
  border: 1px solid var(--line);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  color: var(--orange);
  word-break: break-all;
}

.primary {
  padding: 12px 26px;
  border: 0;
  border-radius: 9px;
  background: linear-gradient(180deg, #ff4b3c, var(--red-deep));
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  box-shadow:
    0 0 14px rgba(255, 59, 47, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  transition: filter 0.15s;
}

.primary:hover {
  filter: brightness(1.14);
}
</style>
