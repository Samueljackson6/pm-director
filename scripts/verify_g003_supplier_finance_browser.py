from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from phase3_review_support import load_development_login, proxy_backend

BASE_URL = "http://127.0.0.1:18090/web"
DB_PATH = Path("database/project_management.db")


def digest() -> str:
    return hashlib.sha256(DB_PATH.read_bytes()).hexdigest()


def login(page: Page, username: str, password: str) -> None:
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded", timeout=60_000)
    page.locator('input[name="username"]').wait_for(state="visible", timeout=60_000)
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    with page.expect_response(
        lambda response: response.url.endswith("/admin-api/system/auth/login")
        and response.request.method == "POST",
        timeout=30_000,
    ) as login_response:
        page.locator('button[aria-label="login"]').click()
    if login_response.value.status >= 400:
        raise RuntimeError(f"local login returned HTTP {login_response.value.status}")
    page.wait_for_timeout(1_000)


def main() -> int:
    before = digest()
    username, password = load_development_login()
    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []
    http_failures: list[str] = []
    write_requests: list[str] = []
    api_responses: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 960}, locale="zh-CN")
        context.route(f"{BASE_URL}/admin-api/**", proxy_backend)
        context.route(f"{BASE_URL}/api/**", proxy_backend)
        page = context.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}") if request.url.startswith(BASE_URL) else None)
        page.on("response", lambda response: http_failures.append(f"{response.status} {response.request.method} {response.url}") if response.url.startswith(BASE_URL) and response.status >= 400 else None)

        def capture_request(request) -> None:
            if request.url.startswith(BASE_URL) and ("/api/" in request.url or "/admin-api/" in request.url) and request.method not in {"GET", "OPTIONS", "POST"}:
                write_requests.append(f"{request.method} {request.url}")

        def capture_response(response) -> None:
            if not response.url.startswith(BASE_URL):
                return
            if "/api/invoices" not in response.url and "/api/suppliers/payments" not in response.url:
                return
            try:
                body = response.json()
            except Exception:
                return
            api_responses.append({"url": response.url, "status": response.status, "body": body})

        page.on("request", capture_request)
        page.on("response", capture_response)
        login(page, username, password)

        with page.expect_response(lambda response: '/api/invoices' in response.url and response.request.method == 'GET', timeout=30_000) as invoice_api:
            page.goto(f"{BASE_URL}/supplier-finance/invoices", wait_until="domcontentloaded", timeout=60_000)
        invoice_response = invoice_api.value
        page.wait_for_timeout(500)
        invoice_text = page.locator('body').inner_text()
        page.screenshot(path="docs/audits/assets/g003-supplier-invoices-browser.png", full_page=True)

        with page.expect_response(lambda response: '/api/suppliers/payments' in response.url and response.request.method == 'GET', timeout=30_000) as payment_api:
            page.goto(f"{BASE_URL}/supplier-finance/payments", wait_until="domcontentloaded", timeout=60_000)
        payment_response = payment_api.value
        page.wait_for_timeout(500)
        payment_text = page.locator('body').inner_text()
        page.screenshot(path="docs/audits/assets/g003-supplier-payments-browser.png", full_page=True)
        relevant = [
            {"url": invoice_response.url, "status": invoice_response.status},
            {"url": payment_response.url, "status": payment_response.status},
        ]
        browser.close()
    after = digest()
    result = {
        "base_url": BASE_URL,
        "invoice_page_rendered": bool(invoice_text.strip()),
        "payment_page_rendered": bool(payment_text.strip()),
        "relevant_api_responses": relevant,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "failed_requests": failed_requests,
        "http_failures": http_failures,
        "write_requests": write_requests,
        "db_sha256_before": before,
        "db_sha256_after": after,
        "database_unchanged": before == after,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if any(entry["status"] != 200 for entry in relevant):
        print("supplier-finance read API returned a non-200 status", file=sys.stderr)
        return 2
    if not result["invoice_page_rendered"] or not result["payment_page_rendered"]:
        print("supplier-finance pages did not render", file=sys.stderr)
        return 3
    relevant_failed_requests = [
        item for item in failed_requests
        if '/api/' in item or '/admin-api/' in item
    ]
    if console_errors or page_errors or relevant_failed_requests or http_failures or write_requests or before != after:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
