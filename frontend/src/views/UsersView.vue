<template>
  <main class="admin-layout users-v2-layout">
    <SideNav />

    <section class="content-area users-v2-content">
      <header class="users-v2-head">
        <div>
          <h1>Gestão de Usuários</h1>
          <p>Listagem, roles e edição de usuários</p>
        </div>
        <div class="users-v2-head-actions">
          <button class="btn btn-primary" type="button" @click="goToCreateUser">+ Novo Usuário</button>
          <input v-model="searchTerm" placeholder="Pesquisar..." />
          <DashboardUserMenu compact />
        </div>
      </header>

      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <section class="users-v2-table-card">
        <div class="users-v2-table-wrap">
          <table>
            <thead>
              <tr>
                <th @click="toggleSort('id')">ID</th>
                <th @click="toggleSort('full_name')">Nome</th>
                <th @click="toggleSort('role')">Papel</th>
                <th @click="toggleSort('is_active')">Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in paginatedUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.full_name }}</td>
                <td>
                  <span class="users-role-badge" :class="roleClass(user.role)">{{ roleLabel(user.role) }}</span>
                </td>
                <td>
                  <span class="users-status-badge" :class="user.is_active ? 'active' : 'inactive'">
                    {{ user.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="users-actions-cell">
                  <div class="users-action-wrap">
                    <button class="btn btn-ghost" type="button" @click="openUserDetail(user.id)">{{ actionLabel }}</button>
                    <button class="users-dropdown-toggle" type="button" @click="toggleActionMenu(user.id)">⌄</button>
                    <div v-if="openActionMenuId === user.id" class="users-dropdown-menu">
                      <button type="button" @click="openUserDetail(user.id)">{{ actionLabel }}</button>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="users-v2-pagination">
          <span>Mostrando {{ pageStart }} - {{ pageEnd }} de {{ filteredUsers.length }} usuários</span>
          <div class="users-v2-pagination-actions">
            <button class="btn btn-ghost" type="button" @click="prevPage" :disabled="currentPage === 1">Anterior</button>
            <span>Página {{ currentPage }}</span>
            <button class="btn btn-ghost" type="button" @click="nextPage" :disabled="currentPage >= totalPages">Próxima</button>
          </div>
        </div>
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
import { useAuthStore } from '../stores/auth'

const users = ref([])
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const currentPage = ref(1)
const pageSize = 10
const sortBy = ref('id')
const sortDir = ref('asc')
const openActionMenuId = ref(0)
const router = useRouter()
const authStore = useAuthStore()
const actionLabel = computed(() => (authStore.user?.role === 'ADMIN' ? 'Ver / Editar' : 'Ver'))

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
    if (typeof va === 'boolean' && typeof vb === 'boolean') return (Number(va) - Number(vb)) * dir
    if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir
    return String(va ?? '').localeCompare(String(vb ?? '')) * dir
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedUsers.value.slice(start, start + pageSize)
})
const pageStart = computed(() => (filteredUsers.value.length ? (currentPage.value - 1) * pageSize + 1 : 0))
const pageEnd = computed(() => Math.min(currentPage.value * pageSize, filteredUsers.value.length))

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
  if (sortBy.value === column) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
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

function roleLabel(role) {
  if (role === 'REITOR') return 'REITOR'
  if (role === 'DIRETOR') return 'DIRETOR'
  if (role === 'CHEFE') return 'CHEFE DEPARTAMENTO'
  if (role === 'ADMIN') return 'ADMINISTRADOR'
  if (role === 'COORDENADOR') return 'COORDENADOR DE CURSO'
  return role
}

function roleClass(role) {
  if (role === 'REITOR') return 'reitor'
  if (role === 'DIRETOR') return 'diretor'
  if (role === 'CHEFE') return 'chefe'
  if (role === 'ADMIN') return 'admin'
  if (role === 'COORDENADOR') return 'coord'
  return 'neutral'
}

function openUserDetail(userId) {
  router.push({ name: 'user-detail', params: { id: userId } })
  openActionMenuId.value = 0
}

function goToCreateUser() {
  router.push({ name: 'user-create' })
}

function toggleActionMenu(id) {
  openActionMenuId.value = openActionMenuId.value === id ? 0 : id
}

async function listUsers() {
  try {
    resetMessages()
    const r = await api.get('/api/users')
    users.value = r.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(listUsers)
</script>
