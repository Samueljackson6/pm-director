import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:wallet', order: 2, title: '客户财务', ignoreAccess: true },
  name: 'CustomerFinance', path: '/customer-finance',
  children: [{
    name: 'CustomerInvoices', path: 'invoices',
    component: () => import('#/views/customer-finance/invoices/index.vue'),
    meta: { title: '客户发票', ignoreAccess: true }
  }, {
    name: 'CustomerInvoiceDetail', path: 'invoice-detail',
    component: () => import('#/views/customer-finance/invoices/detail.vue'),
    meta: { hideInMenu: true, title: '发票详情', ignoreAccess: true }
  }, {
    name: 'CustomerReceipts', path: 'receipts',
    component: () => import('#/views/customer-finance/receipts/index.vue'),
    meta: { title: '客户回款', ignoreAccess: true }
  }, {
    name: 'CustomerReceiptDetail', path: 'receipt-detail',
    component: () => import('#/views/customer-finance/receipts/detail.vue'),
    meta: { hideInMenu: true, title: '回款详情', ignoreAccess: true }
  }]
}];
export default routes;