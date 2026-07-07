import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:file-text', order: 2, title: '合同管理', ignoreAccess: true },
  name: 'Contracts', path: '/contracts',
  children: [{
    name: 'ContractList', path: '',
    component: () => import('#/views/contracts/index.vue'),
    meta: { title: '所有合同', ignoreAccess: true }
  }, {
    name: 'ContractDetail', path: 'detail',
    component: () => import('#/views/contracts/detail.vue'),
    meta: { hideInMenu: true, title: '合同详情', ignoreAccess: true }
  }]
}];
export default routes;
