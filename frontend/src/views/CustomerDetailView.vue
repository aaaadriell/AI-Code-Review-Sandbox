<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCustomer } from '@/api/customers'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'
import type { Customer } from '@/types/customer'

const props = defineProps<{ id: string }>()

const router = useRouter()
const { getToken } = useAuthStore()

const customer = ref<Customer | null>(null)
const error = ref('')
const isLoading = ref(false)

async function loadCustomer() {
  const token = getToken()
  if (!token) return

  isLoading.value = true
  error.value = ''
  customer.value = null
  try {
    customer.value = await fetchCustomer(token, Number(props.id))
  } catch (err) {
    error.value = err instanceof ApiError && err.status === 404 ? 'Customer not found.' : 'Failed to load customer.'
  } finally {
    isLoading.value = false
  }
}

watch(() => props.id, loadCustomer)
onMounted(loadCustomer)

function formatCurrency(value: number) {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
</script>

<template>
  <div class="detail-page">
    <button class="back-link" type="button" @click="router.push({ name: 'dashboard' })">
      ← Back to customers
    </button>

    <p v-if="isLoading" class="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <template v-else-if="customer">
      <header class="detail-header">
        <div>
          <h1>{{ customer.name }}</h1>
          <p class="company">{{ customer.company }}</p>
        </div>
        <span class="status-badge" :class="`status-badge--${customer.status.toLowerCase()}`">
          {{ customer.status }}
        </span>
      </header>

      <div class="stat-row">
        <div class="stat-card">
          <span class="stat-label">Total Orders</span>
          <span class="stat-value">{{ customer.totalOrders }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Total Spent</span>
          <span class="stat-value">{{ formatCurrency(customer.totalSpent) }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Customer Since</span>
          <span class="stat-value">{{ customer.joinDate }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Last Contact</span>
          <span class="stat-value">{{ customer.lastContact }}</span>
        </div>
      </div>

      <div class="detail-card">
        <h2>Contact Information</h2>
        <dl>
          <div class="detail-row">
            <dt>Email</dt>
            <dd>{{ customer.email }}</dd>
          </div>
          <div class="detail-row">
            <dt>Phone</dt>
            <dd>{{ customer.phone }}</dd>
          </div>
          <div class="detail-row">
            <dt>Address</dt>
            <dd>{{ customer.address }}</dd>
          </div>
        </dl>
      </div>

      <div class="detail-card">
        <h2>Notes</h2>
        <p class="notes">{{ customer.notes }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 800px;
}

.back-link {
  border: none;
  background: none;
  color: #4f46e5;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-bottom: 1.5rem;
  font-family: inherit;
}

.back-link:hover {
  text-decoration: underline;
}

.loading,
.error {
  color: #6b7280;
}

.error {
  color: #b91c1c;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.detail-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.6rem;
  color: #111827;
}

.company {
  margin: 0;
  color: #6b7280;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge--active {
  background: #dcfce7;
  color: #166534;
}

.status-badge--inactive {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge--pending {
  background: #fef9c3;
  color: #854d0e;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1rem 1.1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.stat-label {
  font-size: 0.78rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
}

.detail-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.25rem;
}

.detail-card h2 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: #111827;
}

dl {
  margin: 0;
}

.detail-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.9rem;
}

.detail-row:last-child {
  border-bottom: none;
}

dt {
  width: 120px;
  flex-shrink: 0;
  color: #6b7280;
}

dd {
  margin: 0;
  color: #1f2937;
}

.notes {
  margin: 0;
  color: #374151;
  line-height: 1.5;
}
</style>
