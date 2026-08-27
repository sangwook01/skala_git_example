import { createRouter, createWebHistory } from 'vue-router'

// 첫 화면은 진입 즉시 필요하므로 정적 import
import WeatherHomeView from '@/views_ver4/WeatherHomeView.vue'

const routes = [
  {
    path: '/',
    name: 'WeatherHome',
    component: WeatherHomeView,
  },
  {
    // 동적 세그먼트(:cityId) — /weather/city_01 형태로 접근
    path: '/weather/:cityId',
    name: 'WeatherDetail',
    // Lazy Loading : 해당 경로에 처음 진입할 때 파일을 내려받는다
    component: () => import('@/views_ver4/WeatherDetailView.vue'),
  },
  {
    // 본인 추가 view — 기온 순위 페이지
    path: '/rank',
    name: 'WeatherRank',
    component: () => import('@/views_ver4/WeatherRankView.vue'),
  },
  {
    path: '/about',
    name: 'WeatherAbout',
    component: () => import('@/views_ver4/WeatherAboutView.vue'),
  },
  {
    // Catch-all Route : 위 라우트와 매칭되지 않는 모든 경로
    // 반드시 목록의 가장 마지막에 배치해야 한다
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views_ver4/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
