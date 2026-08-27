import { owmClient, geoClient } from './http'

// 1. 현재 날씨
export const fetchCurrentWeather = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/weather', { params: { lat, lon } })
  return data
}

// 2. 5일/3시간 예보
export const fetchForecast = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/forecast', { params: { lat, lon } })
  return data
}

// 3. 대기오염
export const fetchAirPollution = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/air_pollution', { params: { lat, lon } })
  return data
}

// 4. 지오코딩 — 단건 (ver6에서 이어짐)
export const searchCityByName = async (name) => {
  const places = await searchPlaces(name, 1)
  return places[0] ?? null
}

/**
 * 자동완성용 — 후보를 여러 개 반환한다. (ver7 추가)
 */
export const searchPlaces = async (name, count = 6) => {
  const { data } = await geoClient.get('/search', {
    params: { name, count, language: 'ko', format: 'json' },
  })

  return (data.results ?? []).map((found) => ({
    name: found.name,
    lat: found.latitude,
    lon: found.longitude,
    country: found.country ?? '',
  }))
}

// API 응답 → ver1~ver5에서 써 온 도시 객체 형태로 변환
export const toCityItem = (raw, id) => ({
  id,
  name: raw.name,
  temp: Math.round(raw.main.temp),
  status: raw.weather[0].description,
  icon: raw.weather[0].icon,
  feelsLike: Math.round(raw.main.feels_like),
  humidity: raw.main.humidity,
  wind: raw.wind.speed,
  observedAt: new Date(raw.dt * 1000).toLocaleString('ko-KR'),
  lat: raw.coord.lat,
  lon: raw.coord.lon,
})

export const toAirGrade = (aqi) =>
  ({ 1: '좋음', 2: '보통', 3: '나쁨', 4: '매우 나쁨', 5: '위험' })[aqi] ?? '정보 없음'
