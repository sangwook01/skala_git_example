<script setup>
/* ==================================================================
 * SearchBar.vue — n-auto-complete 로 교체한 도시 검색
 *
 * ver6까지는 "검색 → 결과 없음 → [추가] 버튼" 2단계였지만,
 * ver7에서는 타이핑하는 동안 지오코딩 API 를 호출해
 * 후보 도시를 드롭다운으로 바로 보여준다.
 *
 * props : query        — 부모가 소유한 검색어
 * emits : update-query — 검색어 변경 요청 (목록 필터링용)
 *         select-place — 드롭다운에서 도시를 선택 (새 도시 추가용)
 * ================================================================== */
import { ref, watch, onUnmounted } from 'vue'
import { NAutoComplete, NSpin } from 'naive-ui'

import { searchPlaces } from '@/api_ver7/weatherApi'

const props = defineProps({
  query: { type: String, default: '' },
})

const emit = defineEmits(['update-query', 'select-place'])

const options = ref([])
const isSearching = ref(false)
let timer = null

/*
 * 타이핑할 때마다 API 를 호출하면 요청이 과도하게 발생하므로
 * 입력이 멈추고 400ms 가 지난 뒤에 한 번만 호출한다. (디바운스)
 */
const searchPlacesDebounced = (keyword) => {
  clearTimeout(timer)

  if (keyword.trim().length < 2) {
    options.value = []
    return
  }

  timer = setTimeout(async () => {
    isSearching.value = true
    try {
      const places = await searchPlaces(keyword)
      // n-auto-complete 는 { label, value } 형태의 배열을 받는다
      options.value = places.map((place) => ({
        label: `${place.name}${place.country ? ` · ${place.country}` : ''}`,
        value: place.name,
        place, // 선택 시 좌표를 꺼내 쓰기 위해 원본을 함께 보관
      }))
    } catch {
      options.value = []
    } finally {
      isSearching.value = false
    }
  }, 400)
}

// 부모의 검색어가 바뀔 때마다 후보를 갱신한다
watch(
  () => props.query,
  (keyword) => searchPlacesDebounced(keyword),
)

// 컴포넌트가 사라질 때 예약된 타이머를 정리한다
onUnmounted(() => clearTimeout(timer))

const handleUpdate = (value) => {
  emit('update-query', value)
}

const handleSelect = (value) => {
  const picked = options.value.find((option) => option.value === value)
  if (picked) emit('select-place', picked.place)
}
</script>

<template>
  <NAutoComplete
    :value="query"
    :options="options"
    :input-props="{ autocomplete: 'off' }"
    placeholder="도시 이름을 입력하세요 (예: 광주, Tokyo)"
    clearable
    blur-after-select
    @update:value="handleUpdate"
    @select="handleSelect"
  >
    <template #suffix>
      <NSpin v-if="isSearching" :size="12" />
    </template>
  </NAutoComplete>

  <p class="echo">
    검색 중인 도시: <b>{{ query }}</b>
  </p>
</template>

<style scoped>
.echo {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--muted);
}

.echo b {
  color: var(--orange);
}
</style>
