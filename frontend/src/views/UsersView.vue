<template>
  <CreateEntityLayout
    title="Cadastro de Usuário"
    subtitle="Preencha as informações abaixo para cadastrar um novo usuário na aplicação."
    section-label="Usuários"
    section-route="/users"
  >
    <form class="create-form" @submit.prevent="createUser">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome Completo</label>
        <input v-model="form.full_name" placeholder="Digite o nome completo" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Username</label>
          <input v-model="form.username" placeholder="Digite o username" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Papel</label>
          <select v-model="form.role" required>
            <option value="">Selecione o papel</option>
            <option value="REITOR">REITOR</option>
            <option value="DIRETOR">DIRETOR</option>
            <option value="CHEFE">CHEFE</option>
          </select>
        </div>
      </div>

      <div class="create-field">
        <label class="create-label">* Senha</label>
        <input v-model="form.password" type="password" placeholder="Digite a senha" required />
      </div>

      <div class="create-actions">
        <button class="btn btn-ghost" type="button" @click="resetForm">Cancelar</button>
        <button class="btn btn-primary" type="submit">Cadastrar Usuário</button>
      </div>
    </form>

    <section class="create-list-panel">
      <div class="ops-toolbar">
        <button class="btn btn-ghost" type="button" @click="listUsers">Atualizar Lista</button>
        <input v-model="searchTerm" placeholder="Filtrar por nome/username/papel" />
      </div>
      <div class="ops-table-wrap">
        <table>
          <thead>
            <tr>
              <th @click="toggleSort('id')">ID</th>
              <th @click="toggleSort('full_name')">Nome</th>
              <th @click="toggleSort('username')">Username</th>
              <th @click="toggleSort('role')">Papel</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.full_name }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.role }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="ops-pagination" v-if="filteredUsers.length">
        <button class="btn btn-ghost" type="button" @click="prevPage" :disabled="currentPage === 1">Anterior</button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button class="btn btn-ghost" type="button" @click="nextPage" :disabled="currentPage >= totalPages">Próxima</button>
      </div>
      <p class="ops-tip" v-else>Nenhum registro encontrado.</p>
    </section>
  </CreateEntityLayout>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import CreateEntityLayout from '../components/CreateEntityLayout.vue'
import api from '../services/api'

const users = ref([])
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = 8
const sortBy = ref('id')
const sortDir = ref('asc')
const form = reactive({ full_name: '', username: '', password: '', role: '' })

const filteredUsers = computed(() => {
  const q = searchTerm.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter((u) => `${u.full_name} ${u.username} ${u.role}`.toLowerCase().includes(q))
})

const sortedUsers = computed(() => {
  const list = [...filteredUsers.value]
  const key = sortBy.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return list.sort((a, b) => {
    const va = a[key]
    const vb = b[key]
    if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir
    return String(va ?? '').localeCompare(String(vb ?? '')) * dir
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedUsers.value.slice(start, start + pageSize)
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

function resetForm() {
  form.full_name = ''
  form.username = ''
  form.password = ''
  form.role = ''
}

function resetMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function listUsers() {
  try {
    resetMessages()
    const r = await api.get('/api/users')
    users.value = r.data
    successMessage.value = 'Lista de usuários carregada.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function createUser() {
  try {
    resetMessages()
    await api.post('/api/users', form)
    resetForm()
    await listUsers()
    successMessage.value = 'Usuário criado com sucesso.'
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(listUsers)
</script>
