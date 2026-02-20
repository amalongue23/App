<template>
  <main class="admin-layout">
    <SideNav />
    <section class="content-area">
      <section class="ops-card">
      <OperationsNav title="Anos Académicos" subtitle="POST e GET /api/academic-years" />
      <form class="ops-form inline" @submit.prevent="createYear">
        <input v-model="yearLabel" placeholder="Ex: 2026-2027" required />
        <button class="btn btn-primary" type="submit">Abrir Ano</button>
      </form>
      <button class="btn btn-ghost" type="button" @click="listYears">Atualizar Lista</button>
      <div class="ops-table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Ano</th><th>Aberto</th></tr></thead>
          <tbody>
            <tr v-for="year in years" :key="year.id"><td>{{ year.id }}</td><td>{{ year.year_label }}</td><td>{{ year.is_open }}</td></tr>
          </tbody>
        </table>
      </div>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'

import OperationsNav from '../components/OperationsNav.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const yearLabel = ref('')
const years = ref([])
const errorMessage = ref('')

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function listYears() {
  try {
    errorMessage.value = ''
    const r = await api.get('/api/academic-years')
    years.value = r.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function createYear() {
  try {
    errorMessage.value = ''
    await api.post('/api/academic-years', { year_label: yearLabel.value })
    yearLabel.value = ''
    await listYears()
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(listYears)
</script>
