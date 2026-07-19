from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import BrowserContext, Page, Route, sync_playwright

from phase3_review_support import load_development_login, proxy_backend

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'http://127.0.0.1:18090/web'
ASSETS = ROOT / 'docs' / 'audits' / 'assets'
DATABASE = ROOT / 'database' / 'project_management.db'


def cn(*codes: int) -> str:
    return ''.join(chr(code) for code in codes)


def checksum() -> str:
    return hashlib.sha256(DATABASE.read_bytes()).hexdigest()


def install_proxy(context: BrowserContext) -> None:
    context.route(f'{BASE_URL}/admin-api/**', proxy_backend)
    context.route(f'{BASE_URL}/api/**', proxy_backend)


def login(page: Page, username: str, password: str) -> None:
    page.goto(f'{BASE_URL}/auth/login', wait_until='domcontentloaded', timeout=60_000)
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    with page.expect_response(
        lambda response: response.url.endswith('/admin-api/system/auth/login')
        and response.request.method == 'POST',
        timeout=30_000,
    ) as response:
        page.locator('button[aria-label="login"]').click()
    if response.value.status >= 400:
        raise RuntimeError(f'login HTTP {response.value.status}')
    page.wait_for_timeout(500)


def navigate(page: Page, path: str) -> None:
    try:
        page.goto(f'{BASE_URL}{path}', wait_until='domcontentloaded', timeout=60_000)
    except Exception as exc:
        if 'ERR_ABORTED' not in str(exc):
            raise
    try:
        page.wait_for_load_state('networkidle', timeout=10_000)
    except Exception:
        page.wait_for_timeout(1_000)


def attach_network_audit(page: Page, result: dict[str, Any]) -> None:
    result['page_errors'] = []
    result['request_failed'] = []
    result['http_failures'] = []
    result['write_requests'] = []
    page.on('pageerror', lambda error: result['page_errors'].append(str(error)))
    page.on(
        'requestfailed',
        lambda request: result['request_failed'].append(f'{request.method} {request.url}: {request.failure}')
        if request.url.startswith(BASE_URL) else None,
    )
    page.on(
        'response',
        lambda response: result['http_failures'].append(
            f'{response.status} {response.request.method} {response.url}'
        ) if response.url.startswith(BASE_URL) and response.status >= 400 and 'favicon' not in response.url else None,
    )
    def on_request(request) -> None:
        if not request.url.startswith(BASE_URL):
            return
        if '/api/' not in request.url and '/admin-api/' not in request.url:
            return
        if request.url.endswith('/system/auth/login'):
            return
        if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
            result['write_requests'].append(f'{request.method} {request.url}')
    page.on('request', on_request)


def first_detail(page: Page) -> bool:
    target = page.locator('.vxe-body--row [title]').first
    if target.count() == 0:
        target = page.get_by_role('button', name=cn(0x8BE6, 0x60C5)).first
    if target.count() == 0:
        return False
    target.click()
    page.wait_for_timeout(650)
    return 'id=' in page.url


def verify_business_flows(page: Page) -> dict[str, bool]:
    flows: dict[str, bool] = {}
    detail_pages = {
        'contracts': '/contracts/list',
        'projects': '/projects/list',
        'customer_invoices': '/customer-finance/invoices',
        'customer_receipts': '/customer-finance/receipts',
        'suppliers': '/suppliers/list',
    }
    for name, path in detail_pages.items():
        navigate(page, path)
        flows[f'{name}_list'] = page.locator('h1').count() == 1
        if name in {'contracts', 'projects'}:
            field = page.locator('input[placeholder]').first
            if field.count():
                field.fill('ZH02')
                button = page.get_by_role('button', name=cn(0x67E5, 0x8BE2))
                if button.count():
                    button.click()
                    page.wait_for_timeout(300)
        flows[f'{name}_detail'] = first_detail(page)
        if flows[f'{name}_detail']:
            page.go_back(wait_until='domcontentloaded')
            page.wait_for_timeout(450)
            flows[f'{name}_return'] = page.url.endswith(path)
        else:
            flows[f'{name}_return'] = False
    for name, path in {
        'supplier_invoices': '/supplier-finance/invoices',
        'supplier_payments': '/supplier-finance/payments',
    }.items():
        navigate(page, path)
        flows[f'{name}_state'] = page.locator('h1').count() == 1 and bool(page.locator('body').inner_text().strip())
    return flows


def verify_viewports(page: Page) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    paths = [
        '/contracts/list', '/projects/list', '/customer-finance/invoices',
        '/customer-finance/receipts', '/suppliers/list', '/supplier-finance/invoices',
        '/supplier-finance/payments', '/dashboard/overview/index',
    ]
    for width, height in ((1440, 980), (1024, 900), (768, 900), (390, 844)):
        page.set_viewport_size({'width': width, 'height': height})
        for path in paths:
            navigate(page, path)
            key = path.strip('/').replace('/', '_')
            checks[f'{width}_{key}_no_page_overflow'] = page.evaluate(
                'document.documentElement.scrollWidth <= window.innerWidth + 1'
            )
    return checks


