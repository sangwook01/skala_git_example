/* ==================================================================
 * naiveTheme.js — Naive UI 테마 오버라이드
 *
 * Naive UI 는 CSS-in-JS 방식이라 스타일시트를 덮어쓰지 않고
 * JavaScript 객체 하나로 색상 체계를 바꿀 수 있다.
 * ver1부터 사용해 온 SKALA 팔레트를 그대로 옮겨 적었다.
 * ================================================================== */

const palette = {
  bg: '#0b0a0c',
  card: '#17151a',
  card2: '#1e1b21',
  line: '#2c272f',
  line2: '#3a343e',
  text: '#f2eef0',
  muted: '#948d97',
  red: '#ff3b2f',
  redHover: '#ff4b3c',
  redDeep: '#c8140c',
  orange: '#ff8a3d',
  teal: '#4fd1a5',
}

export const themeOverrides = {
  common: {
    // 브랜드 색
    primaryColor: palette.red,
    primaryColorHover: palette.redHover,
    primaryColorPressed: palette.redDeep,
    primaryColorSuppl: palette.redHover,

    // 상태 색
    infoColor: palette.orange,
    successColor: palette.teal,
    warningColor: palette.orange,
    errorColor: palette.red,

    // 바탕과 글자
    bodyColor: palette.bg,
    cardColor: palette.card,
    modalColor: palette.card,
    popoverColor: palette.card2,
    borderColor: palette.line,
    dividerColor: palette.line,
    textColorBase: palette.text,
    textColor1: palette.text,
    textColor2: '#bdb4c0',
    textColor3: palette.muted,
    placeholderColor: '#6b636f',
    inputColor: '#131117',

    borderRadius: '8px',
    fontSize: '13px',
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif",
  },

  // 컴포넌트별 세부 조정
  Card: {
    borderColor: palette.line,
  },
  DataTable: {
    thColor: palette.card2,
    tdColor: '#131117',
    tdColorHover: '#171319',
    borderColor: palette.line,
    thTextColor: palette.muted,
  },
  Tag: {
    borderRadius: '999px',
  },
  Skeleton: {
    color: '#1c191f',
    colorEnd: '#262230',
  },
}

export { palette }
