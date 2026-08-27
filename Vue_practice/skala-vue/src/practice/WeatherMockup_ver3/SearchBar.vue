<script setup>
/* ==================================================================
 * SearchBar.vue — 도시 검색 입력 컴포넌트
 *
 * props : 부모로부터 검색어 반응형 데이터를 전달받아 표시
 * emits : 검색어가 바뀌면 update-query 이벤트로 부모에게 전달
 *
 * 상태(searchQuery)는 부모가 소유하므로 이 컴포넌트는 값을 직접 수정하지 않는다.
 * ================================================================== */
import { ref } from 'vue'

defineProps({
  query: { type: String, default: '' },
})

const emit = defineEmits(['update-query'])

// 한글(IME) 조합 여부 — 입력 자체를 다루는 곳이므로 이 컴포넌트가 관리한다
const isComposing = ref(false)

const handleInput = (event) => {
  if (isComposing.value) return // 한글 조합 중에는 부모에게 전달하지 않음
  emit('update-query', event.target.value)
}

const handleCompositionEnd = (event) => {
  isComposing.value = false
  emit('update-query', event.target.value)
}
</script>

<template>
  <input
    class="input"
    type="text"
    placeholder="검색할 도시 이름 입력"
    :value="query"
    @input="handleInput"
    @compositionstart="isComposing = true"
    @compositionend="handleCompositionEnd"
  />

  <p class="echo">
    검색 중인 도시: <b>{{ query }}</b>
  </p>
</template>

<style scoped>
.input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--line-2);
  border-radius: 8px;
  background: #131117;
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.input::placeholder {
  color: #6b636f;
}

.input:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px rgba(255, 59, 47, 0.14);
}

.echo {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--muted);
}

.echo b {
  color: var(--orange);
}
</style>