def verify_dashboard(page: Page) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    requests: list[str] = []
    page.on('response', lambda response: requests.append(response.url) if '/api/dashboard/overview' in response.url else None)
    navigate(page, '/dashboard/overview/index?view=all')
    page.get_by_role('heading', name=cn(0x73B0, 0x5728, 0x9700, 0x8981, 0x63A8, 0x8FDB, 0x7684, 0x4E8B, 0x9879)).wait_for(timeout=30_000)
    checks['initial_single_aggregation'] = len(requests) == 1
    for label in (cn(0x7ECF, 0x8425), cn(0x9879, 0x76EE), cn(0x8D22, 0x52A1), cn(0x6570, 0x636E, 0x6838, 0x9A8C)):
        page.get_by_role('tab', name=label).click()
        page.wait_for_timeout(150)
    checks['view_switch_no_refetch'] = len(requests) == 1
    page.get_by_role('tab', name=cn(0x7EFC, 0x5408)).click()
    action = page.get_by_role('button', name=cn(0x67E5, 0x770B, 0x5BF9, 0x8C61))
    checks['action_available'] = action.count() > 0
    if action.count():
        action.first.click()
        page.wait_for_timeout(350)
        checks['action_drilldown'] = 'id=' in page.url and '/dashboard/overview' not in page.url
        page.go_back(wait_until='domcontentloaded')
        page.wait_for_timeout(350)
    else:
        checks['action_drilldown'] = False
    page.get_by_role('tab', name=cn(0x7EFC, 0x5408)).focus()
    page.keyboard.press('ArrowRight')
    checks['keyboard_tab_focus'] = page.evaluate(
        '''() => document.activeElement?.getAttribute('role') === 'tab' &&
          (getComputedStyle(document.activeElement).outlineStyle !== 'none' ||
           getComputedStyle(document.activeElement).boxShadow !== 'none')'''
    )
    checks['reduced_motion'] = page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
    return checks


def route_dashboard(context: BrowserContext, mode: str) -> None:
    def handler(route: Route) -> None:
        if mode == 'weak':
            time.sleep(0.9)
            response = route.fetch()
            route.fulfill(response=response)
            return
        if mode == 'error':
            route.fulfill(status=500, content_type='application/json', body=json.dumps({'code': 500, 'message': 'qa'}))
            return
        if mode == 'empty':
            route.fulfill(status=200, content_type='application/json', body=json.dumps({'code': 0, 'data': None}))
            return
        response = route.fetch()
        payload = response.json()
        data = payload['data']
        if mode == 'missing':
            payload['data'] = {'summary': {}}
        elif mode == 'stale':
            for metric in data['data_contract']['metrics']:
                metric['data_as_of'] = '2020-01-01T00:00:00'
        elif mode == 'conflict':
            data['verification_actions'] = [{
                'action_id': 'qa-conflict', 'category': 'verification',
                'title': cn(0x51B2, 0x7A81, 0x6570, 0x636E), 'object_type': 'contract',
                'object_id': 'qa', 'reason': cn(0x51B2, 0x7A81, 0x6838, 0x9A8C),
                'due_date': None, 'owner': None, 'status': 'pending',
                'target': {'path': '/contracts/detail', 'query': {'id': 'qa'}},
            }]
        route.fulfill(status=response.status, content_type='application/json', body=json.dumps(payload, ensure_ascii=False))
    context.route(re.compile(r'.*/admin-api/api/dashboard/overview(?:\?.*)?$'), handler)


