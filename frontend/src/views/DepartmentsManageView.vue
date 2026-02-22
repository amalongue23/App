<template>
  <main class="admin-layout departments-v2-layout">
    <SideNav />

    <section class="content-area departments-v2-content">
      <header class="departments-v2-head">
        <div>
          <h1>Gestão de Departamentos</h1>
          <p>Listagem e atualização em tela separada.</p>
        </div>
        <div class="departments-v2-head-actions">
          <router-link class="btn btn-primary" to="/departments/create">+ Novo Departamento</router-link>
          <button class="btn btn-ghost" type="button" @click="exportCsv">Exportar</button>
          <DashboardUserMenu compact />
        </div>
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="departments-v2-shell">
        <div class="departments-v2-total">Total de <strong>Departamentos</strong> {{ filteredItems.length }}</div>

        <div class="departments-v2-main">
          <aside class="departments-v2-filter-card">
            <h3>Unidade Orgânica</h3>
            <select v-model.number="draftUnitId">
              <option :value="0">Todas unidades</option>
              <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
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
                    <th>Unidade</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in paginatedItems" :key="item.id">
                    <td>{{ item.id }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ item.code }}</td>
                    <td>{{ unitName(item.unit_id) }}</td>
                    <td class="dept-actions-cell">
                      <div class="dept-action-wrap">
                        <button class="btn btn-primary btn-small" type="button" @click="selectForEdit(item)">Editar</button>
                        <button class="dept-dropdown-toggle" type="button" @click="toggleRowMenu(item.id)">⌄</button>
                        <div v-if="openMenuId === item.id" class="dept-dropdown-menu">
                          <button type="button" @click="selectForEdit(item)">Editar</button>
                          <button type="button" @click="manageStaff(item)">Gerenciar Funcionários</button>
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

      <section v-if="selectedItem" class="departments-v2-edit">
        <h3>Editar Departamento: {{ selectedItem.name }}</h3>
        <form class="departments-v2-edit-form" @submit.prevent="updateDepartment">
          <input v-model="updateForm.name" placeholder="Nome" />
          <input v-model="updateForm.code" placeholder="Código" />
          <select v-model.number="updateForm.unit_id">
            <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
          </select>
          <button class="btn btn-primary" type="submit">Salvar</button>
        </form>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const router = useRouter()
const items = ref([])
const units = ref([])
const selectedItem = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
const currentPage = ref(1)
const sortBy = ref('id')
const sortDir = ref('asc')
const pageSize = 8
const openMenuId = ref(0)

const draftUnitId = ref(0)
const appliedUnitId = ref(0)
const draftSearch = ref('')
const appliedSearch = ref('')

const updateForm = reactive({ name: '', code: '', unit_id: 0 })

function err(e) {
  return axios.isAxiosError(e) ? e.response?.data?.message || 'Erro na operação.' : 'Erro na operação.'
}

const filteredItems = computed(() => {
  const q = appliedSearch.value.trim().toLowerCase()
  return items.value.filter((i) => {
    const byUnit = appliedUnitId.value ? i.unit_id === appliedUnitId.value : true
    const bySearch = q ? `${i.name} ${i.code}`.toLowerCase().includes(q) : true
    return byUnit && bySearch
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
  draftSearch.value = ''
  applyFilters()
}

function applyFilters() {
  appliedUnitId.value = draftUnitId.value
  appliedSearch.value = draftSearch.value
  currentPage.value = 1
  openMenuId.value = 0
}

function toggleRowMenu(id) {
  openMenuId.value = openMenuId.value === id ? 0 : id
}

function selectForEdit(item) {
  openMenuId.value = 0
  selectedItem.value = item
  updateForm.name = item.name
  updateForm.code = item.code
  updateForm.unit_id = item.unit_id
}

function manageStaff(item) {
  openMenuId.value = 0
  router.push({ name: 'users', query: { department_id: String(item.id) } })
}

async function loadUnits() {
  const r = await api.get('/api/units')
  units.value = r.data
}

async function listAll() {
  const r = await api.get('/api/departments')
  items.value = r.data
}

async function updateDepartment() {
  try {
    successMessage.value = ''
    errorMessage.value = ''
    const payload = {}
    if (updateForm.name) payload.name = updateForm.name
    if (updateForm.code) payload.code = updateForm.code
    if (updateForm.unit_id) payload.unit_id = updateForm.unit_id
    await api.put(`/api/departments/${selectedItem.value.id}`, payload)
    successMessage.value = 'Departamento atualizado com sucesso.'
    await listAll()
    applyFilters()
  } catch (e) {
    errorMessage.value = err(e)
  }
}

function exportCsv() {
  const header = ['id', 'nome', 'codigo', 'unidade']
  const lines = filteredItems.value.map((r) => [r.id, r.name, r.code, unitName(r.unit_id)].join(','))
  const csv = [header.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'departamentos.csv'
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    await loadUnits()
    await listAll()
  } catch (e) {
    errorMessage.value = err(e)
  }
})
</script>
