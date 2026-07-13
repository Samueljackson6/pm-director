"""Vben Auth Mock endpoints — login, captcha, user info, logout, etc."""

from fastapi import APIRouter

from backend.models import vben_response

router = APIRouter(tags=["auth"])


@router.post('/system/auth/login')
def vben_login():
    return vben_response({
        'accessToken': 'vben-dev-token',
        'refreshToken': 'vben-refresh-token',
        'expires': 9999999999,
    })


@router.post('/system/captcha/get')
def vben_captcha():
    return vben_response({'captchaEnabled': False})


@router.get('/system/user/info')
def vben_user_info():
    return vben_response({
        'username': 'admin',
        'realName': 'Admin',
        'roles': ['admin'],
        'homePath': '/#/dashboard',
    })


@router.post('/system/auth/logout')
def vben_logout():
    return vben_response(True)


@router.post('/system/auth/refresh-token')
def vben_refresh_token(refreshToken: str = ''):
    return vben_response({
        'accessToken': 'vben-dev-token',
        'refreshToken': 'vben-refresh-token',
        'expires': 9999999999,
    })


@router.get('/system/dict-data/simple-list')
def vben_dict_data():
    return vben_response([])


@router.get('/system/notify-message/get-unread-count')
def vben_notify_unread():
    return vben_response(0)


@router.get('/system/auth/get-permission-info')
def vben_permission_info():
    return vben_response({
        'user': {
            'userId': 1,
            'username': 'admin',
            'nickname': '管理员',
            'avatar': '',
        'homePath': '/dashboard/overview/index',
            'roles': ['admin'],
        },
        'roles': ['admin'],
        'permissions': ['*:*:*'],
        'menus': [
            {
                'id': 1,
                'parentId': 0,
                'name': '概览',
                'path': '/dashboard',
                'component': 'BasicLayout',
                'componentName': 'Dashboard',
                'icon': 'lucide:layout-dashboard',
                'visible': True,
                'keepAlive': False,
                'sort': 0,
                'children': [
                    {
                        'id': 11,
                        'parentId': 1,
                        'name': '分析页',
                        'path': 'analytics',
                        'component': '/dashboard/analytics/index',
                        'componentName': 'Analytics',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 0,
                    },
                    {
                        'id': 12,
                        'parentId': 1,
                        'name': '综合看板',
                        'path': 'overview/index',
                        'component': '/dashboard/overview/index',
                        'componentName': 'DashboardOverview',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 1,
                    }
                ],
            },
            {
                'id': 2,
                'parentId': 0,
                'name': '合同管理',
                'path': '/contracts',
                'component': 'BasicLayout',
                'componentName': 'Contracts',
                'icon': 'lucide:file-text',
                'visible': True,
                'keepAlive': False,
                'sort': 1,
                'children': [
                    {
                        'id': 21,
                        'parentId': 2,
                        'name': '合同列表',
                        'path': 'list',
                        'component': '/contracts/index',
                        'componentName': 'ContractList',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    },
                    {
                        'id': 22,
                        'parentId': 2,
                        'name': '合同详情',
                        'path': 'detail',
                        'component': '/contracts/detail',
                        'componentName': 'ContractDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 1,
                    }
                ],
            },
            {
                'id': 3,
                'parentId': 0,
                'name': '客户财务',
                'path': '/customer-finance',
                'component': 'BasicLayout',
                'componentName': 'CustomerFinance',
                'icon': 'lucide:wallet',
                'visible': True,
                'keepAlive': False,
                'sort': 2,
                'children': [
                    {
                        'id': 31,
                        'parentId': 3,
                        'name': '客户发票',
                        'path': 'invoices',
                        'component': '/customer-finance/invoices/index',
                        'componentName': 'CustomerInvoices',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    },
                    {
                        'id': 32,
                        'parentId': 3,
                        'name': '发票详情',
                        'path': 'invoice-detail',
                        'component': '/customer-finance/invoices/detail',
                        'componentName': 'CustomerInvoiceDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 1,
                    },
                    {
                        'id': 33,
                        'parentId': 3,
                        'name': '客户回款',
                        'path': 'receipts',
                        'component': '/customer-finance/receipts/index',
                        'componentName': 'CustomerReceipts',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 2,
                    },
                    {
                        'id': 34,
                        'parentId': 3,
                        'name': '回款详情',
                        'path': 'receipt-detail',
                        'component': '/customer-finance/receipts/detail',
                        'componentName': 'CustomerReceiptDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 3,
                    },
                ],
            },
            {
                'id': 4,
                'parentId': 0,
                'name': '供应商管理',
                'path': '/suppliers',
                'component': 'BasicLayout',
                'componentName': 'Suppliers',
                'icon': 'lucide:users',
                'visible': True,
                'keepAlive': False,
                'sort': 3,
                'children': [
                    {
                        'id': 41,
                        'parentId': 4,
                        'name': '供应商列表',
                        'path': 'list',
                        'component': '/suppliers/list/index',
                        'componentName': 'SupplierList',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    },
                    {
                        'id': 42,
                        'parentId': 4,
                        'name': '供应商详情',
                        'path': 'detail',
                        'component': '/suppliers/detail/index',
                        'componentName': 'SupplierDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 1,
                    },
                ],
            },
            {
                'id': 5,
                'parentId': 0,
                'name': '供应商财务',
                'path': '/supplier-finance',
                'component': 'BasicLayout',
                'componentName': 'SupplierFinance',
                'icon': 'lucide:building-2',
                'visible': True,
                'keepAlive': False,
                'sort': 4,
                'children': [
                    {
                        'id': 51,
                        'parentId': 5,
                        'name': '供应商发票',
                        'path': 'invoices',
                        'component': '/supplier-finance/invoices/index',
                        'componentName': 'SupplierInvoices',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    },
                    {
                        'id': 52,
                        'parentId': 5,
                        'name': '发票详情',
                        'path': 'invoice-detail',
                        'component': '/supplier-finance/invoices/detail',
                        'componentName': 'SupplierInvoiceDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 1,
                    },
                    {
                        'id': 53,
                        'parentId': 5,
                        'name': '供应商付款',
                        'path': 'payments',
                        'component': '/supplier-finance/payments/index',
                        'componentName': 'SupplierPayments',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 2,
                    },
                    {
                        'id': 54,
                        'parentId': 5,
                        'name': '付款详情',
                        'path': 'payment-detail',
                        'component': '/supplier-finance/payments/detail',
                        'componentName': 'SupplierPaymentDetail',
                        'icon': '',
                        'visible': False,
                        'keepAlive': False,
                        'sort': 3,
                    },
                ],
            },
        ],
    })


@router.get('/api/menu/list')
def vben_menu_list():
    return vben_response([
        {
            'path': '/dashboard',
            'name': 'Dashboard',
            'component': 'BasicLayout',
            'meta': {'title': 'Dashboard', 'icon': 'lucide:layout-dashboard'},
            'children': [
                {
                    'path': '/dashboard/analytics',
                    'name': 'Analytics',
                    'component': '/dashboard/analytics/index',
                    'meta': {'title': 'Analytics'},
                }
            ],
        }
    ])
