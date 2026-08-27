import { createRouter, createWebHistory } from 'vue-router'
import WeatherHomeView from '@/views_ver6/WeatherHomeView.vue'

const routes = [
  { path: '/', name: 'WeatherHome', component: WeatherHomeView },
  {
    path: '/weather/:cityId',
    name: 'WeatherDetail',
    component: () => import('@/views_ver6/WeatherDetailView.vue'),
  },
  {
    path: '/rank',
    name: 'WeatherRank',
    component: () => import('@/views_ver6/WeatherRankView.vue'),
  },
  {
    path: '/about',
    name: 'WeatherAbout',
    component: () => import('@/views_ver6/WeatherAboutView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views_ver6/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
