import { reactive, readonly } from 'vue'
import { apiFetch } from '@/api/client'

const TOKEN_STORAGE_KEY = 'crms_token'

const state = reactive({
  token: localStorage.getItem(TOKEN_STORAGE_KEY) as string | null,
})

async function login(username: string, password: string) {
  const { token } = await apiFetch<{ token: string }>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  state.token = token
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

async function logout() {
  try {
    if (state.token) {
      await apiFetch('/api/auth/logout', { method: 'POST' }, state.token)
    }
  } finally {
    state.token = null
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }
}

export function useAuthStore() {
  return {
    state: readonly(state),
    isAuthenticated: () => Boolean(state.token),
    getToken: () => state.token,
    login,
    logout,
  }
}
