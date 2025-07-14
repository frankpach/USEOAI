# Funcionalidades de Mapas - USEOAI Frontend

## 📍 Resumen

Este documento describe las funcionalidades de mapas implementadas en el frontend de USEOAI para el análisis SEO local.

## 🗺️ Componentes de Mapas

### 1. GeoMap.vue - Mapa Interactivo

**Propósito**: Visualización interactiva de rankings locales con funcionalidades avanzadas.

**Características**:
- Mapa interactivo usando Leaflet
- Marcadores coloridos según el ranking (verde=excelente, amarillo=bueno, naranja=regular, rojo=necesita mejora)
- Tooltips informativos con detalles por ubicación
- Filtrado dinámico por palabra clave
- Captura de imagen del mapa
- Leyenda visual

**Props**:
```javascript
{
  geoResults: Object,    // Datos del análisis geográfico
  mapHeight: Number      // Altura del mapa (default: 500)
}
```

**Events**:
```javascript
{
  'map-captured': (mapData) => void  // Cuando se captura una imagen del mapa
}
```

**Uso**:
```vue
<GeoMap 
  :geo-results="geoResults"
  :map-height="600"
  @map-captured="handleMapCaptured"
/>
```

### 2. StaticMap.vue - Generador de Mapas Estáticos

**Propósito**: Generación automática de mapas estáticos de 600x600px para informes PDF.

**Características**:
- Generación automática de mapas por palabra clave
- Mapa estático sin controles interactivos
- Vista previa de mapas generados
- Descarga individual de mapas
- Generación en lote para todas las palabras clave

**Props**:
```javascript
{
  geoResults: Object  // Datos del análisis geográfico
}
```

**Events**:
```javascript
{
  'maps-generated': (maps) => void  // Cuando se generan mapas estáticos
}
```

**Uso**:
```vue
<StaticMap 
  :geo-results="geoResults"
  @maps-generated="handleStaticMapsGenerated"
/>
```

## 🎨 Sistema de Colores

### Marcadores de Ranking

| Ranking | Color | Descripción |
|---------|-------|-------------|
| 1-3 | Verde (#10B981) | Excelente |
| 4-10 | Amarillo (#F59E0B) | Bueno |
| 11-20 | Naranja (#F97316) | Regular |
| 21+ | Rojo (#EF4444) | Necesita mejora |

## 📊 Estructura de Datos

### GeoResults Object

```javascript
{
  id: String,
  company_name: String,
  keywords: Array<String>,
  location: String,
  latitude: Number,
  longitude: Number,
  local_radius_km: Number,
  geo_samples: Number,
  summary: String,
  keyword_rankings: Array<{
    keyword: String,
    location_id: String,
    average_position: Number,
    samples: Array<{
      position: Number,
      timestamp: String
    }>
  }>,
  locations: Array<{
    id: String,
    name: String,
    address: String,
    latitude: Number,
    longitude: Number
  }>,
  timestamp: String
}
```

## 🔧 Funcionalidades Implementadas

### 1. Filtrado por Palabra Clave

- Dropdown para seleccionar palabra clave específica
- Opción "Todas las palabras clave" para vista general
- Actualización dinámica de marcadores según selección

### 2. Tooltips Informativos

- Información detallada por ubicación
- Promedio de rankings
- Desglose por palabra clave
- Dirección y nombre de la ubicación

### 3. Captura de Imágenes

- Captura de mapa interactivo en tiempo real
- Generación de mapas estáticos de 600x600px
- Formato PNG con alta calidad
- Descarga directa de imágenes

### 4. Integración con Informes

- Mapas incluidos en informes detallados
- Generación automática para PDF
- Almacenamiento de imágenes en el backend

## 🚀 API Endpoints

### Guardar Imagen de Mapa

```http
POST /api/analysis/{id}/map-image
Content-Type: application/json

{
  "image_data": "data:image/png;base64,...",
  "keyword": "restaurante madrid",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## 📱 Responsive Design

- Mapas adaptativos para móviles y desktop
- Controles optimizados para touch
- Tooltips responsivos
- Grid de mapas estáticos adaptativo

## 🎯 Casos de Uso

### 1. Análisis SEO Local
- Visualización de rankings en diferentes ubicaciones
- Comparación de posicionamiento por zona
- Identificación de áreas de oportunidad

### 2. Informes para Clientes
- Mapas estáticos incluidos en PDF
- Visualización profesional de resultados
- Documentación de análisis realizados

### 3. Presentaciones
- Captura de mapas para presentaciones
- Exportación de imágenes de alta calidad
- Material visual para reuniones

## 🔍 Ejemplo de Uso Completo

```vue
<template>
  <div class="geo-analysis">
    <!-- Mapa interactivo -->
    <GeoMap 
      :geo-results="geoResults"
      :map-height="600"
      @map-captured="handleMapCaptured"
    />
    
    <!-- Mapas estáticos para informes -->
    <StaticMap 
      :geo-results="geoResults"
      @maps-generated="handleStaticMapsGenerated"
    />
  </div>
</template>

<script setup>
import GeoMap from '@/components/GeoMap.vue'
import StaticMap from '@/components/StaticMap.vue'

const handleMapCaptured = async (mapData) => {
  try {
    await analysisStore.saveMapImage(geoResults.value.id, mapData)
  } catch (error) {
    console.error('Error al guardar el mapa:', error)
  }
}

const handleStaticMapsGenerated = (maps) => {
  console.log('Mapas estáticos generados:', maps)
  // Procesar mapas para informes
}
</script>
```

## 🛠️ Dependencias

- **Leaflet**: Biblioteca de mapas interactivos
- **dom-to-image**: Captura de elementos DOM como imágenes
- **Vue 3**: Framework principal
- **TailwindCSS**: Estilos y diseño responsivo

## 📈 Próximas Mejoras

- [ ] Animaciones de marcadores
- [ ] Clusters para múltiples ubicaciones
- [ ] Heatmaps de densidad
- [ ] Exportación a formatos vectoriales (SVG)
- [ ] Integración con Google Maps API
- [ ] Personalización de estilos de mapa 