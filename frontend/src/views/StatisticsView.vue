<template>
  <main class="admin-layout">
    <SideNav />

    <section class="content-area" :class="{ 'stats-chief-page': isChefe }">
      <header class="topbar">
        <div v-if="isChefe" class="stats-chief-title">Estatísticas <span>do {{ chiefDepartmentName }}</span></div>
        <div v-else>Estatísticas <span>{{ roleTitle }}</span></div>
        <DashboardUserMenu />
      </header>

      <template v-if="isChefe">
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <section class="stats-chief-filters">
          <select v-model="selectedAnoId" @change="onAcademicYearChange">
            <option v-for="item in filters.anos" :key="item.ano_academico_id" :value="item.ano_academico_id">
              {{ item.ano_lectivo }}
            </option>
          </select>
          <select v-model="selectedCourseId" @change="reloadStatistics">
            <option value="">Todos Cursos</option>
            <option v-for="item in filteredCourses" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
          <select v-model="chiefAcademicLevel">
            <option value="">Todos Níveis académicos</option>
            <option v-for="item in academicLevels" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
          <select v-model="chiefSexFilter">
            <option value="">Ambos</option>
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
          </select>
          <select v-model="chiefAgeFilter">
            <option value="">Todas Faixas Etárias</option>
            <option value="17-21">17-21</option>
            <option value="22-26">22-26</option>
            <option value="27+">27+</option>
          </select>
          <select v-model="chiefStatusFilter">
            <option value="">Todos (Sexos)</option>
            <option value="aprovado">Aprovados</option>
            <option value="reprovado">Reprovados</option>
            <option value="desistente">Desistentes</option>
          </select>
        </section>

        <section class="stats-chief-grid top">
          <article class="stats-chief-card">
            <h3>Média de Reprovação e Aprovação por Ano</h3>
            <svg viewBox="0 0 100 42" class="chart-svg" preserveAspectRatio="none">
              <polyline class="chart-line failed" :points="chiefLineA" />
              <polyline class="chart-line neutral" :points="chiefLineB" />
            </svg>
            <div class="chart-axis">
              <span v-for="item in chiefSeriesLabels" :key="`chief-top-${item}`">{{ item }}</span>
            </div>
            <div class="chart-legend-inline">
              <span><i class="dot-line failed"></i>Reprovação</span>
              <span><i class="dot-line neutral"></i>Aprovação</span>
            </div>
          </article>

          <article class="stats-chief-card">
            <h3>Taxa de Aprovação/Reprovação por Curso</h3>
            <div class="stats-chief-course-list">
              <div v-for="item in chiefCourseRates" :key="item.name" class="stats-chief-course-row">
                <span>{{ item.name }}</span>
                <div class="stats-chief-track">
                  <div class="bad" :style="{ width: `${item.failed}%` }"></div>
                  <div class="ok" :style="{ width: `${item.approved}%` }"></div>
                </div>
                <strong>{{ item.approved }}%</strong>
              </div>
            </div>
          </article>
        </section>

        <section class="stats-chief-grid middle">
          <article class="stats-chief-card">
            <h3>Taxa de Aprovação/Reprovação por Sexo</h3>
            <div class="stats-chief-donuts">
              <div class="stats-chief-donut-block">
                <div class="stats-chief-donut" :style="{ background: chiefSexDonutA }"><span>{{ chiefSexA }}%</span></div>
              </div>
              <div class="stats-chief-donut-block">
                <div class="stats-chief-donut" :style="{ background: chiefSexDonutB }"><span>{{ chiefSexB }}%</span></div>
              </div>
            </div>
          </article>

          <article class="stats-chief-card">
            <h3>Aprovações/Reprovações por Sexo</h3>
            <div class="stats-chief-bars">
              <div v-for="item in chiefSexBars" :key="item.label" class="stats-chief-bars-row">
                <span>{{ item.label }}</span>
                <div class="stats-chief-bars-track">
                  <div class="female" :style="{ width: `${item.female}%` }"></div>
                  <div class="male" :style="{ width: `${item.male}%` }"></div>
                </div>
              </div>
            </div>
          </article>

          <article class="stats-chief-card">
            <h3>Aprovações/Reprovações por Nível Académico</h3>
            <svg viewBox="0 0 100 42" class="chart-svg" preserveAspectRatio="none">
              <polyline class="chart-line approved" :points="chiefLineLevel" />
            </svg>
            <div class="chart-axis">
              <span v-for="item in chiefLevelLabels" :key="`chief-level-${item}`">{{ item }}</span>
            </div>
          </article>
        </section>

        <section class="stats-chief-grid bottom">
          <article class="stats-chief-card">
            <h3>Aprovações/Reprovações por Ano Académico</h3>
            <div class="stats-chief-bars years">
              <div v-for="item in chiefYearBars" :key="item.label" class="stats-chief-bars-row">
                <span>{{ item.label }}</span>
                <div class="stats-chief-bars-track">
                  <div class="male" :style="{ width: `${item.approved}%` }"></div>
                  <div class="female" :style="{ width: `${item.failed}%` }"></div>
                </div>
              </div>
            </div>
          </article>

          <article class="stats-chief-card">
            <h3>Taxa e Média de Evasão por Ano</h3>
            <div class="stats-chief-evasion-list">
              <div v-for="item in chiefEvasionByCourse" :key="item.name" class="stats-chief-evasion-row">
                <span>{{ item.name }}</span>
                <div class="stats-chief-mini-track"><div :style="{ width: `${item.value}%` }"></div></div>
                <strong>{{ item.value }}%</strong>
              </div>
            </div>
          </article>

          <article class="stats-chief-card">
            <h3>Taxa e Média de Evasão por Nível Académico</h3>
            <div class="stats-chief-evasion-list">
              <div v-for="item in chiefEvasionByLevel" :key="item.name" class="stats-chief-evasion-row">
                <span>{{ item.name }}</span>
                <div class="stats-chief-mini-track"><div :style="{ width: `${item.value}%` }"></div></div>
                <strong>+ {{ (item.value / 10).toFixed(1) }}</strong>
              </div>
            </div>
          </article>
        </section>
      </template>

      <template v-else>
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
      </template>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import { ACADEMIC_LEVEL_OPTIONS } from '../constants/academicLevels'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const filters = reactive({ anos: [] })
