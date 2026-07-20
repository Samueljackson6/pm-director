"""Vben Auth Mock endpoints — login, captcha, user info, logout, etc."""

from fastapi import APIRouter

from backend.models import vben_response
from backend.routers.auth_menu import build_permission_menus

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
        'menus': build_permission_menus(),
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
