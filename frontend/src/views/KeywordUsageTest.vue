<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Test de Web Key Words</h1>
    <form @submit.prevent="runTest" class="mb-6">
      <div class="mb-2">
        <label class="block font-semibold">URL:</label>
        <input v-model="url" type="text" class="border px-2 py-1 w-full" required />
      </div>
      <div class="mb-2">
        <label class="block font-semibold">Keywords (separadas por coma):</label>
        <input v-model="keywordsInput" type="text" class="border px-2 py-1 w-full" required />
      </div>
      <div class="mb-2">
        <label class="block font-semibold">Modo coincidencia:</label>
        <select v-model="match" class="border px-2 py-1 w-32">
          <option value="exact">Exacta</option>
          <option value="partial">Parcial</option>
        </select>
      </div>
      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Analizar</button>
    </form>
    <div v-if="loading" class="mb-4">Analizando...</div>
    <div v-if="error" class="text-red-600 mb-4">{{ error }}</div>
    <KeywordUsage v-if="result" v-bind="result" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import KeywordUsage from '../components/KeywordUsage.vue'

const url = ref('https://www.example.com')
const keywordsInput = ref('example, domain')
const match = ref('exact')
const loading = ref(false)
const error = ref('')
const result = ref(null)

async function runTest() {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const keywords = keywordsInput.value.split(',').map(k => k.trim()).filter(Boolean)
    const res = await fetch('/api/keyword-usage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value, keywords, match: match.value })
    })
    if (!res.ok) throw new Error('Error en el análisis')
    result.value = await res.json()
  } catch (e) {
    error.value = e.message || 'Error desconocido'
  } finally {
    loading.value = false
  }
}
</script>
