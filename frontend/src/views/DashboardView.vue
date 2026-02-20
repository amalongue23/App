<template>
  <main class="admin-layout rector-layout">
    <SideNav />

    <section class="content-area rector-content">
      <header class="rector-topbar">
        <div class="rector-tenant">Restauro Admin</div>
        <div class="rector-icons">
          <span class="top-icon"></span>
          <span class="top-icon"></span>
          <span class="top-icon"></span>
          <span class="rector-avatar">{{ initials }}</span>
        </div>
      </header>

      <h1 class="rector-title">Bem-vindo, <span>Reitor!</span></h1>
      <p class="rector-subtitle">Um resumo das atividades e estatísticas gerais da instituição.</p>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <section class="kpi-grid rector-kpis">
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.students }}</div>
          <div class="kpi-title">Alunos Ativos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.courses }}</div>
          <div class="kpi-title">Cursos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.departments }}</div>
          <div class="kpi-title">Departamentos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.units }}</div>
          <div class="kpi-title">Unidades Orgânicas</div>
        </article>
      </section>

      <section class="panel-grid rector-panels">
        <article class="panel wide">
          <h3>Desempenho Académico</h3>
          <div class="chart-card">
            <svg viewBox="0 0 100 40" class="chart-svg" preserveAspectRatio="none">
              <polyline class="chart-line approved" :points="approvedPoints" />
              <polyline class="chart-line failed" :points="failedPoints" />
              <circle
                v-for="point in approvedPointMarkers"
                :key="`ap-${point.month}`"
                class="chart-point approved"
                :cx="point.x"
                :cy="point.y"
                r="1.1"
              >
                <title>{{ `${monthLabel(point.month)}: ${point.value} aprovados` }}</title>
              </circle>
              <circle
                v-for="point in failedPointMarkers"
                :key="`rp-${point.month}`"
                class="chart-point failed"
                :cx="point.x"
                :cy="point.y"
                r="1.1"
              >
                <title>{{ `${monthLabel(point.month)}: ${point.value} reprovados` }}</title>
              </circle>
            </svg>
            <div class="chart-axis">
              <span v-for="item in dashboard.performance" :key="`reitor-month-${item.month}`">{{
                monthLabel(item.month)
              }}</span>
            </div>
            <div class="chart-legend-inline">
              <span><i class="dot-line approved"></i>Taxa de Aprovação</span>
              <span><i class="dot-line failed"></i>Taxa de Reprovação</span>
            </div>
          </div>
        </article>

        <article class="panel">
          <h3>Distribuição de Cursos</h3>
          <div class="donut" :style="{ background: distributionGradient }"></div>
          <ul class="legend">
            <li v-for="(item, index) in dashboard.distribution" :key="item.unit">
              <span class="dot" :style="{ background: donutColor(index) }"></span>{{ item.unit }} {{ item.percentage }}%
            </li>
          </ul>
        </article>

        <article class="panel">
          <h3>Atividades Recentes <span class="gold-text">Ver todas</span></h3>
          <ul class="feed-list">
            <li v-for="activity in dashboard.activities" :key="activity.created_at + activity.message">
              <strong>{{ activity.actor }}</strong> — {{ activity.message }}
            </li>
          </ul>
        </article>
      </section>

      <section class="bottom-grid rector-bottom">
        <article class="panel table-panel">
          <div class="panel-head">
            <h3>Resumo por Unidade Orgânica <span class="gold-text">Ver todas</span></h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Unidade Orgânica</th>
                <th>Alunos</th>
                <th>Cursos</th>
                <th>Taxa Aprovação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in dashboard.units" :key="row.unit_id">
                <td>{{ row.unit_name }}</td>
                <td>{{ row.students }}</td>
                <td>{{ row.courses }}</td>
                <td class="gold-text">{{ Math.min(99, 70 + (row.courses % 25)) }}%</td>
              </tr>
            </tbody>
          </table>
        </article>

        <article class="panel">
          <h3>Avisos e Comunicados <span class="gold-text">Ver todos</span></h3>
          <ul class="feed-list">
            <li v-for="notice in dashboard.notices" :key="notice.published_at + notice.title">
              <strong>{{ notice.title }}</strong>
              <p class="notice-text">{{ notice.content }}</p>
            </li>
          </ul>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'

