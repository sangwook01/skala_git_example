import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchCurrentWeather, searchCityByName, toCityItem } from '@/api_ver7/weatherApi'

const DEFAULT_CITIES = [
  { id: 'city_01', lat: 36.1195, lon: 128.3446 }, // 구미
  { id: 'city_02', lat: 35.8714, lon: 128.6014 }, // 대구
  { id: 'city_03', lat: 35.1796, lon: 129.0756 }, // 부산
  { id: 'city_04', lat: 37.5665, lon: 126.978 }, // 서울
  { id: 'city_05', lat: 33.4996, lon: 126.5312 }, // 제주
]

export const useWeatherStore = defineStore('weather', () => {
  // ── state ───────────────────────────────────────────────
  const targets = ref([...DEFAULT_CITIES])
  const weatherList = ref([])
  const isLoading = ref(false)
  const errorMessage = ref('')
  const lastUpdated = ref('')

  // ── getters ─────────────────────────────────────────────
  const cityCount = computed(() => weatherList.value.length)
  const hasError = computed(() => errorMessage.value !== '')
  const findCityById = computed(
    () => (cityId) => weatherList.value.find((city) => city.id === cityId) ?? null,
  )

  // ── actions ─────────────────────────────────────────────
  async function loadAllWeather() {
    isLoading.value = true
    errorMessage.value = ''
    try {
      // 도시마다 순차로 await 하면 통신 시간이 더해지므로 동시에 요청한다
      const responses = await Promise.all(targets.value.map((t) => fetchCurrentWeather(t)))
      weatherList.value = responses.map((raw, i) => toCityItem(raw, targets.value[i].id))
      lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
      console.log(`🌤 [weatherStore] ${weatherList.value.length}개 도시 날씨를 불러왔습니다.`)
    } catch (error) {
      errorMessage.value = error.message
    } finally {
      isLoading.value = false
    }
  }

  /** 이름으로 검색해서 추가 (ver6 방식 — 지오코딩 → 날씨) */
  async function addCityByName(name) {
    const keyword = name.trim()
    if (keyword === '') return

    isLoading.value = true
    errorMessage.value = ''
    try {
      const place = await searchCityByName(keyword)
      if (!place) {
        errorMessage.value = `'${keyword}' 에 해당하는 지역을 찾지 못했습니다.`
        return
      }

      const exists = targets.value.some(
        (t) => Math.abs(t.lat - place.lat) < 0.01 && Math.abs(t.lon - place.lon) < 0.01,
      )
      if (exists) {
        errorMessage.value = `'${place.name}' 은 이미 목록에 있습니다.`
        return
      }

      const raw = await fetchCurrentWeather({ lat: place.lat, lon: place.lon })
      const newId = `city_${String(targets.value.length + 1).padStart(2, '0')}_${Date.now()}`
      targets.value.push({ id: newId, lat: place.lat, lon: place.lon })
      weatherList.value.push(toCityItem(raw, newId))
      console.log(`➕ [weatherStore] ${place.name} 를 목록에 추가했습니다.`)
    } catch (error) {
      errorMessage.value = error.message
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 자동완성에서 고른 도시(좌표를 이미 알고 있음)를 바로 추가한다. (ver7)
   * 지오코딩 단계를 건너뛰므로 요청이 한 번 줄어든다.
   */
  async function addCityByPlace(place) {
    const exists = targets.value.some(
      (t) => Math.abs(t.lat - place.lat) < 0.01 && Math.abs(t.lon - place.lon) < 0.01,
    )
    if (exists) {
      throw new Error(`'${place.name}' 은 이미 목록에 있습니다.`)
    }

    isLoading.value = true
    try {
      const raw = await fetchCurrentWeather({ lat: place.lat, lon: place.lon })
      const newId = `city_${targets.value.length + 1}_${place.name}`
      targets.value.push({ id: newId, lat: place.lat, lon: place.lon })
      weatherList.value.push(toCityItem(raw, newId))
      return place.name
    } finally {
      isLoading.value = false
    }
  }

  function removeCity(cityId) {
    targets.value = targets.value.filter((t) => t.id !== cityId)
    weatherList.value = weatherList.value.filter((c) => c.id !== cityId)
  }

  function clearError() {
    errorMessage.value = ''
  }

  return {
    weatherList,
    isLoading,
    errorMessage,
    lastUpdated,
    cityCount,
    hasError,
    findCityById,
    loadAllWeather,
    addCityByName,
    addCityByPlace,
    removeCity,
    clearError,
  }
})
