<template>
  <main class="admin-layout user-detail-layout">
    <SideNav />

    <section class="content-area user-detail-content user-detail-v3">
      <header class="user-detail-toolbar">
        <div class="user-detail-toolbar-actions">
          <button type="button">🔔</button>
          <button type="button">⚙</button>
        </div>
        <DashboardUserMenu compact />
      </header>

      <header class="user-detail-head">
        <div>
          <h1>{{ isAdmin ? 'Editar Usuário' : 'Ver Usuário' }}</h1>
          <p>Início > Usuários > {{ user.full_name || 'Detalhe' }}</p>
        </div>
        <button v-if="isAdmin" type="button" class="btn btn-danger" @click="deactivateUser">Excluir Usuário</button>
      </header>

      <section class="user-detail-card">
        <div class="user-detail-profile">
          <div class="user-detail-avatar-block">
            <img v-if="user.photo_url" class="user-detail-avatar-image" :src="user.photo_url" alt="Foto do usuário" />
            <div v-else class="user-detail-avatar">{{ initials }}</div>
          </div>
          <div class="user-detail-main">
            <h2>{{ user.full_name || '-' }}</h2>
            <p>@{{ user.username || '-' }}</p>
            <div class="user-detail-meta">
              <span class="users-role-badge" :class="roleClass(form.role || user.role)">{{ roleLabel(form.role || user.role) }}</span>
              <label class="user-detail-active">
                <input v-model="form.is_active" type="checkbox" :disabled="!isAdmin" />
                <span>{{ form.is_active ? 'Ativo' : 'Inativo' }}</span>
              </label>
            </div>
          </div>
          <div class="user-detail-current">
            <span>Status Atual:</span>
            <strong :class="form.is_active ? 'ok' : 'off'">{{ form.is_active ? 'Ativo' : 'Inativo' }}</strong>
          </div>
        </div>

        <div class="user-detail-tabs">
          <button type="button" :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">Informações</button>
          <button type="button" :class="{ active: activeTab === 'activities' }" @click="activeTab = 'activities'">Atividades</button>
        </div>

        <div v-if="activeTab === 'info'" class="user-detail-form-wrap">
          <form class="user-detail-form" @submit.prevent="saveUser">
            <label>
              <span>Nome Completo</span>
              <input v-model="form.full_name" :disabled="!isAdmin" required />
            </label>
            <label>
              <span>Username</span>
              <input v-model="form.username" :disabled="!isAdmin" required />
            </label>
            <label>
              <span>Papel</span>
              <select v-model="form.role" :disabled="!isAdmin" required>
                <option value="ADMIN">ADMIN</option>
                <option value="REITOR">REITOR</option>
                <option value="DIRETOR">DIRETOR</option>
                <option value="CHEFE">CHEFE</option>
                <option value="COORDENADOR">COORDENADOR</option>
                <option value="SECRETARIA">SECRETARIA</option>
                <option value="PROFESSOR">PROFESSOR</option>
                <option value="ASSISTENTE">ASSISTENTE</option>
              </select>
            </label>
            <label v-if="showUnitField">
              <span>Unidade Orgânica</span>
              <select v-model.number="form.unit_id" :disabled="!isAdmin" required>
                <option :value="0" disabled>Selecione a unidade</option>
                <option v-if="form.unit_id && !hasUnitOption(form.unit_id)" :value="form.unit_id">Unidade #{{ form.unit_id }}</option>
                <option v-for="unit in units" :key="unit.id" :value="unit.id">{{ unit.name }} ({{ unit.code }})</option>
              </select>
            </label>
            <label v-if="showDepartmentField">
              <span>Departamento</span>
              <select v-model.number="form.department_id" :disabled="!isAdmin" required>
                <option :value="0" disabled>Selecione o departamento</option>
                <option v-if="form.department_id && !hasDepartmentOption(form.department_id)" :value="form.department_id">Departamento #{{ form.department_id }}</option>
                <option v-for="dep in departments" :key="dep.id" :value="dep.id">{{ dep.name }} ({{ dep.code }})</option>
              </select>
            </label>
            <label>
              <span>Data de Nascimento</span>
              <input v-model="form.birth_date" type="date" :disabled="!isAdmin" />
            </label>
            <label>
              <span>Sexo</span>
              <select v-model="form.sex" :disabled="!isAdmin">
                <option value="">Não informado</option>
                <option value="M">Masculino</option>
                <option value="F">Feminino</option>
              </select>
            </label>
            <label v-if="isAdmin">
              <span>Nova Senha (opcional)</span>
              <input v-model="form.password" type="password" placeholder="Deixe vazio para manter" />
            </label>
            <div class="user-detail-actions">
              <button type="button" class="btn btn-ghost" @click="goBack">Cancelar</button>
              <button v-if="isAdmin" class="btn btn-primary" type="submit">Salvar Alterações</button>
            </div>
          </form>
        </div>

        <div v-else class="user-activities-wrap">
          <div class="user-activities-filters">
            <select v-model="activityFilters.module">
              <option value="">Todos módulos</option>
              <option value="AUTH">Autenticação</option>
              <option value="USER">Usuários</option>
              <option value="UNIT">Unidades</option>
              <option value="DEPARTMENT">Departamentos</option>
              <option value="COURSE">Cursos</option>
              <option value="STUDENT">Estudantes</option>
              <option value="ACADEMIC_YEAR">Ano Acadêmico</option>
              <option value="DATASET">Datasets</option>
              <option value="REPORT">Relatórios</option>
            </select>
            <select v-model="activityFilters.action">
              <option value="">Todas ações</option>
              <option value="LOGIN">Login</option>
              <option value="USER_CREATED">Usuário criado</option>
              <option value="USER_UPDATED">Usuário atualizado</option>
              <option value="USER_DEACTIVATED">Usuário desativado</option>
              <option value="UNIT_CREATED">Unidade criada</option>
              <option value="UNIT_UPDATED">Unidade atualizada</option>
              <option value="DEPARTMENT_CREATED">Departamento criado</option>
              <option value="DEPARTMENT_UPDATED">Departamento atualizado</option>
              <option value="COURSE_CREATED">Curso criado</option>
              <option value="COURSE_UPDATED">Curso atualizado</option>
              <option value="STUDENT_CREATED">Estudante criado</option>
              <option value="STUDENT_UPDATED">Estudante atualizado</option>
              <option value="STUDENT_STATUS_UPDATED">Status estudante</option>
              <option value="STUDENT_CONTROL_TABLE_CREATED">Tabela de controlo</option>
              <option value="ACADEMIC_YEAR_OPENED">Ano aberto</option>
              <option value="DATASET_UNIFIED">Dataset unificado</option>
              <option value="DATASET_VALIDATED">Dataset validado</option>
              <option value="REPORT_GENERATED">Relatório gerado</option>
            </select>
            <select v-model.number="activityFilters.days">
              <option :value="0">Todo período</option>
              <option :value="7">Últimos 7 dias</option>
              <option :value="30">Últimos 30 dias</option>
              <option :value="90">Últimos 90 dias</option>
            </select>
            <input v-model.trim="activityFilters.q" placeholder="Pesquisar descrição..." />
            <button type="button" class="btn btn-primary" @click="loadActivities">Aplicar</button>
            <button type="button" class="btn btn-ghost" @click="clearActivityFilters">Limpar</button>
          </div>
          <p v-if="!activities.length" class="muted">Sem atividades registadas para este usuário.</p>
          <ul v-else class="user-activities-list">
            <li v-for="item in activities" :key="item.id">
              <div class="user-activities-main">
                <strong>{{ formatAction(item.action) }}</strong>
                <p>{{ item.description }}</p>
              </div>
              <small>{{ formatDate(item.created_at) }}<span v-if="item.actor_username"> • por {{ item.actor_username }}</span></small>
            </li>
          </ul>
        </div>
      </section>

      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const user = ref({})
