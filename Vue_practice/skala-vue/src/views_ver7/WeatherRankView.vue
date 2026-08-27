<script setup>
/* ==================================================================
 * WeatherRankView.vue — n-data-table 로 교체한 기온 순위 페이지
 *
 * ver6까지는 직접 만든 목록이라 정렬 기준이 기온 하나로 고정이었지만,
 * n-data-table 은 컬럼 헤더 클릭 정렬과 페이징을 옵션으로 제공한다.
 * ================================================================== */
import { computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NDataTable, NTag, NStatistic, NGrid, NGi } from 'naive-ui'

import BaseDashboardCard from '@/components_ver7/exercise_ver7/BaseDashboardCard.vue'
import StateNotice from '@/components_ver7/exercise_ver7/StateNotice.vue'

import { useConfigStore } from '@/stores_ver7/configStore'
import { useWeatherStore } from '@/stores_ver7/weatherStore'

const router = useRouter()
const configStore = useConfigStore()
const weatherStore = useWeatherStore()

const toDisplayTemp = (rawTemp) =>
  configStore.unit === 'fahrenheit' ? Math.round((rawTemp * 9) / 5 + 32) : rawTemp

// 원본 배열을 정렬하면 다른 화면에도 영향을 주므로 복사본을 만든다
const rankedList = computed(() => [...weatherStore.weatherList].sort((a, b) => b.temp - a.temp))

const hottest = computed(() => rankedList.value[0] ?? null)
const coldest = computed(() => rankedList.value[rankedList.value.length - 1] ?? null)

/*
 * n-data-table 의 컬럼 정의.
 * render 에 h() 를 사용하면 셀 안에 컴포넌트를 그릴 수 있다.
 */
const columns = computed(() => [
  {
    title: '#',
    key: 'rank',
    width: 46,
    render: (_row, index) => index + 1,
  },
  {
    title: '도시',
    key: 'name',
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: '상태',
    key: 'status',
    render: (row) =>
      h(
        NTag,
        { size: 'small', type: row.temp >= 25 ? 'error' : 'success', bordered: false },
        { default: () => row.status },
      ),
  },
  {
    title: '기온',
    key: 'temp',
    align: 'right',
    defaultSortOrder: 'descend',
    sorter: (a, b) => a.temp - b.temp,
    render: (row) => `${toDisplayTemp(row.temp)}${configStore.unitSymbol}`,
  },
])

// 행을 클릭하면 상세 페이지로 이동한다
const rowProps = (row) => ({
  style: 'cursor: pointer;',
  onClick: () => router.push(`/weather/${row.id}`),
})

onMounted(() => {
  if (weatherStore.weatherList.length === 0) {
    weatherStore.loadAllWeather()
  }
})
</script>

<template>
  <div class="view">
    <div class="view-head">
      <h1 class="view-title">기온 순위</h1>
      <p class="view-sub">헤더를 클릭하면 정렬 기준을 바꿀 수 있습니다</p>
    </div>

    <BaseDashboardCard v-if="hottest && coldest" title="요약">
      <NGrid :cols="2" :x-gap="12">
        <NGi>
          <NStatistic label="가장 더운 곳">
            <span class="hot">
              {{ hottest.name }} {{ toDisplayTemp(hottest.temp) }}{{ configStore.unitSymbol }}
            </span>
          </NStatistic>
        </NGi>
        <NGi>
          <NStatistic label="가장 선선한 곳">
            <span class="cool">
              {{ coldest.name }} {{ toDisplayTemp(coldest.temp) }}{{ configStore.unitSymbol }}
            </span>
          </NStatistic>
        </NGi>
      </NGrid>
    </BaseDashboardCard>

    <BaseDashboardCard title="전체 순위" :meta="`${rankedList.length}개 도시`">
      <StateNotice v-if="weatherStore.isLoading" type="loading" :count="3" />

      <NDataTable
        v-else-if="rankedList.length > 0"
        :columns="columns"
        :data="rankedList"
        :row-key="(row) => row.id"
        :row-props="rowProps"
        :pagination="{ pageSize: 8 }"
        size="small"
      />

      <StateNotice v-else type="empty" message="표시할 도시가 없습니다." />
    </BaseDashboardCard>
  </div>
</template>

<style scoped>
.hot {
  font-size: 16px;
  font-weight: 800;
  color: #ff7a6e;
}

.cool {
  font-size: 16px;
  font-weight: 800;
  color: var(--teal);
}
</style>
