<template>
  <main class="admin-layout">
    <SideNav />
    <section class="content-area">
      <header class="topbar">
        <div>Ferramentas de Dataset</div>
        <DashboardUserMenu />
      </header>
      <section class="ops-card">
      <OperationsNav title="Ferramentas de Dataset" subtitle="POST /api/datasets/unify e POST /api/datasets/validate" />

      <section class="ops-grid two">
        <article>
          <h3>Unificar Fontes</h3>
          <p class="ops-tip">Formato: array de fontes, cada fonte é array de objetos.</p>
          <textarea v-model="sourcesJson" class="ops-textarea" />
          <button class="btn btn-primary" type="button" @click="unify">Unificar</button>
          <pre class="ops-pre" v-if="unifyResult">{{ JSON.stringify(unifyResult, null, 2) }}</pre>
        </article>

        <article>
          <h3>Validar Dataset</h3>
          <p class="ops-tip">Formato: array de objetos.</p>
          <textarea v-model="datasetJson" class="ops-textarea" />
          <button class="btn btn-primary" type="button" @click="validate">Validar</button>
          <pre class="ops-pre" v-if="validateResult">{{ JSON.stringify(validateResult, null, 2) }}</pre>
        </article>
      </section>

      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import OperationsNav from '../components/OperationsNav.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const errorMessage = ref('')
const unifyResult = ref(null)
const validateResult = ref(null)

const sourcesJson = ref(`[
  [
    {"id": 1, "name": "Ana", "registration_number": "A-01"}
  ],
  [
    {"id": 1, "name": "Ana Paula", "registration_number": "A-01"},
    {"id": 2, "name": "Bruno", "registration_number": "B-02"}
  ]
]`)

const datasetJson = ref(`[
  {"id": 1, "name": "Ana", "registration_number": "A-01"},
  {"id": 2, "name": "Bruno", "registration_number": "B-02"}
]`)

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

async function unify() {
  try {
    errorMessage.value = ''
    const payload = { sources: JSON.parse(sourcesJson.value) }
    const r = await api.post('/api/datasets/unify', payload)
    unifyResult.value = r.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

async function validate() {
  try {
    errorMessage.value = ''
    const payload = { dataset: JSON.parse(datasetJson.value) }
    const r = await api.post('/api/datasets/validate', payload)
    validateResult.value = r.data
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}
</script>
