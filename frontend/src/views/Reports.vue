<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container mx-auto px-4 py-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Historial de Informes</h1>
            <p class="text-xl text-gray-600">Agrupados por URL</p>
          </div>
        </div>
      </div>
    </div>
    <div class="container mx-auto px-4 py-8">
      <div v-if="isLoading" class="text-center py-12">
        <div class="loading-spinner mx-auto mb-4"></div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Cargando informes...</h3>
      </div>
      <div v-else>
        <div v-for="group in groups" :key="group.url" class="mb-6 border rounded-lg bg-white shadow-sm">
          <div class="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50" @click="expandGroup(group.url)">
            <div>
              <div class="font-bold text-lg text-primary-700">{{ group.url }}</div>
              <div class="text-sm text-gray-500">Total búsquedas: <b>{{ group.total_reports }}</b> | Último reporte: <b>{{ formatDate(group.last_report_date) }}</b> | Tipo: <b>{{ group.last_report_type }}</b></div>
            </div>
            <button class="btn-secondary">{{ expandedGroup === group.url ? 'Cerrar' : 'Ver detalles' }}</button>
          </div>
          <div v-if="expandedGroup === group.url" class="p-4 border-t">
            <div v-if="reportsStore.byUrlLoading" class="text-center py-4">Cargando reportes...</div>
            <div v-else>
              <table class="w-full text-sm mb-2">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="p-2">Fecha</th>
                    <th class="p-2">Tipo</th>
                    <th class="p-2">Estado</th>
                    <th class="p-2">SEO Goal</th>
                    <th class="p-2">Score</th>
                    <th class="p-2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="report in groupReports" :key="report.id">
                    <td class="p-2">{{ formatDate(report.created_at) }}</td>
                    <td class="p-2">{{ report.report_type }}</td>
                    <td class="p-2">{{ report.status }}</td>
                    <td class="p-2">{{ report.seo_goal }}</td>
                    <td class="p-2">{{ report.overall_score ?? 'N/A' }}</td>
                    <td class="p-2 flex gap-2">
                      <button class="btn-primary btn-xs" @click.stop="viewReport(report.id)">Ver</button>
                      <button class="btn-secondary btn-xs" @click.stop="exportReport(report.id)">Exportar</button>
                      <button class="btn-danger btn-xs" @click.stop="deleteReport(report.id)">Eliminar</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="flex justify-between items-center mt-2">
                <button class="btn-secondary btn-xs" :disabled="groupPage === 1" @click="prevGroupPage(group.url)">Anterior</button>
                <span>Página {{ groupPage }} de {{ Math.ceil(groupTotal / groupPerPage) }}</span>
                <button class="btn-secondary btn-xs" :disabled="groupPage * groupPerPage >= groupTotal" @click="nextGroupPage(group.url)">Siguiente</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="hasMore" class="text-center mt-6">
          <button class="btn-primary" @click="loadGroups">Cargar más</button>
        </div>
      </div>
    </div>
    <div v-if="selectedReport && selectedReport.keyword_usage">
      <KeywordUsage v-bind="selectedReport.keyword_usage" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReportsStore } from '@/stores/reports'
import { useToast } from 'vue-toastification'
import KeywordUsage from '../components/KeywordUsage.vue'

const router = useRouter()
const reportsStore = useReportsStore()
const toast = useToast()

const groups = ref([])
const isLoading = computed(() => reportsStore.groupedLoading)
const hasMore = ref(true)
const offset = ref(0)
const limit = 10
const expandedGroup = ref(null)
const groupReports = ref([])
const groupPage = ref(1)
const groupTotal = ref(0)
const groupPerPage = 20

onMounted(async () => {
  await loadGroups()
})

const loadGroups = async () => {
  const data = await reportsStore.fetchGroupedReports({ offset: offset.value, limit })
  if (data.groups.length < limit) hasMore.value = false
  groups.value.push(...data.groups)
  offset.value += data.groups.length
}

const expandGroup = async (url) => {
  if (expandedGroup.value === url) {
    expandedGroup.value = null
    groupReports.value = []
    return
  }
  expandedGroup.value = url
  groupPage.value = 1
  await loadGroupReports(url, 1)
}

const loadGroupReports = async (url, page) => {
  const data = await reportsStore.fetchReportsByUrl(url, page, groupPerPage)
  groupReports.value = data.reports
  groupTotal.value = data.total
  groupPage.value = data.page
}

const nextGroupPage = async (url) => {
  if (groupPage.value * groupPerPage >= groupTotal.value) return
  await loadGroupReports(url, groupPage.value + 1)
}
const prevGroupPage = async (url) => {
  if (groupPage.value === 1) return
  await loadGroupReports(url, groupPage.value - 1)
}

const formatDate = (date) => {
  if (!date) return 'Fecha desconocida'
  return new Date(date).toLocaleString('es-ES', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const viewReport = (id) => router.push(`/report/${id}`)
const exportReport = async (id) => { try { await reportsStore.exportReport(id) } catch (e) { toast.error('Error al exportar') } }
const deleteReport = async (id) => { if (confirm('¿Eliminar este informe?')) { await reportsStore.deleteReport(id); toast.success('Informe eliminado'); } }

</script>
