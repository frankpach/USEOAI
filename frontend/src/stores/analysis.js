import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

export const useAnalysisStore = defineStore('analysis', () => {
  const toast = useToast()
  
  // Estado
  const currentAnalysis = ref(null)
  const analysisHistory = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  
  // Getters
  const hasCurrentAnalysis = computed(() => currentAnalysis.value !== null)
  const analysisCount = computed(() => analysisHistory.value.length)
  const recentAnalyses = computed(() => 
    analysisHistory.value.slice(0, 5)
  )
  
  // Acciones
  const startAnalysis = async (analysisData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/analyze', analysisData)
      currentAnalysis.value = response.data
      
      // Agregar a historial
      analysisHistory.value.unshift({
        id: response.data.id,
        url: analysisData.url,
        timestamp: new Date().toISOString(),
        status: 'completed'
      })
      
      toast.success('Análisis completado exitosamente')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al realizar el análisis'
      toast.error(String(error.value))
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const startGeoAnalysis = async (geoData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/geo-rank-analysis', geoData)
      currentAnalysis.value = response.data
      
      toast.success('Análisis geográfico completado')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al realizar el análisis geográfico'
      toast.error(String(error.value))
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const getAnalysisById = async (id) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/api/analyses/${id}`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al obtener el análisis'
      toast.error(String(error.value))
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getRecentAnalyses = async (limit = 20) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get('/api/analyses', { params: { limit } })
      return response.data.analyses
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al obtener los análisis'
      toast.error(String(error.value))
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteAnalysis = async (id) => {
    try {
      await api.delete(`/api/analyses/${id}`)
      toast.success('Análisis eliminado correctamente')
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar el análisis'
      toast.error(String(error.value))
      throw err
    }
  }

  const getStats = async () => {
    try {
      const response = await api.get('/api/stats')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al obtener estadísticas'
      toast.error(String(error.value))
      throw err
    }
  }
  
  const clearCurrentAnalysis = () => {
    currentAnalysis.value = null
    error.value = null
  }
  
  const clearError = () => {
    error.value = null
  }
  
  const exportReport = async (analysisId, format = 'pdf') => {
    try {
      const response = await api.get(`/api/analysis/${analysisId}/export`, {
        params: { format },
        responseType: 'blob'
      })
      
      // Crear descarga
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reporte-seo-${analysisId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success(`Reporte exportado como ${format.toUpperCase()}`)
    } catch (err) {
      toast.error('Error al exportar el reporte')
      throw err
    }
  }

  const saveMapImage = async (analysisId, mapData) => {
    try {
      const response = await api.post(`/api/analysis/${analysisId}/map-image`, {
        image_data: mapData.dataUrl,
        keyword: mapData.keyword,
        timestamp: mapData.timestamp
      })
      
      toast.success('Imagen del mapa guardada exitosamente')
      return response.data
    } catch (err) {
      toast.error('Error al guardar la imagen del mapa')
      throw err
    }
  }
  
  return {
    // Estado
    currentAnalysis,
    analysisHistory,
    isLoading,
    error,
    
    // Getters
    hasCurrentAnalysis,
    analysisCount,
    recentAnalyses,
    
    // Acciones
    startAnalysis,
    startGeoAnalysis,
    getAnalysisById,
    getRecentAnalyses,
    deleteAnalysis,
    getStats,
    clearCurrentAnalysis,
    clearError,
    exportReport,
    saveMapImage
  }
}) 