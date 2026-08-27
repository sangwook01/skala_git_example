import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default defineConfig([
  {
    name: 'app/files-to-lint',
    files: ['**/*.{js,mjs,jsx,vue}'],
  },

  /* 검사 제외 대상
   * 제출 대상은 ver7 이고 ver1~ver6 은 학습 이력으로 보존만 한다.
   * 실행되지 않는 옛 버전의 미사용 변수까지 잡으면 최종 코드의 경고가 묻힌다. */
  globalIgnores([
    '**/dist/**',
    '**/dist-ssr/**',
    '**/coverage/**',

    // 단계별 학습 이력 (실행 대상 아님)
    'src/practice/**',
    'src/basic/**',
    'src/components_ver4/**',
    'src/data_ver4/**',
    'src/router_ver4/**',
    'src/views_ver4/**',
    'src/App_ver4.vue',
    'src/components_ver5/**',
    'src/data_ver5/**',
    'src/router_ver5/**',
    'src/stores_ver5/**',
    'src/views_ver5/**',
    'src/App_ver5.vue',
    'src/api_ver6/**',
    'src/components_ver6/**',
    'src/router_ver6/**',
    'src/stores_ver6/**',
    'src/views_ver6/**',
    'src/App_ver6.vue',
  ]),

  {
    languageOptions: {
      globals: { ...globals.browser },
    },
  },

  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  ...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),

  /* Custom Rules — 배열은 뒤에 올수록 앞 규칙을 덮어쓰므로
   * skipFormatting 바로 앞에 배치한다 */
  {
    name: 'app/custom-rules',
    rules: {
      eqeqeq: ['error', 'always'], // == 로 인한 암묵적 형변환 차단
      'no-console': 'off', // watch 로그가 학습 목적이므로 허용
      'no-unused-vars': 'warn', // 에러가 아닌 경고로
      'vue/multi-word-component-names': 'off',
    },
  },

  skipFormatting,
])
