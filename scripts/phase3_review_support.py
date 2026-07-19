from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from PIL import Image
from playwright.sync_api import Page, Route
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "ui-vben" / "apps" / "web-antd"
BACKEND_URL = "http://127.0.0.1:18080"


def load_development_login() -> tuple[str, str]:
    values: dict[str, str] = {}
    env_path = APP_ROOT / ".env.development"
    for raw_line in env_path.read_bytes().decode("latin-1").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    username = values.get("VITE_APP_DEFAULT_USERNAME")
    password = values.get("VITE_APP_DEFAULT_PASSWORD")
    if not username or not password:
        raise RuntimeError("开发环境未配置可用于本地验收的默认登录信息")
    return username, password


def dark_pixel_ratio(path: Path) -> float:
    with Image.open(path).convert("RGB") as image:
        thumbnail = image.copy()
        thumbnail.thumbnail((720, 1200))
        pixels = list(thumbnail.get_flattened_data())
    dark_pixels = sum(
        1
        for red, green, blue in pixels
        if (0.2126 * red + 0.7152 * green + 0.0722 * blue) < 48
    )
    return round(dark_pixels / len(pixels), 4)


def wait_for_review(page: Page) -> None:
    page.wait_for_selector(".phase3-review", state="visible", timeout=30_000)
    try:
        page.wait_for_load_state("networkidle", timeout=12_000)
    except PlaywrightTimeoutError:
        page.wait_for_timeout(1_000)


def click_screen(page: Page, label: str, selector: str) -> None:
    page.get_by_text(label, exact=True).last.click()
    page.wait_for_selector(selector, state="visible", timeout=10_000)


def proxy_backend(route: Route) -> None:
    request_url = urlsplit(route.request.url)
    backend_origin = urlsplit(BACKEND_URL)
    backend_path = request_url.path
    if backend_path.startswith("/admin-api"):
        backend_path = backend_path.removeprefix("/admin-api")
    target_url = urlunsplit(
        (
            backend_origin.scheme,
            backend_origin.netloc,
            backend_path,
            request_url.query,
            "",
        )
    )
    response = route.fetch(url=target_url)
    route.fulfill(response=response)
