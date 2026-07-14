"""Verify Phase 3 Fix v2 changes."""
import os

BASE = r'D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\src\views'

files = ['customer-finance/invoices/detail.vue', 'supplier-finance/invoices/detail.vue']

checks = {
    'customer-finance': [
        ('Tax calc formula', 'amount * taxRate / (1 + taxRate)'),
        ('Total uses amount', 'return inv.value.amount || 0'),
        ('KPI label: tax-inclusive', '发票金额（含税）'),
        ('Amount card label', '发票金额（含税/元）'),
    ],
    'supplier-finance': [
        ('Tax calc formula', 'amount * taxRate / (1 + taxRate)'),
        ('Total uses amount', 'return inv.value.amount || 0'),
        ('KPI label: tax-inclusive', '发票金额（含税）'),
    ]
}

for fname in files:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    name = fname.split('/')[0]
    print(f'\n=== {fname} ===')
    for desc, kw in checks[name]:
        found = kw in c
        print(f'  {desc}: {"OK" if found else "MISSING"}')
