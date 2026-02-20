<template>
  <header class="ops-header">
    <div>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>
    <div class="ops-actions">
      <button class="btn btn-ghost" type="button" @click="logout">Sair</button>
    </div>
  </header>

  <nav class="ops-nav">
    <router-link to="/units/create">Cadastro Unidades</router-link>
    <router-link to="/units/manage">Gestão Unidades</router-link>
    <router-link to="/departments/create">Cadastro Departamentos</router-link>
    <router-link to="/departments/manage">Gestão Departamentos</router-link>
    <router-link to="/courses/create">Cadastro Cursos</router-link>
    <router-link to="/courses/manage">Gestão Cursos</router-link>
    <router-link to="/students/create">Cadastro Estudantes</router-link>
    <router-link to="/students/manage">Gestão Estudantes</router-link>
    <router-link to="/academic-years">Anos</router-link>
    <router-link to="/users">Usuários</router-link>
    <router-link to="/datasets">Datasets</router-link>
    <router-link to="/reports">Relatórios</router-link>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})

const router = useRouter()
const authStore = useAuthStore()

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
