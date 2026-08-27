import axios from 'axios'

const OWM_API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY

export const owmClient = axios.create({
  baseURL: 'https://api.openweathermap.org/data/2.5',
  timeout: 8000,
})

// Request Interceptor — 모든 요청에 API Key·단위·언어 자동 주입
owmClient.interceptors.request.use((config) => {
  config.params = { ...config.params, appid: OWM_API_KEY, units: 'metric', lang: 'kr' }
  console.log(`📡 [요청] ${config.baseURL}${config.url}`, config.params)
  return config
})

// Response Interceptor — 상태 코드별 에러 메시지를 한 곳에서 가공
owmClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    let message = '날씨 정보를 불러오지 못했습니다.'

    if (!error.response) message = '네트워크에 연결할 수 없습니다. 인터넷 상태를 확인하세요.'
    else if (status === 401) message = 'API Key가 올바르지 않거나 아직 활성화되지 않았습니다.'
    else if (status === 404) message = '요청한 지역을 찾을 수 없습니다.'
    else if (status === 429) message = '무료 요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.'

    console.error(`❌ [응답 오류] ${status ?? '네트워크'} — ${message}`)
    return Promise.reject(new Error(message))
  },
)

// Open-Meteo Geocoding — API Key 불필요 (기타 외부 API)
export const geoClient = axios.create({
  baseURL: 'https://geocoding-api.open-meteo.com/v1',
  timeout: 8000,
})

geoClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('❌ [지오코딩 오류]', error.message)
    return Promise.reject(new Error('도시 좌표를 찾지 못했습니다.'))
  },
)
