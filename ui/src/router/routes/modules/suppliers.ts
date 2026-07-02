import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:building', order: 4, title: '供应商管理', ignoreAccess: true },
  name: 'Suppliers', path: '/suppliers',
  children: [{
    name: 'SupplierList', path: '',
    component: () => import('#/views/suppliers/index.vue'),
    meta: { title: '所有供应商', ignoreAccess: true }
  }]
}];
export default routes;
