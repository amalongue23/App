<template>
  <main class="admin-layout chief-layout">
    <SideNav />

    <section class="content-area chief-content">
      <header class="chief-topbar">
        <div class="chief-tenant">Restauro Admin</div>
        <DashboardUserMenu />
      </header>

      <h1 class="chief-title">Bem-vindo, <span>Chefe!</span></h1>
      <p class="chief-subtitle">Visão geral do Departamento de {{ dashboard.department.name || '-' }}</p>

      <section class="chief-filters">
        <div class="period-field">
          <label>Ano Académico</label>
          <select v-model="selectedAnoId" @change="onAcademicYearChange">
            <option v-for="item in filters.anos" :key="item.ano_academico_id" :value="item.ano_academico_id">
              {{ item.ano_lectivo }}
            </option>
          </select>
        </div>

        <div class="period-field">
          <label>Ano Lectivo</label>
          <input v-model="selectedAnoLectivo" type="text" readonly />
        </div>
      </section>

      <section class="kpi-grid chief-kpis">
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.students }}</div>
          <div class="kpi-title">Alunos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.courses }}</div>
          <div class="kpi-title">Cursos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.professors }}</div>
          <div class="kpi-title">Professores</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.units }}</div>
          <div class="kpi-title">Unidades Orgânicas</div>
        </article>
      </section>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <section class="chief-panels">
        <article class="panel">
          <h3>Performance Académica</h3>
          <div class="bars-grid">
            <div v-for="item in dashboard.performance" :key="`chief-bar-${item.month}`" class="bars-col">
              <div class="bar-set">
                <div class="bar approved" :style="{ height: barHeight(item.approved) }"></div>
                <div class="bar failed" :style="{ height: barHeight(item.failed) }"></div>
              </div>
              <span>{{ monthLabel(item.month) }}</span>
            </div>
          </div>
          <div class="chart-legend-inline">
            <span><i class="dot-line approved"></i>Aprovados</span>
            <span><i class="dot-line failed"></i>Reprovados</span>
          </div>
        </article>

        <article class="panel">
          <h3>Tendência de Matrículas <span class="growth">+ 5,2%</span></h3>
          <div class="chart-card">
            <svg viewBox="0 0 100 40" class="chart-svg" preserveAspectRatio="none">
              <polyline class="chart-line approved" :points="trendPoints" />
              <circle v-for="point in trendPointMarkers" :key="`trend-${point.month}`" class="chart-point approved" :cx="point.x" :cy="point.y" r="1.1" />
            </svg>
            <div class="chart-axis">
              <span v-for="item in dashboard.trends" :key="`trend-month-${item.month}`">{{ monthLabel(item.month) }}</span>
            </div>
          </div>
        </article>

        <article class="panel">
          <h3>Últimas Atividades <span class="gold-text">Ver todas</span></h3>
          <ul class="feed-list">
            <li v-for="(item, index) in dashboard.activities" :key="`act-${index}`">
              <strong>{{ item.actor }}</strong> — {{ item.message }}
            </li>
          </ul>
        </article>
      </section>

      <section class="chief-bottom">
        <article class="panel table-panel">
          <h3>Desempenho por Curso <span class="gold-text">Ver todas</span></h3>
          <table>
            <thead>
              <tr>
                <th>Curso</th>
                <th>Aprovados</th>
                <th>Reprovados</th>
                <th>Taxa Aprovação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in dashboard.courses" :key="course.course">
                <td>{{ course.course }}</td>
                <td>{{ course.approved }}</td>
                <td>{{ course.failed }}</td>
                <td class="rate-cell">
                  <div class="rate-track">
                    <div class="rate-fill" :style="{ width: `${course.approval_rate}%` }"></div>
                  </div>
                  <span class="gold-text">{{ course.approval_rate }}%</span>
                </td>
              </tr>
            </tbody>
          </table>
        </article>

        <article class="panel">
          <h3>Avisos do Departamento</h3>
          <div v-for="(notice, index) in dashboard.notices" :key="`notice-${index}`" class="notice-item">
            <p class="notice-date">{{ formatDate(notice.published_at) }}</p>
            <strong>{{ notice.title }}</strong>
            <p class="notice-text">{{ notice.content }}</p>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const filters = reactive({ anos: [] })