const selectedAnoId = ref('')
const selectedAnoLectivo = ref('')
const selectedUnitId = ref('')
const selectedDepartmentId = ref('')
const selectedCourseId = ref('')
const chiefAcademicLevel = ref('')
const chiefSexFilter = ref('')
const chiefAgeFilter = ref('')
const chiefStatusFilter = ref('')
const errorMessage = ref('')
const entities = reactive({ units: [], departments: [], courses: [] })

const dashboard = reactive({
  kpis: { students: 0, courses: 0 },
  performance: [],
  statistics: {
    year_labels: [],
    year_approval_rate: [],
    year_failure_rate: [],
    course_rates: [],
    sex_approval_rate: { male: 0, female: 0 },
    sex_status_bars: [],
    level_labels: [],
    level_approval_rates: [],
    year_status_bars: [],
    evasion_by_course: [],
    evasion_by_level: [],
  },
})

const isChefe = computed(() => authStore.user?.role === 'CHEFE')

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

const chiefDepartmentName = computed(() => {
  const dep = entities.departments.find((item) => String(item.id) === String(selectedDepartmentId.value))
  return dep ? `Departamento de ${dep.name.replace(/^Departamento de\s*/i, '')}` : 'Departamento de Computação'
})

const academicLevels = ACADEMIC_LEVEL_OPTIONS

const chiefSeriesLabels = computed(() => dashboard.statistics.year_labels || [])
const chiefLineA = computed(() => buildLine((dashboard.statistics.year_approval_rate || []).map((v) => Number(v || 0))))
const chiefLineB = computed(() => buildLine((dashboard.statistics.year_failure_rate || []).map((v) => Number(v || 0))))
const chiefCourseRates = computed(() => dashboard.statistics.course_rates || [])

const chiefSexA = computed(() => Number(dashboard.statistics.sex_approval_rate?.female || 0))
const chiefSexB = computed(() => Number(dashboard.statistics.sex_approval_rate?.male || 0))
const chiefSexDonutA = computed(() => `conic-gradient(#de7f84 0 ${chiefSexA.value}%, #e0b14d ${chiefSexA.value}% 100%)`)
const chiefSexDonutB = computed(() => `conic-gradient(#de7f84 0 ${chiefSexB.value}%, #e0b14d ${chiefSexB.value}% 100%)`)

const chiefSexBars = computed(() => dashboard.statistics.sex_status_bars || [])

const chiefLevelLabels = computed(() => dashboard.statistics.level_labels || [])
const chiefLineLevel = computed(() => buildLine((dashboard.statistics.level_approval_rates || []).map((v) => Number(v || 0))))

const chiefYearBars = computed(() => dashboard.statistics.year_status_bars || [])
const chiefEvasionByCourse = computed(() => dashboard.statistics.evasion_by_course || [])
const chiefEvasionByLevel = computed(() => dashboard.statistics.evasion_by_level || [])

function buildLine(values) {
  if (!values?.length) return ''
  const max = Math.max(...values, 1)
  const step = values.length > 1 ? 100 / (values.length - 1) : 100
  return values
    .map((value, idx) => {
      const x = (idx * step).toFixed(2)
      const y = (42 - (Math.max(0, value) / max) * 36).toFixed(2)
      return `${x},${y}`
    })
    .join(' ')
}

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
  if (isChefe.value && entities.departments.length && !selectedDepartmentId.value) {
    selectedDepartmentId.value = String(entities.departments[0].id)
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
  dashboard.statistics = payload.statistics || dashboard.statistics
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
