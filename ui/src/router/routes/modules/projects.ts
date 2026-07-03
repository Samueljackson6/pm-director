import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:clipboard-list', order: 3, title: '项目管理', ignoreAccess: true },
  name: 'Projects', path: '/projects',
  children: [{
    name: 'ProjectList', path: '',
    component: () => import('#/views/projects/index.vue'),
    meta: { title: '所有项目', ignoreAccess: true }
  }, {
    name: 'ProjectDetail', path: 'detail/:id',
    component: () => import('#/views/projects/detail.vue'),
    meta: { hideInMenu: true, title: '项目详情', ignoreAccess: true }
  }]
}];
export default routes;
