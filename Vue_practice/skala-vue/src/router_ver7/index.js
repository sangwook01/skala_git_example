import { createRouter, createWebHistory } from 'vue-router'

import WeatherHomeView from '@/views_ver7/WeatherHomeView.vue'

const routes = [
  { path: '/', name: 'WeatherHome', component: WeatherHomeView },
  {
    path: '/weather/:cityId',
    name: 'WeatherDetail',
    component: () => import('@/views_ver7/WeatherDetailView.vue'),
  },
  {
    path: '/rank',
    name: 'WeatherRank',
    component: () => import('@/views_ver7/WeatherRankView.vue'),
  },
  {
    path: '/about',
    name: 'WeatherAbout',
    component: () => import('@/views_ver7/WeatherAboutView.vue'),
  },
  {
    // Catch-all Route : 반드시 목록의 가장 마지막에 배치
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views_ver7/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
