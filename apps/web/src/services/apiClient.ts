import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

function getBrowserToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }

  return window.sessionStorage.getItem('access_token')
}

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getBrowserToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      window.sessionStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

// API Methods
export const apiMethods = {
  // Auth
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (email: string, password: string, fullName: string) =>
    apiClient.post('/auth/register', { email, password, full_name: fullName }),

  // Tickets
  getTickets: (skip = 0, limit = 20, filters?: Record<string, unknown>) =>
    apiClient.get('/tickets', { params: { skip, limit, ...filters } }),
  getTicket: (id: string) => apiClient.get(`/tickets/${id}`),
  createTicket: (data: unknown) => apiClient.post('/tickets', data),
  updateTicket: (id: string, data: unknown) => apiClient.patch(`/tickets/${id}`, data),
  deleteTicket: (id: string) => apiClient.delete(`/tickets/${id}`),
  analyzeTicket: (id: string) => apiClient.post(`/tickets/${id}/analyze`),
  feedbackTicket: (id: string, feedback: string) =>
    apiClient.post(`/tickets/${id}/feedback`, { feedback }),

  // Intel
  getIntelItems: (topic?: string, limit = 50) =>
    apiClient.get('/intel/items', {
      params: { ...(topic ? { topic } : {}), limit },
    }),
  getIntelTopics: () => apiClient.get('/intel/topics'),
  triggerIntelIngest: () => apiClient.post('/intel/ingest'),

  // Agent Chat
  chatWithAgent: (message: string) =>
    apiClient.post('/agent/chat', { message }),

  // Machines
  getMachines: () => apiClient.get('/machines'),
  getMachine: (id: string) => apiClient.get(`/machines/${id}`),

  // Health
  getHealthStatus: () => apiClient.get('/health'),
}
