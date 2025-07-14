<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container mx-auto px-4 py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Análisis SEO Local
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Analiza el posicionamiento geográfico de tu negocio en Google Maps, Apple Maps y Bing Maps
          </p>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Formulario de análisis geográfico -->
        <div class="lg:col-span-1">
          <div class="card sticky top-8">
            <div class="card-header">
              <h2 class="card-title">Configuración del Análisis Local</h2>
            </div>

            <form @submit.prevent="startGeoAnalysis" class="space-y-6">
              <!-- URL del sitio -->
              <div>
                <label for="url" class="form-label">
                  URL del sitio web *
                </label>
                <input
                  id="url"
                  v-model="formData.url"
                  type="url"
                  required
                  placeholder="https://ejemplo.com"
                  class="form-input"
                  :class="{ 'border-danger-500': errors.url }"
                />
                <p v-if="errors.url" class="form-error">{{ errors.url }}</p>
              </div>

              <!-- Nombre de la empresa -->
              <div>
                <label for="companyName" class="form-label">
                  Nombre de la empresa *
                </label>
                <input
                  id="companyName"
                  v-model="formData.company_name"
                  type="text"
                  required
                  placeholder="Mi Empresa S.L."
                  class="form-input"
                  :class="{ 'border-danger-500': errors.company_name }"
                />
                <p v-if="errors.company_name" class="form-error">{{ errors.company_name }}</p>
              </div>

              <!-- Palabras clave -->
              <div>
                <label for="keywords" class="form-label">
                  Palabras clave (separadas por comas) *
                </label>
                <textarea
                  id="keywords"
                  v-model="formData.keywords"
                  required
                  placeholder="restaurante, comida italiana, pizza"
                  rows="3"
                  class="form-input"
                  :class="{ 'border-danger-500': errors.keywords }"
                ></textarea>
                <p v-if="errors.keywords" class="form-error">{{ errors.keywords }}</p>
              </div>

              <!-- Ubicación -->
              <div>
                <label for="location" class="form-label">
                  Ubicación *
                </label>
                <input
                  id="location"
                  v-model="formData.location"
                  type="text"
                  required
                  placeholder="Madrid, España"
                  class="form-input"
                  :class="{ 'border-danger-500': errors.location }"
                />
                <p v-if="errors.location" class="form-error">{{ errors.location }}</p>
              </div>

              <!-- Coordenadas -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="latitude" class="form-label">Latitud</label>
                  <input
                    id="latitude"
                    v-model="formData.latitude"
                    type="number"
                    step="any"
                    placeholder="40.4168"
                    class="form-input"
                  />
                </div>
                <div>
                  <label for="longitude" class="form-label">Longitud</label>
                  <input
                    id="longitude"
                    v-model="formData.longitude"
                    type="number"
                    step="any"
                    placeholder="-3.7038"
                    class="form-input"
                  />
                </div>
              </div>

              <!-- Radio local -->
              <div>
                <label for="localRadius" class="form-label">
                  Radio local (km) *
                </label>
                <input
                  id="localRadius"
                  v-model="formData.local_radius_km"
                  type="number"
                  required
                  min="1"
                  max="100"
                  placeholder="10"
                  class="form-input"
                  :class="{ 'border-danger-500': errors.local_radius_km }"
                />
                <p v-if="errors.local_radius_km" class="form-error">{{ errors.local_radius_km }}</p>
              </div>

              <!-- Muestras geográficas -->
              <div>
                <label for="geoSamples" class="form-label">
                  Muestras geográficas *
                </label>
                <input
                  id="geoSamples"
                  v-model="formData.geo_samples"
                  type="number"
                  required
                  min="1"
                  max="50"
                  placeholder="10"
                  class="form-input"
                  :class="{ 'border-danger-500': errors.geo_samples }"
                />
                <p v-if="errors.geo_samples" class="form-error">{{ errors.geo_samples }}</p>
              </div>

              <!-- Botón de análisis -->
              <button
                type="submit"
                :disabled="isLoading"
                class="btn-primary w-full py-3 text-lg"
              >
                <div v-if="isLoading" class="flex items-center justify-center">
                  <div class="loading-spinner mr-3"></div>
                  Analizando...
                </div>
                <div v-else class="flex items-center justify-center">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Iniciar Análisis Local
                </div>
              </button>
            </form>
          </div>
        </div>

        <!-- Resultados y progreso -->
        <div class="lg:col-span-2">
          <!-- Estado de carga -->
          <div v-if="isLoading" class="card">
            <div class="text-center py-12">
              <div class="loading-spinner mx-auto mb-4"></div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                Analizando posicionamiento local...
              </h3>
              <p class="text-gray-600 mb-6">
                Estamos verificando tu posicionamiento en Google Maps, Apple Maps y Bing Maps.
              </p>
              
              <!-- Progreso -->
              <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div 
                  class="bg-success-600 h-2 rounded-full transition-all duration-500"
                  :style="{ width: progress + '%' }"
                ></div>
              </div>
              <p class="text-sm text-gray-500">{{ progress }}% completado</p>
            </div>
          </div>

                     <!-- Resultados -->
           <div v-else-if="geoResults" class="space-y-6">
             <!-- Resumen ejecutivo -->
             <div class="card">
               <div class="card-header">
                 <h2 class="card-title">Resumen del Análisis Local</h2>
               </div>
               <div class="prose max-w-none">
                 <div v-html="geoResults.summary"></div>
               </div>
             </div>

             <!-- Mapa interactivo -->
             <div v-if="geoResults.locations && geoResults.locations.length > 0" class="card">
               <div class="card-header">
                 <h2 class="card-title">Mapa de Posicionamiento Local</h2>
               </div>
               <GeoMap 
                 :geo-results="geoResults"
                 :map-height="600"
                 @map-captured="handleMapCaptured"
               />
             </div>

             <!-- Mapas estáticos para informes -->
             <div v-if="geoResults.locations && geoResults.locations.length > 0" class="card">
               <div class="card-header">
                 <h2 class="card-title">Mapas Estáticos para Informes</h2>
               </div>
               <StaticMap 
                 :geo-results="geoResults"
                 @maps-generated="handleStaticMapsGenerated"
               />
             </div>

            <!-- Rankings por plataforma -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- Google Maps -->
              <div class="card">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-blue-500 rounded flex items-center justify-center mr-3">
                    <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                  </div>
                  <h3 class="text-lg font-semibold">Google Maps</h3>
                </div>
                <div class="text-center">
                  <div class="text-3xl font-bold text-blue-600 mb-2">
                    {{ geoResults.google_maps_ranking || 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-600">Posición promedio</div>
                </div>
              </div>

              <!-- Apple Maps -->
              <div class="card">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-gray-800 rounded flex items-center justify-center mr-3">
                    <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                  </div>
                  <h3 class="text-lg font-semibold">Apple Maps</h3>
                </div>
                <div class="text-center">
                  <div class="text-3xl font-bold text-gray-800 mb-2">
                    {{ geoResults.apple_maps_ranking || 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-600">Posición promedio</div>
                </div>
              </div>

              <!-- Bing Maps -->
              <div class="card">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-green-600 rounded flex items-center justify-center mr-3">
                    <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                    </svg>
                  </div>
                  <h3 class="text-lg font-semibold">Bing Maps</h3>
                </div>
                <div class="text-center">
                  <div class="text-3xl font-bold text-green-600 mb-2">
                    {{ geoResults.bing_maps_ranking || 'N/A' }}
                  </div>
                  <div class="text-sm text-gray-600">Posición promedio</div>
                </div>
              </div>
            </div>

            <!-- Detalles por palabra clave -->
            <div class="card">
              <div class="card-header">
                <h2 class="card-title">Rankings por Palabra Clave</h2>
              </div>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Palabra Clave
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Google Maps
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Apple Maps
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Bing Maps
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="keyword in geoResults.keyword_rankings" :key="keyword.keyword">
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {{ keyword.keyword }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ keyword.google_maps_position || 'N/A' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ keyword.apple_maps_position || 'N/A' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ keyword.bing_maps_position || 'N/A' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Recomendaciones -->
            <div class="card">
              <div class="card-header">
                <h2 class="card-title">Recomendaciones para SEO Local</h2>
              </div>
              <div class="prose max-w-none">
                <div v-html="geoResults.recommendations"></div>
              </div>
            </div>

            <!-- Acciones -->
            <div class="flex flex-col sm:flex-row gap-4">
              <button 
                @click="exportGeoReport"
                class="btn-primary flex-1"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Exportar Reporte
              </button>
              <router-link 
                to="/analyze" 
                class="btn-secondary flex-1 text-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Análisis SEO Completo
              </router-link>
            </div>
          </div>

          <!-- Estado inicial -->
          <div v-else class="card">
            <div class="text-center py-12">
              <div class="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                ¿Listo para analizar tu SEO local?
              </h3>
              <p class="text-gray-600">
                Completa el formulario y descubre cómo mejorar tu posicionamiento en mapas
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import { useToast } from 'vue-toastification'
import GeoMap from '@/components/GeoMap.vue'
import StaticMap from '@/components/StaticMap.vue'

const analysisStore = useAnalysisStore()
const toast = useToast()

// Estado reactivo
const isLoading = computed(() => analysisStore.isLoading)
const geoResults = ref(null)
const progress = ref(0)

// Formulario
const formData = reactive({
  url: '',
  company_name: '',
  keywords: '',
  location: '',
  latitude: '',
  longitude: '',
  local_radius_km: 10,
  geo_samples: 10
})

// Errores de validación
const errors = reactive({})

// Validación del formulario
const validateForm = () => {
  errors.value = {}
  
  if (!formData.url) {
    errors.url = 'La URL es requerida'
  } else if (!isValidUrl(formData.url)) {
    errors.url = 'Ingresa una URL válida'
  }
  
  if (!formData.company_name) {
    errors.company_name = 'El nombre de la empresa es requerido'
  }
  
  if (!formData.keywords || !formData.keywords.trim()) {
    errors.keywords = 'Las palabras clave son requeridas'
  } else {
    // Validar que al menos una keyword sea válida
    const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0)
    if (keywords.length === 0) {
      errors.keywords = 'Debes ingresar al menos una palabra clave válida'
    }
  }
  
  if (!formData.location) {
    errors.location = 'La ubicación es requerida'
  }
  
  if (!formData.local_radius_km) {
    errors.local_radius_km = 'El radio local es requerido'
  }
  
  if (!formData.geo_samples) {
    errors.geo_samples = 'El número de muestras es requerido'
  }
  
  return Object.keys(errors).length === 0
}

// Validar URL
const isValidUrl = (string) => {
  try {
    new URL(string)
    return true
  } catch (_) {
    return false
  }
}

// Iniciar análisis geográfico
const startGeoAnalysis = async () => {
  if (!validateForm()) {
    toast.error('Por favor, corrige los errores en el formulario')
    return
  }

  // Preparar datos para el backend
  const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0)
  
  const geoData = {
    url: formData.url,
    company_name: formData.company_name,
    keywords: keywords,
    location: formData.location,
    latitude: formData.latitude ? parseFloat(formData.latitude) : null,
    longitude: formData.longitude ? parseFloat(formData.longitude) : null,
    local_radius_km: parseInt(formData.local_radius_km),
    geo_samples: parseInt(formData.geo_samples)
  }

  try {
    // Simular progreso
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 10
      }
    }, 1000)

    const result = await analysisStore.startGeoAnalysis(geoData)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    geoResults.value = result
    
  } catch (error) {
    progress.value = 0
    console.error('Error en el análisis geográfico:', error)
  }
}

// Exportar reporte geográfico
const exportGeoReport = async () => {
  if (!geoResults.value) return
  
  try {
    // Aquí implementarías la exportación del reporte geográfico
    toast.success('Reporte geográfico exportado')
  } catch (error) {
    console.error('Error al exportar:', error)
  }
}

// Manejar captura del mapa
const handleMapCaptured = async (mapData) => {
  try {
    if (geoResults.value?.id) {
      await analysisStore.saveMapImage(geoResults.value.id, mapData)
    } else {
      // Si no hay ID, solo mostrar la imagen
      toast.success(`Mapa capturado para: ${mapData.keyword}`)
    }
  } catch (error) {
    console.error('Error al guardar el mapa:', error)
  }
}

// Manejar mapas estáticos generados
const handleStaticMapsGenerated = (maps) => {
  console.log('Mapas estáticos generados:', maps)
  toast.success(`${maps.length} mapas estáticos generados para informes`)
  
  // Aquí puedes guardar los mapas estáticos o enviarlos al backend
  // maps contiene un array de objetos con keyword, dataUrl y timestamp
}
</script> 