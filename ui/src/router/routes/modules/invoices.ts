import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:receipt', order: 2, title: 'Invoices', ignoreAccess: true },
  name: 'Invoices', path: '/invoices',
  children: [{
    name: 'InvoiceList', path: 'index',
    component: () => import('#/views/invoices/index.vue'),
    meta: { title: 'All Invoices', ignoreAccess: true }
  }]
}];
export default routes;
