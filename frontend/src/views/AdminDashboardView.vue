<template>
  <main class="admin-layout admin-system-layout">
    <SideNav />

    <section class="content-area admin-system-content">
      <header class="admin-system-head">
        <div>
          <h1>Painel do <span>Administrador do Sistema</span></h1>
          <p>Gestão técnica, controlo global e monitorização operacional da plataforma.</p>
        </div>
        <DashboardUserMenu />
      </header>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <section class="admin-system-kpis">
        <article class="admin-kpi">
          <div class="admin-kpi-icon users">👥</div>
          <div>
            <div class="v">{{ dashboard.kpis.total_users }}</div>
            <div class="l">Total de Utilizadores do Sistema</div>
          </div>
        </article>
        <article class="admin-kpi">
          <div class="admin-kpi-icon profiles">🛡️</div>
          <div>
            <div class="v">{{ dashboard.kpis.active_profiles }}</div>
            <div class="l">Perfis Ativos</div>
          </div>
        </article>
        <article class="admin-kpi">
          <div class="admin-kpi-icon years">📅</div>
          <div>
            <div class="v">{{ dashboard.kpis.academic_years }}</div>
            <div class="l">Anos Académicos Configurados</div>
          </div>
        </article>
        <article class="admin-kpi">
          <div class="admin-kpi-icon system">🕒</div>
          <div>
            <div class="v online">{{ dashboard.kpis.system_status || 'Online' }}</div>
            <div class="l">Estado do Sistema</div>
          </div>
        </article>
      </section>

      <section class="admin-system-grid">
        <article class="admin-panel wide">
          <h3>Atividade do Sistema</h3>
          <svg viewBox="0 0 100 44" class="chart-svg admin-activity-chart" preserveAspectRatio="none">
            <polyline class="chart-line approved" :points="loginsPoints" />
            <polyline class="chart-line failed" :points="operationsPoints" />
            <polyline class="chart-line neutral" :points="creationsPoints" />
          </svg>
          <div class="chart-axis">
            <span v-for="label in dashboard.series.labels" :key="label">{{ label }}</span>
          </div>
          <div class="chart-legend-inline">
            <span><i class="dot-line approved"></i>Logins</span>
            <span><i class="dot-line failed"></i>Operações Executadas</span>
            <span><i class="dot-line neutral"></i>Criação de Registos</span>
          </div>
          <div class="admin-activity-kpis">
            <div>
              <strong>{{ dashboard.kpis.logins_total }}</strong>
              <small>Logins</small>
            </div>
            <div>
              <strong>{{ dashboard.kpis.operations_total }}</strong>
              <small>Operações Executadas</small>
            </div>
            <div>
              <strong>{{ dashboard.kpis.creations_total }}</strong>
              <small>Criação de Registos</small>
            </div>
          </div>
        </article>

        <article class="admin-panel admin-side-panel">
          <div class="admin-side-top">
            <h3>Distribuição de Perfis</h3>
            <button type="button">Ver todas</button>
          </div>
          <div class="admin-side-donut-wrap">
            <div class="admin-donut" :style="{ background: donutGradient }">
              <span>{{ donutTotal }}</span>
            </div>
          </div>
          <ul class="legend admin-role-list">
            <li v-for="(item, idx) in dashboard.role_distribution" :key="item.role">
              <span class="dot" :style="{ background: donutColor(idx) }"></span>
              <span class="role-label">{{ item.label }}</span>
              <strong>{{ item.count }}</strong>
            </li>
          </ul>
          <div class="admin-side-top recent">
            <h3>Atividades Recentes</h3>
            <button type="button">⌄</button>
          </div>
          <ul class="admin-feed-compact">
            <li v-for="item in dashboard.recent_activities.slice(0, 4)" :key="`compact-${item.created_at}-${item.message}`">
              <div>
                <strong>{{ item.actor }}</strong>
                <p>{{ item.message }}</p>
              </div>
              <span>{{ relative(item.created_at) }}</span>
            </li>
          </ul>
        </article>
      </section>

      <section class="admin-system-grid admin-system-grid-bottom">
        <article class="admin-panel wide">
          <h3>Monitorização Técnica</h3>
          <div class="admin-tech-grid">
            <div>
              <strong>{{ dashboard.technical.api_response_ms }}ms</strong>
              <small>Tempo médio de resposta da API</small>
            </div>
            <div>
              <strong>{{ dashboard.technical.last_backup_label }}</strong>
              <small>Último backup realizado</small>
            </div>
            <div>
              <strong>{{ dashboard.technical.app_version }}</strong>
              <small>Versão da Aplicação</small>
            </div>
          </div>
          <div class="admin-competitors-row">
            <h4>Base de Competitors</h4>
          </div>
        </article>

        <article class="admin-panel admin-activities-panel">
          <div class="admin-side-top">
            <h3>Atividades Recentes</h3>
            <button type="button">🔎</button>
          </div>
          <ul class="admin-feed">
            <li v-for="item in dashboard.recent_activities.slice(0, 6)" :key="`full-${item.created_at}-${item.message}`">
              <div>
                <strong>{{ item.actor }}</strong>
                <p>{{ item.message }}</p>
              </div>
              <span>{{ relative(item.created_at) }}</span>
            </li>
          </ul>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'

