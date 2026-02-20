<template>
  <CreateEntityLayout
    title="Cadastro de Curso"
    subtitle="Preencha as informações abaixo para cadastrar um novo curso na aplicação."
    section-label="Cursos"
    section-route="/courses/create"
  >
    <form class="create-form" @submit.prevent="createCourse">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome do Curso</label>
        <input v-model="form.name" placeholder="Digite o nome do curso" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Código</label>
          <input v-model="form.code" placeholder="Digite o código" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Créditos</label>
          <input v-model.number="form.credits" type="number" min="0" placeholder="Créditos" required />
        </div>
      </div>

      <div class="create-field">
        <label class="create-label">* Departamento</label>
        <select v-model.number="form.department_id" required>
          <option :value="0" disabled>Selecione o departamento</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }} ({{ d.code }})</option>
        </select>
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/courses/manage">Cancelar</router-link>
        <button class="btn btn-primary" type="submit">Cadastrar Curso</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>
<script setup>
import axios from 'axios'; import { onMounted, reactive, ref } from 'vue'
import CreateEntityLayout from '../components/CreateEntityLayout.vue'; import api from '../services/api'
const departments=ref([]), successMessage=ref(''), errorMessage=ref(''); const form=reactive({ name:'', code:'', department_id:0, credits:0 })
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
async function loadDepartments(){ const r=await api.get('/api/departments'); departments.value=r.data }
async function createCourse(){ try{successMessage.value=''; errorMessage.value=''; await api.post('/api/courses', form); form.name=''; form.code=''; form.department_id=0; form.credits=0; successMessage.value='Curso cadastrado com sucesso.' }catch(e){errorMessage.value=err(e)} }
onMounted(async()=>{try{await loadDepartments()}catch(e){errorMessage.value=err(e)}})
</script>
