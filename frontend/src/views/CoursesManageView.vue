<template>
  <main class="admin-layout departments-v2-layout">
    <SideNav />

    <section class="content-area departments-v2-content">
      <header class="departments-v2-head">
        <div>
          <h1>Gestão de Cursos</h1>
          <p>Listagem e atualização em tela separada.</p>
        </div>
        <div class="departments-v2-head-actions">
          <router-link class="btn btn-primary" to="/courses/create">+ Novo Curso</router-link>
          <button class="btn btn-ghost" type="button" @click="exportCsv">Exportar</button>
        </div>
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="departments-v2-shell">
        <div class="departments-v2-total">Total de <strong>Cursos</strong> {{ filteredItems.length }}</div>

        <div class="departments-v2-main">
          <aside class="departments-v2-filter-card">
            <h3>Unidade Orgânica</h3>
            <select v-model.number="draftUnitId">
              <option :value="0">Todas unidades</option>
              <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>
            <h3 class="courses-filter-heading">Departamento</h3>
            <select v-model.number="draftDepartmentId">
              <option :value="0">Todos departamentos</option>
              <option v-for="d in filteredDepartmentsByUnit" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
            <div class="departments-v2-filter-actions">
              <button class="btn btn-primary" type="button" @click="applyFilters">Aplicar Filtro</button>
              <button class="btn btn-ghost" type="button" @click="clearFilters">Limpar</button>
            </div>
          </aside>

          <article class="departments-v2-table-card">
            <div class="departments-v2-search-row">
              <input v-model="draftSearch" placeholder="Filtrar por nome ou código" />
              <button class="btn btn-primary" type="button" @click="applyFilters">Aplicar Filtro</button>
              <button class="btn btn-ghost" type="button" @click="clearSearch">Limpar</button>
            </div>

            <div class="departments-v2-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th @click="toggleSort('id')">ID</th>
                    <th @click="toggleSort('name')">Nome</th>
                    <th @click="toggleSort('code')">Código</th>
                    <th @click="toggleSort('credits')">Créditos</th>
                    <th>Departamento</th>
                    <th>Unidade</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in paginatedItems" :key="item.id">
                    <td>{{ item.id }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ item.code }}</td>
                    <td>{{ item.credits }}</td>
                    <td>{{ departmentName(item.department_id) }}</td>
                    <td>{{ unitName(item.unit_id) }}</td>
                    <td class="dept-actions-cell">
                      <div class="dept-action-wrap">
                        <button class="btn btn-primary btn-small" type="button" @click="goToEdit(item)">{{ canEdit ? 'Editar' : 'Ver' }}</button>
                        <button class="dept-dropdown-toggle" type="button" @click="toggleRowMenu(item.id)">⌄</button>
                        <div v-if="openMenuId === item.id" class="dept-dropdown-menu">
                          <button type="button" @click="goToEdit(item)">{{ canEdit ? 'Editar' : 'Ver' }}</button>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="departments-v2-pagination" v-if="totalPages > 1">
              <button class="btn btn-ghost" type="button" @click="prevPage" :disabled="currentPage===1">Anterior</button>
              <span>Página {{ currentPage }} de {{ totalPages }}</span>
              <button class="btn btn-ghost" type="button" @click="nextPage" :disabled="currentPage>=totalPages">Próxima</button>
            </div>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const items = ref([])
const units = ref([])
const departments = ref([])
const successMessage = ref('')
const errorMessage = ref('')
const currentPage = ref(1)
const sortBy = ref('id')
const sortDir = ref('asc')
const pageSize = 8
const openMenuId = ref(0)

const draftUnitId = ref(0)
const draftDepartmentId = ref(0)
const appliedUnitId = ref(0)
const appliedDepartmentId = ref(0)
const draftSearch = ref('')
const appliedSearch = ref('')
const canEdit = computed(() => authStore.user?.role === 'ADMIN')

function err(e) {
  return axios.isAxiosError(e) ? e.response?.data?.message || 'Erro na operação.' : 'Erro na operação.'
}

const filteredDepartmentsByUnit = computed(() => {
  if (!draftUnitId.value) return departments.value
  return departments.value.filter((d) => d.unit_id === draftUnitId.value)
})

watch(draftUnitId, () => {
  if (draftDepartmentId.value && !filteredDepartmentsByUnit.value.some((d) => d.id === draftDepartmentId.value)) {
    draftDepartmentId.value = 0
  }
})

const filteredItems = computed(() => {
  const q = appliedSearch.value.trim().toLowerCase()
  return items.value.filter((i) => {
    const byUnit = appliedUnitId.value ? i.unit_id === appliedUnitId.value : true
    const byDepartment = appliedDepartmentId.value ? i.department_id === appliedDepartmentId.value : true
    const bySearch = q ? `${i.name} ${i.code}`.toLowerCase().includes(q) : true
    return byUnit && byDepartment && bySearch
  })
})

const sortedItems = computed(() => {
  const list = [...filteredItems.value]
  const key = sortBy.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return list.sort((a, b) => (typeof a[key] === 'number' && typeof b[key] === 'number' ? a[key] - b[key] : String(a[key] ?? '').localeCompare(String(b[key] ?? ''))) * dir)
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedItems.value.length / pageSize)))
const paginatedItems = computed(() => sortedItems.value.slice((currentPage.value - 1) * pageSize, (currentPage.value - 1) * pageSize + pageSize))

function unitName(id) {
  return units.value.find((u) => u.id === id)?.name || '-'
}

function departmentName(id) {
  return departments.value.find((d) => d.id === id)?.name || '-'
}

function toggleSort(column) {
  if (sortBy.value === column) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

function clearSearch() {
  draftSearch.value = ''
  applyFilters()
}

function clearFilters() {
  draftUnitId.value = 0
  draftDepartmentId.value = 0
  draftSearch.value = ''
  applyFilters()
}

function applyFilters() {
  appliedUnitId.value = draftUnitId.value
  appliedDepartmentId.value = draftDepartmentId.value
  appliedSearch.value = draftSearch.value
  currentPage.value = 1
  openMenuId.value = 0
}

function toggleRowMenu(id) {
  openMenuId.value = openMenuId.value === id ? 0 : id
}

function goToEdit(item) {
  openMenuId.value = 0
  router.push({ name: 'courses-edit', params: { id: item.id }, query: { mode: canEdit.value ? 'edit' : 'view' } })
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  units.value = response.data.units || []
  departments.value = response.data.departments || []
}

async function listAll() {
  const all = []
  const seen = new Set()
  const responses = await Promise.all(departments.value.map((dep) => api.get(`/api/courses/by-department/${dep.id}`)))
  for (const response of responses) {
    const rows = response.data || []
    for (const row of rows) {
      if (seen.has(row.id)) continue
      seen.add(row.id)
      all.push({
        ...row,
        unit_id: departments.value.find((d) => d.id === row.department_id)?.unit_id || 0,
      })
    }
  }
  items.value = all
}

function exportCsv() {
  const header = ['id', 'nome', 'codigo', 'creditos', 'departamento', 'unidade']
  const lines = filteredItems.value.map((r) => [r.id, r.name, r.code, r.credits, departmentName(r.department_id), unitName(r.unit_id)].join(','))
  const csv = [header.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'cursos.csv'
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    await loadFilters()
    await listAll()
  } catch (e) {
    errorMessage.value = err(e)
  }
})
</script>
