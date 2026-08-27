import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useFavoriteStore = defineStore('favorite', () => {
  // ── state ───────────────────────────────────────────────
  const favoriteIds = ref([])

  // ── getters ─────────────────────────────────────────────
  const favoriteCount = computed(() => favoriteIds.value.length)

  // getter 가 함수를 반환하면 인자를 받아 판단할 수 있다 (이 경우 캐싱되지 않음)
  const isFavorite = computed(() => (cityId) => favoriteIds.value.includes(cityId))

  // ── actions ─────────────────────────────────────────────
  function toggleFavorite(cityId) {
    if (favoriteIds.value.includes(cityId)) {
      favoriteIds.value = favoriteIds.value.filter((id) => id !== cityId)
      console.log(`☆ [favoriteStore] ${cityId} 즐겨찾기 해제`)
    } else {
      favoriteIds.value.push(cityId)
      console.log(`★ [favoriteStore] ${cityId} 즐겨찾기 추가`)
    }
  }

  function clearFavorites() {
    favoriteIds.value = []
  }

  return { favoriteIds, favoriteCount, isFavorite, toggleFavorite, clearFavorites }
})
