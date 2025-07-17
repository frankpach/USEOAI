<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-primary-50 to-primary-100 py-20">
      <div class="container mx-auto px-4 text-center">
        <div class="max-w-4xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Análisis SEO con
            <span class="text-primary-600">Inteligencia Artificial</span>
          </h1>
          <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Optimiza tu sitio web con herramientas gratuitas y recomendaciones personalizadas. 
            Obtén análisis completos de SEO técnico, on-page y local con la ayuda de IA.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/analyze" 
              class="btn-primary text-lg px-8 py-4"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Análisis Gratuito
            </router-link>
            <router-link 
              to="/geo-analysis" 
              class="btn-secondary text-lg px-8 py-4"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Análisis Local
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Características principales -->
    <section class="py-20 bg-white">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            ¿Por qué elegir USEOAI?
          </h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Herramientas profesionales de SEO sin costo, respaldadas por inteligencia artificial
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Característica 1 -->
          <div class="card text-center hover:shadow-lg transition-shadow">
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Análisis Completo</h3>
            <p class="text-gray-600">
              Evaluación técnica, on-page, off-page y análisis de competencia con herramientas gratuitas
            </p>
          </div>

          <!-- Característica 2 -->
          <div class="card text-center hover:shadow-lg transition-shadow">
            <div class="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg class="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-4">100% Gratuito</h3>
            <p class="text-gray-600">
              Sin costos ocultos, sin límites de análisis. Todas las herramientas son completamente gratuitas
            </p>
          </div>

          <!-- Característica 3 -->
          <div class="card text-center hover:shadow-lg transition-shadow">
            <div class="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg class="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-4">IA Inteligente</h3>
            <p class="text-gray-600">
              Recomendaciones personalizadas basadas en IA que te ayudan a mejorar tu posicionamiento
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Funcionalidades detalladas -->
    <section class="py-20 bg-gray-50">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            Funcionalidades Principales
          </h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Todo lo que necesitas para optimizar tu SEO en una sola plataforma
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <!-- Análisis Técnico -->
          <div class="card">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Análisis Técnico</h3>
                <ul class="text-gray-600 space-y-2">
                  <li>• Verificación de estado HTTP y redirecciones</li>
                  <li>• Análisis de estructura HTML y metadatos</li>
                  <li>• Evaluación de enlaces internos y externos</li>
                  <li>• Detección de datos estructurados</li>
                  <li>• Análisis de velocidad de carga</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- SEO Local -->
          <div class="card">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">SEO Local</h3>
                <ul class="text-gray-600 space-y-2">
                  <li>• Posicionamiento en Google Maps</li>
                  <li>• Análisis de Apple Maps y Bing Maps</li>
                  <li>• Evaluación de visibilidad local</li>
                  <li>• Consistencia de información NAP</li>
                  <li>• Recomendaciones para GMB</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Informes Detallados -->
          <div class="card">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Informes Detallados</h3>
                <ul class="text-gray-600 space-y-2">
                  <li>• Resumen ejecutivo con prioridades</li>
                  <li>• Checklist interactivo de tareas</li>
                  <li>• Instrucciones paso a paso</li>
                  <li>• Exportación a PDF</li>
                  <li>• Seguimiento de mejoras</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Herramientas Gratuitas -->
          <div class="card">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Herramientas Gratuitas</h3>
                <ul class="text-gray-600 space-y-2">
                  <li>• Google PageSpeed Insights</li>
                  <li>• Screaming Frog (versión gratuita)</li>
                  <li>• Ahrefs Web Audit</li>
                  <li>• Wappalyzer</li>
                  <li>• SEO Meta en 1 Click</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-primary-600">
      <div class="container mx-auto px-4 text-center">
        <h2 class="text-4xl font-bold text-white mb-4">
          ¿Listo para mejorar tu SEO?
        </h2>
        <p class="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
          Comienza tu análisis gratuito ahora y obtén recomendaciones personalizadas para optimizar tu sitio web
        </p>
        <router-link 
          to="/analyze" 
          class="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-4"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Comenzar Análisis Gratuito
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
// No se necesita lógica adicional
</script> 