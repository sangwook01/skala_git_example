<script setup>
/* ==================================================================
 * App_ver7.vue — 앱의 껍데기 + Naive UI 테마 주입
 *
 * n-config-provider 로 앱 전체를 감싸면 하위의 모든 Naive UI 컴포넌트가
 * 같은 테마를 사용한다. darkTheme 을 기본으로 두고 themeOverrides 로
 * SKALA 색상을 덮어써서 ver1부터의 디자인을 그대로 유지한다.
 *
 * n-message-provider 는 useMessage() 로 토스트를 띄우기 위한 전제 조건이다.
 * ================================================================== */
import { RouterLink, RouterView } from 'vue-router'
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'

import UnitToggler from '@/components_ver7/exercise_ver7/UnitToggler.vue'
import { themeOverrides } from '@/theme_ver7/naiveTheme'
</script>

<template>
  <NConfigProvider :theme="darkTheme" :theme-overrides="themeOverrides">
    <NMessageProvider :max="3" placement="top">
      <div class="app">
        <header class="nav">
          <div class="nav-left">
            <RouterLink to="/" class="brand">SKALA</RouterLink>

            <nav class="menu">
              <RouterLink to="/">대시보드</RouterLink>
              <RouterLink to="/rank">기온 순위</RouterLink>
              <RouterLink to="/about">서비스 소개</RouterLink>
            </nav>
          </div>

          <UnitToggler />
        </header>

        <main class="main">
          <RouterView />
        </main>
      </div>
    </NMessageProvider>
  </NConfigProvider>
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

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  max-width: 560px;
  margin: 0 auto;
  padding: 22px 20px 18px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
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
 * 전역 스타일 — Naive UI 가 관리하지 않는 레이아웃과 CSS 변수
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

#app {
  max-width: none;
  padding: 0;
  margin: 0;
  display: block;
}

.view {
  width: 100%;
  max-width: 500px;
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
