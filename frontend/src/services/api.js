import axios from 'axios'

// Configuración base de axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 300000, // 5 minutos para análisis largos
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    // Agregar token si existe
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Let the calling code handle toast notifications
    return Promise.reject(error)
  }
)

// Funciones específicas de la API
export const analysisAPI = {
  // Análisis SEO completo
  analyze: (data) => api.post('/api/analyze', data),
  
  // Análisis geográfico
  geoAnalysis: (data) => api.post('/api/geo-rank-analysis', data),
  
  // Obtener análisis por ID
  getById: (id) => api.get(`/api/analyses/${id}`),
  
  // Obtener análisis recientes
  getRecent: (limit = 20) => api.get('/api/analyses', { params: { limit } }),
  
  // Eliminar análisis
  delete: (id) => api.delete(`/api/analyses/${id}`),
  
  // Obtener estadísticas
  getStats: () => api.get('/api/stats'),
  
  // Exportar reporte
  exportReport: (id, format = 'pdf') => 
    api.get(`/api/analysis/${id}/export`, {
      params: { format },
      responseType: 'blob'
    }),
  
  // Análisis de sitemap
  sitemapAnalysis: (data) => api.post('/api/sitemap-analysis', data),
  
  // Análisis de crawl
  crawlAnalysis: (data) => api.post('/api/crawl-analysis', data),
  
  // Health check
  health: () => api.get('/api/health'),
}

export const batchAPI = {
  // Análisis por lotes
  batchAnalyze: (data) => api.post('/api/batch-analyze', data),
  
  // Obtener estado del batch
  getBatchStatus: (id) => api.get(`/api/batch/${id}/status`),
  
  // Obtener resultados del batch
  getBatchResults: (id) => api.get(`/api/batch/${id}/results`),
}

export default api 