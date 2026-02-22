<template>
  <main class="admin-layout students-v2-layout">
    <SideNav />

    <section class="content-area students-v2-content">
      <header class="students-v2-head">
        <div>
          <h1>Gestão de Estudantes</h1>
          <p>{{ scopeSubtitle }}</p>
        </div>
        <div class="students-v2-head-actions">
          <router-link v-if="canCreate" class="btn btn-primary" to="/students/create">+ Novo Estudante</router-link>
          <button class="btn btn-ghost" type="button" @click="exportCsv">Exportar</button>
          <DashboardUserMenu compact />
        </div>
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="students-v2-kpis">
        <article class="kpi-card"><div class="kpi-title">Total de Estudantes</div><div class="kpi-value">{{ kpis.total }}</div></article>
        <article class="kpi-card"><div class="kpi-title">Aprovados</div><div class="kpi-value">{{ kpis.aprovados }}</div></article>
        <article class="kpi-card"><div class="kpi-title">Reprovados</div><div class="kpi-value">{{ kpis.reprovados }}</div></article>
        <article class="kpi-card"><div class="kpi-title">Desistentes</div><div class="kpi-value">{{ kpis.desistentes }}</div></article>
      </section>

      <section class="students-v2-grid">
        <aside class="students-v2-filter-card">
          <h3>Filtros de Pesquisa</h3>
          <select v-model="draft.department_id">
            <option value="">Todos os departamentos</option>
            <option v-for="dep in departments" :key="dep.id" :value="String(dep.id)">{{ dep.name }}</option>
          </select>
          <select v-model="draft.course_id">
            <option value="">Todos os cursos</option>
            <option v-for="course in filteredCoursesByDepartment" :key="course.id" :value="String(course.id)">{{ course.name }}</option>
          </select>
          <select v-model="draft.academic_level">
            <option value="">Todos os anos de frequência</option>
            <option v-for="item in academicLevels" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
          <select v-model.number="draft.year_id">
            <option :value="0" disabled>Selecione o ano</option>
            <option v-for="year in years" :key="year.ano_academico_id" :value="year.ano_academico_id">{{ year.ano_lectivo }}</option>
          </select>
          <div class="students-v2-filter-actions">
            <button class="btn btn-primary" type="button" @click="applyFilters">Aplicar Filtro</button>
            <button class="btn btn-ghost" type="button" @click="clearFilters">Limpar</button>
          </div>
        </aside>

        <article class="students-v2-table-card">
          <div class="students-v2-search-row">
            <input v-model="draft.search" placeholder="Pesquisar por nome, matrícula, email ou curso" />
            <button class="btn btn-primary" type="button" @click="applyFilters">Aplicar Filtro</button>
            <button class="btn btn-ghost" type="button" @click="clearSearch">Limpar</button>
          </div>

          <div class="students-v2-table-wrap">
            <table>
              <thead>
                <tr>
                  <th @click="toggleSort('id')">ID</th>
                  <th @click="toggleSort('full_name')">Nome</th>
                  <th @click="toggleSort('registration_number')">Matrícula</th>
                  <th @click="toggleSort('email')">Email</th>
                  <th>Curso</th>
                  <th @click="toggleSort('academic_level')">Ano de Frequência</th>
                  <th>Status</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedItems" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td>{{ item.full_name }}</td>
                  <td>{{ item.registration_number }}</td>
                  <td>{{ item.email }}</td>
                  <td>{{ item.course_name || '-' }}</td>
                  <td>{{ academicLevelLabel(item.academic_level) }}</td>
                  <td>
                    <span class="status-tag" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
                  </td>
                  <td>
                    <button class="btn btn-ghost btn-small" type="button" @click="goToStatus(item.id)">
                      {{ canEdit ? 'Editar' : 'Ver' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="students-v2-pagination" v-if="totalPages > 1">
            <button class="btn btn-ghost" type="button" @click="prevPage" :disabled="currentPage === 1">Anterior</button>
            <span>Página {{ currentPage }} de {{ totalPages }}</span>
            <button class="btn btn-ghost" type="button" @click="nextPage" :disabled="currentPage >= totalPages">Próxima</button>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import { ACADEMIC_LEVEL_OPTIONS, academicLevelLabel } from '../constants/academicLevels'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const pageSize = 8

const errorMessage = ref('')
const successMessage = ref('')
const departments = ref([])
const courses = ref([])
const years = ref([])
const students = ref([])
const currentPage = ref(1)
const sortBy = ref('id')
const sortDir = ref('asc')
const statusMap = reactive({})
const academicLevels = ACADEMIC_LEVEL_OPTIONS

const draft = reactive({ department_id: '', course_id: '', academic_level: '', year_id: 0, search: '' })
const applied = reactive({ department_id: '', course_id: '', academic_level: '', year_id: 0, search: '' })

const isAdmin = computed(() => authStore.user?.role === 'ADMIN')
const isChefe = computed(() => authStore.user?.role === 'CHEFE')
const isDirector = computed(() => authStore.user?.role === 'DIRETOR')
const isReitor = computed(() => authStore.user?.role === 'REITOR')
const canEdit = computed(() => isAdmin.value || isChefe.value)
const canCreate = computed(() => canEdit.value)

const selectedYearLabel = computed(() => years.value.find((y) => y.ano_academico_id === Number(applied.year_id))?.ano_lectivo || '-')
const selectedDepartmentName = computed(() => departments.value.find((d) => String(d.id) === String(applied.department_id))?.name || 'Todos os departamentos')
const scopeSubtitle = computed(() => `${selectedDepartmentName.value} • Ano ${selectedYearLabel.value}`)

const filteredCoursesByDepartment = computed(() => {
  if (!draft.department_id) return courses.value
  return courses.value.filter((c) => String(c.department_id) === String(draft.department_id))
})

const mergedItems = computed(() =>
  students.value.map((s) => ({
    ...s,
    status: (statusMap[s.id] || {}).status || 'nao_definido',
    academic_level: (statusMap[s.id] || {}).academic_level || s.academic_level,
  })),
)

const filteredItems = computed(() => {
  const search = applied.search.trim().toLowerCase()
  return mergedItems.value.filter((item) => {
    const byCourse = applied.course_id ? String(item.course_id || '') === String(applied.course_id) : true
    const byAcademicLevel = applied.academic_level ? String(item.academic_level || '') === String(applied.academic_level) : true
    const haystack = `${item.full_name} ${item.registration_number} ${item.email} ${item.course_name || ''} ${academicLevelLabel(item.academic_level)}`.toLowerCase()
    const bySearch = search ? haystack.includes(search) : true
    return byCourse && byAcademicLevel && bySearch
  })
})

const sortedItems = computed(() => {
  const list = [...filteredItems.value]
  const key = sortBy.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return list.sort((a, b) => {
    const av = a[key] ?? ''
    const bv = b[key] ?? ''
    if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
    return String(av).localeCompare(String(bv)) * dir
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedItems.value.length / pageSize)))
const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedItems.value.slice(start, start + pageSize)
})

const kpis = computed(() => {
  const rows = filteredItems.value
  return {
    total: rows.length,
    aprovados: rows.filter((r) => r.status === 'aprovado').length,
    reprovados: rows.filter((r) => r.status === 'reprovado').length,
    desistentes: rows.filter((r) => r.status === 'desistente').length,
  }
})

watch(
  () => draft.department_id,
  () => {
    if (draft.course_id && !filteredCoursesByDepartment.value.some((c) => String(c.id) === String(draft.course_id))) {
      draft.course_id = ''
    }
  },
)

function err(e) {
  return axios.isAxiosError(e) ? e.response?.data?.message || 'Erro na operação.' : 'Erro na operação.'
}

function statusLabel(v) {
  if (!v || v === 'nao_definido') return 'Não definido'
  if (v === 'active') return 'Em Curso'
  if (v === 'aprovado') return 'Aprovado'
  if (v === 'reprovado') return 'Reprovado'
  if (v === 'desistente') return 'Desistente'
  return v
}

function statusClass(v) {
  if (v === 'aprovado') return 'status-ok'
  if (v === 'reprovado') return 'status-bad'
  if (v === 'desistente') return 'status-warn'
  if (v === 'active') return 'status-active'
  return 'status-neutral'
}

function toggleSort(column) {
  if (sortBy.value === column) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function goToStatus(studentId) {
  router.push({ name: 'student-status', params: { id: studentId } })
}

function exportCsv() {
  const rows = filteredItems.value
  const header = ['id', 'nome', 'matricula', 'email', 'curso', 'ano_frequencia', 'status']
  const lines = rows.map((r) => [r.id, r.full_name, r.registration_number, r.email, r.course_name || '', academicLevelLabel(r.academic_level), statusLabel(r.status)].join(','))
  const csv = [header.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'estudantes.csv'
  link.click()
  URL.revokeObjectURL(url)
}

function clearSearch() {
  draft.search = ''
  applyFilters()
}

function clearFilters() {
  draft.department_id = isChefe.value && departments.value.length ? String(departments.value[0].id) : ''
  draft.course_id = ''
  draft.academic_level = ''
  draft.search = ''
  if (years.value.length) draft.year_id = years.value[0].ano_academico_id
  applyFilters()
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  departments.value = response.data.departments || []
  courses.value = response.data.courses || []
  years.value = response.data.anos || []

  if (isChefe.value && departments.value.length) draft.department_id = String(departments.value[0].id)
  if (!draft.year_id && years.value.length) draft.year_id = years.value[0].ano_academico_id
}

async function loadStudentsAndStatus() {
  const departmentIds = applied.department_id
    ? [Number(applied.department_id)]
    : departments.value.map((d) => d.id)

  if (!departmentIds.length) {
    students.value = []
    Object.keys(statusMap).forEach((k) => delete statusMap[k])
    return
  }

  const studentsResponses = await Promise.all(
    departmentIds.map((depId) => api.get(`/api/students/by-department/${depId}`)),
  )
  const merged = []
  const seen = new Set()
  for (const response of studentsResponses) {
    for (const row of response.data || []) {
      if (seen.has(row.id)) continue
      seen.add(row.id)
      merged.push(row)
    }
  }
  students.value = merged

  Object.keys(statusMap).forEach((k) => delete statusMap[k])
  if (!applied.year_id) return

  const statusResponses = await Promise.all(
    departmentIds.map((depId) =>
      api.get(`/api/students/status/by-department/${depId}`, { params: { academic_year_id: applied.year_id } }),
    ),
  )
  for (const response of statusResponses) {
    for (const row of response.data || []) statusMap[row.student_id] = { status: row.status, academic_level: row.academic_level }
  }
}

async function applyFilters() {
  applied.department_id = draft.department_id
  applied.course_id = draft.course_id
  applied.academic_level = draft.academic_level
  applied.year_id = Number(draft.year_id || 0)
  applied.search = draft.search
  currentPage.value = 1
  try {
    errorMessage.value = ''
    successMessage.value = ''
    await loadStudentsAndStatus()
  } catch (e) {
    errorMessage.value = err(e)
  }
}

onMounted(async () => {
  try {
    await loadFilters()
    await applyFilters()
  } catch (e) {
    errorMessage.value = err(e)
  }
})
</script>
