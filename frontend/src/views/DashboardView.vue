<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCustomers } from '@/api/customers'
import { useAuthStore } from '@/stores/auth'
import type { Customer } from '@/types/customer'

const router = useRouter()
const { getToken } = useAuthStore()

const customers = ref<Customer[]>([])
const search = ref('')
const isLoading = ref(false)
const error = ref('')

async function loadCustomers() {
  const token = getToken()
  if (!token) return

  isLoading.value = true
  error.value = ''
  try {
    customers.value = await fetchCustomers(token, search.value)
  } catch {
    error.value = 'Failed to load customers.'
  } finally {
    isLoading.value = false
  }
}

let debounceTimer: ReturnType<typeof setTimeout>
watch(search, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadCustomers, 250)
})

onMounted(loadCustomers)

function goToCustomer(id: number) {
  router.push({ name: 'customer-detail', params: { id } })
}

function formatCurrency(value: number) {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
</script>

<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Customers</h1>
        <p>{{ customers.length }} customer{{ customers.length === 1 ? '' : 's' }} found</p>
      </div>
      <input
        v-model="search"
        type="search"
        class="search-input"
        placeholder="Search by name or company…"
      />
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="table-card">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>Email</th>
            <th>Status</th>
            <th>Total Spent</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="customer in customers"
            :key="customer.id"
            class="customer-row"
            @click="goToCustomer(customer.id)"
          >
            <td class="name-cell">{{ customer.name }}</td>
            <td>{{ customer.company }}</td>
            <td>{{ customer.email }}</td>
            <td>
              <span class="status-badge" :class="`status-badge--${customer.status.toLowerCase()}`">
                {{ customer.status }}
              </span>
            </td>
            <td>{{ formatCurrency(customer.totalSpent) }}</td>
          </tr>
          <tr v-if="!isLoading && customers.length === 0">
            <td colspan="5" class="empty-state">No customers match your search.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1100px;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.dashboard-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.6rem;
  color: #111827;
}

.dashboard-header p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.search-input {
  min-width: 280px;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  background: white;
}

.search-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.error {
  color: #b91c1c;
  margin-bottom: 1rem;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

td {
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  color: #1f2937;
  font-size: 0.9rem;
}

.customer-row {
  cursor: pointer;
  transition: background 0.12s ease;
}

.customer-row:hover {
  background: #f9fafb;
}

.customer-row:last-child td {
  border-bottom: none;
}

.name-cell {
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.78rem;
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

.empty-state {
  text-align: center;
  color: #9ca3af;
  padding: 2rem 1.25rem;
}
</style>
