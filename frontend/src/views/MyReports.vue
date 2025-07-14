<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Mis Informes</h1>
            <p class="mt-1 text-sm text-gray-500">
              Gestiona y visualiza todos tus análisis SEO guardados
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="exportAllReports"
              :disabled="isExporting"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ isExporting ? 'Exportando...' : 'Exportar Todo' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Buscar
            </label>
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por URL, keywords, o tipo de análisis..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Filter by Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Análisis
            </label>
            <select
              v-model="selectedType"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos los tipos</option>
              <option value="seo">Análisis SEO Completo</option>
              <option value="geo">Análisis Local</option>
              <option value="sitemap">Análisis Sitemap</option>
              <option value="crawl">Análisis Crawl</option>
            </select>
          </div>

          <!-- Filter by Date Range -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Rango de Fechas
            </label>
            <select
              v-model="selectedDateRange"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todas las fechas</option>
              <option value="today">Hoy</option>
              <option value="week">Última semana</option>
              <option value="month">Último mes</option>
              <option value="quarter">Último trimestre</option>
            </select>
          </div>
        </div>

        <!-- Active Filters -->
        <div v-if="hasActiveFilters" class="mt-4 flex flex-wrap gap-2">
          <span class="text-sm text-gray-500">Filtros activos:</span>
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200"
          >
            "{{ searchQuery }}"
            <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <button
            v-if="selectedType"
            @click="clearTypeFilter"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200"
          >
            Tipo: {{ getTypeLabel(selectedType) }}
            <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <button
            v-if="selectedDateRange"
            @click="clearDateFilter"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 hover:bg-purple-200"
          >
            Fecha: {{ getDateRangeLabel(selectedDateRange) }}
            <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <button
            @click="clearAllFilters"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 hover:bg-gray-200"
          >
            Limpiar todos
          </button>
        </div>
      </div>

      <!-- URL Groups -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="filteredUrlGroups.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No se encontraron informes</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ hasActiveFilters ? 'Intenta ajustar los filtros de búsqueda.' : 'Aún no has realizado ningún análisis.' }}
        </p>
      </div>

      <div v-else class="space-y-6">
        <!-- URL Group Cards -->
        <div
          v-for="urlGroup in paginatedUrlGroups"
          :key="urlGroup.url"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <!-- URL Group Header -->
          <div
            @click="toggleUrlGroup(urlGroup.url)"
            class="px-6 py-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                      </svg>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ urlGroup.url }}
                    </p>
                    <div class="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{{ urlGroup.totalAnalyses }} análisis</span>
                      <span>Último: {{ formatDate(urlGroup.lastAnalysisDate) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-500">
                  {{ urlGroup.totalAnalyses }} análisis
                </span>
                <svg
                  :class="[
                    'w-5 h-5 text-gray-400 transition-transform',
                    expandedUrlGroups.includes(urlGroup.url) ? 'rotate-180' : ''
                  ]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Reports Table (when expanded) -->
          <div v-if="expandedUrlGroups.includes(urlGroup.url)" class="overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Keywords
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Web Key Words
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="report in urlGroup.reports"
                    :key="report.id"
                    class="hover:bg-gray-50"
                  >
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatDate(report.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="[
                          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                          getTypeBadgeClass(report.analysis_type)
                        ]"
                      >
                        {{ getTypeLabel(report.analysis_type) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-900">
                      <div v-if="report.analysis_type === 'geo' && report.keywords" class="max-w-xs">
                        <div class="flex flex-wrap gap-1">
                          <span
                            v-for="keyword in report.keywords.split(',').slice(0, 3)"
                            :key="keyword"
                            class="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 text-blue-800"
                          >
                            {{ keyword.trim() }}
                          </span>
                          <span
                            v-if="report.keywords.split(',').length > 3"
                            class="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-600"
                          >
                            +{{ report.keywords.split(',').length - 3 }} más
                          </span>
                        </div>
                      </div>
                      <span v-else class="text-gray-500">-</span>
                    </td>
                    <td class="px-6 py-4 text-sm">
                      <span v-if="report.keyword_usage && report.keyword_usage.keywords && report.keyword_usage.keywords.length > 0">
                        <span v-for="(kw, i) in report.keyword_usage.keywords.slice(0, 3)" :key="i" class="inline-block bg-green-100 text-green-800 px-2 py-0.5 rounded mr-1">
                          {{ kw }}
                        </span>
                        <span v-if="report.keyword_usage.keywords.length > 3" class="text-xs text-gray-500">+{{ report.keyword_usage.keywords.length - 3 }} más</span>
                      </span>
                      <span v-else class="text-gray-400">—</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="[
                          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                          report.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        ]"
                      >
                        {{ report.status === 'completed' ? 'Completado' : 'En proceso' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center space-x-2">
                        <button
                          @click="viewReport(report)"
                          class="text-blue-600 hover:text-blue-900"
                        >
                          Ver
                        </button>
                        <button
                          @click="exportReport(report)"
                          class="text-green-600 hover:text-green-900"
                        >
                          Exportar
                        </button>
                        <button
                          @click="deleteReport(report.id)"
                          class="text-red-600 hover:text-red-900"
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex items-center justify-between bg-white px-4 py-3 border-t border-gray-200 sm:px-6 rounded-lg shadow">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Mostrando
                <span class="font-medium">{{ startIndex + 1 }}</span>
                a
                <span class="font-medium">{{ endIndex }}</span>
                de
                <span class="font-medium">{{ filteredUrlGroups.length }}</span>
                URLs
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="previousPage"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <span class="sr-only">Anterior</span>
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === currentPage
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
                <button
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <span class="sr-only">Siguiente</span>
                  <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeDeleteModal"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">
            Confirmar eliminación
          </h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">
              ¿Estás seguro de que quieres eliminar este informe? Esta acción no se puede deshacer.
            </p>
          </div>
          <div class="items-center px-4 py-3">
            <button
              @click="confirmDelete"
              class="px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300"
            >
              Eliminar
            </button>
            <button
              @click="closeDeleteModal"
              class="mt-2 px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useReportsStore } from '@/stores/reports'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const router = useRouter()
const reportsStore = useReportsStore()

// Reactive data
const loading = ref(false)
const searchQuery = ref('')
const selectedType = ref('')
const selectedDateRange = ref('')
const expandedUrlGroups = ref([])
const currentPage = ref(1)
const itemsPerPage = ref(5)
const showDeleteModal = ref(false)
const reportToDelete = ref(null)
const isExporting = ref(false)

// Computed properties
const hasActiveFilters = computed(() => {
  return searchQuery.value || selectedType.value || selectedDateRange.value
})

const filteredUrlGroups = computed(() => {
  let filtered = reportsStore.urlGroups

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(group => {
      return group.url.toLowerCase().includes(query) ||
             group.reports.some(report =>
               (report.keywords && report.keywords.toLowerCase().includes(query)) ||
               getTypeLabel(report.analysis_type).toLowerCase().includes(query)
             )
    })
  }

  // Filter by type
  if (selectedType.value) {
    filtered = filtered.filter(group => {
      return group.reports.some(report => report.analysis_type === selectedType.value)
    })
  }

  // Filter by date range
  if (selectedDateRange.value) {
    const now = new Date()
    let startDate = new Date()

    switch (selectedDateRange.value) {
      case 'today':
        startDate.setHours(0, 0, 0, 0)
        break
      case 'week':
        startDate.setDate(now.getDate() - 7)
        break
      case 'month':
        startDate.setMonth(now.getMonth() - 1)
        break
      case 'quarter':
        startDate.setMonth(now.getMonth() - 3)
        break
    }

    filtered = filtered.filter(group => {
      return group.reports.some(report => {
        const reportDate = new Date(report.created_at)
        return reportDate >= startDate
      })
    })
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredUrlGroups.value.length / itemsPerPage.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value
})

const endIndex = computed(() => {
  return Math.min(startIndex.value + itemsPerPage.value, filteredUrlGroups.value.length)
})

const paginatedUrlGroups = computed(() => {
  return filteredUrlGroups.value.slice(startIndex.value, endIndex.value)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// Methods
const loadReports = async () => {
  loading.value = true
  try {
    await reportsStore.fetchReports()
  } catch (error) {
    console.error('Error loading reports:', error)
  } finally {
    loading.value = false
  }
}

const toggleUrlGroup = (url) => {
  const index = expandedUrlGroups.value.indexOf(url)
  if (index > -1) {
    expandedUrlGroups.value.splice(index, 1)
  } else {
    expandedUrlGroups.value.push(url)
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const clearTypeFilter = () => {
  selectedType.value = ''
}

const clearDateFilter = () => {
  selectedDateRange.value = ''
}

const clearAllFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  selectedDateRange.value = ''
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const goToPage = (page) => {
  currentPage.value = page
}

const viewReport = (report) => {
  router.push(`/report/${report.id}`)
}

const exportReport = async (report) => {
  try {
    await reportsStore.exportReport(report.id)
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

const deleteReport = (reportId) => {
  reportToDelete.value = reportId
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (reportToDelete.value) {
    try {
      await reportsStore.deleteReport(reportToDelete.value)
      showDeleteModal.value = false
      reportToDelete.value = null
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  reportToDelete.value = null
}

const exportAllReports = async () => {
  isExporting.value = true
  try {
    await reportsStore.exportAllReports()
  } catch (error) {
    console.error('Error exporting all reports:', error)
  } finally {
    isExporting.value = false
  }
}

const formatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es })
  } catch {
    return 'Fecha inválida'
  }
}

const getTypeLabel = (type) => {
  const labels = {
    'seo': 'Análisis SEO Completo',
    'geo': 'Análisis Local',
    'sitemap': 'Análisis Sitemap',
    'crawl': 'Análisis Crawl'
  }
  return labels[type] || type
}

const getTypeBadgeClass = (type) => {
  const classes = {
    'seo': 'bg-blue-100 text-blue-800',
    'geo': 'bg-green-100 text-green-800',
    'sitemap': 'bg-purple-100 text-purple-800',
    'crawl': 'bg-orange-100 text-orange-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getDateRangeLabel = (range) => {
  const labels = {
    'today': 'Hoy',
    'week': 'Última semana',
    'month': 'Último mes',
    'quarter': 'Último trimestre'
  }
  return labels[range] || range
}

// Watchers
watch([searchQuery, selectedType, selectedDateRange], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(() => {
  loadReports()
})
</script>
