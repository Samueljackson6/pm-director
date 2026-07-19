/**
 * 旧路由重定向模块
 * 用于处理历史遗留路径的重定向，确保旧 URL 不会返回 404
 *
 * 重定向规则：
 * - /invoices → /customer-finance/invoices
 * - /invoices/detail → /customer-finance/invoice-detail
 * - /projects → /projects/list
 *
 * 退役日期：2026-07-20
 * 详见：docs/规范路由清单-20260713.md
 */
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  // 旧发票路径重定向
  {
    name: 'LegacyInvoices',
    path: '/invoices',
    redirect: '/customer-finance/invoices',
    meta: { hideInMenu: true, hideInTab: true, title: '旧发票页重定向' },
  },
  {
    name: 'LegacyInvoiceDetail',
    path: '/invoices/detail',
    redirect: (to) => {
      // 保持 query 参数
      return { path: '/customer-finance/invoice-detail', query: to.query };
    },
    meta: { hideInMenu: true, hideInTab: true, title: '旧发票详情重定向' },
  },
  {
    name: 'LegacyProjects',
    path: '/projects',
    redirect: '/projects/list',
    meta: { hideInMenu: true, hideInTab: true, title: '旧项目页重定向' },
  },
];

export default routes;
