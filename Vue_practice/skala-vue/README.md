# skala-vue

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

### 2026.08.24 실습 내용 (Code Challenge)

- **Vue 3 SFC 기본 구조 파악 (`HelloWorld.vue`)**
  - `<script setup>`, `<template>`, `<style scoped>` 기본 문법 및 컴포넌트 prop(`defineProps`) 전달 방식 실습

- **반응형 상태(Reactivity) 테스트 (`SampleOne.vue`)**
  - 일반 JS 변수와 Vue `ref()` 변수의 화면 렌더링 동작 차이 확인
  - 반응형 상태 변경 시 템플릿 리렌더링 흐름 확인
  
- **보간법(Text Interpolation) 및 표현식 활용 (`SampleTwo.vue`)**
  - `{{ }}` 내부에서 메서드 호출(`toUpperCase()`) 및 JavaScript 연산식(`Math.random()`) 직접 처리 실습

