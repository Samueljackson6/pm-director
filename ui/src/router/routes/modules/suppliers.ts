import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:building', order: 3, title: 'Suppliers', ignoreAccess: true },
  name: 'Suppliers', path: '/suppliers',
  children: [{
    name: 'SupplierList', path: '',
    component: () => import('#/views/suppliers/index.vue'),
    meta: { title: 'All Suppliers', ignoreAccess: true }
  }]
}];
export default routes;
