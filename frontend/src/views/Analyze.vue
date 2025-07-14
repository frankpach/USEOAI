<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container mx-auto px-4 py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Análisis SEO Completo
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Analiza tu sitio web con herramientas gratuitas y obtén recomendaciones personalizadas con IA
          </p>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Formulario de análisis -->
        <div class="lg:col-span-1">
          <div class="card sticky top-8">
            <div class="card-header">
              <h2 class="card-title">Configuración del Análisis</h2>
            </div>

            <form @submit.prevent="startAnalysis" class="space-y-6">
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

              <!-- Objetivo SEO -->
              <div>
                <label for="seoGoal" class="form-label">
                  Objetivo SEO *
                </label>
                <select
                  id="seoGoal"
                  v-model="formData.seo_goal"
                  required
                  class="form-input"
                  :class="{ 'border-danger-500': errors.seo_goal }"
                >
                  <option value="">Selecciona un objetivo</option>
                  <option value="Rank for web development services">Servicios de Desarrollo Web</option>
                  <option value="Improve local restaurant visibility">Visibilidad Local de Restaurantes</option>
                  <option value="Increase e-commerce sales">Aumentar Ventas E-commerce</option>
                  <option value="Blog content optimization">Optimización de Contenido de Blog</option>
                  <option value="Professional services ranking">Posicionamiento de Servicios Profesionales</option>
                </select>
                <p v-if="errors.seo_goal" class="form-error">{{ errors.seo_goal }}</p>
              </div>

              <!-- Idioma -->
              <div>
                <label for="language" class="form-label">
                  Idioma *
                </label>
                <select
                  id="language"
                  v-model="formData.language"
                  required
                  class="form-input"
                  :class="{ 'border-danger-500': errors.language }"
                >
                  <option value="">Selecciona un idioma</option>
                  <option value="es">Español</option>
                  <option value="en">Inglés</option>
                  <option value="fr">Francés</option>
                  <option value="de">Alemán</option>
                  <option value="it">Italiano</option>
                  <option value="pt">Portugués</option>
                </select>
                <p v-if="errors.language" class="form-error">{{ errors.language }}</p>
              </div>

              <!-- Sector/Industria -->
              <div>
                <label for="industry" class="form-label">
                  Sector/Industria
                </label>
                <select
                  id="industry"
                  v-model="formData.industry"
                  class="form-input"
                >
                  <option value="">Selecciona un sector</option>
                  <option value="technology">Tecnología</option>
                  <option value="healthcare">Salud</option>
                  <option value="education">Educación</option>
                  <option value="finance">Finanzas</option>
                  <option value="retail">Comercio</option>
                  <option value="travel">Viajes</option>
                  <option value="food">Restaurantes</option>
                  <option value="real_estate">Bienes Raíces</option>
                  <option value="automotive">Automotriz</option>
                  <option value="other">Otro</option>
                </select>
              </div>

              <!-- Configuración de geolocalización -->
              <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">
                  Configuración Local (Opcional)
                </h3>

                <!-- Checkbox para incluir análisis local -->
                <div class="flex items-center mb-4">
                  <input
                    type="checkbox"
                    id="includeLocal"
                    v-model="includeLocal"
                    class="form-checkbox mr-2"
                  />
                  <label for="includeLocal" class="form-label">
                    Incluir Análisis de Posicionamiento Local
                  </label>
                </div>
                <p v-if="!includeLocal" class="text-sm text-gray-500 mb-4">
                  Si deseas analizar el posicionamiento de tu sitio en mapas y resultados locales, activa esta opción y completa los campos de geolocalización.
                </p>

                <!-- Ubicación -->
                <div v-if="includeLocal" class="mb-4">
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

                <!-- Palabras clave para análisis local -->
                <div v-if="includeLocal" class="mb-4">
                  <label for="keywords" class="form-label">
                    Palabras clave para análisis local
                    <span class="text-sm text-gray-500">(opcional)</span>
                  </label>
                  <textarea
                    id="keywords"
                    v-model="formData.keywords"
                    placeholder="restaurante, comida italiana, pizza (separadas por comas)"
                    rows="3"
                    class="form-input"
                    :class="{ 'border-danger-500': errors.keywords }"
                  ></textarea>
                  <p v-if="errors.keywords" class="form-error">{{ errors.keywords }}</p>
                  <p class="text-sm text-gray-500 mt-1">
                    Si proporcionas palabras clave, se realizará un análisis local específico con estas keywords.
                  </p>
                </div>

                <!-- Coordenadas -->
                <div v-if="includeLocal" class="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label for="latitude" class="form-label">Latitud</label>
                    <input
                      id="latitude"
                      v-model="formData.latitude"
                      type="number"
                      step="any"
                      placeholder="40.4168"
                      class="form-input"
                      :class="{ 'border-danger-500': errors.latitude }"
                    />
                    <p v-if="errors.latitude" class="form-error">{{ errors.latitude }}</p>
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
                      :class="{ 'border-danger-500': errors.longitude }"
                    />
                    <p v-if="errors.longitude" class="form-error">{{ errors.longitude }}</p>
                  </div>
                </div>

                <!-- Radio local -->
                <div v-if="includeLocal" class="mb-4">
                  <label for="localRadius" class="form-label">
                    Radio local (km)
                  </label>
                  <input
                    id="localRadius"
                    v-model="formData.local_radius_km"
                    type="number"
                    min="1"
                    max="100"
                    placeholder="10"
                    class="form-input"
                    :class="{ 'border-danger-500': errors.local_radius_km }"
                  />
                  <p v-if="errors.local_radius_km" class="form-error">{{ errors.local_radius_km }}</p>
                </div>

                <!-- Muestras geográficas -->
                <div v-if="includeLocal" class="mb-4">
                  <label for="geoSamples" class="form-label">
                    Muestras geográficas
                  </label>
                  <input
                    id="geoSamples"
                    v-model="formData.geo_samples"
                    type="number"
                    min="1"
                    max="50"
                    placeholder="10"
                    class="form-input"
                    :class="{ 'border-danger-500': errors.geo_samples }"
                  />
                  <p v-if="errors.geo_samples" class="form-error">{{ errors.geo_samples }}</p>
                </div>
              </div>

              <!-- Checkbox para forzar Playwright (avanzado) -->
              <div class="flex items-center mb-4">
                <input
                  type="checkbox"
                  id="forcePlaywright"
                  v-model="forcePlaywright"
                  class="form-checkbox mr-2"
                />
                <label for="forcePlaywright" class="form-label">
                  Forzar renderizado JS (Playwright)
                </label>
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Iniciar Análisis
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
                Analizando tu sitio web...
              </h3>
              <p class="text-gray-600 mb-6">
                Esto puede tomar unos minutos. Estamos realizando un análisis completo.
              </p>

              <!-- Progreso -->
              <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all duration-500"
                  :style="{ width: progress + '%' }"
                ></div>
              </div>
              <p class="text-sm text-gray-500">{{ progress }}% completado</p>
            </div>
          </div>

          <!-- Resultados -->
          <div v-else-if="currentAnalysis" class="space-y-6">
            <!-- Resumen ejecutivo -->
            <div class="card">
              <div class="card-header">
                <h2 class="card-title">Resumen Ejecutivo</h2>
              </div>
              <div class="prose max-w-none">
                <div v-html="currentAnalysis.executive_summary"></div>
              </div>
            </div>

            <!-- Métricas principales -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="card text-center">
                <div class="text-3xl font-bold text-primary-600 mb-2">
                  {{ currentAnalysis.technical_score || 'N/A' }}
                </div>
                <div class="text-sm text-gray-600">Puntuación Técnica</div>
              </div>
              <div class="card text-center">
                <div class="text-3xl font-bold text-success-600 mb-2">
                  {{ currentAnalysis.onpage_score || 'N/A' }}
                </div>
                <div class="text-sm text-gray-600">Puntuación On-Page</div>
              </div>
              <div class="card text-center">
                <div class="text-3xl font-bold text-warning-600 mb-2">
                  {{ currentAnalysis.offpage_score || 'N/A' }}
                </div>
                <div class="text-sm text-gray-600">Puntuación Off-Page</div>
              </div>
            </div>

            <!-- Acciones -->
            <div class="flex flex-col sm:flex-row gap-4">
              <router-link
                :to="`/report/${currentAnalysis.id}`"
                class="btn-primary flex-1 text-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Ver Informe Completo
              </router-link>
              <button
                @click="exportReport"
                class="btn-secondary flex-1"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Exportar PDF
              </button>
            </div>
          </div>

          <!-- Estado inicial -->
          <div v-else class="card">
            <div class="text-center py-12">
              <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                ¿Listo para analizar?
              </h3>
              <p class="text-gray-600">
                Completa el formulario y obtén un análisis SEO completo de tu sitio web
              </p>
            </div>
          </div>

          <!-- Sección avanzada: Comparar análisis en línea vs HTML local -->
          <div class="mt-8 p-4 border rounded bg-gray-50">
            <h3 class="font-bold mb-2">Comparar análisis en línea vs HTML local</h3>
            <div class="mb-2">
              <label class="block mb-1">Subir archivo HTML local:</label>
              <input type="file" accept=".html" @change="onHtmlFileChange" />
            </div>
            <button
              class="bg-blue-600 text-white px-4 py-2 rounded mt-2"
              :disabled="!htmlFile || loadingCompare"
              @click="compareOnlineVsLocal"
            >
              Comparar análisis
            </button>
            <div v-if="compareError" class="text-red-600 mt-2">{{ compareError }}</div>
            <div v-if="loadingCompare" class="mt-2">Comparando...</div>
            <div v-if="compareResult" class="mt-4 grid grid-cols-2 gap-4">
              <div>
                <h4 class="font-semibold">Análisis en línea</h4>
                <div v-if="compareResult.online">
                  <p><b>Total de Imágenes:</b> {{ compareResult.online.images_count ?? (compareResult.online.page_metrics?.resource_counts?.images_total ?? 'N/A') }}</p>
                  <p><b>Tiempo de Carga:</b> {{ compareResult.online.page_metrics?.load_time ?? 'N/A' }}s</p>
                  <p><b>Tamaño de Página:</b> {{ compareResult.online.page_metrics?.page_size_kb ?? 'N/A' }}KB</p>
                </div>
              </div>
              <div>
                <h4 class="font-semibold">Análisis HTML local</h4>
                <div v-if="compareResult.local">
                  <p><b>Total de Imágenes:</b> {{ compareResult.local.images_count ?? (compareResult.local.page_metrics?.resource_counts?.images_total ?? 'N/A') }}</p>
                  <p><b>Tiempo de Carga:</b> {{ compareResult.local.page_metrics?.load_time ?? 'N/A' }}s</p>
                  <p><b>Tamaño de Página:</b> {{ compareResult.local.page_metrics?.page_size_kb ?? 'N/A' }}KB</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useToast } from 'vue-toastification'

