"""Shared response helpers: Vben-compatible wrappers and Pydantic models."""


def vben_response(data):
    """Wrap data in Vben's expected format: {code: 0, data: ...}"""
    return {'code': 0, 'data': data, 'message': 'success'}


def vben_list(page: int, size: int, total: int, items: list, data_state: str | None = None):
    """Paginated list in Vben format; data_state keeps zero, missing and pending data distinct."""
    data = {'total': total, 'page': page, 'size': size, 'items': items}
    if data_state is not None:
        data['data_state'] = data_state
    return {'code': 0, 'data': data, 'message': 'success'}
