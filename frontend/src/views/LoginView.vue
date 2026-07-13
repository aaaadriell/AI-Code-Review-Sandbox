<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'

const username = ref('')
const password = ref('')
const error = ref('')
const isSubmitting = ref(false)

const router = useRouter()
const { login } = useAuthStore()

async function handleSubmit() {
  error.value = ''
  isSubmitting.value = true
  try {
    await login(username.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Something went wrong. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">C</div>
        <h1>CRMS</h1>
        <p>Sign in to manage your customers</p>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>Username</span>
          <input v-model="username" type="text" autocomplete="username" placeholder="admin" required />
        </label>

        <label class="field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
          />
        </label>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit-button" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="hint">Demo credentials: <strong>admin</strong> / <strong>password</strong></p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #4338ca, #111827 55%);
  padding: 1.5rem;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: white;
  border-radius: 16px;
  padding: 2.5rem 2.25rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  box-sizing: border-box;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-weight: 700;
  font-size: 1.4rem;
}

.login-header h1 {
  margin: 0 0 0.35rem;
  font-size: 1.5rem;
  color: #111827;
}

.login-header p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.field input {
  font-size: 0.95rem;
  font-weight: 400;
  padding: 0.65rem 0.8rem;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  font-family: inherit;
}

.field input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.error {
  margin: 0;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 0.85rem;
}

.submit-button {
  margin-top: 0.4rem;
  padding: 0.7rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.15s ease, transform 0.1s ease;
}

.submit-button:hover:not(:disabled) {
  opacity: 0.92;
}

.submit-button:active:not(:disabled) {
  transform: translateY(1px);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  margin: 1.5rem 0 0;
  text-align: center;
  font-size: 0.8rem;
  color: #9ca3af;
}
</style>
