<template>
  <div class="dashboard-user-menu" ref="rootRef">
    <button type="button" class="dashboard-user-btn" :class="{ compact }" @click="toggleMenu">
      <img v-if="photoUrl" :src="photoUrl" alt="Foto do utilizador" class="dashboard-user-photo" />
      <span v-else class="dashboard-user-initials">{{ initials }}</span>
      <span class="dashboard-user-meta">
        <strong>{{ displayName }}</strong>
        <small>{{ displayUsername }}</small>
        <small v-if="!compact" class="role">{{ roleLabel }}</small>
      </span>
      <span class="dashboard-user-caret">⌄</span>
    </button>

    <div v-if="menuOpen" class="dashboard-user-dropdown">
      <button type="button" @click="logout">Sair</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
defineProps({
  compact: { type: Boolean, default: false },
})

const rootRef = ref(null)
const menuOpen = ref(false)

const displayUsername = computed(() => authStore.user?.username || 'utilizador')
const displayName = computed(() => authStore.user?.name || authStore.user?.full_name || displayUsername.value)
const photoUrl = computed(() => authStore.user?.photo_url || '')
const initials = computed(() => displayName.value.slice(0, 2).toUpperCase())

const roleLabel = computed(() => {
  const role = authStore.user?.role
  if (role === 'ADMIN') return 'Administrador'
  if (role === 'REITOR') return 'Reitor'
  if (role === 'DIRETOR') return 'Diretor'
  if (role === 'CHEFE') return 'Chefe de Departamento'
  return 'Utilizador'
})

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function onDocumentClick(event) {
  const root = rootRef.value
  if (!root) return
  if (!root.contains(event.target)) menuOpen.value = false
}

function logout() {
  menuOpen.value = false
  authStore.logout()
  router.push({ name: 'login' })
}

onMounted(() => document.addEventListener('click', onDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocumentClick))
</script>
