import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:receipt', order: 3, title: '发票管理', ignoreAccess: true },
  name: 'Invoices', path: '/invoices',
  children: [{
    name: 'InvoiceList', path: '',
    component: () => import('#/views/invoices/index.vue'),
    meta: { title: '所有发票', ignoreAccess: true }
  }, {
    name: 'InvoiceDetail', path: 'detail',
    component: () => import('#/views/invoices/detail.vue'),
    meta: { hideInMenu: true, title: '发票详情', ignoreAccess: true }
  }]
}];
export default routes;
