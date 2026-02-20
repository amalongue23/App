<template>
  <main class="admin-layout">
    <SideNav />
    <section class="content-area">
      <section class="ops-card">
      <OperationsNav title="Relatórios" subtitle="POST /api/reports/generate" />

      <form class="ops-form" @submit.prevent="generate">
        <input v-model="reportType" placeholder="report_type (ex: students_by_department)" required />
        <textarea v-model="paramsJson" class="ops-textarea" />
        <button class="btn btn-primary" type="submit">Gerar Relatório</button>
      </form>

      <pre class="ops-pre" v-if="result">{{ JSON.stringify(result, null, 2) }}</pre>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'

import OperationsNav from '../components/OperationsNav.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const reportType = ref('students_by_department')
const paramsJson = ref('{}')
const result = ref(null)
const errorMessage = ref('')

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function generate() {
  try {
    errorMessage.value = ''
    const payload = { report_type: reportType.value, params: JSON.parse(paramsJson.value || '{}') }
    const r = await api.post('/api/reports/generate', payload)
    result.value = r.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}
</script>