const selectedAnoId = ref('')
const selectedAnoLectivo = ref('')
const selectedUnitId = ref('')
const selectedDepartmentId = ref('')
const selectedCourseId = ref('')
const errorMessage = ref('')
const entities = reactive({ units: [], departments: [], courses: [] })

const dashboard = reactive({
  department: { name: '' },
  kpis: { students: 0, courses: 0, professors: 0, units: 0 },
  performance: [],
  trends: [],
  courses: [],
  activities: [],
  notices: [],
})

const filteredUnits = computed(() => entities.units)
const filteredDepartments = computed(() => {
  if (!selectedUnitId.value) return entities.departments
  return entities.departments.filter((item) => String(item.unit_id) === selectedUnitId.value)
})
const filteredCourses = computed(() => {
  if (!selectedDepartmentId.value) return entities.courses
  return entities.courses.filter((item) => String(item.department_id) === selectedDepartmentId.value)
})

const chartMax = computed(() => {
  const values = dashboard.performance.flatMap((item) => [item.approved || 0, item.failed || 0])
  return Math.max(...values, 1)
})

const approvedPoints = computed(() =>
  buildSeriesPoints(
    dashboard.performance.map((item) => item.approved || 0),
    chartMax.value,
  ),
)

const failedPoints = computed(() =>
  buildSeriesPoints(
    dashboard.performance.map((item) => item.failed || 0),
    chartMax.value,
  ),
)

const approvedPointMarkers = computed(() =>
  buildSeriesPointObjects(
    dashboard.performance.map((item) => ({ month: item.month, value: item.approved || 0 })),
    chartMax.value,
  ),
)

const failedPointMarkers = computed(() =>
  buildSeriesPointObjects(
    dashboard.performance.map((item) => ({ month: item.month, value: item.failed || 0 })),
    chartMax.value,
  ),
)

const trendPoints = computed(() =>
  buildSeriesPoints(
    dashboard.trends.map((item) => item.enrollments || 0),
    Math.max(...dashboard.trends.map((item) => item.enrollments || 0), 1),
  ),
)

const trendPointMarkers = computed(() =>
  buildSeriesPointObjects(
    dashboard.trends.map((item) => ({ month: item.month, value: item.enrollments || 0 })),
    Math.max(...dashboard.trends.map((item) => item.enrollments || 0), 1),
  ),
)

function monthLabel(month) {
  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return labels[(month || 1) - 1] || String(month)
}

function buildSeriesPoints(values, maxValue) {
  if (!values.length) return ''
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

function barHeight(value) {
  const maxValue = chartMax.value
  const pct = Math.max(0, Math.min(1, (value || 0) / maxValue))
  return `${20 + pct * 140}px`
}

function formatDate(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  return date.toLocaleDateString('pt-PT', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  filters.anos = response.data.anos || []
  entities.units = response.data.units || []
  entities.departments = response.data.departments || []
  entities.courses = response.data.courses || []
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
  if (selectedUnitId.value) params.unit_id = selectedUnitId.value
  if (selectedDepartmentId.value) params.department_id = selectedDepartmentId.value
  if (selectedCourseId.value) params.course_id = selectedCourseId.value

  const response = await api.get('/api/dashboard/chief', {
    params,
  })

  Object.assign(dashboard, response.data)
}

async function onAcademicYearChange() {
  const found = filters.anos.find((item) => item.ano_academico_id === Number(selectedAnoId.value))
  selectedAnoLectivo.value = found?.ano_lectivo || ''
  await reloadDashboard()
}

async function onUnitChange() {
  if (!selectedUnitId.value) {
    selectedDepartmentId.value = ''
    selectedCourseId.value = ''
  } else if (!filteredDepartments.value.some((item) => String(item.id) === selectedDepartmentId.value)) {
    selectedDepartmentId.value = ''
    selectedCourseId.value = ''
  }
  await reloadDashboard()
}

async function onDepartmentChange() {
  if (!selectedDepartmentId.value) {
    selectedCourseId.value = ''
  } else if (!filteredCourses.value.some((item) => String(item.id) === selectedCourseId.value)) {
    selectedCourseId.value = ''
  }
  await reloadDashboard()
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
