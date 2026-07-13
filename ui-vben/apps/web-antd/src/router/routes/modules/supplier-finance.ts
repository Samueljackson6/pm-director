import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:building-2', order: 3, title: '供应商财务', ignoreAccess: true },
  name: 'SupplierFinance', path: '/supplier-finance',
  children: [{
    name: 'SupplierInvoices', path: 'invoices',
    component: () => import('#/views/supplier-finance/invoices/index.vue'),
    meta: { title: '供应商发票', ignoreAccess: true }
  }, {
    name: 'SupplierInvoiceDetail', path: 'invoice-detail',
    component: () => import('#/views/supplier-finance/invoices/detail.vue'),
    meta: { hideInMenu: true, title: '发票详情', ignoreAccess: true }
  }, {
    name: 'SupplierPayments', path: 'payments',
    component: () => import('#/views/supplier-finance/payments/index.vue'),
    meta: { title: '供应商付款', ignoreAccess: true }
  }, {
    name: 'SupplierPaymentDetail', path: 'payment-detail',
    component: () => import('#/views/supplier-finance/payments/detail.vue'),
    meta: { hideInMenu: true, title: '付款详情', ignoreAccess: true }
  }]
}];
export default routes;