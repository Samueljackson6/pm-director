"""Amount unit conversion utilities.

DB keeps mixed units: contracts/payments/finance = 万元, invoices/receipts = 元.
All API responses output amounts in 元. Frontend divides by 10000 for display.
"""


def wan_to_yuan(value):
    """Convert 万元 to 元."""
    if value is None:
        return None
    return round(value * 10000, 2)


def yuan_to_wan(value):
    """Convert 元 to 万元."""
    if value is None:
        return None
    return round(value / 10000, 2)


def convert_fields(obj, fields):
    """Convert specified fields in a dict from 万元 to 元."""
    if obj is None:
        return obj
    for field in fields:
        if field in obj and obj[field] is not None:
            obj[field] = wan_to_yuan(obj[field])
    return obj


def convert_list_fields(items, fields):
    """Convert specified fields in a list of dicts from 万元 to 元."""
    if items is None:
        return items
    for item in items:
        convert_fields(item, fields)
    return items
