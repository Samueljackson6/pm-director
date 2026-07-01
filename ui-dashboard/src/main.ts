import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import ContractList from './views/ContractList.vue'
import ContractDetail from './views/ContractDetail.vue'
import InvoiceTracking from './views/InvoiceTracking.vue'
import SupplierManagement from './views/SupplierManagement.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/contracts', name: 'ContractList', component: ContractList },
  { path: '/contracts/:id', name: 'ContractDetail', component: ContractDetail },
  { path: '/invoices', name: 'InvoiceTracking', component: InvoiceTracking },
  { path: '/suppliers', name: 'SupplierManagement', component: SupplierManagement },
]

const router = createRouter({ history: createWebHistory(), routes })
createApp(App).use(router).mount('#app')
