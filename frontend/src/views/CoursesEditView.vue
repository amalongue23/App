<template>
  <CreateEntityLayout
    :title="isReadOnly ? 'Ver Curso' : 'Editar Curso'"
    :subtitle="isReadOnly ? 'Visualização do curso em tela separada.' : 'Atualize as informações do curso em tela separada.'"
    section-label="Cursos"
    section-route="/courses/manage"
  >
    <form class="create-form" @submit.prevent="saveCourse">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome do Curso</label>
        <input v-model.trim="form.name" :disabled="isReadOnly" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Código</label>
          <input v-model.trim="form.code" :disabled="isReadOnly" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Créditos</label>
          <input v-model.number="form.credits" type="number" min="0" :disabled="isReadOnly" required />
        </div>
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Unidade Orgânica</label>
          <select v-model.number="form.unit_id" :disabled="isReadOnly" required>
            <option :value="0" disabled>Selecione a unidade</option>
            <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
          </select>
        </div>
        <div class="create-field">
          <label class="create-label">* Departamento</label>
          <select v-model.number="form.department_id" :disabled="isReadOnly" required>
            <option :value="0" disabled>Selecione o departamento</option>
            <option v-for="d in departmentsByUnit" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/courses/manage">Cancelar</router-link>
        <button v-if="!isReadOnly" class="btn btn-primary" type="submit">Salvar Alterações</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import CreateEntityLayout from '../components/CreateEntityLayout.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const units = ref([])
const departments = ref([])
const successMessage = ref('')
const errorMessage = ref('')
const isReadOnly = computed(() => route.query.mode === 'view' || authStore.user?.role !== 'ADMIN')

const form = reactive({
  name: '',
  code: '',
  credits: 0,
  unit_id: 0,
  department_id: 0,
})

const departmentsByUnit = computed(() => {
  if (!form.unit_id) return departments.value
  return departments.value.filter((d) => d.unit_id === form.unit_id)
})

watch(
  () => form.unit_id,
  () => {
    if (form.department_id && !departmentsByUnit.value.some((d) => d.id === form.department_id)) {
      form.department_id = 0
    }
  },
)

function err(e) {
  return axios.isAxiosError(e) ? e.response?.data?.message || 'Erro na operação.' : 'Erro na operação.'
}

async function loadFilters() {
  const response = await api.get('/api/dashboard/filters')
  units.value = response.data.units || []
  departments.value = response.data.departments || []
}

async function loadCourse() {
  const id = Number(route.params.id)
  const responses = await Promise.all(departments.value.map((dep) => api.get(`/api/courses/by-department/${dep.id}`)))
  const rows = responses.flatMap((r) => r.data || [])
  const course = rows.find((item) => item.id === id)
  if (!course) throw new Error('Curso não encontrado.')
  form.name = course.name
  form.code = course.code
  form.credits = course.credits
  form.department_id = course.department_id
  form.unit_id = departments.value.find((d) => d.id === course.department_id)?.unit_id || 0
}

async function saveCourse() {
  if (isReadOnly.value) return
  try {
    successMessage.value = ''
    errorMessage.value = ''
    if (!form.department_id) {
      errorMessage.value = 'Selecione um departamento.'
      return
    }
    await api.put(`/api/courses/${route.params.id}`, {
      name: form.name,
      code: form.code,
      credits: form.credits,
      department_id: form.department_id,
    })
    successMessage.value = 'Curso atualizado com sucesso.'
    setTimeout(() => router.push({ name: 'courses-manage' }), 500)
  } catch (e) {
    errorMessage.value = err(e)
  }
}

onMounted(async () => {
  try {
    await loadFilters()
    await loadCourse()
  } catch (e) {
    errorMessage.value = err(e)
  }
})
</script>
