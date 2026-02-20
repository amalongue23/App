<template>
  <main class="ops-page">
    <section class="ops-card">
      <OperationsNav title="CRUD Departamentos" subtitle="POST, GET, GET by-unit, GET por ID, PUT em /api/departments" />

      <section class="ops-grid two">
        <article>
          <h3>Criar Departamento</h3>
          <form class="ops-form" @submit.prevent="createDepartment">
            <input v-model="createForm.name" placeholder="Nome" required />
            <input v-model="createForm.code" placeholder="Código" required />
            <input v-model.number="createForm.unit_id" type="number" min="1" placeholder="Unit ID" required />
            <button class="btn btn-primary" type="submit">Criar</button>
          </form>
        </article>

        <article>
          <h3>Consultar por ID</h3>
          <form class="ops-form" @submit.prevent="getById">
            <input v-model.number="detailId" type="number" min="1" placeholder="Department ID" required />
            <button class="btn btn-primary" type="submit">Buscar</button>
          </form>
          <pre class="ops-pre" v-if="detailItem">{{ JSON.stringify(detailItem, null, 2) }}</pre>
        </article>
      </section>

      <section class="ops-grid two">
        <article>
          <h3>Listar por Unidade</h3>
          <form class="ops-form" @submit.prevent="listByUnit">
            <input v-model.number="unitFilterId" type="number" min="1" placeholder="Unit ID" required />
            <button class="btn btn-primary" type="submit">Listar</button>
          </form>
        </article>

        <article>
          <h3>Atualizar Departamento</h3>
          <form class="ops-form" @submit.prevent="updateDepartment">
            <input v-model.number="updateForm.id" type="number" min="1" placeholder="Department ID" required />
            <input v-model="updateForm.name" placeholder="Nome" />
            <input v-model="updateForm.code" placeholder="Código" />
            <input v-model.number="updateForm.unit_id" type="number" min="1" placeholder="Unit ID" />
            <button class="btn btn-primary" type="submit">Atualizar</button>
          </form>
        </article>
      </section>

      <h3>Listar Todos</h3>
      <div class="ops-toolbar">
        <button class="btn btn-ghost" type="button" @click="listAll">Atualizar Lista</button>
        <input v-model="searchTerm" placeholder="Filtrar por nome/código" />
      </div>
      <div class="ops-table-wrap">
        <table>
          <thead>
            <tr>
              <th @click="toggleSort('id')">ID</th>
              <th @click="toggleSort('name')">Nome</th>
              <th @click="toggleSort('code')">Código</th>
              <th @click="toggleSort('unit_id')">Unit ID</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedItems" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.code }}</td><td>{{ item.unit_id }}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="ops-pagination" v-if="filteredItems.length">
        <button class="btn btn-ghost" type="button" @click="prevPage" :disabled="currentPage === 1">Anterior</button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button class="btn btn-ghost" type="button" @click="nextPage" :disabled="currentPage >= totalPages">Próxima</button>
      </div>
      <p class="ops-tip" v-else>Nenhum registro encontrado.</p>

      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import OperationsNav from '../components/OperationsNav.vue'
import api from '../services/api'

const items = ref([])
const detailItem = ref(null)
const detailId = ref('')
const unitFilterId = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = 6
const sortBy = ref('id')
const sortDir = ref('asc')

const createForm = reactive({ name: '', code: '', unit_id: '' })
const updateForm = reactive({ id: '', name: '', code: '', unit_id: '' })

const filteredItems = computed(() => {
  const q = searchTerm.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) => `${item.name} ${item.code} ${item.unit_id}`.toLowerCase().includes(q))
})

const sortedItems = computed(() => {
  const list = [...filteredItems.value]
  const key = sortBy.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return list.sort((a, b) => {
    const va = a[key]
    const vb = b[key]
    if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir
    return String(va ?? '').localeCompare(String(vb ?? '')) * dir
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / pageSize)))
const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedItems.value.slice(start, start + pageSize)
})

watch(searchTerm, () => {
  currentPage.value = 1
})

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

function toggleSort(column) {
  if (sortBy.value === column) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
}

function resetMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function listAll() {
  try {
    resetMessages()
    const r = await api.get('/api/departments')
    items.value = r.data
    successMessage.value = 'Lista de departamentos carregada.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function createDepartment() {
  try {
    resetMessages()
    await api.post('/api/departments', createForm)
    createForm.name = ''
    createForm.code = ''
    createForm.unit_id = ''
    await listAll()
    successMessage.value = 'Departamento criado com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function getById() {
  try {
    resetMessages()
    const r = await api.get(`/api/departments/${detailId.value}`)
    detailItem.value = r.data
    successMessage.value = 'Departamento consultado com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function listByUnit() {
  try {
    resetMessages()
    const r = await api.get(`/api/departments/by-unit/${unitFilterId.value}`)
    items.value = r.data
    successMessage.value = 'Departamentos por unidade carregados.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function updateDepartment() {
  try {
    resetMessages()
    const payload = {}
    if (updateForm.name) payload.name = updateForm.name
    if (updateForm.code) payload.code = updateForm.code
    if (updateForm.unit_id) payload.unit_id = updateForm.unit_id
    await api.put(`/api/departments/${updateForm.id}`, payload)
    await listAll()
    successMessage.value = 'Departamento atualizado com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(listAll)
</script>
