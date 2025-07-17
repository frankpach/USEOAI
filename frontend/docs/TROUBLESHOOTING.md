# Solución de Problemas - USEOAI Frontend

## 🔧 Problemas Comunes y Soluciones

### 1. Conflictos de Dependencias

**Problema**: Error `ERESOLVE unable to resolve dependency tree`

**Solución**:
```bash
# Opción 1: Usar legacy-peer-deps
npm install --legacy-peer-deps

# Opción 2: Limpiar cache e instalar
npm cache clean --force
npm install --legacy-peer-deps

# Opción 3: Usar scripts automáticos
# Windows: install.bat
# Linux/Mac: ./install.sh
```

### 2. Error de ApexCharts

**Problema**: `peer apexcharts@">=4.0.0" from vue3-apexcharts`

**Solución**:
- Verificar que `apexcharts` esté en versión 4.0.0 o superior
- Usar `--legacy-peer-deps` durante la instalación
- Configurar `.npmrc` con `legacy-peer-deps=true`

### 3. Mapas No Se Cargan

**Problema**: Los mapas de Leaflet no aparecen

**Solución**:
- Verificar que `leaflet` esté instalado: `npm list leaflet`
- Comprobar que los estilos CSS estén importados
- Verificar la conexión a internet (los mapas usan OpenStreetMap)

### 4. Error de CORS

**Problema**: Error de CORS al conectar con el backend

**Solución**:
- Verificar que el backend esté ejecutándose en `http://localhost:8000`
- Comprobar la configuración de `VITE_API_URL` en `.env.local`
- Verificar que el backend tenga CORS configurado correctamente

### 5. Captura de Imágenes No Funciona

**Problema**: `dom-to-image` no genera imágenes

**Solución**:
- Verificar que `dom-to-image` esté instalado
- Comprobar que el elemento tenga dimensiones definidas
- Asegurar que el mapa esté completamente renderizado antes de capturar

### 6. Errores de TypeScript/Vue

**Problema**: Errores de tipos o compilación

**Solución**:
```bash
# Limpiar cache
npm run lint -- --fix

# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### 7. Problemas de Rendimiento

**Problema**: La aplicación es lenta o no responde

**Solución**:
- Verificar el uso de memoria del navegador
- Comprobar que no haya múltiples instancias de mapas
- Optimizar imágenes y assets
- Usar modo de desarrollo: `VITE_DEV_MODE=true`

## 🚀 Comandos Útiles

### Instalación y Configuración
```bash
# Instalación limpia
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Verificar dependencias
npm list --depth=0

# Limpiar cache
npm cache clean --force
```

### Desarrollo
```bash
# Servidor de desarrollo
npm run dev

# Construcción para producción
npm run build

# Vista previa de producción
npm run preview

# Linting
npm run lint
```

### Debugging
```bash
# Ver logs detallados
npm run dev -- --debug

# Verificar configuración
cat .env.local
npm list --depth=0
```

## 📋 Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] Node.js versión 16+ instalado
- [ ] Dependencias instaladas con `--legacy-peer-deps`
- [ ] Archivo `.env.local` configurado correctamente
- [ ] Backend ejecutándose en `http://localhost:8000`
- [ ] Conexión a internet activa
- [ ] Navegador actualizado
- [ ] Cache del navegador limpiado

## 🔍 Logs y Debugging

### Habilitar Debug de Mapas
```env
VITE_DEBUG_MAPS=true
```

### Ver Logs del Navegador
1. Abrir DevTools (F12)
2. Ir a la pestaña Console
3. Filtrar por errores relacionados con mapas

### Ver Logs del Servidor
```bash
npm run dev 2>&1 | tee server.log
```

## 📞 Soporte

Si los problemas persisten:

1. **Revisar logs**: Verificar consola del navegador y terminal
2. **Documentación**: Consultar `MAPS_FEATURES.md`
3. **Issues**: Crear issue en el repositorio con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs de error
   - Configuración del sistema 