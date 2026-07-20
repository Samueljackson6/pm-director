from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from phase3_review_support import load_development_login, proxy_backend


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / 'docs' / 'audits' / 'assets'
BASE_URL = 'http://127.0.0.1:18090/web'


def login(page: Page, username: str, password: str) -> None:
    """使用本地开发账号登录；账号信息不写入脚本和报告。"""
    page.goto(f'{BASE_URL}/auth/login', wait_until='domcontentloaded', timeout=60_000)
    page.locator('input[name="username"]').wait_for(state='visible', timeout=60_000)
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    with page.expect_response(
        lambda response: response.url.endswith('/admin-api/system/auth/login')
        and response.request.method == 'POST',
        timeout=30_000,
    ) as login_response:
        page.locator('button[aria-label="login"]').click()
    if login_response.value.status >= 400:
        raise RuntimeError(f'本地登录接口返回 HTTP {login_response.value.status}')
    page.wait_for_timeout(500)


def main() -> None:
    """核验 G005 正式驾驶舱的单路由、五视角和可下钻动作。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    username, password = load_development_login()
    checks: dict[str, bool | int | list[str]] = {}
    dashboard_requests: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    http_failures: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            locale='zh-CN',
            reduced_motion='reduce',
            viewport={'width': 1440, 'height': 1000},
        )
        context.route(f'{BASE_URL}/admin-api/**', proxy_backend)
        context.route(f'{BASE_URL}/api/**', proxy_backend)
        page = context.new_page()
        page.on('pageerror', lambda error: page_errors.append(str(error)))
        page.on(
            'requestfailed',
            lambda request: request_failures.append(
                f'{request.method} {request.url}: {request.failure}'
            )
            if request.url.startswith(BASE_URL)
            else None,
        )
        page.on(
            'response',
            lambda response: dashboard_requests.append(response.url)
            if '/api/dashboard/overview' in response.url
            else None,
        )
        page.on(
            'response',
            lambda response: http_failures.append(
                f'{response.status} {response.request.method} {response.url}'
            )
            if response.url.startswith(BASE_URL)
            and response.status >= 400
            and 'favicon' not in response.url
            else None,
        )

        login(page, username, password)
        page.goto(
            f'{BASE_URL}/dashboard/overview/index?view=all',
            wait_until='networkidle',
            timeout=60_000,
        )
        page.get_by_role('heading', name='现在需要推进的事项').wait_for(
            state='visible', timeout=30_000
        )
        checks['formal_dashboard_not_review_demo'] = page.locator('.phase3-review').count() == 0
        checks['first_view_task_queue'] = page.get_by_role(
            'heading', name='现在需要推进的事项'
        ).count() == 1
        checks['initial_single_aggregation'] = len(dashboard_requests) == 1

        tab_expectations = {
            '经营': '需优先决策的合同与资金缺口',
            '项目': '近期项目',
            '财务': '需核对的回款、发票与付款条件',
            '数据核验': '可回溯的数据缺口',
        }
        for label, expected in tab_expectations.items():
            page.get_by_role('tab', name=label).click()
            page.get_by_text(expected, exact=False).first.wait_for(state='visible', timeout=20_000)
            checks[f'view_{label}'] = True

        page.get_by_role('tab', name='综合').click()
        page.get_by_role('heading', name='现在需要推进的事项').wait_for(
            state='visible', timeout=20_000
        )
        target_button = page.get_by_role('button', name='查看对象').first
        checks['action_available'] = target_button.count() == 1
        target_button.click()
        page.wait_for_timeout(800)
        checks['action_drilldown_has_id'] = 'id=' in page.url
        checks['action_drilldown_not_dashboard'] = '/dashboard/overview' not in page.url

        page.goto(
            f'{BASE_URL}/dashboard/overview/index?view=verification',
            wait_until='networkidle',
            timeout=60_000,
        )
        page.get_by_text('可回溯的数据缺口', exact=True).wait_for(
            state='visible', timeout=30_000
        )
        checks['verification_route_consumes_view_query'] = 'view=verification' in page.url
        checks['tab_switch_does_not_reaggregate'] = len(dashboard_requests) == 2
        page.screenshot(
            path=str(OUTPUT_DIR / 'stage3-g005-dashboard-browser.png'),
            full_page=True,
        )
        browser.close()

    actionable_request_failures = [
        failure for failure in request_failures if 'net::ERR_ABORTED' not in failure
    ]
    checks['dashboard_request_count'] = len(dashboard_requests)
    checks['page_errors'] = page_errors
    checks['request_failures'] = actionable_request_failures
    checks['http_failures'] = http_failures

    boolean_failures = [
        name for name, value in checks.items() if isinstance(value, bool) and not value
    ]
    report = {
        'status': 'passed'
        if not boolean_failures
        and not page_errors
        and not actionable_request_failures
        and not http_failures
        else 'failed',
        'boolean_failures': boolean_failures,
        'checks': checks,
        'screenshot': 'docs/audits/assets/stage3-g005-dashboard-browser.png',
    }
    report_path = OUTPUT_DIR / 'stage3-g005-dashboard-browser.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
