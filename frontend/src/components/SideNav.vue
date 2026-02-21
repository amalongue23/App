<template>
  <aside class="sidebar side-nav">
    <div>
      <div class="brand-strip">
        <AppLogo />
      </div>
      <p class="menu-title">Menu Principal</p>
      <nav class="menu-list">
        <router-link
          v-for="item in visibleItems"
          :key="item.key"
          class="menu-item menu-link"
          :class="{ active: isActive(item.key) }"
          :to="item.to"
        >
          <span class="menu-item-icon" v-html="item.icon"></span>
          <span>{{ item.label }}</span>
        </router-link>
        <button v-if="showSettings" class="menu-item" type="button">
          <span class="menu-item-icon" v-html="icons.settings"></span>
          <span>Configurações</span>
        </button>
      </nav>
    </div>
    <div>
      <div class="profile-card">
        <div class="profile-avatar">{{ initials }}</div>
        <div>
          <div class="profile-name">{{ authStore.user?.username || 'Utilizador' }}</div>
          <div class="profile-role">{{ roleLabel }}</div>
        </div>
      </div>
      <button class="menu-item logout-item" type="button" @click="logout">
        <span class="menu-item-icon" v-html="icons.logout"></span>
        <span>Sair</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppLogo from './AppLogo.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const icons = {
  dashboard:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11.5 12 4l9 7.5v7.5a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  statistics:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 20V10m7 10V4m7 16v-7" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  academic:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16v10H4zM7 17v3h10v-3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  units:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 21h16M6 21V7l6-4 6 4v14M9 21v-6h6v6" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  departments:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16v12H4zM8 7V4h8v3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  courses:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v14H4zM8 9h8M8 13h8" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  students:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4zm-7 9a7 7 0 0 1 14 0" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  users:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 11a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm8 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3zM3 20a5 5 0 0 1 10 0m-3 0a5 5 0 0 1 10 0" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  reports:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l3 3v15H6zM9 12h6M9 16h6M9 8h3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
  settings:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8.5a3.5 3.5 0 1 0 3.5 3.5A3.5 3.5 0 0 0 12 8.5zm8 3.5-1.8.6a6.8 6.8 0 0 1-.7 1.7l1 1.6-2 2-1.6-1a6.8 6.8 0 0 1-1.7.7L12 20l-.6-1.8a6.8 6.8 0 0 1-1.7-.7l-1.6 1-2-2 1-1.6a6.8 6.8 0 0 1-.7-1.7L4 12l1.8-.6a6.8 6.8 0 0 1 .7-1.7l-1-1.6 2-2 1.6 1a6.8 6.8 0 0 1 1.7-.7L12 4l.6 1.8a6.8 6.8 0 0 1 1.7.7l1.6-1 2 2-1 1.6a6.8 6.8 0 0 1 .7 1.7z" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>',
  logout:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 6h8v12h-8M6 12h10M6 12l3-3M6 12l3 3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
}

const items = [
  { key: 'dashboard', label: 'Dashboard', to: '/dashboard', icon: icons.dashboard },
  { key: 'statistics', label: 'Estatísticas', to: '/statistics', icon: icons.statistics },
  { key: 'academic-years', label: 'Gestão de Ano', to: '/academic-years', icon: icons.academic },
  { key: 'operations', label: 'Gestão Académica', to: '/operations', icon: icons.academic },
  { key: 'units', label: 'Unidades Orgânicas', to: '/units/manage', icon: icons.units },
  { key: 'departments', label: 'Departamentos', to: '/departments/manage', icon: icons.departments },
  { key: 'courses', label: 'Cursos', to: '/courses/manage', icon: icons.courses },
  { key: 'students', label: 'Estudantes', to: '/students/manage', icon: icons.students },
  { key: 'users', label: 'Usuários', to: '/users', icon: icons.users },
  { key: 'reports', label: 'Relatórios', to: '/reports', icon: icons.reports },
]

const visibleItems = computed(() => {
  const role = authStore.user?.role
  if (role === 'ADMIN') {
    return items
  }
  if (role === 'CHEFE') {
    return items.filter((item) => item.key !== 'units' && item.key !== 'departments' && item.key !== 'academic-years' && item.key !== 'users')
  }
  return items.filter((item) => item.key !== 'departments' && item.key !== 'academic-years' && item.key !== 'users')
})

const initials = computed(() => {
  const name = authStore.user?.username || 'US'
  return name.slice(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const role = authStore.user?.role
  if (role === 'REITOR') return 'Administrador'
  if (role === 'ADMIN') return 'Administrador'
  if (role === 'DIRETOR') return 'Diretor'
  if (role === 'CHEFE') return 'Chefe de Departamento'
  return 'Administrador'
})

const showSettings = computed(() => !['REITOR', 'DIRETOR', 'CHEFE'].includes(authStore.user?.role || ''))

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}

function isActive(key) {
  const name = String(route.name || '')
  if (key === 'dashboard') return name.startsWith('dashboard')
  if (key === 'statistics') return name === 'statistics'
  if (key === 'academic-years') return name === 'academic-years'
  if (key === 'operations') return name === 'operations'
  if (key === 'units') return name.startsWith('units-')
  if (key === 'departments') return name.startsWith('departments-')
  if (key === 'courses') return name.startsWith('courses-')
  if (key === 'students') return name.startsWith('students-') || name === 'student-status'
  if (key === 'users') return name === 'users' || name === 'user-detail' || name === 'user-create'
  if (key === 'reports') return name === 'reports'
  return false
}
</script>