const router = useRouter()
const analysisStore = useAnalysisStore()
const toast = useToast()

// Estado reactivo
const isLoading = computed(() => analysisStore.isLoading)
const currentAnalysis = computed(() => analysisStore.currentAnalysis)
const progress = ref(0)
const includeLocal = ref(false)
const forcePlaywright = ref(false)

// Formulario
const formData = reactive({
  url: '',
  seo_goal: '',
  language: '',
  industry: '',
  location: '',
  keywords: '',
  latitude: '',
  longitude: '',
  local_radius_km: 10,
  geo_samples: 10
})

// Watch para limpiar campos locales si se desactiva el checkbox
watch(includeLocal, (val) => {
  if (!val) {
    formData.location = ''
    formData.keywords = ''
    formData.latitude = ''
    formData.longitude = ''
    formData.local_radius_km = 10
    formData.geo_samples = 10
  }
})

// Errores de validación
const errors = reactive({})

// Validación del formulario
const validateForm = () => {
  // Limpiar errores previos
  Object.keys(errors).forEach(key => delete errors[key])

  if (!formData.url) {
    errors.url = 'La URL es requerida'
  } else if (!isValidUrl(formData.url)) {
    errors.url = 'Ingresa una URL válida'
  }

  if (!formData.seo_goal) {
    errors.seo_goal = 'Selecciona un objetivo SEO'
  }

  if (!formData.language) {
    errors.language = 'Selecciona un idioma'
  }

  // Validación local solo si el checkbox está activo
  if (includeLocal.value) {
    // Al menos ubicación o lat/lon
    if (!formData.location && (!formData.latitude || !formData.longitude)) {
      errors.location = 'Debes ingresar una ubicación o latitud y longitud'
      errors.latitude = 'Debes ingresar una ubicación o latitud y longitud'
      errors.longitude = 'Debes ingresar una ubicación o latitud y longitud'
    }
    // Validar lat/lon si se llenan
    if (formData.latitude) {
      const lat = parseFloat(formData.latitude)
      if (isNaN(lat) || lat < -90 || lat > 90) {
        errors.latitude = 'La latitud debe estar entre -90 y 90'
      }
    }
    if (formData.longitude) {
      const lng = parseFloat(formData.longitude)
      if (isNaN(lng) || lng < -180 || lng > 180) {
        errors.longitude = 'La longitud debe estar entre -180 y 180'
      }
    }
    // Validar radio
    if (formData.local_radius_km) {
      const radius = parseInt(formData.local_radius_km)
      if (isNaN(radius) || radius < 1 || radius > 100) {
        errors.local_radius_km = 'El radio debe estar entre 1 y 100 km'
      }
    }
    // Validar muestras
    if (formData.geo_samples) {
      const samples = parseInt(formData.geo_samples)
      if (isNaN(samples) || samples < 1 || samples > 50) {
        errors.geo_samples = 'Las muestras deben estar entre 1 y 50'
      }
    }
    // Validar keywords (si se llenan)
    if (formData.keywords && formData.keywords.trim()) {
      const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0)
      if (keywords.length === 0) {
        errors.keywords = 'Debes ingresar al menos una palabra clave válida'
      }
    }
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

// Iniciar análisis
const startAnalysis = async () => {
  if (!validateForm()) {
    const errorMessages = Object.values(errors).join(', ')
    toast.error(`Por favor, corrige los errores en el formulario: ${errorMessages}`)
    return
  }

  // Preparar datos para el backend
  const keywords = formData.keywords ? formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0) : []

  const analysisData = {
    url: formData.url,
    seo_goal: formData.seo_goal,
    language: formData.language,
    location: formData.location,
    keywords: keywords,
    latitude: formData.latitude ? parseFloat(formData.latitude) : null,
    longitude: formData.longitude ? parseFloat(formData.longitude) : null,
    local_radius_km: formData.local_radius_km ? parseInt(formData.local_radius_km) : null,
    geo_samples: formData.geo_samples ? parseInt(formData.geo_samples) : null
  }
  // Incluir el campo force_playwright si el usuario lo activa
  if (forcePlaywright.value) {
    analysisData.force_playwright = true
  }

  try {
    // Simular progreso
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 10
      }
    }, 1000)

    const result = await analysisStore.startAnalysis(analysisData)

    clearInterval(progressInterval)
    progress.value = 100

    // Redirigir al informe después de un breve delay
    setTimeout(() => {
      router.push(`/report/${result.id}`)
    }, 2000)

  } catch (error) {
    progress.value = 0
    console.error('Error en el análisis:', error)
  }
}

