/**
 * 供应商模块 Legacy 重定向
 *
 * 后端模式(accessMode: 'backend')下，业务路由由后端动态生成
 * 此文件仅保留旧路由重定向，确保历史 URL 不返回 404
 *
 * 规范路由：
 * - SupplierList → /suppliers/list (后端菜单)
 * - SupplierDetail → /suppliers/detail (后端菜单)
 *
 * 详见：docs/规范路由清单-20260713.md
 */
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  // Legacy: /suppliers (空子路径) → /suppliers/list
  {
    path: '/suppliers',
    redirect: '/suppliers/list',
    name: 'LegacySuppliersRoot',
    meta: { hideInMenu: true, title: '供应商管理（旧）' },
  },
];

export default routes;