import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'
import api from '../services/api'
const errorMessage = ref('')
const dashboard = reactive({
  kpis: { total_users: 0, active_profiles: 0, academic_years: 0, logins_total: 0, operations_total: 0, creations_total: 0 },
  series: { labels: [], logins: [], operations: [], creations: [] },
  role_distribution: [],
  recent_activities: [],
  technical: { api_response_ms: 0, last_backup_label: '-', app_version: '-' },
})

const maxSeries = computed(() => Math.max(1, ...dashboard.series.logins, ...dashboard.series.operations, ...dashboard.series.creations))

const loginsPoints = computed(() => buildSeriesPoints(dashboard.series.logins, maxSeries.value))
const operationsPoints = computed(() => buildSeriesPoints(dashboard.series.operations, maxSeries.value))
const creationsPoints = computed(() => buildSeriesPoints(dashboard.series.creations, maxSeries.value))

const donutGradient = computed(() => {
  if (!dashboard.role_distribution.length) return 'conic-gradient(#ddd 0 100%)'
  let offset = 0
  const slices = dashboard.role_distribution.map((item, idx) => {
    const start = offset
    offset += Number(item.percentage || 0)
    return `${donutColor(idx)} ${start}% ${offset}%`
  })
  return `conic-gradient(${slices.join(', ')})`
})
const donutTotal = computed(() => dashboard.role_distribution.reduce((total, item) => total + Number(item.count || 0), 0))

function buildSeriesPoints(values, maxValue) {
  if (!values?.length) return ''
  const xStep = values.length > 1 ? 100 / (values.length - 1) : 100
  return values
    .map((value, index) => {
      const x = (index * xStep).toFixed(2)
      const y = (44 - (Math.max(0, value) / maxValue) * 38).toFixed(2)
      return `${x},${y}`
    })
    .join(' ')
}

function donutColor(index) {
  const palette = ['#d3a23a', '#db786e', '#6a7dd5', '#b9a06a', '#98a9da', '#8ebf9b', '#b6a2d4']
  return palette[index % palette.length]
}

function relative(iso) {
  if (!iso) return '-'
  const diffMs = Date.now() - new Date(iso).getTime()
  const hours = Math.max(1, Math.floor(diffMs / 3600000))
  if (hours < 24) return `${hours} h`
  const days = Math.floor(hours / 24)
  return `${days} d`
}

async function loadDashboard() {
  try {
    errorMessage.value = ''
    const response = await api.get('/api/dashboard/admin')
    Object.assign(dashboard, response.data)
  } catch (error) {
    if (axios.isAxiosError(error)) errorMessage.value = error.response?.data?.message || 'Falha ao carregar dashboard.'
    else errorMessage.value = 'Falha ao carregar dashboard.'
  }
}

onMounted(loadDashboard)
</script>