import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const filters = reactive({ anos: [] })
const selectedAnoId = ref('')
const selectedAnoLectivo = ref('')
const errorMessage = ref('')

const dashboard = reactive({
  kpis: { students: 0, courses: 0, departments: 0, units: 0 },
  performance: [],
  distribution: [],
  units: [],
  activities: [],
  notices: [],
})

const initials = computed(() => {
  const name = authStore.user?.username || 'UL'
  return name.slice(0, 2).toUpperCase()
})

const chartMax = computed(() => {
  const values = dashboard.performance.flatMap((item) => [item.approved || 0, item.failed || 0])
  return Math.max(...values, 1)
})

const approvedPoints = computed(() => {
  return buildSeriesPoints(
    dashboard.performance.map((item) => item.approved || 0),
    chartMax.value,
  )
})

const failedPoints = computed(() => {
  return buildSeriesPoints(
    dashboard.performance.map((item) => item.failed || 0),
    chartMax.value,
  )
})

const approvedPointMarkers = computed(() => {
  return buildSeriesPointObjects(
    dashboard.performance.map((item) => ({ month: item.month, value: item.approved || 0 })),
    chartMax.value,
  )
})

const failedPointMarkers = computed(() => {
  return buildSeriesPointObjects(
    dashboard.performance.map((item) => ({ month: item.month, value: item.failed || 0 })),
    chartMax.value,
  )
})

const distributionGradient = computed(() => {
  if (!dashboard.distribution.length) {
    return 'conic-gradient(#d9ccb7 0 100%)'
  }

  let offset = 0
  const segments = dashboard.distribution.map((item, index) => {
    const start = offset
    const percentage = Math.max(0, Number(item.percentage) || 0)
    offset += percentage
    return `${donutColor(index)} ${start}% ${offset}%`
  })
  return `conic-gradient(${segments.join(', ')})`
})

function buildSeriesPoints(values, maxValue) {
  if (!values.length) {
    return ''
  }
  const xStep = values.length > 1 ? 100 / (values.length - 1) : 100
  return values
    .map((value, index) => {
      const x = (index * xStep).toFixed(2)
      const y = (40 - (Math.max(0, value) / maxValue) * 36).toFixed(2)
      return `${x},${y}`
    })
    .join(' ')
}

function buildSeriesPointObjects(items, maxValue) {
  if (!items.length) return []
  const xStep = items.length > 1 ? 100 / (items.length - 1) : 100
  return items.map((item, index) => ({
    month: item.month,
    value: item.value,
    x: Number((index * xStep).toFixed(2)),
    y: Number((40 - (Math.max(0, item.value) / maxValue) * 36).toFixed(2)),
  }))
}

function donutColor(index) {
  const palette = ['#c29132', '#d8b980', '#ead8b7', '#b37a1f', '#f0e2cc', '#9f6a17']
  return palette[index % palette.length]
}

function monthLabel(month) {
  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return labels[(month || 1) - 1] || String(month)
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  filters.anos = response.data.anos || []
  if (filters.anos.length > 0) {
    selectedAnoId.value = filters.anos[0].ano_academico_id
    selectedAnoLectivo.value = filters.anos[0].ano_lectivo
  }
}

async function loadDashboard() {
  if (!selectedAnoId.value || !selectedAnoLectivo.value) return
  const params = {
    ano_academico_id: selectedAnoId.value,
    ano_lectivo: selectedAnoLectivo.value,
  }

  const response = await api.get('/api/dashboard/reitor', {
    params,
  })
  Object.assign(dashboard, response.data)
}

async function reloadDashboard() {
  try {
    errorMessage.value = ''
    await loadDashboard()
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Falha ao carregar dados do dashboard.'
    } else {
      errorMessage.value = 'Falha ao carregar dados do dashboard.'
    }
  }
}

onMounted(async () => {
  try {
    errorMessage.value = ''
    await loadFilters()
    await loadDashboard()
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Falha ao carregar dados do dashboard.'
    } else {
      errorMessage.value = 'Falha ao carregar dados do dashboard.'
    }
  }
})
</script>
