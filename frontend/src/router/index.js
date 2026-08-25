import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import UploadView from '../views/UploadView.vue'
import MaterialsManageView from '../views/MaterialsManageView.vue'
import MaterialDetailView from '../views/MaterialDetailView.vue'
import ValidationView from '../views/ValidationView.vue'
import ConversionView from '../views/ConversionView.vue'
import StatisticsView from '../views/StatisticsView.vue'
import AlgorithmView from '../views/AlgorithmView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView },
    { path: '/upload', component: UploadView },
    { path: '/manage', component: MaterialsManageView },
    { path: '/materials', component: MaterialDetailView },
    { path: '/validation', component: ValidationView },
    { path: '/conversion', component: ConversionView },
    { path: '/statistics', component: StatisticsView },
    { path: '/algorithms', component: AlgorithmView }
  ]
})
 