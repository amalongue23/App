<template>
  <main class="ops-page">
    <section class="ops-card">
      <OperationsNav title="CRUD Estudantes" subtitle="POST, PUT e GET by-department" />

      <section class="ops-grid two">
        <article>
          <h3>Criar Estudante</h3>
          <form class="ops-form" @submit.prevent="createStudent">
            <input v-model="createForm.full_name" placeholder="Nome completo" required />
            <input v-model="createForm.registration_number" placeholder="Matrícula" required />
            <input v-model="createForm.email" type="email" placeholder="Email" required />
            <input v-model.number="createForm.department_id" type="number" min="1" placeholder="Department ID" required />
            <input v-model="createForm.academic_level" placeholder="Ano (ex: LICENCIATURA_1)" required />
            <button class="btn btn-primary" type="submit">Criar</button>
          </form>
        </article>

        <article>
          <h3>Atualizar Estudante (PUT)</h3>
          <form class="ops-form" @submit.prevent="updateStudent">
            <input v-model.number="updateForm.id" type="number" min="1" placeholder="Student ID" required />
            <input v-model="updateForm.full_name" placeholder="Nome completo" />
            <input v-model="updateForm.registration_number" placeholder="Matrícula" />
            <input v-model="updateForm.email" type="email" placeholder="Email" />
            <input v-model.number="updateForm.department_id" type="number" min="1" placeholder="Department ID" />
            <input v-model="updateForm.academic_level" placeholder="Ano (ex: MESTRADO_1)" />
            <button class="btn btn-primary" type="submit">Atualizar</button>
          </form>
        </article>
      </section>

      <section class="ops-grid two">
        <article>
          <h3>Listar por Departamento</h3>
          <form class="ops-form inline" @submit.prevent="listByDepartment">
            <input v-model.number="departmentFilterId" type="number" min="1" placeholder="Department ID" required />
            <button class="btn btn-primary" type="submit">Listar</button>
          </form>
          <div class="ops-toolbar">
            <input v-model="searchTerm" placeholder="Filtrar por nome/matrícula/email" />
          </div>
          <div class="ops-table-wrap">
            <table>
              <thead>
                <tr>
                  <th @click="toggleSort('id')">ID</th>
                  <th @click="toggleSort('full_name')">Nome</th>
                  <th @click="toggleSort('registration_number')">Matrícula</th>
                  <th @click="toggleSort('email')">Email</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedItems" :key="item.id">
                  <td>{{ item.id }}</td><td>{{ item.full_name }}</td><td>{{ item.registration_number }}</td><td>{{ item.email }}</td>
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
        </article>
      </section>

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

const createForm = reactive({ full_name: '', registration_number: '', email: '', department_id: '', academic_level: 'LICENCIATURA_1' })
const updateForm = reactive({ id: '', full_name: '', registration_number: '', email: '', department_id: '', academic_level: '' })

const filteredItems = computed(() => {
  const q = searchTerm.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) =>
    `${item.full_name} ${item.registration_number} ${item.email}`.toLowerCase().includes(q),
  )
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
    const r = await api.get(`/api/students/by-department/${departmentFilterId.value}`)
    items.value = r.data
    successMessage.value = 'Estudantes carregados com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function createStudent() {
  try {
    resetMessages()
    await api.post('/api/students', createForm)
    successMessage.value = 'Estudante criado com sucesso.'
    if (departmentFilterId.value) await listByDepartment()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function updateStudent() {
  try {
    resetMessages()
    const payload = {}
    if (updateForm.full_name) payload.full_name = updateForm.full_name
    if (updateForm.registration_number) payload.registration_number = updateForm.registration_number
    if (updateForm.email) payload.email = updateForm.email
    if (updateForm.department_id) payload.department_id = updateForm.department_id
    if (updateForm.academic_level) payload.academic_level = updateForm.academic_level
    await api.put(`/api/students/${updateForm.id}`, payload)
    successMessage.value = 'Estudante atualizado com sucesso.'
    if (departmentFilterId.value) await listByDepartment()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

</script>
