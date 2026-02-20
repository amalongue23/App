<template>
  <CreateEntityLayout
    title="Cadastro de Estudante"
    subtitle="Preencha as informações abaixo para cadastrar um novo estudante na aplicação."
    section-label="Estudantes"
    section-route="/students/create"
  >
    <form class="create-form" @submit.prevent="createStudent">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome Completo</label>
        <input v-model="form.full_name" placeholder="Digite o nome completo" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Matrícula</label>
          <input v-model="form.registration_number" placeholder="Digite a matrícula" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Email</label>
          <input v-model="form.email" type="email" placeholder="Digite o email" required />
        </div>
      </div>

      <div class="create-field">
        <label class="create-label">* Departamento</label>
        <select v-model.number="form.department_id" required @change="onDepartmentChange">
          <option :value="0" disabled>Selecione o departamento</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>

      <div class="create-field">
        <label class="create-label">* Curso</label>
        <select v-model.number="form.course_id" required :disabled="!form.department_id">
          <option :value="0" disabled>Selecione o curso</option>
          <option v-for="c in filteredCourses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Data de Nascimento</label>
          <input v-model="form.birth_date" type="date" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Sexo</label>
          <select v-model="form.sex" required>
            <option value="" disabled>Selecione o sexo</option>
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
          </select>
        </div>
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/students/manage">Cancelar</router-link>
        <button class="btn btn-primary" type="submit">Cadastrar Estudante</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>
<script setup>
import axios from 'axios'; import { computed, onMounted, reactive, ref } from 'vue'
import CreateEntityLayout from '../components/CreateEntityLayout.vue'; import api from '../services/api'
const departments=ref([]), courses=ref([]), successMessage=ref(''), errorMessage=ref(''); const form=reactive({ full_name:'', registration_number:'', email:'', department_id:0, course_id:0, birth_date:'', sex:'' })
const filteredCourses = computed(() => courses.value.filter((c) => c.department_id === form.department_id))
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
async function loadDepartments(){ const r=await api.get('/api/dashboard/filters'); departments.value=r.data.departments||[]; courses.value=r.data.courses||[]; if(!form.department_id&&departments.value.length){form.department_id=departments.value[0].id; onDepartmentChange()} }
function onDepartmentChange(){ if(!filteredCourses.value.some((c)=>c.id===form.course_id)){ form.course_id = filteredCourses.value.length ? filteredCourses.value[0].id : 0 } }
async function createStudent(){ try{successMessage.value=''; errorMessage.value=''; await api.post('/api/students', form); form.full_name=''; form.registration_number=''; form.email=''; form.birth_date=''; form.sex=''; form.department_id=departments.value.length?departments.value[0].id:0; onDepartmentChange(); successMessage.value='Estudante cadastrado com sucesso.' }catch(e){errorMessage.value=err(e)} }
onMounted(async()=>{try{await loadDepartments()}catch(e){errorMessage.value=err(e)}})
</script>
