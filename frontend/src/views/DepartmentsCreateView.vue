<template>
  <CreateEntityLayout
    title="Cadastro de Departamento"
    subtitle="Preencha as informações abaixo para cadastrar um novo departamento na aplicação."
    section-label="Departamentos"
    section-route="/departments/create"
  >
    <form class="create-form" @submit.prevent="createDepartment">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome do Departamento</label>
        <input v-model="form.name" placeholder="Digite o nome do departamento" required />
      </div>

      <div class="form-grid-2">
        <div class="create-field">
          <label class="create-label">* Código</label>
          <input v-model="form.code" placeholder="Digite o código" required />
        </div>
        <div class="create-field">
          <label class="create-label">* Unidade Orgânica</label>
          <select v-model.number="form.unit_id" required>
            <option :value="0" disabled>Selecione a unidade orgânica</option>
            <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }} ({{ u.code }})</option>
          </select>
        </div>
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/departments/manage">Cancelar</router-link>
        <button class="btn btn-primary" type="submit">Cadastrar Departamento</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>
<script setup>
import axios from 'axios'; import { onMounted, reactive, ref } from 'vue'
import CreateEntityLayout from '../components/CreateEntityLayout.vue'; import api from '../services/api'
const units=ref([]), successMessage=ref(''), errorMessage=ref(''); const form=reactive({ name:'', code:'', unit_id:0 })
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
async function loadUnits(){ const r=await api.get('/api/units'); units.value=r.data }
async function createDepartment(){ try{successMessage.value=''; errorMessage.value=''; await api.post('/api/departments', form); form.name=''; form.code=''; form.unit_id=0; successMessage.value='Departamento cadastrado com sucesso.' }catch(e){ errorMessage.value=err(e) }}
onMounted(async()=>{try{await loadUnits()}catch(e){errorMessage.value=err(e)}})
</script>
