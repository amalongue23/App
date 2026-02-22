<template>
  <main class="admin-layout director-layout">
    <SideNav />

    <section class="content-area director-content">
      <header class="topbar">
        <div class="director-topbar-title">Bem-vindo, <span class="welcome-highlight">Diretor!</span></div>
        <DashboardUserMenu />
      </header>

      <section class="period-filters">
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
      <section class="period-filters">
        <div class="period-field">
          <label>Unidade Orgânica</label>
          <select v-model="selectedUnitId" @change="onUnitChange">
            <option value="">Sem filtro</option>
            <option v-for="item in filteredUnits" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
        </div>
        <div class="period-field">
          <label>Departamento</label>
          <select v-model="selectedDepartmentId" @change="onDepartmentChange">
            <option value="">Sem filtro</option>
            <option v-for="item in filteredDepartments" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
        </div>
      </section>
      <section class="period-filters">
        <div class="period-field">
          <label>Curso</label>
          <select v-model="selectedCourseId" @change="reloadDashboard">
            <option value="">Sem filtro</option>
            <option v-for="item in filteredCourses" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
        </div>
      </section>

      <p class="lead">Resumo das atividades e estatísticas gerais da unidade {{ dashboard.unit.name || '-' }}.</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <section class="kpi-grid role-kpis">
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.students }}</div>
          <div class="kpi-title">Alunos Ativos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.courses }}</div>
          <div class="kpi-title">Cursos</div>
        </article>
      </section>

      <section class="panel-grid single">
        <article class="panel wide">
          <h3>Desempenho Académico</h3>
          <div class="chart-card">
            <svg viewBox="0 0 100 40" class="chart-svg" preserveAspectRatio="none">
              <polyline class="chart-line approved" :points="approvedPoints" />
              <polyline class="chart-line failed" :points="failedPoints" />
              <circle v-for="point in approvedPointMarkers" :key="`d-ap-${point.month}`" class="chart-point approved" :cx="point.x" :cy="point.y" r="1.1">
                <title>{{ `${monthLabel(point.month)}: ${point.value} aprovados` }}</title>
              </circle>
              <circle v-for="point in failedPointMarkers" :key="`d-rp-${point.month}`" class="chart-point failed" :cx="point.x" :cy="point.y" r="1.1">
                <title>{{ `${monthLabel(point.month)}: ${point.value} reprovados` }}</title>
              </circle>
            </svg>
            <div class="chart-axis">
              <span v-for="item in dashboard.performance" :key="`director-month-${item.month}`">{{ monthLabel(item.month) }}</span>
            </div>
            <div class="chart-legend-inline">
              <span><i class="dot-line approved"></i>Aprovados</span>
              <span><i class="dot-line failed"></i>Reprovados</span>
            </div>
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
  unit: { name: '' },
  kpis: { students: 0, courses: 0, professors: 0, departments: 0 },
  departments: [],
  activities: [],
  notices: [],
  performance: [],
  trends: [],
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

  const response = await api.get('/api/dashboard/director', {
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
