/**
 * 旧路由重定向模块
 * 用于处理历史遗留路径的重定向，确保旧 URL 不会返回 404
 *
 * 重定向规则：
 * - /invoices → /customer-finance/invoices
 * - /invoices/detail → /customer-finance/invoice-detail
 * - /projects → 待定（项目模块未纳入菜单）
 * - /projects/detail → 待定
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
  // 旧项目路径 - 暂时显示 404（项目模块未纳入菜单）
  {
    name: 'LegacyProjects',
    path: '/projects',
    redirect: '/dashboard/overview/index',  // 暂时重定向到综合看板
    meta: { hideInMenu: true, hideInTab: true, title: '旧项目页重定向' },
  },
  {
    name: 'LegacyProjectDetail',
    path: '/projects/detail',
    redirect: (to) => {
      // 项目详情需要特殊处理，暂时重定向到合同详情
      // 因为项目和合同有关联关系
      return { path: '/contracts/detail', query: to.query };
    },
    meta: { hideInMenu: true, hideInTab: true, title: '旧项目详情重定向' },
  },
];

export default routes;