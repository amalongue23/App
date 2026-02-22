<template>
  <main class="admin-layout academic-v3-layout">
    <SideNav />

    <section class="content-area academic-v3-content">
      <header class="academic-v3-head">
        <div>
          <h1>Gestão de Anos Académicos</h1>
          <p>Início > Gestão de Ano</p>
        </div>
        <DashboardUserMenu />
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="academic-v3-card">
        <header class="academic-v3-card-head">
          <h2>Gestão de Anos Académicos</h2>
          <router-link class="btn btn-primary" to="/academic-years/new">+ Novo Ano Académico</router-link>
        </header>

        <div class="academic-v3-filters">
          <select v-model="draftStatus">
            <option value="ALL">Todos</option>
            <option value="OPEN">Abertos</option>
            <option value="CLOSED">Fechados</option>
          </select>
          <input v-model="draftSearch" placeholder="Pesquisar ano..." />
          <button class="btn btn-primary" type="button" @click="applyFilters">Aplicar Filtro</button>
          <button class="btn btn-ghost" type="button" @click="clearFilters">Limpar</button>
        </div>

        <div class="academic-v3-table-wrap">
          <table>
            <thead>
              <tr>
                <th @click="toggleSort('id')">ID</th>
                <th @click="toggleSort('year_label')">Ano</th>
                <th @click="toggleSort('is_open')">Aberto</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="year in paginatedItems" :key="year.id">
                <td>{{ String(year.id).padStart(3, '0') }}</td>
                <td>
                  <strong>{{ year.year_label }}</strong>
                </td>
                <td>
                  <span class="academic-status" :class="year.is_open ? 'open' : 'closed'">
                    {{ year.is_open ? 'Aberto' : 'Fechado' }}
                  </span>
                </td>
                <td>
                  <button v-if="!year.is_open" class="btn btn-ghost btn-small" type="button" @click="openFromRow(year)">
                    Abrir Ano
                  </button>
                  <span v-else class="academic-kebab">•••</span>
                </td>
              </tr>
              <tr v-if="!paginatedItems.length">
                <td colspan="4">Nenhum ano encontrado.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer class="academic-v3-footer">
          <div class="academic-v3-summary">Exibindo {{ pageStart }} a {{ pageEnd }} de {{ filteredItems.length }} anos</div>
          <div class="academic-v3-pagination">
            <select v-model.number="pageSize">
              <option :value="10">10 por página</option>
              <option :value="20">20 por página</option>
              <option :value="50">50 por página</option>
            </select>
            <button type="button" @click="prevPage" :disabled="currentPage === 1">‹</button>
            <span class="current">{{ currentPage }}</span>
            <button type="button" @click="nextPage" :disabled="currentPage >= totalPages">›</button>
          </div>
        </footer>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const router = useRouter()
const years = ref([])
const errorMessage = ref('')
const successMessage = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('id')
const sortDir = ref('asc')

const draftStatus = ref('ALL')
const appliedStatus = ref('ALL')
const draftSearch = ref('')
const appliedSearch = ref('')

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

const filteredItems = computed(() => {
  const q = appliedSearch.value.trim().toLowerCase()
  return years.value.filter((item) => {
    const byStatus =
      appliedStatus.value === 'ALL'
        ? true
        : appliedStatus.value === 'OPEN'
        ? item.is_open
        : !item.is_open
    const bySearch = q ? String(item.year_label || '').toLowerCase().includes(q) : true
    return byStatus && bySearch
  })
})

const sortedItems = computed(() => {
  const list = [...filteredItems.value]
  const key = sortBy.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return list.sort((a, b) => {
    const av = a[key] ?? ''
    const bv = b[key] ?? ''
    if (typeof av === 'boolean' && typeof bv === 'boolean') return (Number(av) - Number(bv)) * dir
    if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
    return String(av).localeCompare(String(bv)) * dir
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedItems.value.length / pageSize.value)))
const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return sortedItems.value.slice(start, start + pageSize.value)
})
const pageStart = computed(() => (filteredItems.value.length ? (currentPage.value - 1) * pageSize.value + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * pageSize.value, filteredItems.value.length))

watch([draftStatus, draftSearch, pageSize], () => {
  applyFilters()
})


function toggleSort(column) {
  if (sortBy.value === column) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
}

function applyFilters() {
  appliedStatus.value = draftStatus.value
  appliedSearch.value = draftSearch.value
  currentPage.value = 1
}

function clearFilters() {
  draftStatus.value = 'ALL'
  draftSearch.value = ''
  applyFilters()
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

function openFromRow(year) {
  router.push({ name: 'academic-years-new', query: { year_label: year.year_label } })
}

async function listYears() {
  try {
    errorMessage.value = ''
    const response = await api.get('/api/academic-years')
    years.value = response.data || []
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(listYears)
</script>
