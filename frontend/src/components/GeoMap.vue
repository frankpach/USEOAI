<template>
  <div class="geo-map-container">
    <!-- Controles del mapa -->
    <div class="map-controls mb-4">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div class="flex-1">
          <label for="keywordSelect" class="form-label">Palabra Clave</label>
          <select
            id="keywordSelect"
            v-model="selectedKeyword"
            class="form-input"
            @change="updateMapMarkers"
          >
            <option value="">Todas las palabras clave</option>
            <option 
              v-for="keyword in keywords" 
              :key="keyword" 
              :value="keyword"
            >
              {{ keyword }}
            </option>
          </select>
        </div>
        <div class="flex gap-2">
          <button 
            @click="captureMapImage"
            class="btn-secondary"
            :disabled="isCapturing"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ isCapturing ? 'Capturando...' : 'Capturar Mapa' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Mapa interactivo -->
    <div 
      ref="mapContainer" 
      class="map-container"
      :style="{ height: mapHeight + 'px' }"
    >
      <div 
        ref="mapElement" 
        class="w-full h-full"
      ></div>
    </div>

    <!-- Leyenda del mapa -->
    <div class="map-legend mt-4 p-4 bg-gray-50 rounded-lg">
      <h4 class="font-semibold text-gray-900 mb-2">Leyenda</h4>
      <div class="flex flex-wrap gap-4">
        <div class="flex items-center">
          <div class="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
          <span class="text-sm text-gray-600">Excelente (1-3)</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
          <span class="text-sm text-gray-600">Bueno (4-10)</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
          <span class="text-sm text-gray-600">Regular (11-20)</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
          <span class="text-sm text-gray-600">Necesita mejora (21+)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import domtoimage from 'dom-to-image'

// Props
const props = defineProps({
  geoResults: {
    type: Object,
    required: true
  },
  mapHeight: {
    type: Number,
    default: 500
  }
})

// Emits
const emit = defineEmits(['map-captured'])

// Estado reactivo
const mapContainer = ref(null)
const mapElement = ref(null)
const selectedKeyword = ref('')
const isCapturing = ref(false)

// Variables del mapa
let map = null
let markers = []
let markerLayer = null

// Computed
const keywords = computed(() => {
  if (!props.geoResults?.keyword_rankings) return []
  return props.geoResults.keyword_rankings.map(k => k.keyword)
})

const locations = computed(() => {
  if (!props.geoResults?.locations) return []
  return props.geoResults.locations
})

// Inicializar mapa
const initMap = () => {
  if (!mapElement.value) return

  // Crear mapa
  map = L.map(mapElement.value, {
    center: [40.4168, -3.7038], // Madrid por defecto
    zoom: 10,
    zoomControl: true,
    scrollWheelZoom: true
  })

  // Agregar capa de tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Crear capa de marcadores
  markerLayer = L.layerGroup().addTo(map)

  // Centrar mapa en las ubicaciones
  centerMapOnLocations()
}

// Centrar mapa en las ubicaciones
const centerMapOnLocations = () => {
  if (!locations.value.length) return

  const bounds = L.latLngBounds(
    locations.value.map(loc => [loc.latitude, loc.longitude])
  )
  map.fitBounds(bounds, { padding: [20, 20] })
}

// Obtener color del marcador según el ranking
const getMarkerColor = (ranking) => {
  if (ranking <= 3) return '#10B981' // Verde - Excelente
  if (ranking <= 10) return '#F59E0B' // Amarillo - Bueno
  if (ranking <= 20) return '#F97316' // Naranja - Regular
  return '#EF4444' // Rojo - Necesita mejora
}

// Obtener datos filtrados por palabra clave
const getFilteredData = () => {
  if (!selectedKeyword.value) {
    return props.geoResults
  }

  const filtered = {
    ...props.geoResults,
    keyword_rankings: props.geoResults.keyword_rankings.filter(
      k => k.keyword === selectedKeyword.value
    )
  }

  return filtered
}

// Actualizar marcadores del mapa
const updateMapMarkers = () => {
  if (!map || !markerLayer) return

  // Limpiar marcadores existentes
  markerLayer.clearLayers()
  markers = []

  const data = getFilteredData()
  if (!data.locations || !data.keyword_rankings) return

  // Crear marcadores para cada ubicación
  data.locations.forEach((location, index) => {
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
      className: 'custom-marker',
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
    const marker = L.marker([location.latitude, location.longitude], {
      icon: markerIcon
    }).addTo(markerLayer)

    // Crear tooltip con información detallada
    const tooltipContent = createTooltipContent(location, locationRankings, avgRanking)
    marker.bindTooltip(tooltipContent, {
      direction: 'top',
      offset: [0, -40],
      className: 'custom-tooltip'
    })

    markers.push(marker)
  })
}

// Crear contenido del tooltip
const createTooltipContent = (location, rankings, avgRanking) => {
  const rankingsList = rankings.map(r => 
    `<div class="flex justify-between">
       <span>${r.keyword}:</span>
       <span class="font-semibold">${r.average_position || 'N/A'}</span>
     </div>`
  ).join('')

  return `
    <div class="p-3 max-w-xs">
      <h4 class="font-bold text-gray-900 mb-2">${location.name}</h4>
      <div class="text-sm text-gray-600 mb-2">
        <div>${location.address}</div>
        <div>Promedio: <span class="font-semibold">${avgRanking}</span></div>
      </div>
      <div class="text-xs text-gray-500">
        ${rankingsList}
      </div>
    </div>
  `
}

// Capturar imagen del mapa
const captureMapImage = async () => {
  if (!mapContainer.value) return

  isCapturing.value = true

  try {
    // Esperar a que el mapa se renderice completamente
    await nextTick()
    
    // Capturar imagen
    const dataUrl = await domtoimage.toPng(mapContainer.value, {
      width: 600,
      height: 600,
      quality: 1.0
    })

    // Emitir evento con la imagen
    emit('map-captured', {
      dataUrl,
      keyword: selectedKeyword.value || 'Todas las palabras clave',
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Error al capturar el mapa:', error)
  } finally {
    isCapturing.value = false
  }
}

// Watchers
watch(() => props.geoResults, () => {
  if (map) {
    updateMapMarkers()
  }
}, { deep: true })

watch(selectedKeyword, () => {
  updateMapMarkers()
})

// Lifecycle
onMounted(() => {
  nextTick(() => {
    initMap()
    updateMapMarkers()
  })
})
</script>

<style scoped>
.geo-map-container {
  @apply w-full;
}

.map-container {
  @apply relative border border-gray-200 rounded-lg overflow-hidden;
}

.map-container :deep(.leaflet-container) {
  @apply w-full h-full;
}

.map-container :deep(.custom-tooltip) {
  @apply bg-white border border-gray-200 rounded-lg shadow-lg;
}

.map-container :deep(.leaflet-tooltip-content) {
  @apply m-0;
}

.map-container :deep(.custom-marker) {
  @apply border-0;
}
</style> 