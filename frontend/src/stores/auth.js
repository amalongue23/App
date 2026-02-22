import { defineStore } from 'pinia'

import api from '../services/api'
import { parseJwtPayload } from '../utils/jwt'

const TOKEN_KEY = 'mpuna_token'
const USER_KEY = 'mpuna_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    restoreSession() {
      if (this.token) {
        return
      }

      const token = localStorage.getItem(TOKEN_KEY)
      const userRaw = localStorage.getItem(USER_KEY)

      if (!token || !userRaw) {
        return
      }

      this.token = token
      this.user = JSON.parse(userRaw)
    },
    async login({ username, password }) {
      const response = await api.post('/api/auth/login', {
        username,
        password,
      })

      const token = response.data.access_token
      const claims = parseJwtPayload(token) || {}

      const user = {
        username: claims.username || username,
        role: claims.role || null,
        full_name: claims.full_name || claims.name || response.data?.user?.full_name || response.data?.user?.name || '',
        name: claims.name || response.data?.user?.name || claims.full_name || '',
        photo_url: claims.photo_url || claims.avatar_url || response.data?.user?.photo_url || response.data?.user?.avatar_url || '',
      }

      this.token = token
      this.user = user

      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