const activities = ref([])
const units = ref([])
const departments = ref([])
const activeTab = ref('info')
const successMessage = ref('')
const errorMessage = ref('')
const form = reactive({
  full_name: '',
  username: '',
  role: 'DIRETOR',
  is_active: true,
  password: '',
  birth_date: '',
  sex: '',
  unit_id: 0,
  department_id: 0,
})
const activityFilters = reactive({
  module: '',
  action: '',
  q: '',
  days: 30,
})

const isAdmin = computed(() => authStore.user?.role === 'ADMIN')
const showDepartmentField = computed(() => form.role === 'CHEFE')
const showUnitField = computed(() => form.role === 'DIRETOR')
const initials = computed(() => {
  const name = user.value.full_name || ''
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('') || 'US'
})

watch(
  () => form.role,
  (role) => {
    if (!isAdmin.value) return
    if (role === 'CHEFE') {
      form.unit_id = 0
      return
    }
    if (role === 'DIRETOR') {
      form.department_id = 0
      return
    }
    form.unit_id = 0
    form.department_id = 0
  },
)

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

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('pt-PT')
}

function formatAction(action) {
  if (action === 'LOGIN') return 'Login'
  if (action === 'USER_CREATED') return 'Cadastro de usuário'
  if (action === 'USER_UPDATED') return 'Atualização de usuário'
  if (action === 'USER_DEACTIVATED') return 'Desativação de usuário'
  if (action === 'UNIT_CREATED') return 'Cadastro de unidade orgânica'
  if (action === 'UNIT_UPDATED') return 'Atualização de unidade orgânica'
  if (action === 'DEPARTMENT_CREATED') return 'Cadastro de departamento'
  if (action === 'DEPARTMENT_UPDATED') return 'Atualização de departamento'
  if (action === 'COURSE_CREATED') return 'Cadastro de curso'
  if (action === 'COURSE_UPDATED') return 'Atualização de curso'
  if (action === 'STUDENT_CREATED') return 'Cadastro de estudante'
  if (action === 'STUDENT_UPDATED') return 'Atualização de estudante'
  if (action === 'STUDENT_STATUS_UPDATED') return 'Alteração de status de estudante'
  if (action === 'STUDENT_CONTROL_TABLE_CREATED') return 'Criação da tabela de controlo'
  if (action === 'ACADEMIC_YEAR_OPENED') return 'Abertura de ano acadêmico'
  if (action === 'DATASET_UNIFIED') return 'Unificação de dataset'
  if (action === 'DATASET_VALIDATED') return 'Validação de dataset'
  if (action === 'REPORT_GENERATED') return 'Geração de relatório'
  return action
}

