<template>
  <main class="admin-layout">
    <SideNav />

    <section class="content-area">
      <header class="topbar">
        <div>Estatísticas <span>{{ roleTitle }}</span></div>
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
            <option v-for="item in filteredUnits" :key="item.id" :value="String(item.id)">
              {{ item.name }}
            </option>
          </select>
        </div>

        <div class="period-field">
          <label>Departamento</label>
          <select v-model="selectedDepartmentId" @change="onDepartmentChange">
            <option value="">Sem filtro</option>
            <option v-for="item in filteredDepartments" :key="item.id" :value="String(item.id)">
              {{ item.name }}
            </option>
          </select>
        </div>
      </section>

      <section class="period-filters">
        <div class="period-field">
          <label>Curso</label>
          <select v-model="selectedCourseId" @change="reloadStatistics">
            <option value="">Sem filtro</option>
            <option v-for="item in filteredCourses" :key="item.id" :value="String(item.id)">
              {{ item.name }}
            </option>
          </select>
        </div>
      </section>

      <p class="lead">Visão estatística consolidada por período letivo.</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <section class="kpi-grid role-kpis">
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.students }}</div>
          <div class="kpi-title">Alunos</div>
        </article>
        <article class="kpi-card">
          <div class="kpi-value">{{ dashboard.kpis.courses }}</div>
          <div class="kpi-title">Cursos</div>
        </article>
      </section>

      <section class="panel-grid single">
        <article class="panel wide table-panel">
          <h3>Performance Mensal</h3>
          <table>
            <thead>
              <tr>
                <th>Mês</th>
                <th>Aprovados</th>
                <th>Reprovados</th>
                <th>Taxa Aprovação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in dashboard.performance" :key="row.month">
                <td>{{ monthLabel(row.month) }}</td>
                <td>{{ row.approved || 0 }}</td>
                <td>{{ row.failed || 0 }}</td>
                <td class="gold-text">{{ approvalRate(row) }}%</td>
              </tr>
            </tbody>
          </table>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const filters = reactive({ anos: [] })
const selectedAnoId = ref('')
const selectedAnoLectivo = ref('')
const selectedUnitId = ref('')
const selectedDepartmentId = ref('')
const selectedCourseId = ref('')
const errorMessage = ref('')
const entities = reactive({ units: [], departments: [], courses: [] })

const dashboard = reactive({
  kpis: { students: 0, courses: 0 },
  performance: [],
})

const roleTitle = computed(() => {
  if (authStore.user?.role === 'REITOR' || authStore.user?.role === 'ADMIN') return 'Institucionais'
  if (authStore.user?.role === 'DIRETOR') return 'da Unidade'
  if (authStore.user?.role === 'CHEFE') return 'do Departamento'
  return 'Gerais'
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


function monthLabel(month) {
  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return labels[(month || 1) - 1] || String(month)
}

function approvalRate(row) {
  const approved = Number(row.approved || 0)
  const failed = Number(row.failed || 0)
  const total = approved + failed
  if (!total) return 0
  return ((approved / total) * 100).toFixed(1)
}

function endpointByRole() {
  if (authStore.user?.role === 'REITOR' || authStore.user?.role === 'ADMIN') return '/api/dashboard/reitor'
  if (authStore.user?.role === 'DIRETOR') return '/api/dashboard/director'
  return '/api/dashboard/chief'
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

async function loadStatistics() {
  if (!selectedAnoId.value || !selectedAnoLectivo.value) return
  const params = {
    ano_academico_id: selectedAnoId.value,
    ano_lectivo: selectedAnoLectivo.value,
  }
  if (selectedUnitId.value) params.unit_id = selectedUnitId.value
  if (selectedDepartmentId.value) params.department_id = selectedDepartmentId.value
  if (selectedCourseId.value) params.course_id = selectedCourseId.value

  const response = await api.get(endpointByRole(), {
    params,
  })

  const payload = response.data || {}
  dashboard.kpis.students = payload.kpis?.students || 0
  dashboard.kpis.courses = payload.kpis?.courses || 0
  dashboard.performance = payload.performance || []
}

async function onAcademicYearChange() {
  const found = filters.anos.find((item) => item.ano_academico_id === Number(selectedAnoId.value))
  selectedAnoLectivo.value = found?.ano_lectivo || ''
  await reloadStatistics()
}

async function onUnitChange() {
  if (selectedUnitId.value) {
    const foundDepartment = filteredDepartments.value[0]
    if (!foundDepartment || String(foundDepartment.id) !== selectedDepartmentId.value) {
      selectedDepartmentId.value = ''
      selectedCourseId.value = ''
    }
  } else {
    selectedDepartmentId.value = ''
    selectedCourseId.value = ''
  }
  await reloadStatistics()
}

async function onDepartmentChange() {
  if (selectedDepartmentId.value) {
    const foundCourse = filteredCourses.value[0]
    if (!foundCourse || String(foundCourse.id) !== selectedCourseId.value) {
      selectedCourseId.value = ''
    }
  } else {
    selectedCourseId.value = ''
  }
  await reloadStatistics()
}

async function reloadStatistics() {
  try {
    errorMessage.value = ''
    await loadStatistics()
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Falha ao carregar estatísticas.'
    } else {
      errorMessage.value = 'Falha ao carregar estatísticas.'
    }
  }
}

onMounted(async () => {
  try {
    errorMessage.value = ''
    await loadFilters()
    await loadStatistics()
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Falha ao carregar estatísticas.'
    } else {
      errorMessage.value = 'Falha ao carregar estatísticas.'
    }
  }
})
</script>
