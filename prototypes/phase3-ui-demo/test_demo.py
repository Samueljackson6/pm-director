# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ─── How to run ───
# PHASE3_DEMO_URL=http://127.0.0.1:4173 python test_demo.py

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Final

from playwright.sync_api import ConsoleMessage, Page, Request, Response, sync_playwright


BASE_URL: Final = os.environ.get("PHASE3_DEMO_URL", "http://127.0.0.1:4173")
ARTIFACT_DIR: Final = Path(
    os.environ.get("PHASE3_DEMO_ARTIFACT_DIR", ".devtest/phase3-demo-artifacts")
)


def register_diagnostics(
    page: Page,
    console_errors: list[str],
    page_errors: list[str],
    failed_requests: list[str],
    http_failures: list[str],
) -> None:
    def record_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            console_errors.append(message.text)

    def record_page_error(error: str) -> None:
        page_errors.append(error)

    def record_failed_request(request: Request) -> None:
        failed_requests.append(f"{request.method} {request.url}")

    def record_http_failure(response: Response) -> None:
        if response.status >= 400:
            http_failures.append(f"{response.status} {response.url}")

    page.on("console", record_console)
    page.on("pageerror", record_page_error)
    page.on("requestfailed", record_failed_request)
    page.on("response", record_http_failure)


def verify_desktop_flow(page: Page) -> None:
    page.goto(f"{BASE_URL}/#dashboard?view=all", wait_until="networkidle")
    page.get_by_test_id("page-dashboard").wait_for()
    page.get_by_test_id("view-finance").click()
    page.wait_for_url(re.compile(r"#dashboard\?view=finance$"))
    page.reload(wait_until="networkidle")
    page.get_by_test_id("view-finance").evaluate(
        "element => { if (!element.classList.contains('is-active')) throw new Error('视图状态未保持') }"
    )
    page.screenshot(path=str(ARTIFACT_DIR / "phase3-dashboard-desktop.png"), full_page=True)

    page.get_by_test_id("action-overdue").click()
    page.wait_for_url(re.compile(r"#receivables\?tab=invoice&filter=overdue$"))
    page.get_by_test_id("page-receivables").wait_for()

    page.get_by_test_id("nav-contracts").click()
    page.get_by_test_id("page-contracts").wait_for()
    page.locator("#contract-search").fill("管廊")
    page.get_by_role("button", name="应用筛选").click()
    page.wait_for_url(re.compile(r"#contracts\?q=.*&page=1&sort=next_action$"))
    if page.locator(".data-table tbody tr").count() != 1:
        raise AssertionError("合同关键词筛选结果数量不正确")

    page.locator(".data-table tbody tr:first-child .entity-link").first.click()
    page.get_by_test_id("page-contract-detail").wait_for()
    page.get_by_test_id("fulfillment-chain").wait_for()
    page.evaluate("document.activeElement?.blur()")
    page.screenshot(
        path=str(ARTIFACT_DIR / "phase3-contract-detail-desktop.png"),
        full_page=True,
    )
    page.get_by_role("button", name="进入项目").click()
    page.get_by_test_id("page-project-detail").wait_for()
    page.get_by_test_id("back-button").click()
    page.get_by_test_id("page-contract-detail").wait_for()
    page.get_by_test_id("back-button").click()
    page.get_by_test_id("page-contracts").wait_for()
    if "q=" not in page.url:
        raise AssertionError("合同详情返回后未保留列表筛选")

    page.locator('[data-action="toggle-theme"]').click()
    if page.locator("html").get_attribute("data-theme") != "dark":
        raise AssertionError("深色主题切换失败")
    page.locator("#review-state").select_option("error")
    page.get_by_role("heading", name="合同台账加载失败").wait_for()
    page.get_by_role("button", name="重新加载").click()
    page.get_by_test_id("page-contracts").wait_for()


def verify_mobile_flow(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/#dashboard?view=all", wait_until="networkidle")
    page.locator('[data-action="open-menu"]').click()
    page.locator("body.menu-open").wait_for()
    page.get_by_test_id("nav-suppliers").click()
    page.get_by_test_id("page-suppliers").wait_for()
    page.locator(".data-table tbody tr:first-child .entity-link").first.click()
    page.get_by_test_id("page-supplier-detail").wait_for()
    page.get_by_test_id("page-supplier-detail").get_by_role(
        "button", name="供应商发票"
    ).click()
    page.get_by_text("INV-GY-2026-071").wait_for()
    page.evaluate("document.activeElement?.blur()")
    page.locator(".skip-link").evaluate("element => element.style.display = 'none'")
    page.locator(".toast-region").evaluate("element => element.style.display = 'none'")
    page.screenshot(path=str(ARTIFACT_DIR / "phase3-supplier-mobile.png"), full_page=True)
    no_overflow = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    if not no_overflow:
        raise AssertionError("移动端页面存在横向溢出")


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []
    http_failures: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        register_diagnostics(
            page,
            console_errors,
            page_errors,
            failed_requests,
            http_failures,
        )
        verify_desktop_flow(page)
        verify_mobile_flow(page)
        context.close()
        browser.close()

    diagnostics = {
        "console_errors": console_errors,
        "page_errors": page_errors,
        "failed_requests": failed_requests,
        "http_failures": http_failures,
    }
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    if any(diagnostics.values()):
        raise AssertionError("浏览器诊断发现错误，请检查上方 JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
