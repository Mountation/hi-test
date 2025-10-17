import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import DatasetList from '../pages/DatasetList.vue'
import DatasetCreate from '../pages/DatasetCreate.vue'
import DatasetRun from '../pages/DatasetRun.vue'
import DatasetView from '../pages/DatasetView.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/datasets/list', component: DatasetList },
  { path: '/datasets/create', component: DatasetCreate },
  { path: '/datasets/run', component: DatasetRun },
  { path: '/datasets/view/:id', component: DatasetView, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
