<template>
  <main class="admin-layout academic-detail-layout">
    <SideNav />

    <section class="content-area academic-detail-content">
      <header class="academic-v3-head">
        <div>
          <h1>Detalhes do Ano Académico</h1>
          <p>Início > Gestão de Ano > Detalhes do Ano Académico</p>
        </div>
        <DashboardUserMenu />
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="academic-detail-card">
        <header class="academic-detail-card-head">
          <h2>Ano Académico</h2>
        </header>

        <form class="academic-detail-form" @submit.prevent="saveYear">
          <input v-model.trim="yearLabel" placeholder="Ex: 2026-2027" required />

          <div class="academic-detail-status-box">
            <label>Status do Ano</label>
            <select v-model="status" disabled>
              <option value="ABERTO">Aberto</option>
            </select>
            <p class="academic-detail-warning">
              Ao fechar este ano, ele será marcado como concluído e não será mais possível editá-lo.
            </p>
          </div>

          <p v-if="yearPatternMessage" class="error">{{ yearPatternMessage }}</p>

          <div class="academic-detail-actions">
            <router-link class="btn btn-ghost" to="/academic-years">Cancelar</router-link>
            <button class="btn btn-primary" type="submit">Salvar Alterações</button>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const yearLabel = ref('')
const status = ref('ABERTO')
const yearPatternMessage = ref('')
const errorMessage = ref('')
const successMessage = ref('')

function parseError(error) {
  if (axios.isAxiosError(error)) return error.response?.data?.message || 'Erro na operação.'
  return 'Erro na operação.'
}

watch(yearLabel, () => {
  yearPatternMessage.value = ''
})

async function saveYear() {
  try {
    errorMessage.value = ''
    successMessage.value = ''
    yearPatternMessage.value = ''

    const label = yearLabel.value.trim()
    const match = /^(\d{4})-(\d{4})$/.exec(label)
    if (!match) {
      yearPatternMessage.value = 'Formato inválido. Use YYYY-YYYY.'
      return
    }
    const start = Number(match[1])
    const end = Number(match[2])
    if (end !== start + 1) {
      yearPatternMessage.value = 'Ano final inválido. Deve ser o ano inicial + 1.'
      return
    }

    await api.post('/api/academic-years', { year_label: label })
    successMessage.value = 'Ano académico aberto com sucesso.'
    setTimeout(() => router.push({ name: 'academic-years' }), 500)
  } catch (error) {
    errorMessage.value = parseError(error)
  }
}

onMounted(() => {
  const prefill = String(route.query.year_label || '').trim()
  if (prefill) yearLabel.value = prefill
})
</script>
