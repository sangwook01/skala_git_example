import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  // ── state ───────────────────────────────────────────────
  const unit = ref('celsius')

  // ── getters ─────────────────────────────────────────────
  const unitSymbol = computed(() => (unit.value === 'fahrenheit' ? '°F' : '°C'))

  const unitLabel = computed(() =>
    unit.value === 'fahrenheit' ? `화씨(${unitSymbol.value})` : `섭씨(${unitSymbol.value})`,
  )

  // ── actions ─────────────────────────────────────────────
  function toggleUnit() {
    unit.value = unit.value === 'celsius' ? 'fahrenheit' : 'celsius'
    console.log(`🌡 [configStore] 단위가 ${unit.value} 로 변경되었습니다.`)
  }

  return { unit, unitSymbol, unitLabel, toggleUnit }
})
