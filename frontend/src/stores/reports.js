import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useReportsStore = defineStore('reports', () => {
  // State
  const reports = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Estado para grupos y reportes individuales
  const grouped = ref([])
  const groupedLoading = ref(false)
  const groupedError = ref(null)
  const byUrlReports = ref([])
  const byUrlLoading = ref(false)
  const byUrlError = ref(null)

  // Getters
  const urlGroups = computed(() => {
    const groups = {}

    reports.value.forEach(report => {
      if (!groups[report.url]) {
        groups[report.url] = {
          url: report.url,
          reports: [],
          totalAnalyses: 0,
          lastAnalysisDate: null
        }
      }

      groups[report.url].reports.push(report)
      groups[report.url].totalAnalyses++

      const reportDate = new Date(report.created_at)
      if (!groups[report.url].lastAnalysisDate || reportDate > new Date(groups[report.url].lastAnalysisDate)) {
        groups[report.url].lastAnalysisDate = report.created_at
      }
    })

    // Sort reports within each group by date (newest first)
    Object.values(groups).forEach(group => {
      group.reports.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    })

    // Convert to array and sort by last analysis date (newest first)
    return Object.values(groups).sort((a, b) =>
      new Date(b.lastAnalysisDate) - new Date(a.lastAnalysisDate)
    )
  })

  const getReportById = computed(() => {
    return (id) => reports.value.find(report => report.id === id)
  })

  const getReportsByUrl = computed(() => {
    return (url) => reports.value.filter(report => report.url === url)
  })

  // Actions
  const fetchReports = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/api/reports')
      reports.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar los informes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchReport = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/reports/${id}`)
      const report = response.data

      // Update or add the report to the store
      const index = reports.value.findIndex(r => r.id === id)
      if (index > -1) {
        reports.value[index] = report
      } else {
        reports.value.push(report)
      }

      return report
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar el informe'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteReport = async (id) => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/api/reports/${id}`)
      reports.value = reports.value.filter(report => report.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar el informe'
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportReport = async (id) => {
    try {
      const response = await api.get(`/api/reports/${id}/export`, {
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report-${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al exportar el informe'
      throw err
    }
  }

  const exportAllReports = async () => {
    try {
      const response = await api.get('/api/reports/export-all', {
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `all-reports-${new Date().toISOString().split('T')[0]}.zip`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al exportar todos los informes'
      throw err
    }
  }

  const searchReports = async (query, filters = {}) => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (query) params.append('q', query)
      if (filters.type) params.append('type', filters.type)
      if (filters.dateRange) params.append('date_range', filters.dateRange)

      const response = await api.get(`/api/reports/search?${params.toString()}`)
      reports.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error en la búsqueda'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Acción para cargar reportes agrupados
  const fetchGroupedReports = async (params = {}) => {
    groupedLoading.value = true
    groupedError.value = null
    try {
      const response = await api.get('/api/reports/grouped', { params })
      grouped.value = response.data.groups
      return response.data
    } catch (err) {
      groupedError.value = err.response?.data?.detail || 'Error al cargar los grupos'
      throw err
    } finally {
      groupedLoading.value = false
    }
  }

  // Acción para cargar reportes individuales de una URL
  const fetchReportsByUrl = async (url, page = 1, perPage = 20) => {
    byUrlLoading.value = true
    byUrlError.value = null
    try {
      const response = await api.get('/api/reports/by-url', { params: { url, page, per_page: perPage } })
      byUrlReports.value = response.data.reports
      return response.data
    } catch (err) {
      byUrlError.value = err.response?.data?.detail || 'Error al cargar los reportes de la URL'
      throw err
    } finally {
      byUrlLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    reports,
    loading,
    error,
    grouped,
    groupedLoading,
    groupedError,
    byUrlReports,
    byUrlLoading,
    byUrlError,

    // Getters
    urlGroups,
    getReportById,
    getReportsByUrl,

    // Actions
    fetchReports,
    fetchReport,
    deleteReport,
    exportReport,
    exportAllReports,
    searchReports,
    fetchGroupedReports,
    fetchReportsByUrl,
    clearError
  }
})
