# USEOAI Frontend

Frontend de la aplicación USEOAI - Análisis SEO con Inteligencia Artificial.

## 🚀 Características

- **Vue 3** con Composition API
- **TailwindCSS** para estilos
- **Pinia** para gestión de estado
- **Vue Router** para navegación
- **Axios** para comunicación con API
- **Vue Toastification** para notificaciones
- **Chart.js** para gráficos
- **Leaflet** para mapas interactivos
- **Mapas Estáticos** para informes PDF
- **Responsive Design** para móviles y desktop

## 📋 Requisitos Previos

- Node.js 16+ 
- npm o yarn
- Backend USEOAI ejecutándose en `http://localhost:8000`

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd USEOAI_App/frontend
```

2. **Instalar dependencias**

**Opción 1: Usando scripts automáticos**
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

**Opción 2: Instalación manual**
```bash
npm install --legacy-peer-deps
# o
yarn install --legacy-peer-deps
```

**Nota**: Usamos `--legacy-peer-deps` para evitar conflictos de dependencias entre ApexCharts y Vue3-ApexCharts.

3. **Configurar variables de entorno**
```bash
# Crear archivo .env.local
cp env.example .env.local
```

Editar `.env.local`:
```env
# URL del backend USEOAI
VITE_API_URL=http://localhost:8000

# Configuración de desarrollo
VITE_DEV_MODE=true
VITE_DEBUG_MAPS=false

# Configuración de mapas
VITE_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
VITE_MAP_ATTRIBUTION=© OpenStreetMap contributors
```

4. **Ejecutar en desarrollo**
```bash
npm run dev
# o
yarn dev
```

La aplicación estará disponible en `http://localhost:3000`

## 🏗️ Scripts Disponibles

```bash
# Desarrollo
npm run dev

# Construir para producción
npm run build

# Vista previa de producción
npm run preview

# Linting
npm run lint
```

## 📁 Estructura del Proyecto

```
frontend/
├── public/                 # Archivos estáticos
├── src/
│   ├── components/         # Componentes reutilizables
│   │   └── layout/        # Componentes de layout
│   ├── router/            # Configuración de rutas
│   ├── services/          # Servicios de API
│   ├── stores/            # Stores de Pinia
│   ├── views/             # Páginas de la aplicación
│   ├── App.vue           # Componente raíz
│   ├── main.js           # Punto de entrada
│   └── style.css         # Estilos globales
├── index.html            # HTML principal
├── package.json          # Dependencias
├── vite.config.js        # Configuración de Vite
└── tailwind.config.js    # Configuración de TailwindCSS
```

## 🎨 Componentes Principales

### Layout
- **NavBar.vue** - Navegación principal
- **FooterComponent.vue** - Pie de página

### Páginas
- **Home.vue** - Página de inicio
- **Analyze.vue** - Análisis SEO completo
- **GeoAnalysis.vue** - Análisis SEO local
- **Report.vue** - Vista de informe detallado
- **Reports.vue** - Historial de informes
- **About.vue** - Información del proyecto
- **NotFound.vue** - Página 404

### Componentes de Mapas
- **GeoMap.vue** - Mapa interactivo con Leaflet
- **StaticMap.vue** - Generador de mapas estáticos para informes

### Stores
- **analysis.js** - Gestión de análisis SEO

### Servicios
- **api.js** - Configuración de Axios y endpoints

## 🔧 Configuración

### Variables de Entorno

```env
# URL del backend
VITE_API_URL=http://localhost:8000
```

### TailwindCSS

El proyecto usa TailwindCSS con configuración personalizada en `tailwind.config.js`:

- Colores personalizados (primary, success, warning, danger)
- Fuente Inter
- Animaciones personalizadas
- Plugins: forms, typography

### Vite

Configuración en `vite.config.js`:

- Proxy para desarrollo (`/api` → `http://localhost:8000`)
- Alias `@` para `src/`
- Puerto 3000

## 📱 Funcionalidades

### Análisis SEO Completo
- Formulario de configuración
- Progreso en tiempo real
- Resultados detallados
- Exportación a PDF

### Análisis SEO Local
- Configuración geográfica
- Rankings en Google Maps, Apple Maps, Bing Maps
- Análisis por palabra clave
- **Mapas Interactivos**: Visualización de rankings con marcadores coloridos
- **Filtrado Dinámico**: Selección de palabras clave para análisis específicos
- **Tooltips Informativos**: Información detallada de rankings por ubicación
- **Mapas Estáticos**: Generación automática de mapas de 600x600px para informes PDF

### Informes
- Vista detallada de resultados
- Métricas y gráficos
- Checklist interactivo
- Recomendaciones personalizadas

### Historial
- Lista de análisis realizados
- Exportación de informes
- Gestión de historial

## 🎯 Rutas de la API

El frontend se comunica con el backend a través de:

- `POST /api/analyze` - Análisis SEO completo
- `POST /api/geo-rank-analysis` - Análisis geográfico
- `GET /api/analysis/{id}` - Obtener análisis por ID
- `GET /api/analysis/{id}/export` - Exportar informe
- `GET /api/health` - Health check

## 🚀 Despliegue

### Desarrollo
```bash
npm run dev
```

### Producción
```bash
npm run build
npm run preview
```

### Docker (opcional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🧪 Testing

```bash
# Ejecutar tests
npm run test

# Tests en modo watch
npm run test:watch

# Cobertura de tests
npm run test:coverage
```

## 📦 Dependencias Principales

### Producción
- `vue` - Framework principal
- `vue-router` - Enrutamiento
- `pinia` - Gestión de estado
- `axios` - Cliente HTTP
- `tailwindcss` - Framework CSS
- `chart.js` - Gráficos
- `vue-chartjs` - Integración Vue-Chart.js
- `vue-toastification` - Notificaciones
- `html2canvas` - Captura de pantalla
- `jspdf` - Generación de PDF

### Desarrollo
- `@vitejs/plugin-vue` - Plugin Vue para Vite
- `vite` - Build tool
- `autoprefixer` - Autoprefixer CSS
- `postcss` - PostCSS
- `eslint` - Linting
- `prettier` - Formateo de código

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](../LICENSE) para detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

## 🔗 Enlaces Útiles

- [Vue 3 Documentation](https://vuejs.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Pinia Documentation](https://pinia.vuejs.org/) 