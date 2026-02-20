<template>
  <main class="admin-layout student-layout">
    <SideNav />

    <section class="content-area student-content">
      <header class="student-topbar">
        <div class="student-breadcrumb">Gestão de Estudantes <span>›</span> Alterar Status do Estudante</div>
        <div class="student-icons">
          <span class="top-icon"></span>
          <span class="top-icon"></span>
          <span class="top-icon"></span>
          <span class="student-avatar">{{ initials }}</span>
        </div>
      </header>

      <h1 class="student-title">Gestão de Estudantes <span>›</span> Alterar Status do Estudante</h1>

      <section class="student-card student-status-card">
        <div class="status-profile">
          <div class="status-avatar"></div>
          <div class="status-profile-info">
            <h2>{{ student?.full_name || 'Estudante' }}</h2>
            <p>
              ID: {{ student?.registration_number || student?.id || '-' }}
              <span>•</span>
              Curso: {{ courseName || 'Não informado' }}
              <span>•</span>
              Departamento: {{ departmentName || '-' }}
            </p>
          </div>
          <div class="status-current">
            Status Atual:
            <span class="status-tag" :class="statusClass(currentStatus)">{{ statusLabel(currentStatus) }}</span>
          </div>
        </div>
      </section>

      <div v-if="errorMessage" class="error status-message">{{ errorMessage }}</div>
      <div v-if="successMessage" class="success status-message">{{ successMessage }}</div>

      <section class="student-status-grid">
        <article class="student-card student-status-card">
          <h3>Alterar Status Académico</h3>
          <div class="status-options">
            <button class="status-chip" :class="{ active: selectedStatus==='aprovado', disabled: isReadOnly }" :disabled="isReadOnly" @click="selectedStatus='aprovado'">
              Aprovado
            </button>
            <button class="status-chip" :class="{ active: selectedStatus==='reprovado', disabled: isReadOnly }" :disabled="isReadOnly" @click="selectedStatus='reprovado'">
              Reprovado
            </button>
            <button class="status-chip" :class="{ active: selectedStatus==='desistente', disabled: isReadOnly }" :disabled="isReadOnly" @click="selectedStatus='desistente'">
              Desistente
            </button>
          </div>

          <div class="status-form">
            <div class="status-field">
              <label>Ano</label>
              <select v-model.number="selectedYearId" @change="onYearChange">
                <option :value="0" disabled>Selecione o Ano</option>
                <option v-for="y in years" :key="y.ano_academico_id" :value="y.ano_academico_id">
                  {{ y.ano_lectivo }}
                </option>
              </select>
            </div>
          </div>

          <div class="status-actions">
            <button class="btn btn-ghost" type="button" @click="goBack">{{ isReadOnly ? 'Voltar' : 'Cancelar' }}</button>
            <button v-if="!isReadOnly" class="btn btn-primary" type="button" @click="saveStatus" :disabled="!canSave">
              Salvar Alteração
            </button>
          </div>
        </article>

        <aside class="student-card student-status-card">
          <h3>Histórico do Estudante</h3>
          <ul class="status-history">
            <li v-for="item in statusHistory" :key="item.yearId">
              <span class="status-year">{{ item.yearLabel }}</span>
              <span class="status-dot" :class="statusClass(item.status)"></span>
              <span class="status-tag" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
            </li>
          </ul>
        </aside>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import SideNav from '../components/SideNav.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const studentId = Number(route.params.id)
const student = ref(null)
const departments = ref([])
const courses = ref([])
const years = ref([])
const selectedYearId = ref(0)
const selectedStatus = ref('')
const currentStatus = ref('nao_definido')
const statusHistory = ref([])
const errorMessage = ref('')
const successMessage = ref('')

const initials = computed(() => {
  const name = authStore.user?.username || 'UL'
  return name.slice(0, 2).toUpperCase()
})

const isReadOnly = computed(() => authStore.user?.role === 'DIRETOR' || authStore.user?.role === 'REITOR')

const departmentName = computed(() => {
  const department = departments.value.find((d) => d.id === student.value?.department_id)
  return department?.name || ''
})

const courseName = computed(() => {
  if (student.value?.course_name) return student.value.course_name
  const course = courses.value.find((c) => c.id === student.value?.course_id)
  return course?.name || ''
})

const canSave = computed(() => selectedYearId.value > 0 && selectedStatus.value)

function statusLabel(value) {
  if (!value || value === 'nao_definido') return 'Não definido'
  if (value === 'aprovado') return 'Aprovado'
  if (value === 'reprovado') return 'Reprovado'
  if (value === 'desistente') return 'Desistente'
  if (value === 'active') return 'Em Curso'
  return value
}

function statusClass(value) {
  if (value === 'aprovado') return 'status-ok'
  if (value === 'reprovado') return 'status-bad'
  if (value === 'desistente') return 'status-warn'
  if (value === 'active') return 'status-active'
  return 'status-neutral'
}

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  departments.value = response.data.departments || []
  courses.value = response.data.courses || []
  years.value = response.data.anos || []
  if (!selectedYearId.value && years.value.length) {
    selectedYearId.value = years.value[0].ano_academico_id
  }
}

async function loadStudent() {
  const response = await api.get(`/api/students/${studentId}`)
  student.value = response.data
}

async function loadCurrentStatus() {
  if (!selectedYearId.value) return
  const response = await api.get(`/api/students/${studentId}/status`, {
    params: { academic_year_id: selectedYearId.value },
  })
  currentStatus.value = response.data?.status || 'nao_definido'
  selectedStatus.value = currentStatus.value === 'nao_definido' ? '' : currentStatus.value
}

async function loadHistory() {
  if (!years.value.length) {
    statusHistory.value = []
    return
  }
  const entries = await Promise.all(
    years.value.map(async (year) => {
      try {
        const response = await api.get(`/api/students/${studentId}/status`, {
          params: { academic_year_id: year.ano_academico_id },
        })
        return {
          yearId: year.ano_academico_id,
          yearLabel: year.ano_lectivo,
          status: response.data?.status || 'nao_definido',
        }
      } catch {
        return {
          yearId: year.ano_academico_id,
          yearLabel: year.ano_lectivo,
          status: 'nao_definido',
        }
      }
    }),
  )
  statusHistory.value = entries
}

async function onYearChange() {
  await loadCurrentStatus()
}

async function saveStatus() {
  errorMessage.value = ''
  successMessage.value = ''
  try {
    if (isReadOnly.value) {
      errorMessage.value = 'Perfil não autorizado a alterar o status.'
      return
    }
    if (!canSave.value) {
      errorMessage.value = 'Selecione o ano e o status.'
      return
    }
    await api.put(`/api/students/${studentId}/status`, {
      academic_year_id: selectedYearId.value,
      status: selectedStatus.value,
    })
    successMessage.value = 'Status atualizado com sucesso.'
    await loadCurrentStatus()
    await loadHistory()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

function goBack() {
  router.push({ name: 'students-manage' })
}

onMounted(async () => {
  try {
    await loadFilters()
    await loadStudent()
    await loadCurrentStatus()
    await loadHistory()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
})
</script>
