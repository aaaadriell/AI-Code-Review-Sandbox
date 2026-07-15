// Customer interface representing a customer entity in the application
export interface Customer {
  id: number
  name: string
  company: string
  email: string
  phone: string
  status: 'Active' | 'Inactive' | 'Pending'
  joinDate: string
  address: string
  totalOrders: number
  totalSpent: number
  lastContact: string
  notes: string
}
