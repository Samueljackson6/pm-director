from typing import NotRequired, TypedDict


class MenuItem(TypedDict):
    id: int
    parentId: int
    name: str
    path: str
    component: str
    componentName: str
    icon: str
    visible: bool
    keepAlive: bool
    sort: int
    children: NotRequired[list["MenuItem"]]


def _menu_item(
    *,
    menu_id: int,
    parent_id: int,
    name: str,
    path: str,
    component: str,
    component_name: str,
    sort: int,
    icon: str = "",
    visible: bool = True,
    children: list[MenuItem] | None = None,
) -> MenuItem:
    item: MenuItem = {
        "id": menu_id,
        "parentId": parent_id,
        "name": name,
        "path": path,
        "component": component,
        "componentName": component_name,
        "icon": icon,
        "visible": visible,
        "keepAlive": False,
        "sort": sort,
    }
    if children is not None:
        item["children"] = children
    return item


def _dashboard_menu() -> MenuItem:
    return _menu_item(
        menu_id=1,
        parent_id=0,
        name="经营工作台",
        path="/dashboard",
        component="BasicLayout",
        component_name="Dashboard",
        icon="lucide:layout-dashboard",
        sort=0,
        children=[
            _menu_item(
                menu_id=11, parent_id=1, name="分析页", path="analytics",
                component="/dashboard/analytics/index", component_name="Analytics",
                visible=False, sort=0,
            ),
            _menu_item(
                menu_id=12, parent_id=1, name="经营总览", path="overview/index",
                component="/dashboard/overview/index",
                component_name="DashboardOverview", sort=1,
            ),
        ],
    )


def _contract_menu() -> MenuItem:
    return _menu_item(
        menu_id=2,
        parent_id=0,
        name="合同履约",
        path="/contracts",
        component="BasicLayout",
        component_name="Contracts",
        icon="lucide:file-text",
        sort=1,
        children=[
            _menu_item(
                menu_id=21, parent_id=2, name="合同列表", path="list",
                component="/contracts/index", component_name="ContractList", sort=0,
            ),
            _menu_item(
                menu_id=22, parent_id=2, name="合同详情", path="detail",
                component="/contracts/detail", component_name="ContractDetail",
                visible=False, sort=2,
            ),
            _menu_item(
                menu_id=23, parent_id=2, name="项目台账", path="/projects/list",
                component="/projects/index", component_name="ProjectList", sort=1,
            ),
            _menu_item(
                menu_id=24, parent_id=2, name="项目详情", path="/projects/detail",
                component="/projects/detail", component_name="ProjectDetail",
                visible=False, sort=3,
            ),
        ],
    )


def _customer_finance_menu() -> MenuItem:
    return _menu_item(
        menu_id=3,
        parent_id=0,
        name="客户应收",
        path="/customer-finance",
        component="BasicLayout",
        component_name="CustomerFinance",
        icon="lucide:wallet",
        sort=2,
        children=[
            _menu_item(
                menu_id=31, parent_id=3, name="客户发票", path="invoices",
                component="/customer-finance/invoices/index",
                component_name="CustomerInvoices", sort=0,
            ),
            _menu_item(
                menu_id=32, parent_id=3, name="发票详情", path="invoice-detail",
                component="/customer-finance/invoices/detail",
                component_name="CustomerInvoiceDetail", visible=False, sort=1,
            ),
            _menu_item(
                menu_id=33, parent_id=3, name="客户回款", path="receipts",
                component="/customer-finance/receipts/index",
                component_name="CustomerReceipts", sort=2,
            ),
            _menu_item(
                menu_id=34, parent_id=3, name="回款详情", path="receipt-detail",
                component="/customer-finance/receipts/detail",
                component_name="CustomerReceiptDetail", visible=False, sort=3,
            ),
        ],
    )


def _supplier_menu() -> MenuItem:
    return _menu_item(
        menu_id=4,
        parent_id=0,
        name="供应链",
        path="/suppliers",
        component="BasicLayout",
        component_name="Suppliers",
        icon="lucide:users",
        sort=3,
        children=[
            _menu_item(
                menu_id=41, parent_id=4, name="供应商列表", path="list",
                component="/suppliers/list/index", component_name="SupplierList", sort=0,
            ),
            _menu_item(
                menu_id=42, parent_id=4, name="供应商详情", path="detail",
                component="/suppliers/detail/index", component_name="SupplierDetail",
                visible=False, sort=1,
            ),
            _menu_item(
                menu_id=51, parent_id=4, name="供应商发票",
                path="/supplier-finance/invoices",
                component="/supplier-finance/invoices/index",
                component_name="SupplierInvoices", sort=2,
            ),
            _menu_item(
                menu_id=52, parent_id=4, name="发票详情",
                path="/supplier-finance/invoice-detail",
                component="/supplier-finance/invoices/detail",
                component_name="SupplierInvoiceDetail", visible=False, sort=3,
            ),
            _menu_item(
                menu_id=53, parent_id=4, name="供应商付款",
                path="/supplier-finance/payments",
                component="/supplier-finance/payments/index",
                component_name="SupplierPayments", sort=4,
            ),
            _menu_item(
                menu_id=54, parent_id=4, name="付款详情",
                path="/supplier-finance/payment-detail",
                component="/supplier-finance/payments/detail",
                component_name="SupplierPaymentDetail", visible=False, sort=5,
            ),
        ],
    )


def build_permission_menus() -> list[MenuItem]:
    return [
        _dashboard_menu(),
        _contract_menu(),
        _customer_finance_menu(),
        _supplier_menu(),
    ]
