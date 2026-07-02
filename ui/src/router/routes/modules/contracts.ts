import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:file-text', order: 1, title: 'Contracts', ignoreAccess: true },
  name: 'Contracts', path: '/contracts',
  children: [{
    name: 'ContractList', path: '',
    component: () => import('#/views/contracts/index.vue'),
    meta: { title: 'All Contracts', ignoreAccess: true }
  }, {
    name: 'ContractDetail', path: 'detail/:id',
    component: () => import('#/views/contracts/detail.vue'),
    meta: { hideInMenu: true, title: 'Detail', ignoreAccess: true }
  }]
}];
export default routes;
