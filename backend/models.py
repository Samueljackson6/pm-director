"""Shared response helpers: Vben-compatible wrappers and Pydantic models."""


def vben_response(data):
    """Wrap data in Vben's expected format: {code: 0, data: ...}"""
    return {'code': 0, 'data': data, 'message': 'success'}


def vben_list(page: int, size: int, total: int, items: list):
    """Paginated list in Vben format."""
    return {
        'code': 0,
        'data': {'total': total, 'page': page, 'size': size, 'items': items},
        'message': 'success',
    }
