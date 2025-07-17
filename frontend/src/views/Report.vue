<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header del informe -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container mx-auto px-4 py-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 class="text-4xl font-bold text-gray-900 mb-2">
              Informe SEO
            </h1>
            <p class="text-xl text-gray-600">
              Análisis completo de {{ report?.url || 'tu sitio web' }}
            </p>
          </div>
          <div class="flex flex-col sm:flex-row gap-4 mt-4 md:mt-0">
            <button
              @click="exportReport"
              class="btn-primary"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Exportar PDF
            </button>
            <router-link
              to="/analyze"
              class="btn-secondary"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Nuevo Análisis
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <!-- Estado de carga -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="loading-spinner mx-auto mb-4"></div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">
          Cargando informe...
        </h3>
        <p class="text-gray-600">Obteniendo los resultados del análisis</p>
      </div>

      <!-- Contenido del informe -->
      <div v-else-if="report" class="space-y-8">
        <!-- Resumen ejecutivo -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Resumen Ejecutivo</h2>
          </div>
          <div class="prose max-w-none">
            <div v-html="report.executive_summary || report.semantic_summary?.executive_summary || ''"></div>
          </div>
        </div>

        <!-- Métricas principales como barras de progreso -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="card text-center">
            <div class="mb-2">
              <progress :value="report.technical_score ?? report.semantic_summary?.technical_score" max="100" class="w-full h-4"></progress>
            </div>
            <div class="text-2xl font-bold text-primary-600 mb-1">
              {{ report.technical_score ?? report.semantic_summary?.technical_score ?? 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Puntuación Técnica</div>
          </div>
          <div class="card text-center">
            <div class="mb-2">
              <progress :value="report.onpage_score ?? report.semantic_summary?.onpage_score" max="100" class="w-full h-4"></progress>
            </div>
            <div class="text-2xl font-bold text-success-600 mb-1">
              {{ report.onpage_score ?? report.semantic_summary?.onpage_score ?? 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Puntuación On-Page</div>
          </div>
          <div class="card text-center">
            <div class="mb-2">
              <progress :value="report.offpage_score ?? report.semantic_summary?.offpage_score" max="100" class="w-full h-4"></progress>
            </div>
            <div class="text-2xl font-bold text-warning-600 mb-1">
              {{ report.offpage_score ?? report.semantic_summary?.offpage_score ?? 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Puntuación Off-Page</div>
          </div>
          <div class="card text-center">
            <div class="mb-2">
              <progress :value="report.overall_score ?? report.semantic_summary?.overall_score" max="100" class="w-full h-4"></progress>
            </div>
            <div class="text-2xl font-bold text-danger-600 mb-1">
              {{ report.overall_score ?? report.semantic_summary?.overall_score ?? 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Puntuación General</div>
          </div>
        </div>

        <!-- Análisis técnico -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Análisis Técnico</h2>
          </div>
          <div class="space-y-6">
            <!-- Estado HTTP -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Estado HTTP</h3>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Código de respuesta:</span>
                  <span class="badge" :class="getStatusBadgeClass(report.status_code || report.http_status)">
                    {{ report.status_code || report.http_status || 'N/A' }}
                  </span>
                </div>
                <div v-if="report.redirections && report.redirections.length > 0" class="mt-2">
                  <span class="text-sm text-gray-600">Redirecciones:</span>
                  <ul class="mt-1 text-sm text-gray-700">
                    <li v-for="(redirect, index) in report.redirections" :key="index">
                      {{ redirect }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Metadatos -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Metadatos</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-50 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 mb-2">Title</h4>
                  <p class="text-sm text-gray-700">{{ report.title?.text || report.title || 'No encontrado' }}</p>
                  <div class="mt-2">
                    <span class="text-xs text-gray-500">
                      Longitud: {{ report.title?.length || (typeof report.title === 'string' ? report.title.length : 0) }} caracteres
                    </span>
                  </div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4">
                  <h4 class="font-medium text-gray-900 mb-2">Meta Description</h4>
                  <p class="text-sm text-gray-700">{{ report.meta_description?.text || report.meta_description || 'No encontrado' }}</p>
                  <div class="mt-2">
                    <span class="text-xs text-gray-500">
                      Longitud: {{ report.meta_description?.length || (typeof report.meta_description === 'string' ? report.meta_description.length : 0) }} caracteres
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Estructura HTML -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Estructura HTML</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.h_tags?.h1?.length || report.h1_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">H1</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.h_tags?.h2?.length || report.h2_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">H2</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.h_tags?.h3?.length || report.h3_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">H3</div>
                </div>
              </div>
            </div>

            <!-- Enlaces -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Enlaces</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.links?.internal?.length || report.internal_links_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">Enlaces Internos</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.links?.external?.length || report.external_links_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">Enlaces Externos</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.links?.broken?.length || report.broken_links_count || 0 }}
                  </div>
                  <div class="text-sm text-gray-600">Enlaces Rotos</div>
                </div>
              </div>
              <!-- Lista de enlaces rotos -->
              <div v-if="report.links && report.links.broken && report.links.broken.length" class="mt-4">
                <h4 class="font-medium text-gray-800 mb-2">URLs de enlaces rotos:</h4>
                <ul class="list-disc pl-6 text-sm">
                  <li v-for="(url, idx) in report.links.broken" :key="idx">
                    <a :href="url" target="_blank" class="text-red-600 underline">{{ url }}</a>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Imágenes -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Imágenes</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.images_count ?? (report.page_metrics?.resource_counts?.images_total ?? 'N/A') }}
                  </div>
                  <div class="text-sm text-gray-600">Total de Imágenes</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-primary-600 mb-1">
                    {{ report.images_without_alt?.length ?? report.images_without_alt ?? 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-600">Sin Alt Text</div>
                </div>
              </div>
              <!-- Lista de imágenes sin alt -->
              <div v-if="report.images_without_alt && report.images_without_alt.length" class="mt-4">
                <h4 class="font-medium text-gray-800 mb-2">URLs de imágenes sin alt:</h4>
                <ul class="list-disc pl-6 text-sm">
                  <li v-for="(img, idx) in report.images_without_alt" :key="idx">
                    <a :href="img.src" target="_blank" class="text-blue-600 underline">{{ img.src }}</a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Análisis de velocidad -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Análisis de Velocidad</h2>
          </div>
          <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600 mb-2">
                  {{ report.speed_metrics?.ttfb_ms ?? report.ttfb ?? 'N/A' }}ms
                </div>
                <div class="text-sm text-gray-600">Time to First Byte</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600 mb-2">
                  {{ report.page_metrics?.load_time ?? 'N/A' }}s
                </div>
                <div class="text-sm text-gray-600">Tiempo de Carga</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600 mb-2">
                  {{ report.page_metrics?.page_size_kb ?? 'N/A' }}KB
                </div>
                <div class="text-sm text-gray-600">Tamaño de Página</div>
              </div>
            </div>
          </div>
        </div>

                 <!-- Análisis local (si existe) -->
         <div v-if="report.local_analysis" class="card">
           <div class="card-header">
             <h2 class="card-title">Análisis SEO Local</h2>
           </div>
           <div class="space-y-6">
             <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
               <div class="text-center">
                 <div class="text-3xl font-bold text-blue-600 mb-2">
                   {{ report.local_analysis.google_maps_ranking || 'N/A' }}
                 </div>
                 <div class="text-sm text-gray-600">Google Maps</div>
               </div>
               <div class="text-center">
                 <div class="text-3xl font-bold text-gray-800 mb-2">
                   {{ report.local_analysis.apple_maps_ranking || 'N/A' }}
                 </div>
                 <div class="text-sm text-gray-600">Apple Maps</div>
               </div>
               <div class="text-center">
                 <div class="text-3xl font-bold text-green-600 mb-2">
                   {{ report.local_analysis.bing_maps_ranking || 'N/A' }}
                 </div>
                 <div class="text-sm text-gray-600">Bing Maps</div>
               </div>
             </div>

             <!-- Mapa interactivo para análisis local -->
             <div v-if="report.local_analysis.locations && report.local_analysis.locations.length > 0">
               <h3 class="text-lg font-semibold text-gray-900 mb-4">Mapa de Posicionamiento</h3>
               <GeoMap
                 :geo-results="report.local_analysis"
                 :map-height="500"
                 @map-captured="handleMapCaptured"
               />
             </div>
           </div>
         </div>

        <!-- Problemas encontrados -->
        <div class="card" v-if="(report.issues && report.issues.length) || (report.semantic_summary?.issues && report.semantic_summary.issues.length)">
          <div class="card-header">
            <h2 class="card-title">Problemas Encontrados</h2>
          </div>
          <ul class="divide-y divide-gray-200">
            <li v-for="(issue, idx) in (report.issues || report.semantic_summary?.issues || [])" :key="idx" class="py-4">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-semibold">{{ issue.title }}</div>
                  <div class="text-gray-700 text-sm">{{ issue.description }}</div>
                </div>
                <span
                  class="ml-4 px-2 py-1 rounded text-xs font-bold"
                  :class="{
                    'bg-red-100 text-red-700': issue.priority === 'high',
                    'bg-yellow-100 text-yellow-700': issue.priority === 'medium',
                    'bg-green-100 text-green-700': issue.priority === 'low'
                  }"
                >
                  {{ issue.priority }}
                </span>
              </div>
            </li>
          </ul>
        </div>

        <!-- Recomendaciones -->
        <div class="card" v-if="(report.llm_recommendations && report.llm_recommendations.length) || (report.recommendations && report.recommendations.length)">
          <div class="card-header">
            <h2 class="card-title">Recomendaciones</h2>
          </div>
          <ul class="list-disc pl-6">
            <li v-for="(rec, idx) in (report.llm_recommendations || report.recommendations || [])" :key="idx">
              {{ rec }}
            </li>
          </ul>
        </div>

        <!-- Checklist accionable -->
        <div class="card" v-if="(report.checklist && report.checklist.length) || (report.semantic_summary?.checklist && report.semantic_summary.checklist.length)">
          <div class="card-header">
            <h2 class="card-title">Checklist Accionable</h2>
          </div>
          <ul class="list-inside list-decimal">
            <li v-for="(task, idx) in (report.checklist || report.semantic_summary?.checklist || [])" :key="idx">
              {{ task }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card">
        <div class="text-center py-12">
          <div class="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">
            Error al cargar el informe
          </h3>
          <p class="text-gray-600 mb-4">{{ error }}</p>
          <router-link
            to="/analyze"
            class="btn-primary"
          >
            Realizar Nuevo Análisis
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useToast } from 'vue-toastification'
import GeoMap from '@/components/GeoMap.vue'

const route = useRoute()
const analysisStore = useAnalysisStore()
const toast = useToast()

// Estado reactivo
const report = ref(null)
const error = ref(null)
const isLoading = computed(() => analysisStore.isLoading)

// Cargar informe al montar el componente
onMounted(async () => {
  const reportId = route.params.id
  if (reportId && reportId !== 'undefined' && !isNaN(parseInt(reportId))) {
    try {
      const data = await analysisStore.getAnalysisById(reportId)
      report.value = data
    } catch (err) {
      error.value = 'No se pudo cargar el informe. Verifica que el ID sea correcto.'
    }
  } else {
    error.value = 'ID de informe inválido o no proporcionado.'
  }
})

// Obtener clase del badge según el estado HTTP
const getStatusBadgeClass = (status) => {
  if (status >= 200 && status < 300) return 'badge-success'
  if (status >= 300 && status < 400) return 'badge-warning'
  if (status >= 400) return 'badge-danger'
  return 'badge-info'
}

// Obtener clase del badge según la prioridad
const getPriorityBadgeClass = (priority) => {
  switch (priority.toLowerCase()) {
    case 'alta': return 'badge-danger'
    case 'media': return 'badge-warning'
    case 'baja': return 'badge-info'
    default: return 'badge-info'
  }
}

// Exportar reporte
const exportReport = async () => {
  if (!report.value) return

  try {
    await analysisStore.exportReport(report.value.id, 'pdf')
  } catch (error) {
    console.error('Error al exportar:', error)
  }
}

// Manejar captura del mapa
const handleMapCaptured = async (mapData) => {
  try {
    if (report.value?.id) {
      await analysisStore.saveMapImage(report.value.id, mapData)
    } else {
      // Si no hay ID, solo mostrar la imagen
      toast.success(`Mapa capturado para: ${mapData.keyword}`)
    }
  } catch (error) {
    console.error('Error al guardar el mapa:', error)
  }
}
</script>
