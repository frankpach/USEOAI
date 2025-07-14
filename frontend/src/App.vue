<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <nav-bar />
    <main class="container mx-auto px-4 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer-component />
  </div>
</template>

<script setup>
import NavBar from '@/components/layout/NavBar.vue'
import FooterComponent from '@/components/layout/FooterComponent.vue'
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style> 