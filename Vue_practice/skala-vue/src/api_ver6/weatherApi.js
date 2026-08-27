import { owmClient, geoClient } from './http'

// 1. 현재 날씨 (요구사항 1)
export const fetchCurrentWeather = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/weather', { params: { lat, lon } })
  return data
}

// 2. 5일/3시간 예보 (요구사항 2)
export const fetchForecast = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/forecast', { params: { lat, lon } })
  return data
}

// 3. 대기오염 (요구사항 2)
export const fetchAirPollution = async ({ lat, lon }) => {
  const { data } = await owmClient.get('/air_pollution', { params: { lat, lon } })
  return data
}

// 4. 도시 이름 → 좌표 (요구사항 3 — 외부 API)
export const searchCityByName = async (name) => {
  const { data } = await geoClient.get('/search', {
    params: { name, count: 1, language: 'ko', format: 'json' },
  })
  const found = data.results?.[0]
  if (!found) return null
  return {
    name: found.name,
    lat: found.latitude,
    lon: found.longitude,
    country: found.country ?? '',
  }
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
