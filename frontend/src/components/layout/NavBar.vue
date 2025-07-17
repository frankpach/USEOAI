<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">USEOAI</span>
          </router-link>
        </div>

        <!-- Navegación principal -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link
            to="/"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Home' }"
          >
            Inicio
          </router-link>
          <router-link
            to="/analyze"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Analyze' }"
          >
            Análisis SEO
          </router-link>
          <router-link
            to="/geo-analysis"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'GeoAnalysis' }"
          >
            Análisis Local
          </router-link>
          <router-link
            to="/reports"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Reports' }"
          >
            Mis Informes
          </router-link>
          <router-link
            to="/keyword-usage-test"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'KeywordUsageTest' }"
          >
            Web Key Words
          </router-link>
          <router-link
            to="/about"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'About' }"
          >
            Acerca de
          </router-link>

        </div>

        <!-- Botones de acción -->
        <div class="flex items-center space-x-4">
          <!-- Botón de análisis rápido -->
          <router-link
            to="/analyze"
            class="btn-primary text-sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Análisis Rápido
          </router-link>

          <!-- Menú móvil -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-md text-gray-700 hover:text-primary-600 hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Menú móvil -->
      <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-gray-200">
        <div class="flex flex-col space-y-2">
          <router-link
            to="/"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Home' }"
          >
            Inicio
          </router-link>
          <router-link
            to="/analyze"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Analyze' }"
          >
            Análisis SEO
          </router-link>
          <router-link
            to="/geo-analysis"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'GeoAnalysis' }"
          >
            Análisis Local
          </router-link>
          <router-link
            to="/reports"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Reports' }"
          >
            Mis Informes
          </router-link>
          <router-link
            to="/about"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'About' }"
          >
            Acerca de
          </router-link>
          <router-link
            to="/keyword-usage-test"
            @click="mobileMenuOpen = false"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-primary-600 bg-primary-50': $route.name === 'KeywordUsageTest' }"
          >
            Web Key Words
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}
</script>
