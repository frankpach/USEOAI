<template>
  <div class="keyword-usage">
    <h2 class="text-xl font-bold mb-2">Web Key Words</h2>
    <div class="mb-2">
      <span class="font-semibold">URL:</span> {{ url }}
    </div>
    <div class="mb-2">
      <span class="font-semibold">Keywords:</span> <span v-for="(kw, i) in keywords" :key="i" class="mr-2">{{ kw }}</span>
    </div>
    <div class="mb-4">
      <span class="font-semibold">Modo coincidencia:</span> {{ match }}
    </div>
    <table class="min-w-full border text-sm">
      <thead>
        <tr>
          <th class="border px-2 py-1">Keyword</th>
          <th class="border px-2 py-1">h1-h6</th>
          <th class="border px-2 py-1">p</th>
          <th class="border px-2 py-1">Frecuencia</th>
          <th class="border px-2 py-1">Observación</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in results" :key="row.keyword" :class="row.color">
          <td class="border px-2 py-1">{{ row.keyword }}</td>
          <td class="border px-2 py-1 text-center">
            <span v-if="row.h1_h6" class="text-green-600 font-bold">✔</span>
            <span v-else class="text-red-600 font-bold">✘</span>
          </td>
          <td class="border px-2 py-1 text-center">
            <span v-if="row.p" class="text-green-600 font-bold">✔</span>
            <span v-else class="text-red-600 font-bold">✘</span>
          </td>
          <td class="border px-2 py-1 text-center">{{ row.freq }}</td>
          <td class="border px-2 py-1">
            <span :class="{
              'text-green-700': row.color === 'green',
              'text-yellow-700': row.color === 'yellow',
              'text-red-700': row.color === 'red',
              'text-orange-700': row.color === 'orange',
            }">{{ row.obs }}</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="mt-4">
      <h3 class="font-semibold mb-1">Checklist</h3>
      <ul class="list-disc ml-6">
        <li v-for="(item, i) in checklist" :key="i">{{ item }}</li>
      </ul>
    </div>
    <div class="mt-4">
      <h4 class="font-semibold mb-1">Leyenda de colores:</h4>
      <ul class="list-disc ml-6 text-sm">
        <li><span class="text-green-700 font-bold">Verde:</span> Correcto</li>
        <li><span class="text-yellow-700 font-bold">Amarillo:</span> Sugerido</li>
        <li><span class="text-red-700 font-bold">Rojo:</span> Ausente</li>
        <li><span class="text-orange-700 font-bold">Naranja:</span> Sobreuso</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  results: { type: Array, required: true },
  checklist: { type: Array, default: () => [] },
  url: { type: String, required: true },
  keywords: { type: Array, required: true },
  match: { type: String, default: 'exact' },
})
</script>

<style scoped>
.green { background-color: #e6ffe6; }
.yellow { background-color: #fffbe6; }
.red { background-color: #ffe6e6; }
.orange { background-color: #fff2e6; }
</style>
