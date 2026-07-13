import { apiFetch } from '@/api/client'
import type { Customer } from '@/types/customer'

export function fetchCustomers(token: string, search = ''): Promise<Customer[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : ''
  return apiFetch<Customer[]>(`/api/customers${query}`, {}, token)
}

export function fetchCustomer(token: string, id: number): Promise<Customer> {
  return apiFetch<Customer>(`/api/customers/${id}`, {}, token)
}
