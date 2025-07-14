<template>
  <div class="static-map-container">
    <!-- Controles para generar mapas estáticos -->
    <div class="map-controls mb-4">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div class="flex-1">
          <label class="form-label">Generar mapas estáticos para:</label>
          <div class="flex flex-wrap gap-2 mt-2">
            <button
              v-for="keyword in keywords"
              :key="keyword"
              @click="generateStaticMap(keyword)"
              class="btn-secondary text-sm"
              :disabled="isGenerating"
            >
              {{ keyword }}
            </button>
            <button
              @click="generateAllMaps"
              class="btn-primary text-sm"
              :disabled="isGenerating"
            >
              Todas las palabras clave
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Vista previa de mapas generados -->
    <div v-if="generatedMaps.length > 0" class="generated-maps">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Mapas Generados</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="map in generatedMaps" 
          :key="map.keyword"
          class="map-preview-card"
        >
          <div class="map-preview-header">
            <h4 class="font-medium text-gray-900">{{ map.keyword }}</h4>
            <span class="text-xs text-gray-500">{{ map.timestamp }}</span>
          </div>
          <div class="map-preview-image">
            <img 
              :src="map.dataUrl" 
              :alt="`Mapa para ${map.keyword}`"
              class="w-full h-auto border border-gray-200 rounded"
            />
          </div>
          <div class="map-preview-actions">
            <button 
              @click="downloadMap(map)"
              class="btn-secondary text-xs"
            >
              Descargar
            </button>
            <button 
              @click="removeMap(map.keyword)"
              class="btn-danger text-xs"
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import domtoimage from 'dom-to-image'

// Props
const props = defineProps({
  geoResults: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['maps-generated'])

// Estado reactivo
const isGenerating = ref(false)
const generatedMaps = ref([])

// Computed
const keywords = computed(() => {
  if (!props.geoResults?.keyword_rankings) return []
  return [...new Set(props.geoResults.keyword_rankings.map(k => k.keyword))]
})

// Generar mapa estático para una palabra clave específica
const generateStaticMap = async (keyword) => {
  isGenerating.value = true
  
  try {
    // Crear contenedor temporal para el mapa
    const tempContainer = document.createElement('div')
    tempContainer.style.width = '600px'
    tempContainer.style.height = '600px'
    tempContainer.style.position = 'absolute'
    tempContainer.style.left = '-9999px'
    tempContainer.style.top = '-9999px'
    document.body.appendChild(tempContainer)

    // Crear mapa temporal
    const map = L.map(tempContainer, {
      center: [40.4168, -3.7038],
      zoom: 10,
      zoomControl: false,
      scrollWheelZoom: false,
      dragging: false,
      touchZoom: false,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: false
    })

    // Agregar capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    // Filtrar datos por palabra clave
    const filteredData = {
      ...props.geoResults,
      keyword_rankings: props.geoResults.keyword_rankings.filter(
        k => k.keyword === keyword
      )
    }

    // Agregar marcadores
    await addMarkersToMap(map, filteredData)

    // Centrar mapa en las ubicaciones
    if (filteredData.locations && filteredData.locations.length > 0) {
      const bounds = L.latLngBounds(
        filteredData.locations.map(loc => [loc.latitude, loc.longitude])
      )
      map.fitBounds(bounds, { padding: [20, 20] })
    }

    // Esperar a que el mapa se renderice
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Capturar imagen
    const dataUrl = await domtoimage.toPng(tempContainer, {
      width: 600,
      height: 600,
      quality: 1.0
    })

    // Limpiar
    map.remove()
    document.body.removeChild(tempContainer)

    // Agregar a la lista de mapas generados
    const mapData = {
      keyword,
      dataUrl,
      timestamp: new Date().toLocaleString('es-ES')
    }

    // Reemplazar si ya existe
    const existingIndex = generatedMaps.value.findIndex(m => m.keyword === keyword)
    if (existingIndex >= 0) {
      generatedMaps.value[existingIndex] = mapData
    } else {
      generatedMaps.value.push(mapData)
    }

    emit('maps-generated', generatedMaps.value)

  } catch (error) {
    console.error('Error al generar mapa estático:', error)
  } finally {
    isGenerating.value = false
  }
}

// Generar mapas para todas las palabras clave
const generateAllMaps = async () => {
  isGenerating.value = true
  
  try {
    for (const keyword of keywords.value) {
      await generateStaticMap(keyword)
      // Pequeña pausa entre generaciones
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  } catch (error) {
    console.error('Error al generar todos los mapas:', error)
  } finally {
    isGenerating.value = false
  }
}

// Agregar marcadores al mapa
const addMarkersToMap = async (map, data) => {
  if (!data.locations || !data.keyword_rankings) return

  data.locations.forEach((location) => {
    const locationRankings = data.keyword_rankings.filter(
      k => k.location_id === location.id
    )

    if (locationRankings.length === 0) return

    // Calcular promedio de rankings
    const avgRanking = Math.round(
      locationRankings.reduce((sum, k) => sum + (k.average_position || 0), 0) / 
      locationRankings.length
    )

    // Crear marcador personalizado
    const markerColor = getMarkerColor(avgRanking)
    const markerIcon = L.divIcon({
      className: 'static-marker',
      html: `
        <div style="
          background-color: ${markerColor};
          width: 30px;
          height: 30px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 12px;
        ">
          ${avgRanking}
        </div>
      `,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    })

    // Crear marcador
    L.marker([location.latitude, location.longitude], {
      icon: markerIcon
    }).addTo(map)
  })
}

// Obtener color del marcador según el ranking
const getMarkerColor = (ranking) => {
  if (ranking <= 3) return '#10B981' // Verde - Excelente
  if (ranking <= 10) return '#F59E0B' // Amarillo - Bueno
  if (ranking <= 20) return '#F97316' // Naranja - Regular
  return '#EF4444' // Rojo - Necesita mejora
}

// Descargar mapa
const downloadMap = (map) => {
  const link = document.createElement('a')
  link.href = map.dataUrl
  link.download = `mapa-${map.keyword.replace(/\s+/g, '-')}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Eliminar mapa
const removeMap = (keyword) => {
  generatedMaps.value = generatedMaps.value.filter(m => m.keyword !== keyword)
  emit('maps-generated', generatedMaps.value)
}

// Lifecycle
onMounted(() => {
  // Generar mapas automáticamente si hay datos
  if (keywords.value.length > 0) {
    generateAllMaps()
  }
})
</script>

<style scoped>
.static-map-container {
  @apply w-full;
}

.map-preview-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.map-preview-header {
  @apply flex justify-between items-center mb-3;
}

.map-preview-image {
  @apply mb-3;
}

.map-preview-actions {
  @apply flex gap-2;
}
</style> 