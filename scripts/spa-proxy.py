#!/usr/bin/env python3
"""本地开发代理：SPA 路由支持 + API 代理"""

import http.server
import socketserver
import urllib.request
from pathlib import Path

FRONTEND_DIST = Path(r'D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\dist')
BACKEND_PORT = 18804
PROXY_PORT = 18890


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIST), **kwargs)

    def do_GET(self):
        if self.path.startswith('/admin-api/') or self.path.startswith('/api/') or self.path.startswith('/system/') or self.path.startswith('/health'):
            self._proxy('GET')
            return

        # SPA 路由：/web/xxx
        if self.path.startswith('/web/'):
            relative_path = self.path[4:].lstrip('/')
            target = FRONTEND_DIST / relative_path
            if target.exists() and target.is_file():
                self.path = '/' + relative_path
            else:
                self.path = '/index.html'
            super().do_GET()
            return

        # 其他路径
        target = FRONTEND_DIST / self.path.lstrip('/')
        if not target.exists() or target.is_dir():
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        self._proxy('POST')

    def do_PUT(self):
        self._proxy('PUT')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _proxy(self, method):
        try:
            if self.path.startswith('/admin-api/'):
                backend_path = self.path[10:]
            else:
                backend_path = self.path
            url = f'http://127.0.0.1:{BACKEND_PORT}{backend_path}'
            body = None
            if method in ('POST', 'PUT'):
                cl = int(self.headers.get('Content-Length', 0))
                if cl > 0:
                    body = self.rfile.read(cl)
            req = urllib.request.Request(
                url,
                data=body,
                method=method,
                headers={'Content-Type': self.headers.get('Content-Type', 'application/json')},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.status)
                for h, v in resp.headers.items():
                    if h.lower() not in ('transfer-encoding', 'content-encoding', 'connection'):
                        self.send_header(h, v)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f'{{"error":"{str(e)}"}}'.encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


if __name__ == '__main__':
    with socketserver.TCPServer(('', PROXY_PORT), SPAHandler) as httpd:
        print(f'[SPA Proxy] http://localhost:{PROXY_PORT}/web/')
        httpd.serve_forever()
