<template>
  <CreateEntityLayout
    title="Cadastro de Unidade Orgânica"
    subtitle="Preencha as informações abaixo para cadastrar uma nova unidade orgânica na aplicação."
    section-label="Unidades Orgânicas"
    section-route="/units/create"
  >
    <form class="create-form" @submit.prevent="createUnit">
      <p class="success" v-if="successMessage">{{ successMessage }}</p>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

      <div class="create-field">
        <label class="create-label">* Nome da Unidade</label>
        <input v-model="form.name" placeholder="Digite o nome da unidade" required />
      </div>

      <div class="create-field">
        <label class="create-label">* Código</label>
        <input v-model="form.code" placeholder="Digite o código" required />
      </div>

      <div class="create-field">
        <label class="create-label">Descrição</label>
        <input v-model="form.description" placeholder="Descrição da unidade (opcional)" />
      </div>

      <div class="create-actions">
        <router-link class="btn btn-ghost" to="/units/manage">Cancelar</router-link>
        <button class="btn btn-primary" type="submit">Cadastrar Unidade</button>
      </div>
    </form>
  </CreateEntityLayout>
</template>
<script setup>
import axios from 'axios'; import { reactive, ref } from 'vue'
import CreateEntityLayout from '../components/CreateEntityLayout.vue'; import api from '../services/api'
const form = reactive({ name:'', code:'', description:'' }); const successMessage=ref(''); const errorMessage=ref('')
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
async function createUnit(){ try{ successMessage.value=''; errorMessage.value=''; await api.post('/api/units', form); form.name=''; form.code=''; form.description=''; successMessage.value='Unidade cadastrada com sucesso.' }catch(e){ errorMessage.value=err(e) } }
</script>
