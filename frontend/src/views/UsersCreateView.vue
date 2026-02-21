<template>
  <CreateEntityLayout
    title="Cadastro de Usuários"
    subtitle="Preencha as informações abaixo para cadastrar um novo usuário na aplicação."
    section-label="Usuários"
    section-route="/users/create"
  >
    <form class="create-form users-create-form" @submit.prevent="createUser">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome Completo</label>
        <input v-model.trim="form.full_name" placeholder="Digite o nome completo" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Username</label>
          <input v-model.trim="form.username" placeholder="Digite o username" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Senha</label>
          <input v-model="form.password" type="password" placeholder="Digite a senha" required />
        </div>
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Papel</label>
          <select v-model="form.role" required>
            <option value="" disabled>Selecione o papel</option>
            <option value="ADMIN">ADMIN</option>
            <option value="REITOR">REITOR</option>
            <option value="DIRETOR">DIRECTOR</option>
            <option value="CHEFE">CHEFE</option>
            <option value="COORDENADOR">COORDENADOR</option>
            <option value="SECRETARIA">SECRETARIA</option>
            <option value="PROFESSOR">PROFESSOR</option>
            <option value="ASSISTENTE">ASSISTENTE</option>
          </select>
        </div>
        <div class="create-field" v-if="showUnitField">
          <label class="create-label">* Unidade Orgânica</label>
          <select v-model.number="form.unit_id" required>
            <option :value="0" disabled>Selecione a unidade orgânica</option>
            <option v-for="unit in units" :key="unit.id" :value="unit.id">{{ unit.name }} ({{ unit.code }})</option>
          </select>
        </div>
        <div class="create-field" v-if="showDepartmentField">
          <label class="create-label">* Departamento</label>
          <select v-model.number="form.department_id" required>
            <option :value="0" disabled>Selecione o departamento</option>
            <option v-for="dep in departments" :key="dep.id" :value="dep.id">{{ dep.name }} ({{ dep.code }})</option>
          </select>
        </div>
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">Data de Nascimento</label>
          <input v-model="form.birth_date" type="date" />
        </div>
        <div class="create-field">
          <label class="create-label">Sexo</label>
          <select v-model="form.sex">
            <option value="">Selecione</option>
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
          </select>
        </div>
      </div>

      <div class="create-field">
        <label class="create-label">Foto do Usuário</label>
        <input type="file" accept="image/*" @change="onFileChange" />
        <div v-if="form.photo_url" class="users-create-photo-preview">
          <img :src="form.photo_url" alt="Preview da foto" />
        </div>
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/users">Cancelar</router-link>
        <button class="btn btn-primary" type="submit">Cadastrar Usuário</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import CreateEntityLayout from '../components/CreateEntityLayout.vue'
import api from '../services/api'

const router = useRouter()
const units = ref([])
const departments = ref([])
const successMessage = ref('')
const errorMessage = ref('')
const form = reactive({
  full_name: '',
  username: '',
  password: '',
  role: '',
  unit_id: 0,
  department_id: 0,
  birth_date: '',
  sex: '',
  photo_url: '',
})

const showDepartmentField = computed(() => form.role === 'CHEFE')
const showUnitField = computed(() => form.role === 'DIRETOR')

watch(
  () => form.role,
  (role) => {
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

async function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) {
    form.photo_url = ''
    return
  }
  form.photo_url = await toBase64(file)
}

function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('Falha ao carregar imagem'))
    reader.readAsDataURL(file)
  })
}

async function loadFilters() {
  const [unitsRes, depsRes] = await Promise.allSettled([api.get('/api/units'), api.get('/api/departments')])
  if (unitsRes.status === 'fulfilled') units.value = unitsRes.value.data
  if (depsRes.status === 'fulfilled') departments.value = depsRes.value.data
}

function resetForm() {
  form.full_name = ''
  form.username = ''
  form.password = ''
  form.role = ''
  form.unit_id = 0
  form.department_id = 0
  form.birth_date = ''
  form.sex = ''
  form.photo_url = ''
}

async function createUser() {
  try {
    errorMessage.value = ''
    successMessage.value = ''
    const payload = {
      full_name: form.full_name,
      username: form.username,
      password: form.password,
      role: form.role,
      birth_date: form.birth_date || null,
      sex: form.sex || null,
      photo_url: form.photo_url || null,
    }
    if (showDepartmentField.value) payload.department_id = form.department_id || null
    if (showUnitField.value) payload.unit_id = form.unit_id || null

    await api.post('/api/users', payload)
    successMessage.value = 'Usuário cadastrado com sucesso.'
    resetForm()
    setTimeout(() => router.push({ name: 'users' }), 700)
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(async () => {
  try {
    await loadFilters()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
})
</script>
