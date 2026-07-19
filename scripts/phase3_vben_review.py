from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from phase3_review_support import (
    click_screen,
    dark_pixel_ratio,
    load_development_login,
    proxy_backend,
    wait_for_review,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "audits" / "assets"
BASE_URL = "http://127.0.0.1:18090/web"
CheckValue = bool | float | int | list[str]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    username, password = load_development_login()
    desktop_path = OUTPUT_DIR / "phase3-vben-workbench-desktop.png"
    detail_path = OUTPUT_DIR / "phase3-vben-contract-detail.png"
    review_path = OUTPUT_DIR / "phase3-vben-data-review.png"
    mobile_path = OUTPUT_DIR / "phase3-vben-mobile-task.png"

    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []
    http_failures: list[str] = []
    checks: dict[str, CheckValue] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            locale="zh-CN",
            reduced_motion="reduce",
            viewport={"width": 1440, "height": 1000},
        )
        context.route(f"{BASE_URL}/admin-api/**", proxy_backend)
        context.route(f"{BASE_URL}/api/**", proxy_backend)
        page = context.new_page()
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: failed_requests.append(
                f"{request.method} {request.url}: {request.failure}"
            ),
        )
        page.on(
            "response",
            lambda response: http_failures.append(
                f"{response.status} {response.request.method} {response.url}"
            )
            if response.status >= 400
            else None,
        )

        login_response = page.goto(
            f"{BASE_URL}/auth/login", wait_until="domcontentloaded"
        )
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        login_wait_error: str | None = None
        try:
            username_input.wait_for(state="visible", timeout=120_000)
            password_input.wait_for(state="visible", timeout=120_000)
        except PlaywrightTimeoutError as error:
            login_wait_error = str(error)
        inputs = page.locator("input")
        if login_wait_error or inputs.count() < 2:
            probe_path = OUTPUT_DIR / "phase3-login-probe.png"
            page.screenshot(path=str(probe_path), full_page=True)
            probe = {
                "status": login_response.status if login_response else None,
                "url": page.url,
                "title": page.title(),
                "body": page.locator("body").inner_text()[:800],
                "input_count": inputs.count(),
                "wait_error": login_wait_error,
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": failed_requests,
                "http_failures": http_failures,
            }
            print(json.dumps(probe, ensure_ascii=True, indent=2))
            raise RuntimeError("登录页未渲染用户名和密码输入框")
        username_input.fill(username)
        password_input.fill(password)
        with page.expect_response(
            lambda response: response.url.endswith("/admin-api/system/auth/login")
            and response.request.method == "POST",
            timeout=20_000,
        ) as login_api:
            page.locator('button[aria-label="login"]').click()
        if login_api.value.status >= 400:
            raise RuntimeError(f"本地登录接口返回 {login_api.value.status}")
        page.wait_for_timeout(500)

        page.goto(BASE_URL, wait_until="domcontentloaded")
        review_response = page.goto(
            f"{BASE_URL}/dashboard/overview/index?review=phase3",
            wait_until="commit",
        )
        page.wait_for_timeout(1500)
        try:
            wait_for_review(page)
        except PlaywrightTimeoutError:
            review_probe_path = OUTPUT_DIR / "phase3-review-probe.png"
            page.screenshot(path=str(review_probe_path), full_page=True)
            review_probe = {
                "status": review_response.status if review_response else None,
                "url": page.url,
                "title": page.title(),
                "body": page.locator("body").inner_text()[:1200],
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": failed_requests,
                "http_failures": http_failures,
            }
            print(json.dumps(review_probe, ensure_ascii=True, indent=2))
            raise

        checks["review_route"] = "review=phase3" in page.url
        checks["vben_shell"] = (
            page.locator("#__vben_main_content .phase3-review").count() == 1
        )
        checks["snapshot_metrics"] = page.locator(".review-metric").count() == 4
        checks["vxe_grid"] = page.locator(".vxe-grid").count() == 1
        contract_ids = (
            "ZH02-2026-DEMO-01",
            "ZH02-2026-DEMO-02",
            "ZH02-2026-DEMO-03",
        )
        checks["contract_rows"] = all(
            page.get_by_text(contract_id, exact=True).count() >= 1
            for contract_id in contract_ids
        )
        checks["customer_supplier_split"] = (
            page.get_by_text("客户应收链", exact=True).count() == 1
            and page.get_by_text("供应商应付链", exact=True).count() == 1
        )
        page.screenshot(path=str(desktop_path), full_page=True)

        page.locator(".vxe-body--row").first.click()
        page.wait_for_selector(".contract-detail-hero", state="visible")
        checks["row_to_detail"] = (
            page.locator(".contract-detail-hero").is_visible()
            and page.locator(".evidence-node").count() == 4
        )
        checks["dual_identifier"] = (
            page.get_by_text(re.compile("ZH02-|SGSC"), exact=False).count() >= 2
        )
        page.screenshot(path=str(detail_path), full_page=True)

        click_screen(page, "数据核验", ".issue-grid")
        checks["review_issues"] = page.locator(".issue-card").count() == 4
        page.locator(".issue-card").first.click()
        page.wait_for_selector(".issue-drawer", state="visible")
        checks["vben_drawer"] = page.locator(".issue-drawer").count() == 1
        page.screenshot(path=str(review_path), full_page=True)
        page.keyboard.press("Escape")

        click_screen(page, "移动任务", ".mobile-device")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(500)
        page.get_by_text("快速核验", exact=True).click()
        checks["mobile_task_switch"] = (
            page.get_by_text("原值与候选值并排，不自动采用", exact=True).count() == 1
        )
        checks["mobile_no_body_overflow"] = page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        )
        page.evaluate("window.scrollTo(0, 0)")
        page.screenshot(path=str(mobile_path), full_page=True)
        browser.close()

    checks["desktop_dark_ratio"] = dark_pixel_ratio(desktop_path)
    checks["mobile_dark_ratio"] = dark_pixel_ratio(mobile_path)
    checks["desktop_dark_area_ok"] = checks["desktop_dark_ratio"] < 0.25
    checks["mobile_dark_area_ok"] = checks["mobile_dark_ratio"] < 0.25

    ignored_http = ("favicon", "iconify")
    relevant_http_failures = [
        failure
        for failure in http_failures
        if not any(marker in failure.lower() for marker in ignored_http)
    ]
    actionable_request_failures = [
        failure
        for failure in failed_requests
        if "net::ERR_ABORTED" not in failure
    ]
    checks["console_errors"] = console_errors
    checks["page_errors"] = page_errors
    checks["request_failures"] = actionable_request_failures
    checks["ignored_navigation_aborts"] = (
        len(failed_requests) - len(actionable_request_failures)
    )
    checks["http_failures"] = relevant_http_failures

    boolean_failures = [
        name for name, value in checks.items() if isinstance(value, bool) and not value
    ]
    runtime_failures = (
        console_errors
        + page_errors
        + actionable_request_failures
        + relevant_http_failures
    )
    report = {
        "status": "passed" if not boolean_failures and not runtime_failures else "failed",
        "boolean_failures": boolean_failures,
        "checks": checks,
        "screenshots": [
            str(desktop_path.relative_to(ROOT)),
            str(detail_path.relative_to(ROOT)),
            str(review_path.relative_to(ROOT)),
            str(mobile_path.relative_to(ROOT)),
        ],
    }
    report_path = OUTPUT_DIR / "phase3-vben-review-results.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
