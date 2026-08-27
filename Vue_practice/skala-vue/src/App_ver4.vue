<script setup>
/* ==================================================================
 * App.vue — 앱의 껍데기
 *
 * 화면마다 바뀌지 않는 요소(브랜드, 내비게이션 바)만 두고,
 * 실제 페이지는 <RouterView /> 자리에서 교체된다.
 * ================================================================== */
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app">
    <!-- Navigation Bar : <a> 대신 <RouterLink> 를 사용해 새로고침 없이 이동 -->
    <header class="nav">
      <RouterLink to="/" class="brand">SKALA</RouterLink>

      <nav class="menu">
        <RouterLink to="/">대시보드</RouterLink>
        <RouterLink to="/rank">기온 순위</RouterLink>
        <RouterLink to="/about">서비스 소개</RouterLink>
      </nav>
    </header>

    <!-- 메인 콘텐츠 영역 : 현재 경로에 매칭된 컴포넌트가 여기에 렌더링된다 -->
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--bg);
  background-image:
    radial-gradient(58% 42% at 12% -6%, rgba(255, 59, 47, 0.2), transparent 62%),
    radial-gradient(50% 38% at 96% 8%, rgba(255, 138, 61, 0.13), transparent 60%),
    radial-gradient(70% 55% at 50% 108%, rgba(200, 20, 12, 0.16), transparent 66%);
  background-attachment: fixed;
}

/* ── 내비게이션 바 ── */
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  max-width: 520px;
  margin: 0 auto;
  padding: 22px 20px 18px;
}

.brand {
  padding: 6px 17px 7px;
  border: 1.5px solid var(--red);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(255, 59, 47, 0.1), rgba(200, 20, 12, 0.03));
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 2.4px;
  text-decoration: none;
  text-shadow: 0 0 14px rgba(255, 59, 47, 0.55);
  box-shadow:
    0 0 0 1px rgba(255, 59, 47, 0.18),
    0 0 22px rgba(255, 59, 47, 0.3),
    inset 0 0 18px rgba(255, 59, 47, 0.14);
}

.menu {
  display: flex;
  gap: 4px;
}

.menu a {
  padding: 6px 12px;
  border-radius: 7px;
  color: var(--muted);
  font-size: 13px;
  text-decoration: none;
  transition:
    color 0.15s,
    background 0.15s;
}

.menu a:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}

/*
  RouterLink 는 현재 경로와 일치하면 router-link-active 클래스를 자동으로 붙여준다.
  exact-active 는 경로가 완전히 일치할 때만 붙는다.
*/
.menu a.router-link-exact-active {
  color: var(--red);
  background: rgba(255, 59, 47, 0.1);
  font-weight: 700;
}

.main {
  padding-bottom: 60px;
}
</style>

<style>
/* ------------------------------------------------------------------
 * 전역 스타일 — 모든 View 가 공유한다.
 * CSS 변수를 :root 에 선언하면 어떤 컴포넌트에서도 var() 로 사용 가능하다.
 * ------------------------------------------------------------------ */
:root {
  --bg: #0b0a0c;
  --card: #17151a;
  --card-2: #1e1b21;
  --line: #2c272f;
  --line-2: #3a343e;
  --text: #f2eef0;
  --muted: #948d97;
  --red: #ff3b2f;
  --red-deep: #c8140c;
  --orange: #ff8a3d;
  --teal: #4fd1a5;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family:
    -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR',
    sans-serif;
  line-height: 1.6;
}

/* 스캐폴딩 기본 스타일(#app 여백·그리드) 초기화 */
#app {
  max-width: none;
  padding: 0;
  margin: 0;
  display: block;
}

/* 모든 View 가 사용하는 페이지 컨테이너 */
.view {
  width: 100%;
  max-width: 460px;
  margin: 0 auto;
  padding: 8px 20px 0;
}

.view-head {
  margin-bottom: 22px;
}

.view-title {
  margin: 0 0 6px;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.6px;
  background: linear-gradient(92deg, #ffffff 12%, #ffb9a8 62%, var(--red) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.view-sub {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}
</style>
