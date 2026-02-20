<template>
  <div class="auth-page">
    <div class="auth-shell">
      <section class="login-card">
        <div class="brand-wrap">
          <AppLogo />
        </div>

        <h2>Entrar na <span>Plataforma</span></h2>
        <p class="subtitle">
          Preencha os dados abaixo para entrar na aplicação e continuar a gestão académica.
        </p>

        <form class="form" @submit.prevent="submitLogin">
          <label for="username">* Utilizador</label>
          <div class="field">
            <input
              id="username"
              v-model.trim="form.username"
              type="text"
              autocomplete="username"
              placeholder="Digite o utilizador"
              required
            />
          </div>

          <label for="password">* Senha</label>
          <div class="field">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Digite a senha"
              required
            />
            <button type="button" class="field-action" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>

          <div class="label-row">
            <span />
            <a href="#" @click.prevent>Esqueceu sua senha?</a>
          </div>

          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

          <div class="actions">
            <button type="button" class="btn btn-ghost" @click="clearForm">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Entrando...' : 'Entrar' }}
            </button>
          </div>
        </form>

        <footer>
          Precisa de ajuda? <a href="mailto:suporte@mpuna.com">suporte@mpuna.com</a>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLogo from '../components/AppLogo.vue'
import { resolveDashboardByRole } from '../constants/roles'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  password: '',
})

function clearForm() {
  form.username = ''
  form.password = ''
  errorMessage.value = ''
}

async function submitLogin() {
  errorMessage.value = ''
  loading.value = true

  try {
    await authStore.login({
      username: form.username,
      password: form.password,
    })
    router.push(resolveDashboardByRole(authStore.user?.role))
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.message || 'Credenciais inválidas.'
    } else {
      errorMessage.value = 'Falha ao autenticar. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}
</script>
