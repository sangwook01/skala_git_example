// 지역별 날씨 목록 (ver1~ver3과 동일한 데이터)
export const weatherList = [
  { id: 'city_01', name: '구미', temp: 28, status: '맑음' },
  { id: 'city_02', name: '대구', temp: 24, status: '비' },
  { id: 'city_03', name: '부산', temp: 26, status: '구름' },
  { id: 'city_04', name: '서울', temp: 22, status: '흐림' },
  { id: 'city_05', name: '제주', temp: 30, status: '맑음' },
]

// 도시 코드(cityId)에 해당하는 상세 기상관측 정보
export const weatherDetailMap = {
  city_01: {
    feelsLike: 30,
    humidity: 45,
    wind: 2.3,
    rainChance: 10,
    dust: '보통',
    observedAt: '2026-08-26 09:00',
    comment: '낮 동안 구름 없이 맑겠습니다. 자외선 지수가 높으니 주의하세요.',
  },
  city_02: {
    feelsLike: 26,
    humidity: 82,
    wind: 3.1,
    rainChance: 80,
    dust: '좋음',
    observedAt: '2026-08-26 09:00',
    comment: '오후까지 비가 이어지겠습니다. 우산을 챙기세요.',
  },
  city_03: {
    feelsLike: 28,
    humidity: 68,
    wind: 4.5,
    rainChance: 30,
    dust: '보통',
    observedAt: '2026-08-26 09:00',
    comment: '구름이 많고 해안가는 바람이 다소 강하겠습니다.',
  },
  city_04: {
    feelsLike: 23,
    humidity: 71,
    wind: 1.8,
    rainChance: 40,
    dust: '나쁨',
    observedAt: '2026-08-26 09:00',
    comment: '하늘이 흐리고 미세먼지 농도가 높습니다. 실외 활동을 줄이세요.',
  },
  city_05: {
    feelsLike: 33,
    humidity: 58,
    wind: 5.2,
    rainChance: 5,
    dust: '좋음',
    observedAt: '2026-08-26 09:00',
    comment: '맑고 무덥습니다. 수분을 충분히 섭취하세요.',
  },
}

/** cityId 로 도시 기본 정보를 찾는다. 없으면 null */
export const findCityById = (cityId) => weatherList.find((city) => city.id === cityId) ?? null

/** cityId 로 상세 관측 정보를 찾는다. 없으면 null */
export const findDetailById = (cityId) => weatherDetailMap[cityId] ?? null
