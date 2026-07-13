#!/usr/bin/env python3
"""本地开发代理：提供前端静态文件 + 代理 API 到后端"""

import http.server
import socketserver
import urllib.request
from pathlib import Path
import threading
import subprocess
import time
import sys

# 配置
FRONTEND_DIST = Path(r'D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\dist')
BACKEND_PORT = 8800
PROXY_PORT = 8900


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """处理前端静态文件 + API 代理"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIST), **kwargs)

    def do_GET(self):
        if self.path.startswith('/admin-api/'):
            self._proxy_request('GET')
        elif self.path.startswith('/api/'):
            self._proxy_request('GET')
        elif self.path.startswith('/system/'):
            self._proxy_request('GET')
        elif self.path.startswith('/health'):
            self._proxy_request('GET')
        else:
            # 前端路由：/web/xxx -> 提供静态文件
            if self.path.startswith('/web/'):
                self.path = self.path[4:]  # 去掉 /web 前缀
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/admin-api/') or self.path.startswith('/api/') or self.path.startswith('/system/'):
            self._proxy_request('POST')
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith('/admin-api/') or self.path.startswith('/api/') or self.path.startswith('/system/'):
            self._proxy_request('PUT')
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/admin-api/') or self.path.startswith('/api/') or self.path.startswith('/system/'):
            self._proxy_request('DELETE')
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def _proxy_request(self, method):
        """代理请求到后端"""
        try:
            # 转换路径：/admin-api/xxx -> /xxx, /api/xxx -> /api/xxx
            if self.path.startswith('/admin-api/'):
                backend_path = self.path[10:]  # 去掉 /admin-api
            else:
                backend_path = self.path

            backend_url = f'http://localhost:{BACKEND_PORT}{backend_path}'

            # 读取请求体（POST/PUT）
            body = None
            if method in ('POST', 'PUT'):
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)

            # 创建请求
            req = urllib.request.Request(
                backend_url,
                data=body,
                method=method,
                headers={
                    'Content-Type': self.headers.get('Content-Type', 'application/json'),
                }
            )

            # 发送请求并返回响应
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ('transfer-encoding', 'content-encoding', 'connection'):
                        self.send_header(header, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "Proxy error: {str(e)}"}}'.encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def start_backend():
    """启动后端服务"""
    print(f'[Backend] 启动后端服务 (port {BACKEND_PORT})...')
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', str(BACKEND_PORT)],
        cwd=r'D:\Tare-workspace\pm-director',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # 等待后端启动
    time.sleep(3)
    return proc


def start_frontend_proxy():
    """启动前端代理服务"""
    print(f'[Frontend] 启动前端代理 (port {PROXY_PORT})...')
    print(f'[Frontend] 静态文件目录: {FRONTEND_DIST}')
    handler = ProxyHandler
    with socketserver.TCPServer(('', PROXY_PORT), handler) as httpd:
        print(f'[Proxy] 访问 http://localhost:{PROXY_PORT}/web/')
        httpd.serve_forever()


if __name__ == '__main__':
    # 启动后端
    backend_proc = start_backend()

    # 启动前端代理（在主线程）
    try:
        start_frontend_proxy()
    except KeyboardInterrupt:
        print('\n[Shutdown] 停止服务...')
        backend_proc.terminate()
        backend_proc.wait()
        print('[Shutdown] 服务已停止')
