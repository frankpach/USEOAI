import { createRouter, createWebHistory } from 'vue-router'
import KeywordUsageTest from '../views/KeywordUsageTest.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'USEOAI - Análisis SEO con IA' }
  },
  {
    path: '/analyze',
    name: 'Analyze',
    component: () => import('@/views/Analyze.vue'),
    meta: { title: 'Análisis SEO - USEOAI' }
  },
  {
    path: '/geo-analysis',
    name: 'GeoAnalysis',
    component: () => import('@/views/GeoAnalysis.vue'),
    meta: { title: 'Análisis Geográfico - USEOAI' }
  },
  {
    path: '/report/:id',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { title: 'Informe SEO - USEOAI' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/MyReports.vue'),
    meta: { title: 'Mis Informes - USEOAI' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: { title: 'Acerca de - USEOAI' }
  },
  {
    path: '/keyword-usage-test',
    name: 'KeywordUsageTest',
    component: KeywordUsageTest
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Página no encontrada - USEOAI' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Cambiar título de la página
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