def verify_states(browser, username: str, password: str) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for mode in ('weak', 'error', 'empty', 'missing', 'stale', 'conflict'):
        context = browser.new_context(locale='zh-CN', reduced_motion='reduce', viewport={'width': 1024, 'height': 900})
        install_proxy(context)
        route_dashboard(context, mode)
        page = context.new_page()
        try:
            login(page, username, password)
            page.goto(f'{BASE_URL}/dashboard/overview/index', wait_until='domcontentloaded', timeout=60_000)
            if mode == 'weak':
                loading = page.get_by_text(cn(0x52A0, 0x8F7D, 0x4E2D))
                loading.wait_for(state='visible', timeout=8_000)
                page.get_by_role('heading', name=cn(0x73B0, 0x5728, 0x9700, 0x8981, 0x63A8, 0x8FDB, 0x7684, 0x4E8B, 0x9879)).wait_for(timeout=30_000)
                checks[mode] = True
            elif mode in {'error', 'missing'}:
                page.get_by_role('alert').wait_for(timeout=20_000)
                checks[mode] = page.get_by_role('button', name=cn(0x91CD, 0x8BD5)).count() == 1
            elif mode == 'empty':
                page.get_by_text(cn(0x6682, 0x65E0, 0x53EF, 0x7528, 0x7684, 0x9A7E, 0x9A76, 0x8231, 0x805A, 0x5408, 0x6570, 0x636E)).wait_for(timeout=20_000)
                checks[mode] = True
            elif mode == 'stale':
                page.get_by_role('tab', name=cn(0x6570, 0x636E, 0x6838, 0x9A8C)).click()
                checks[mode] = page.get_by_text(cn(0x5386, 0x53F2, 0x5FEB, 0x7167, 0xFF0C, 0x9700, 0x590D, 0x6838)).count() > 0
            else:
                page.get_by_role('tab', name=cn(0x6570, 0x636E, 0x6838, 0x9A8C)).click()
                page.get_by_text(cn(0x51B2, 0x7A81, 0x6570, 0x636E)).wait_for(timeout=20_000)
                checks[mode] = True
        finally:
            context.close()
    return checks


def run_axe(page: Page, axe_source: str, name: str) -> dict[str, Any]:
    """仅审计本次重构的业务内容，不将 Vben 全局壳层计入业务页验收。"""
    scope = '.pm-workbench-page'
    if page.locator(scope).count() != 1:
        raise RuntimeError(f'{name}: missing unique accessibility scope {scope}')

    page.add_script_tag(content=axe_source)
    report = page.evaluate(
        """async (scope) => await axe.run(scope, {
          runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
        })""",
        scope,
    )
    serious = [
        {
            'id': item['id'],
            'impact': item.get('impact'),
            'nodes': len(item.get('nodes', [])),
            'targets': [node['target'] for node in item.get('nodes', [])],
        }
        for item in report['violations'] if item.get('impact') in {'critical', 'serious'}
    ]
    return {
        'name': name,
        'scope': scope,
        'serious_or_critical': serious,
        'violations': len(report['violations']),
    }


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {'database_before': checksum()}
    username, password = load_development_login()
    axe_path = next((ROOT / 'ui-vben' / 'node_modules' / '.pnpm').glob('axe-core@*/node_modules/axe-core/axe.min.js'))
    axe_source = axe_path.read_text(encoding='utf-8')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(locale='zh-CN', reduced_motion='reduce', viewport={'width': 1440, 'height': 980})
        install_proxy(context)
        page = context.new_page()
        attach_network_audit(page, result)
        login(page, username, password)
        result['business_flows'] = verify_business_flows(page)
        result['viewport_checks'] = verify_viewports(page)
        page.set_viewport_size({'width': 1440, 'height': 980})
        result['dashboard_checks'] = verify_dashboard(page)
        result['state_checks'] = verify_states(browser, username, password)
        result['axe'] = []
        for name, path in {
            'contracts': '/contracts/list', 'projects': '/projects/list',
            'invoices': '/customer-finance/invoices', 'suppliers': '/suppliers/list',
            'dashboard': '/dashboard/overview/index',
        }.items():
            navigate(page, path)
            result['axe'].append(run_axe(page, axe_source, name))
        result['forbidden_fallback'] = (
            (ROOT / 'ui-vben' / 'apps' / 'web-antd' / 'src' / 'router' / 'access.ts')
            .read_text(encoding='utf-8')
            .find('forbiddenComponent') >= 0
        )
        navigate(page, '/dashboard/overview/index')
        page.screenshot(path=str(ASSETS / 'stage3-g006-dashboard-1440.png'), full_page=True)
        context.close()
        browser.close()
    result['database_after'] = checksum()
    result['database_unchanged'] = result['database_before'] == result['database_after']
    result['boolean_failures'] = [
        name for group in ('business_flows', 'viewport_checks', 'dashboard_checks', 'state_checks')
        for name, value in result[group].items() if value is not True
    ]
    result['axe_failures'] = [item for report in result['axe'] for item in report['serious_or_critical']]
    result['actionable_request_failed'] = [
        failure for failure in result['request_failed'] if 'net::ERR_ABORTED' not in failure
    ]
    result['runtime_failures'] = result['page_errors'] + result['actionable_request_failed'] + result['http_failures'] + result['write_requests']
    result['status'] = 'passed' if not (result['boolean_failures'] or result['axe_failures'] or result['runtime_failures'] or not result['database_unchanged'] or not result['forbidden_fallback']) else 'failed'
    output = ASSETS / 'stage3-g006-final-browser.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('status', 'boolean_failures', 'axe_failures', 'runtime_failures', 'database_unchanged', 'forbidden_fallback')}, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'passed' else 1

if __name__ == '__main__':
    raise SystemExit(main())
