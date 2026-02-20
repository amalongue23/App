<template>
  <main class="ops-page">
    <section class="ops-card">
      <OperationsNav title="CRUD Cursos" subtitle="POST, PUT e GET by-department de /api/courses" />

      <section class="ops-grid two">
        <article>
          <h3>Criar Curso</h3>
          <form class="ops-form" @submit.prevent="createCourse">
            <input v-model="createForm.name" placeholder="Nome" required />
            <input v-model="createForm.code" placeholder="Código" required />
            <input v-model.number="createForm.department_id" type="number" min="1" placeholder="Department ID" required />
            <input v-model.number="createForm.credits" type="number" min="0" placeholder="Créditos" required />
            <button class="btn btn-primary" type="submit">Criar</button>
          </form>
        </article>

        <article>
          <h3>Atualizar Curso (PUT)</h3>
          <form class="ops-form" @submit.prevent="updateCourse">
            <input v-model.number="updateForm.id" type="number" min="1" placeholder="Course ID" required />
            <input v-model="updateForm.name" placeholder="Nome" />
            <input v-model="updateForm.code" placeholder="Código" />
            <input v-model.number="updateForm.department_id" type="number" min="1" placeholder="Department ID" />
            <input v-model.number="updateForm.credits" type="number" min="0" placeholder="Créditos" />
            <button class="btn btn-primary" type="submit">Atualizar</button>
          </form>
        </article>
      </section>

      <h3>Listar por Departamento</h3>
      <form class="ops-form inline" @submit.prevent="listByDepartment">
        <input v-model.number="departmentFilterId" type="number" min="1" placeholder="Department ID" required />
        <button class="btn btn-primary" type="submit">Listar</button>
      </form>
      <div class="ops-toolbar">
        <input v-model="searchTerm" placeholder="Filtrar por nome/código" />
      </div>

      <div class="ops-table-wrap">
        <table>
          <thead>
            <tr>
              <th @click="toggleSort('id')">ID</th>
              <th @click="toggleSort('name')">Nome</th>
              <th @click="toggleSort('code')">Código</th>
              <th @click="toggleSort('department_id')">Department ID</th>
              <th @click="toggleSort('credits')">Créditos</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedItems" :key="item.id">
              <td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.code }}</td><td>{{ item.department_id }}</td><td>{{ item.credits }}</td>
            </tr>
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
import { computed, reactive, ref, watch } from 'vue'

import OperationsNav from '../components/OperationsNav.vue'
import api from '../services/api'

const items = ref([])
const departmentFilterId = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = 6
const sortBy = ref('id')
const sortDir = ref('asc')

const createForm = reactive({ name: '', code: '', department_id: '', credits: 0 })
const updateForm = reactive({ id: '', name: '', code: '', department_id: '', credits: '' })

const filteredItems = computed(() => {
  const q = searchTerm.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) => `${item.name} ${item.code}`.toLowerCase().includes(q))
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

async function listByDepartment() {
  try {
    resetMessages()
    const r = await api.get(`/api/courses/by-department/${departmentFilterId.value}`)
    items.value = r.data
    successMessage.value = 'Cursos carregados com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function createCourse() {
  try {
    resetMessages()
    await api.post('/api/courses', createForm)
    successMessage.value = 'Curso criado com sucesso.'
    if (departmentFilterId.value) await listByDepartment()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function updateCourse() {
  try {
    resetMessages()
    const payload = {}
    if (updateForm.name) payload.name = updateForm.name
    if (updateForm.code) payload.code = updateForm.code
    if (updateForm.department_id) payload.department_id = updateForm.department_id
    if (updateForm.credits !== '' && updateForm.credits !== null) payload.credits = updateForm.credits
    await api.put(`/api/courses/${updateForm.id}`, payload)
    successMessage.value = 'Curso atualizado com sucesso.'
    if (departmentFilterId.value) await listByDepartment()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}
</script>
