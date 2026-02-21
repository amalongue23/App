<template>
  <main class="admin-layout oc-layout">
    <SideNav />

    <section class="content-area oc-content">
      <header class="oc-topbar">
        <div class="oc-top-icons">
          <span class="oc-icon"></span>
          <span class="oc-icon"></span>
          <span class="oc-icon"></span>
          <span class="oc-avatar">{{ initials }}</span>
        </div>
      </header>

      <h1 class="oc-title">Centro de Operações</h1>
      <p class="oc-subtitle">Administração e Estrutura Académica</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <section class="oc-group">
        <h2>Estrutura Institucional</h2>
        <div class="oc-grid two">
          <article class="oc-card" v-if="isAdmin">
            <h3>Departamentos</h3>
            <p>{{ counts.departments }} registados</p>
            <div class="oc-actions">
              <router-link class="oc-btn manage" to="/departments/manage">Gerir</router-link>
              <router-link class="oc-btn new" to="/departments/create">+ Novo</router-link>
            </div>
          </article>
          <article class="oc-card" v-if="isChefe || isDirector || isReitor || isAdmin">
            <h3>Cursos</h3>
            <p>{{ counts.courses }} registados</p>
            <div class="oc-actions">
              <router-link class="oc-btn manage" to="/courses/manage">Gerir</router-link>
              <router-link v-if="!isChefe" class="oc-btn new" to="/courses/create">+ Novo</router-link>
            </div>
          </article>
          <article class="oc-card" v-if="!isChefe">
            <h3>Unidades Orgânicas</h3>
            <p>{{ counts.units }} registadas</p>
            <div class="oc-actions">
              <router-link class="oc-btn manage" to="/units/manage">Gerir</router-link>
              <router-link class="oc-btn new" to="/units/create">+ Novo</router-link>
            </div>
          </article>
          <article class="oc-card" v-if="!isChefe">
            <h3>Anos Académicos</h3>
            <p>{{ counts.academicYears }} registados</p>
            <div class="oc-actions">
              <router-link class="oc-btn manage" to="/academic-years">Gerir</router-link>
              <router-link class="oc-btn new" to="/academic-years">+ Novo</router-link>
            </div>
          </article>
        </div>
      </section>

      <section class="oc-lower">
        <div class="oc-col">
          <h2>Corpo Académico</h2>
          <article class="oc-line-card" v-if="isChefe || isDirector || isReitor || isAdmin">
            <div>
              <h3>Estudantes</h3>
              <p>{{ counts.students }} registados</p>
            </div>
            <div class="oc-actions small">
              <router-link class="oc-btn manage" to="/students/manage">Gerir</router-link>
              <router-link v-if="!isChefe" class="oc-btn new" to="/students/create">+</router-link>
            </div>
          </article>
          <article class="oc-line-card" v-if="!isChefe">
            <div>
              <h3>Usuários</h3>
              <p>{{ counts.users }} registados</p>
            </div>
            <div class="oc-actions small">
              <router-link class="oc-btn manage" to="/users">Gerir</router-link>
              <router-link class="oc-btn new" to="/users">+</router-link>
            </div>
          </article>
        </div>
        <div class="oc-col">
          <h2>Dados e Inteligência</h2>
          <article class="oc-line-card" v-if="!isChefe">
            <div>
              <h3>Datasets</h3>
              <p>Unificar e validar</p>
            </div>
            <div class="oc-actions small">
              <router-link class="oc-btn new" to="/datasets">+ Novo</router-link>
            </div>
          </article>
          <article class="oc-line-card">
            <div>
              <h3>Relatórios</h3>
              <p>Gerar relatórios</p>
            </div>
            <div class="oc-actions small">
              <router-link class="oc-btn manage" to="/reports">Gerar Relatórios</router-link>
            </div>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const counts = reactive({
  units: '-',
  departments: '-',
  courses: '-',
  academicYears: '-',
  students: '-',
  users: '-',
})
const errorMessage = ref('')

const initials = computed(() => {
  const name = authStore.user?.username || 'UL'
  return name.slice(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const role = authStore.user?.role
  if (role === 'REITOR') return 'Administrador'
  if (role === 'DIRETOR') return 'Diretor'
  if (role === 'CHEFE') return 'Chefe de Departamento'
  return 'Administrador'
})

const isChefe = computed(() => authStore.user?.role === 'CHEFE')
const isDirector = computed(() => authStore.user?.role === 'DIRETOR')
const isReitor = computed(() => authStore.user?.role === 'REITOR')
const isAdmin = computed(() => authStore.user?.role === 'ADMIN')

const showSettings = computed(() => !['REITOR', 'DIRETOR', 'CHEFE'].includes(authStore.user?.role || ''))

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}

function countFromResponse(data) {
  if (Array.isArray(data)) return data.length
  if (Array.isArray(data?.items)) return data.items.length
  return '-'
}

function dashboardEndpointByRole() {
  if (authStore.user?.role === 'REITOR' || authStore.user?.role === 'ADMIN') return '/api/dashboard/reitor'
  if (authStore.user?.role === 'DIRETOR') return '/api/dashboard/director'
  return '/api/dashboard/chief'
}

async function loadCounts() {
  errorMessage.value = ''
  try {
    const filtersResponse = await api.get('/api/dashboard/filters')
    const filtersData = filtersResponse.data || {}

    counts.units = countFromResponse(filtersData.units || [])
    counts.departments = countFromResponse(filtersData.departments || [])
    counts.courses = countFromResponse(filtersData.courses || [])
    counts.academicYears = countFromResponse(filtersData.anos || [])

    const firstYear = (filtersData.anos || [])[0]
    if (firstYear?.ano_academico_id && firstYear?.ano_lectivo) {
      const dashboardResponse = await api.get(dashboardEndpointByRole(), {
        params: {
          ano_academico_id: firstYear.ano_academico_id,
          ano_lectivo: firstYear.ano_lectivo,
        },
      })
      counts.students = dashboardResponse.data?.kpis?.students ?? '-'
    } else {
      counts.students = '-'
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Falha ao carregar contadores do centro de operações.'
    } else {
      errorMessage.value = 'Falha ao carregar contadores do centro de operações.'
    }
  }

  try {
    if (authStore.user?.role === 'CHEFE') {
      counts.users = '-'
    } else {
      const users = await api.get('/api/users')
      counts.users = countFromResponse(users.data)
    }
  } catch {
    counts.users = '-'
  }
}

onMounted(loadCounts)
</script>