// Exportar reporte
const exportReport = async () => {
  if (!currentAnalysis.value) return

  try {
    await analysisStore.exportReport(currentAnalysis.value.id, 'pdf')
  } catch (error) {
    console.error('Error al exportar:', error)
  }
}

// Comparar análisis en línea vs HTML local
const htmlFile = ref(null)
const compareResult = ref(null)
const compareError = ref('')
const loadingCompare = ref(false)

const onHtmlFileChange = (e) => {
  htmlFile.value = e.target.files[0] || null
}

const compareOnlineVsLocal = async () => {
  compareError.value = ''
  compareResult.value = null
  if (!htmlFile.value) {
    compareError.value = 'Debes subir un archivo HTML.'
    return
  }
  loadingCompare.value = true
  try {
    // 1. Analizar en línea (API normal)
    const onlineRes = await analysisStore.getAnalysisByUrl({
      url: formData.url,
      seo_goal: formData.seo_goal,
      language: formData.language,
      industry: formData.industry,
      location: formData.location,
      keywords: formData.keywords ? formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0) : [],
      latitude: formData.latitude ? parseFloat(formData.latitude) : null,
      longitude: formData.longitude ? parseFloat(formData.longitude) : null,
      local_radius_km: formData.local_radius_km ? parseInt(formData.local_radius_km) : null,
      geo_samples: formData.geo_samples ? parseInt(formData.geo_samples) : null,
      force_playwright: forcePlaywright.value
    })
    // 2. Analizar HTML local (API especial para HTML)
    const formData = new FormData()
    formData.append('html_file', htmlFile.value)
    formData.append('seo_goal', formData.seo_goal)
    formData.append('language', formData.language)
    formData.append('industry', formData.industry)
    formData.append('url', formData.url)
    formData.append('location', formData.location)
    formData.append('keywords', formData.keywords)
    formData.append('latitude', formData.latitude)
    formData.append('longitude', formData.longitude)
    formData.append('local_radius_km', formData.local_radius_km)
    formData.append('geo_samples', formData.geo_samples)
    formData.append('force_playwright', forcePlaywright.value)

    const localRes = await analysisStore.analyzeHtmlFile(formData)
    compareResult.value = {
      online: onlineRes,
      local: localRes
    }
  } catch (err) {
    compareError.value = 'Error al comparar: ' + (err.message || err)
  } finally {
    loadingCompare.value = false
  }
}
</script>
