import type { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:layout-dashboard', order: 1, title: '概览', ignoreAccess: true },
  name: 'Dashboard', path: '/dashboard',
  children: [{
    name: 'DashboardOverview', path: '',
    component: () => import('#/views/dashboard/index.vue'),
    meta: { title: '综合看板', ignoreAccess: true }
  }]
}];
export default routes;
