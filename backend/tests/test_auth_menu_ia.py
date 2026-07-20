from collections.abc import Iterable

from fastapi.testclient import TestClient


REQUIRED_MENU_KEYS = {
    "id",
    "parentId",
    "name",
    "path",
    "component",
    "componentName",
    "icon",
    "visible",
    "keepAlive",
    "sort",
}


def _permission_menus(client: TestClient) -> list[dict]:
    response = client.get("/system/auth/get-permission-info")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    return body["data"]["menus"]


def _children(menu: dict) -> list[dict]:
    children = menu.get("children", [])
    assert isinstance(children, list)
    return children


def _visible(items: Iterable[dict]) -> list[dict]:
    return [item for item in items if item["visible"] is True]


def _full_path(parent_path: str, child_path: str) -> str:
    if child_path.startswith("/"):
        return child_path
    return f"{parent_path.rstrip('/')}/{child_path.lstrip('/')}"


def test_permission_menu_has_four_task_groups_in_business_order(
    client: TestClient,
) -> None:
    menus = _permission_menus(client)

    actual = [
        (menu["name"], menu["path"], menu["sort"])
        for menu in sorted(_visible(menus), key=lambda item: item["sort"])
    ]

    assert actual == [
        ("经营工作台", "/dashboard", 0),
        ("合同履约", "/contracts", 1),
        ("客户应收", "/customer-finance", 2),
        ("供应链", "/suppliers", 3),
    ]


def test_visible_business_routes_are_owned_by_the_four_task_groups(
    client: TestClient,
) -> None:
    menus = _permission_menus(client)
    visible_by_parent = {
        menu["name"]: {
            _full_path(menu["path"], child["path"]): (
                child["component"],
                child["componentName"],
            )
            for child in _visible(_children(menu))
        }
        for menu in _visible(menus)
    }

    assert visible_by_parent == {
        "经营工作台": {
            "/dashboard/overview/index": (
                "/dashboard/overview/index",
                "DashboardOverview",
            ),
        },
        "合同履约": {
            "/contracts/list": ("/contracts/index", "ContractList"),
            "/projects/list": ("/projects/index", "ProjectList"),
        },
        "客户应收": {
            "/customer-finance/invoices": (
                "/customer-finance/invoices/index",
                "CustomerInvoices",
            ),
            "/customer-finance/receipts": (
                "/customer-finance/receipts/index",
                "CustomerReceipts",
            ),
        },
        "供应链": {
            "/supplier-finance/invoices": (
                "/supplier-finance/invoices/index",
                "SupplierInvoices",
            ),
            "/supplier-finance/payments": (
                "/supplier-finance/payments/index",
                "SupplierPayments",
            ),
            "/suppliers/list": ("/suppliers/list/index", "SupplierList"),
        },
    }


def test_core_detail_routes_are_hidden_under_their_business_owner(
    client: TestClient,
) -> None:
    menus = _permission_menus(client)
    owner_by_detail_route = {
        _full_path(menu["path"], child["path"]): menu["name"]
        for menu in _visible(menus)
        for child in _children(menu)
        if child["visible"] is False
        and str(child["componentName"]).endswith("Detail")
    }

    assert owner_by_detail_route == {
        "/contracts/detail": "合同履约",
        "/customer-finance/invoice-detail": "客户应收",
        "/customer-finance/receipt-detail": "客户应收",
        "/projects/detail": "合同履约",
        "/supplier-finance/invoice-detail": "供应链",
        "/supplier-finance/payment-detail": "供应链",
        "/suppliers/detail": "供应链",
    }


def test_project_list_and_detail_are_formal_dynamic_routes(
    client: TestClient,
) -> None:
    menus = _permission_menus(client)
    contracts_group = next(menu for menu in menus if menu["path"] == "/contracts")
    project_routes = {
        child["componentName"]: child for child in _children(contracts_group)
        if str(child["componentName"]).startswith("Project")
    }

    assert project_routes["ProjectList"] == {
        "id": 23,
        "parentId": contracts_group["id"],
        "name": "项目台账",
        "path": "/projects/list",
        "component": "/projects/index",
        "componentName": "ProjectList",
        "icon": "",
        "visible": True,
        "keepAlive": False,
        "sort": 1,
    }
    assert project_routes["ProjectDetail"] == {
        "id": 24,
        "parentId": contracts_group["id"],
        "name": "项目详情",
        "path": "/projects/detail",
        "component": "/projects/detail",
        "componentName": "ProjectDetail",
        "icon": "",
        "visible": False,
        "keepAlive": False,
        "sort": 3,
    }


def test_every_dynamic_route_has_vben_required_fields_and_unique_identity(
    client: TestClient,
) -> None:
    menus = _permission_menus(client)
    items = [menu for menu in menus]
    items.extend(child for menu in menus for child in _children(menu))

    for item in items:
        assert REQUIRED_MENU_KEYS <= item.keys(), item.get("name", "未命名菜单")

    ids = [item["id"] for item in items]
    component_names = [item["componentName"] for item in items]
    assert len(ids) == len(set(ids))
    assert len(component_names) == len(set(component_names))
