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
        'homePath': '/dashboard',
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
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
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
                    }
                ],
            },
            {
                'id': 3,
                'parentId': 0,
                'name': '发票管理',
                'path': '/invoices',
                'component': 'BasicLayout',
                'componentName': 'Invoices',
                'icon': 'lucide:receipt',
                'visible': True,
                'keepAlive': False,
                'sort': 2,
                'children': [
                    {
                        'id': 31,
                        'parentId': 3,
                        'name': '发票列表',
                        'path': 'list',
                        'component': '/invoices/index',
                        'componentName': 'InvoiceList',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    }
                ],
            },
            {
                'id': 4,
                'parentId': 0,
                'name': '供应商管理',
                'path': '/suppliers',
                'component': 'BasicLayout',
                'componentName': 'Suppliers',
                'icon': 'lucide:building',
                'visible': True,
                'keepAlive': False,
                'sort': 3,
                'children': [
                    {
                        'id': 41,
                        'parentId': 4,
                        'name': '供应商列表',
                        'path': 'list',
                        'component': '/suppliers/index',
                        'componentName': 'SupplierList',
                        'icon': '',
                        'visible': True,
                        'keepAlive': False,
                        'sort': 0,
                    }
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
