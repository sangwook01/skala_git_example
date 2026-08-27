<script setup>
/* ==================================================================
 * WeatherAboutView.vue — 서비스 소개용 정적 페이지
 *
 * 반응형 상태 없이 내용만 렌더링하며,
 * 대시보드로 돌아가는 이동은 <RouterLink> 로 처리한다.
 * ================================================================== */
import { RouterLink } from 'vue-router'
import BaseDashboardCard from '@/components_ver4/exercise_ver4/BaseDashboardCard.vue'
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">서비스 소개</h1>
      <p class="view-sub">SKALA Vue.js 교육과정 실습 프로젝트</p>
    </div>

    <BaseDashboardCard title="무엇을 하는 서비스인가">
      <p class="text">
        지역별 날씨 정보를 카드 형태로 보여주는 대시보드입니다. 도시 이름으로 검색하고, 기온
        조건으로 걸러 보고, 각 도시의 상세 관측 정보를 확인할 수 있습니다.
      </p>
      <p class="text">
        실제 기상 API 대신 학습용 Mock Data를 사용하며, Vue 3의 문법을 단계적으로 적용해 나가는 것이
        목적입니다.
      </p>
    </BaseDashboardCard>

    <BaseDashboardCard title="단계별 실습 내용">
      <ul class="steps">
        <li>
          <span class="tag">ver1</span>
          <span>v-for, v-if, 이벤트 수식어 등 템플릿 기본 문법</span>
        </li>
        <li>
          <span class="tag">ver2</span>
          <span>ref, computed, watch, watchEffect 반응형 상태 관리</span>
        </li>
        <li>
          <span class="tag">ver3</span>
          <span>props, emits, slot을 이용한 Component 분리</span>
        </li>
        <li>
          <span class="tag tag--now">ver4</span>
          <span>Vue Router를 이용한 페이지 라우팅</span>
        </li>
      </ul>
    </BaseDashboardCard>

    <RouterLink to="/" class="home-link">← 메인 대시보드로 돌아가기</RouterLink>
  </div>
</template>

<style scoped>
.text {
  margin: 0 0 10px;
  font-size: 13.5px;
  color: #bdb4c0;
}

.text:last-child {
  margin-bottom: 0;
}

/* ── 단계 목록 ── */
.steps {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.steps li {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 13px;
  color: #bdb4c0;
}

.tag {
  flex-shrink: 0;
  padding: 2px 9px;
  border: 1px solid var(--line-2);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.tag--now {
  border-color: rgba(255, 59, 47, 0.45);
  background: rgba(255, 59, 47, 0.12);
  color: #ff7a6e;
}

/* ── 돌아가기 ── */
.home-link {
  display: block;
  padding: 13px 16px;
  border: 1px solid var(--line);
  border-left: 3px solid var(--orange);
  border-radius: 10px;
  background: linear-gradient(180deg, var(--card-2), var(--card));
  color: var(--orange);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  text-align: center;
  transition: filter 0.15s;
}

.home-link:hover {
  filter: brightness(1.2);
}
</style>