function hasUnitOption(unitId) {
  return units.value.some((item) => Number(item.id) === Number(unitId))
}

function hasDepartmentOption(departmentId) {
  return departments.value.some((item) => Number(item.id) === Number(departmentId))
}

function goBack() {
  router.push({ name: 'users' })
}

async function loadUser() {
  try {
    errorMessage.value = ''
    const { data } = await api.get(`/api/users/${route.params.id}`)
    user.value = data
    form.full_name = data.full_name || ''
    form.username = data.username || ''
    form.role = data.role || 'DIRETOR'
    form.is_active = Boolean(data.is_active)
    form.birth_date = data.birth_date || ''
    form.sex = data.sex || ''
    form.unit_id = Number(data.unit_id || 0)
    form.department_id = Number(data.department_id || 0)
    form.password = ''
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function loadScopeOptions() {
  if (!isAdmin.value) return
  try {
    const [unitsRes, depsRes] = await Promise.allSettled([api.get('/api/units'), api.get('/api/departments')])
    if (unitsRes.status === 'fulfilled') units.value = unitsRes.value.data
    if (depsRes.status === 'fulfilled') departments.value = depsRes.value.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function loadActivities() {
  try {
    const params = {
      module: activityFilters.module || undefined,
      action: activityFilters.action || undefined,
      q: activityFilters.q || undefined,
      days: activityFilters.days > 0 ? activityFilters.days : undefined,
    }
    const { data } = await api.get(`/api/users/${route.params.id}/activities`, { params })
    activities.value = data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

function clearActivityFilters() {
  activityFilters.module = ''
  activityFilters.action = ''
  activityFilters.q = ''
  activityFilters.days = 30
  loadActivities()
}

async function saveUser() {
  if (!isAdmin.value) return
  try {
    errorMessage.value = ''
    successMessage.value = ''
    const payload = {
      full_name: form.full_name,
      username: form.username,
      role: form.role,
      is_active: form.is_active,
      birth_date: form.birth_date || null,
      sex: form.sex || null,
    }
    if (showDepartmentField.value) {
      if (!form.department_id) {
        errorMessage.value = 'Selecione o departamento para o papel CHEFE.'
        return
      }
      payload.department_id = form.department_id
      payload.unit_id = null
    } else if (showUnitField.value) {
      if (!form.unit_id) {
        errorMessage.value = 'Selecione a unidade orgânica para o papel DIRETOR.'
        return
      }
      payload.unit_id = form.unit_id
      payload.department_id = null
    } else {
      payload.unit_id = null
      payload.department_id = null
    }
    if (form.password.trim()) payload.password = form.password.trim()
    await api.put(`/api/users/${route.params.id}`, payload)
    successMessage.value = 'Usuário atualizado com sucesso.'
    await loadUser()
    await loadActivities()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function deactivateUser() {
  if (!isAdmin.value) return
  try {
    errorMessage.value = ''
    successMessage.value = ''
    await api.delete(`/api/users/${route.params.id}`)
    successMessage.value = 'Usuário desativado com sucesso.'
    await loadUser()
    await loadActivities()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(async () => {
  await loadUser()
  await loadScopeOptions()
  await loadActivities()
})
</script>
